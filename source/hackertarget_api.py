#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced HackerTarget API client with retry logic, error handling, session management, and caching.
"""

import time
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    APIError,
    RateLimitError,
    NetworkError,
    TimeoutError as CustomTimeoutError,
    ValidationError
)
from .logger import get_logger
from .utils import validate_target, clean_target


class HackerTargetAPI:
    """
    Enhanced API client for HackerTarget services.
    
    Features:
    - Automatic retries with exponential backoff
    - Connection pooling
    - Timeout handling
    - Rate limit detection
    - Detailed logging
    - Response validation
    """
    
    BASE_URL = "https://api.hackertarget.com"
    
    # API endpoint mappings
    ENDPOINTS = {
        1: "/mtr/",
        2: "/nping/",
        3: "/dnslookup/",
        4: "/reversedns/",
        5: "/hostsearch/",
        6: "/findshareddns/",
        7: "/zonetransfer/",
        8: "/whois/",
        9: "/geoip/",
        10: "/reverseiplookup/",
        11: "/nmap/",
        12: "/subnetcalc/",
        13: "/httpheaders/",
        14: "/pagelinks/",
    }
    
    # Tool names for better logging
    TOOL_NAMES = {
        1: "Traceroute (MTR)",
        2: "Ping Test",
        3: "DNS Lookup",
        4: "Reverse DNS",
        5: "Find DNS Host",
        6: "Find Shared DNS",
        7: "Zone Transfer",
        8: "Whois Lookup",
        9: "IP Location Lookup",
        10: "Reverse IP Lookup",
        11: "TCP Port Scan (Nmap)",
        12: "Subnet Lookup",
        13: "HTTP Header Check",
        14: "Extract Page Links",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        verify_ssl: bool = True,
        use_cache: bool = None,
    ):
        """
        Initialize the HackerTarget API client.
        
        Args:
            api_key: Optional API key for premium features
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retries
            verify_ssl: Verify SSL certificates
            use_cache: Enable caching (None = use config default)
        """
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.logger = get_logger()
        
        # Initialize cache
        if use_cache is None:
            from .config import get_config
            config = get_config()
            use_cache = config.get('cache', 'enabled', False)
        
        if use_cache:
            from .cache import get_cache
            self.cache = get_cache()
        else:
            self.cache = None
        
        # Create session with retry strategy
        self.session = self._create_session(max_retries, backoff_factor)
        
        cache_status = "enabled" if self.cache and self.cache.enabled else "disabled"
        self.logger.debug(f"HackerTargetAPI initialized with timeout={timeout}s, max_retries={max_retries}, cache={cache_status}")
    
    def _create_session(self, max_retries: int, backoff_factor: float) -> requests.Session:
        """
        Create a requests session with retry configuration.
        
        Args:
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retries
            
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'HackerTarget-CLI/3.0 (https://github.com/ismailtasdelen/hackertarget)'
        })
        
        return session
    
    def _build_url(self, choice: int, target: str) -> str:
        """
        Build the API URL for a given tool and target.
        
        Args:
            choice: Tool choice number (1-14)
            target: Target domain or IP
            
        Returns:
            Complete API URL
            
        Raises:
            ValidationError: If choice is invalid
        """
        if choice not in self.ENDPOINTS:
            raise ValidationError(
                f"Invalid tool choice: {choice}. Must be between 1 and {len(self.ENDPOINTS)}",
                field="choice"
            )
        
        endpoint = self.ENDPOINTS[choice]
        url = f"{self.BASE_URL}{endpoint}?q={target}"
        
        # Add API key if available
        if self.api_key:
            url += f"&apikey={self.api_key}"
        
        return url
    
    def _validate_response(self, response: requests.Response, tool_name: str) -> str:
        """
        Validate API response and handle errors.
        
        Args:
            response: Requests response object
            tool_name: Name of the tool being used
            
        Returns:
            Response text if valid
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        # Check for rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            self.logger.warning(f"Rate limit exceeded for {tool_name}")
            raise RateLimitError(retry_after=int(retry_after))
        
        # Check for other HTTP errors
        if response.status_code >= 400:
            error_msg = f"HTTP {response.status_code} error for {tool_name}"
            self.logger.error(error_msg)
            raise APIError(error_msg, status_code=response.status_code, response=response.text)
        
        # Check response content
        text = response.text.strip()
        
        if not text:
            raise APIError(f"Empty response from {tool_name}")
        
        # Check for API error messages
        error_indicators = [
            "error check your search parameter",
            "invalid",
            "API count exceeded",
            "please slow down"
        ]
        
        text_lower = text.lower()
        for indicator in error_indicators:
            if indicator in text_lower:
                if "api count" in text_lower or "slow down" in text_lower:
                    raise RateLimitError()
                raise APIError(f"API error: {text}", response=text)
        
        return text
    
    def query(self, choice: int, target: str, validate: bool = True, use_cache: bool = True) -> str:
        """
        Query the HackerTarget API with a specific tool.
        
        Args:
            choice: Tool choice number (1-14)
            target: Target domain or IP address
            validate: Whether to validate the target before querying
            use_cache: Whether to use cache for this query
            
        Returns:
            API response text
            
        Raises:
            ValidationError: If target validation fails
            APIError: If API request fails
            NetworkError: If network operation fails
            TimeoutError: If request times out
        """
        tool_name = self.TOOL_NAMES.get(choice, f"Tool {choice}")
        
        # Validate and clean target
        if validate:
            try:
                validate_target(target)
            except ValidationError as e:
                self.logger.error(f"Target validation failed: {e}")
                raise
        
        cleaned_target = clean_target(target)
        
        # Check cache first
        if use_cache and self.cache and self.cache.enabled:
            cached_result = self.cache.get(choice, cleaned_target)
            if cached_result:
                self.logger.info(f"Using cached result for {tool_name} on {cleaned_target}")
                return cached_result
        
        # Build URL
        try:
            url = self._build_url(choice, cleaned_target)
        except ValidationError as e:
            self.logger.error(f"URL building failed: {e}")
            raise
        
        self.logger.info(f"Querying {tool_name} for target: {cleaned_target}")
        self.logger.debug(f"Request URL: {url}")
        
        # Make request
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            # Validate response
            result = self._validate_response(response, tool_name)
            
            # Cache the result
            if use_cache and self.cache and self.cache.enabled:
                self.cache.set(choice, cleaned_target, result)
            
            self.logger.info(f"{tool_name} query completed successfully")
            self.logger.debug(f"Response length: {len(result)} characters")
            
            return result
            
        except requests.exceptions.Timeout:
            error_msg = f"Request timed out after {self.timeout} seconds"
            self.logger.error(f"{tool_name}: {error_msg}")
            raise CustomTimeoutError(error_msg, timeout=self.timeout)
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: Unable to reach HackerTarget API"
            self.logger.error(f"{tool_name}: {error_msg}")
            raise NetworkError(error_msg, original_error=e)
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            self.logger.error(f"{tool_name}: {error_msg}")
            raise NetworkError(error_msg, original_error=e)
    
    def batch_query(
        self,
        choice: int,
        targets: list,
        delay: float = 1.0,
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Query multiple targets with the same tool.
        
        Args:
            choice: Tool choice number (1-14)
            targets: List of target domains or IPs
            delay: Delay between requests in seconds
            continue_on_error: Continue on individual errors
            
        Returns:
            Dictionary with targets as keys and results/errors as values
        """
        results = {}
        tool_name = self.TOOL_NAMES.get(choice, f"Tool {choice}")
        
        self.logger.info(f"Starting batch query with {tool_name} for {len(targets)} targets")
        
        for i, target in enumerate(targets, 1):
            try:
                self.logger.debug(f"Processing target {i}/{len(targets)}: {target}")
                result = self.query(choice, target)
                results[target] = {"success": True, "data": result}
                
                # Delay between requests to avoid rate limiting
                if i < len(targets):
                    time.sleep(delay)
                    
            except Exception as e:
                error_msg = str(e)
                self.logger.warning(f"Error processing {target}: {error_msg}")
                results[target] = {"success": False, "error": error_msg}
                
                if not continue_on_error:
                    raise
        
        success_count = sum(1 for r in results.values() if r.get("success"))
        self.logger.info(f"Batch query completed: {success_count}/{len(targets)} successful")
        
        return results
    
    def get_tool_name(self, choice: int) -> str:
        """
        Get the name of a tool by its choice number.
        
        Args:
            choice: Tool choice number
            
        Returns:
            Tool name
        """
        return self.TOOL_NAMES.get(choice, f"Unknown Tool ({choice})")
    
    def close(self):
        """Close the API session."""
        if self.session:
            self.session.close()
            self.logger.debug("API session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Backward compatibility function
def hackertarget_api(choice: int, target: str) -> str:
    """
    Legacy API function for backward compatibility.
    
    Args:
        choice: Tool choice number (1-14)
        target: Target domain or IP
        
    Returns:
        API response text
    """
    with HackerTargetAPI() as api:
        return api.query(choice, target)

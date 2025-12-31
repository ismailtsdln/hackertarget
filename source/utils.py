#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility functions for HackerTarget CLI.
Includes validation, helper functions, and common operations.
"""

import re
import ipaddress
from typing import Union, List
from urllib.parse import urlparse
from .exceptions import ValidationError


def validate_domain(domain: str) -> bool:
    """
    Validate if a string is a valid domain name.
    
    Args:
        domain: The domain name to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If domain is invalid
    """
    if not domain or not isinstance(domain, str):
        raise ValidationError("Domain cannot be empty", field="domain")
    
    # Remove protocol if present
    if '://' in domain:
        domain = urlparse(domain).netloc or urlparse(domain).path
    
    # Remove port if present
    domain = domain.split(':')[0]
    
    # Basic domain validation regex
    domain_regex = re.compile(
        r'^(?:[a-zA-Z0-9]'  # First character
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'  # Sub domain
        r'+[a-zA-Z]{2,}$'  # Top level domain
    )
    
    if not domain_regex.match(domain):
        raise ValidationError(f"Invalid domain format: {domain}", field="domain")
    
    return True


def validate_ip(ip: str) -> bool:
    """
    Validate if a string is a valid IP address (IPv4 or IPv6).
    
    Args:
        ip: The IP address to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If IP is invalid
    """
    if not ip or not isinstance(ip, str):
        raise ValidationError("IP address cannot be empty", field="ip")
    
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        raise ValidationError(f"Invalid IP address format: {ip}", field="ip")


def validate_target(target: str) -> str:
    """
    Validate if a string is either a valid domain or IP address.
    
    Args:
        target: The target to validate (domain or IP)
        
    Returns:
        The validated target string
        
    Raises:
        ValidationError: If target is neither valid domain nor IP
    """
    if not target or not isinstance(target, str):
        raise ValidationError("Target cannot be empty", field="target")
    
    target = target.strip()
    
    # Try IP first
    try:
        validate_ip(target)
        return target
    except ValidationError:
        pass
    
    # Try domain
    try:
        validate_domain(target)
        return target
    except ValidationError:
        raise ValidationError(
            f"Invalid target: '{target}' is neither a valid domain nor IP address",
            field="target"
        )


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL cannot be empty", field="url")
    
    url_regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    if not url_regex.match(url):
        raise ValidationError(f"Invalid URL format: {url}", field="url")
    
    return True


def validate_port(port: Union[int, str]) -> int:
    """
    Validate if a value is a valid port number.
    
    Args:
        port: The port number to validate
        
    Returns:
        The port number as an integer
        
    Raises:
        ValidationError: If port is invalid
    """
    try:
        port_num = int(port)
        if not 1 <= port_num <= 65535:
            raise ValidationError(
                f"Port must be between 1 and 65535, got {port_num}",
                field="port"
            )
        return port_num
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid port format: {port}", field="port")


def clean_target(target: str) -> str:
    """
    Clean and normalize a target string.
    Removes protocol, port, path from URLs.
    
    Args:
        target: The target string to clean
        
    Returns:
        Cleaned target string
    """
    if not target:
        return target
    
    target = target.strip()
    
    # Remove protocol
    if '://' in target:
        parsed = urlparse(target)
        target = parsed.netloc or parsed.path
    
    # Remove port
    if ':' in target and not target.count(':') > 1:  # Not IPv6
        target = target.split(':')[0]
    
    # Remove path
    if '/' in target:
        target = target.split('/')[0]
    
    return target


def read_targets_from_file(filepath: str) -> List[str]:
    """
    Read targets from a file (one per line).
    
    Args:
        filepath: Path to the file containing targets
        
    Returns:
        List of target strings
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValidationError: If file is empty or has invalid content
    """
    try:
        with open(filepath, 'r') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not targets:
            raise ValidationError(f"File is empty or contains no valid targets: {filepath}")
        
        return targets
    except FileNotFoundError:
        raise ValidationError(f"File not found: {filepath}", field="file")
    except Exception as e:
        raise ValidationError(f"Error reading file: {str(e)}", field="file")


def format_output(data: str, style: str = "simple") -> str:
    """
    Format output data based on style.
    
    Args:
        data: The data to format
        style: Output style (simple, bordered, clean)
        
    Returns:
        Formatted string
    """
    if style == "bordered":
        lines = data.split('\n')
        max_len = max(len(line) for line in lines) if lines else 0
        border = "=" * (max_len + 4)
        formatted = [border]
        for line in lines:
            formatted.append(f"| {line.ljust(max_len)} |")
        formatted.append(border)
        return '\n'.join(formatted)
    
    elif style == "clean":
        # Remove empty lines and strip whitespace
        lines = [line.strip() for line in data.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    else:  # simple
        return data


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: The text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Ensure filename isn't empty
    if not filename:
        filename = "output"
    return filename

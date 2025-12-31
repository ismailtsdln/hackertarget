#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom exceptions for HackerTarget CLI.
These exceptions provide better error handling and more informative error messages.
"""


class HackerTargetException(Exception):
    """Base exception class for all HackerTarget errors."""
    pass


class APIError(HackerTargetException):
    """Raised when the HackerTarget API returns an error."""
    
    def __init__(self, message: str, status_code: int = None, response: str = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)
    
    def __str__(self):
        if self.status_code:
            return f"API Error (HTTP {self.status_code}): {self.message}"
        return f"API Error: {self.message}"


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, message: str = "API rate limit exceeded", retry_after: int = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
    
    def __str__(self):
        if self.retry_after:
            return f"Rate limit exceeded. Retry after {self.retry_after} seconds."
        return "Rate limit exceeded. Please wait before making more requests."


class ValidationError(HackerTargetException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)
    
    def __str__(self):
        if self.field:
            return f"Validation Error ({self.field}): {self.message}"
        return f"Validation Error: {self.message}"


class ConfigError(HackerTargetException):
    """Raised when configuration loading or parsing fails."""
    
    def __init__(self, message: str, config_file: str = None):
        self.message = message
        self.config_file = config_file
        super().__init__(self.message)
    
    def __str__(self):
        if self.config_file:
            return f"Config Error ({self.config_file}): {self.message}"
        return f"Config Error: {self.message}"


class CacheError(HackerTargetException):
    """Raised when cache operations fail."""
    
    def __init__(self, message: str, operation: str = None):
        self.message = message
        self.operation = operation
        super().__init__(self.message)
    
    def __str__(self):
        if self.operation:
            return f"Cache Error ({self.operation}): {self.message}"
        return f"Cache Error: {self.message}"


class NetworkError(HackerTargetException):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)
    
    def __str__(self):
        if self.original_error:
            return f"Network Error: {self.message} (Original: {str(self.original_error)})"
        return f"Network Error: {self.message}"


class TimeoutError(NetworkError):
    """Raised when a request times out."""
    
    def __init__(self, message: str = "Request timed out", timeout: float = None):
        super().__init__(message)
        self.timeout = timeout
    
    def __str__(self):
        if self.timeout:
            return f"Request timed out after {self.timeout} seconds"
        return "Request timed out"

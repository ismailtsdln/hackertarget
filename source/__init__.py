"""
HackerTarget CLI - Network reconnaissance and security testing toolkit.

This package provides a modern command-line interface for HackerTarget API services,
including DNS lookup, port scanning, whois, and many other network tools.
"""

__version__ = '3.0.0'
__author__ = 'İsmail Taşdelen'
__license__ = 'MIT'

from .hackertarget_api import HackerTargetAPI, hackertarget_api
from .exceptions import (
    HackerTargetException,
    APIError,
    RateLimitError,
    NetworkError,
    ValidationError,
)

__all__ = [
    'HackerTargetAPI',
    'hackertarget_api',
    'HackerTargetException',
    'APIError',
    'RateLimitError',
    'NetworkError',
    'ValidationError',
]

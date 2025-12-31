#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cache system for HackerTarget API responses.
Uses SQLite for persistent caching with TTL (Time To Live) support.
"""

import sqlite3
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Any
from datetime import datetime, timedelta

from .exceptions import CacheError
from .logger import get_logger


class Cache:
    """
    SQLite-based cache for API responses with TTL support.
    
    Features:
    - Persistent storage with SQLite
    - TTL (Time To Live) for automatic expiration
    - Cache statistics
    - Automatic cleanup of expired entries
    """
    
    def __init__(self, cache_dir: str = None, ttl: int = 3600, enabled: bool = True):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory for cache database
            ttl: Time to live in seconds (default: 1 hour)
            enabled: Whether caching is enabled
        """
        self.enabled = enabled
        self.ttl = ttl
        self.logger = get_logger()
        
        if not self.enabled:
            self.logger.debug("Cache is disabled")
            return
        
        # Set cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir).expanduser()
        else:
            self.cache_dir = Path.home() / '.hackertarget' / 'cache'
        
        # Create directory if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / 'cache.db'
        
        # Initialize database
        self._init_db()
        
        self.logger.debug(f"Cache initialized at {self.db_path} with TTL={ttl}s")
    
    def _init_db(self):
        """Initialize SQLite database with schema."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    tool_id INTEGER,
                    target TEXT,
                    hits INTEGER DEFAULT 0
                )
            ''')
            
            # Create index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON cache(expires_at)
            ''')
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            raise CacheError(f"Failed to initialize cache database: {e}", operation="init")
    
    def _make_key(self, tool_id: int, target: str) -> str:
        """
        Create cache key from tool ID and target.
        
        Args:
            tool_id: Tool choice number
            target: Target domain or IP
            
        Returns:
            SHA256 hash of the key
        """
        key_str = f"{tool_id}:{target.lower()}"
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get(self, tool_id: int, target: str) -> Optional[str]:
        """
        Get cached result.
        
        Args:
            tool_id: Tool choice number
            target: Target domain or IP
            
        Returns:
            Cached result if found and not expired, None otherwise
        """
        if not self.enabled:
            return None
        
        key = self._make_key(tool_id, target)
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get entry
            cursor.execute('''
                SELECT value, expires_at, hits 
                FROM cache 
                WHERE key = ?
            ''', (key,))
            
            row = cursor.fetchone()
            
            if row:
                value, expires_at, hits = row
                
                # Check if expired
                if time.time() < expires_at:
                    # Update hit count
                    cursor.execute('''
                        UPDATE cache 
                        SET hits = hits + 1 
                        WHERE key = ?
                    ''', (key,))
                    conn.commit()
                    
                    self.logger.debug(f"Cache HIT for {target} (tool {tool_id})")
                    conn.close()
                    return value
                else:
                    # Expired, delete it
                    cursor.execute('DELETE FROM cache WHERE key = ?', (key,))
                    conn.commit()
                    self.logger.debug(f"Cache EXPIRED for {target} (tool {tool_id})")
            else:
                self.logger.debug(f"Cache MISS for {target} (tool {tool_id})")
            
            conn.close()
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, tool_id: int, target: str, value: str) -> bool:
        """
        Store result in cache.
        
        Args:
            tool_id: Tool choice number
            target: Target domain or IP
            value: Result to cache
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        key = self._make_key(tool_id, target)
        created_at = int(time.time())
        expires_at = created_at + self.ttl
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Insert or replace
            cursor.execute('''
                INSERT OR REPLACE INTO cache 
                (key, value, created_at, expires_at, tool_id, target, hits)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            ''', (key, value, created_at, expires_at, tool_id, target))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Cached result for {target} (tool {tool_id})")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, tool_id: int, target: str) -> bool:
        """
        Delete cached entry.
        
        Args:
            tool_id: Tool choice number
            target: Target domain or IP
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.enabled:
            return False
        
        key = self._make_key(tool_id, target)
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cache WHERE key = ?', (key,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if deleted:
                self.logger.debug(f"Deleted cache for {target} (tool {tool_id})")
            
            return deleted
            
        except sqlite3.Error as e:
            self.logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cache')
            count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleared {count} cache entries")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Cache clear error: {e}")
            return False
    
    def cleanup(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            current_time = int(time.time())
            cursor.execute('DELETE FROM cache WHERE expires_at < ?', (current_time,))
            count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if count > 0:
                self.logger.info(f"Cleaned up {count} expired cache entries")
            
            return count
            
        except sqlite3.Error as e:
            self.logger.error(f"Cache cleanup error: {e}")
            return 0
    
    def stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.enabled:
            return {
                'enabled': False,
                'total_entries': 0,
                'expired_entries': 0,
                'active_entries': 0,
                'total_hits': 0,
                'cache_size_bytes': 0
            }
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            current_time = int(time.time())
            
            # Total entries
            cursor.execute('SELECT COUNT(*) FROM cache')
            total = cursor.fetchone()[0]
            
            # Expired entries
            cursor.execute('SELECT COUNT(*) FROM cache WHERE expires_at < ?', (current_time,))
            expired = cursor.fetchone()[0]
            
            # Total hits
            cursor.execute('SELECT SUM(hits) FROM cache')
            hits_sum = cursor.fetchone()[0] or 0
            
            # Database size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            conn.close()
            
            return {
                'enabled': True,
                'total_entries': total,
                'expired_entries': expired,
                'active_entries': total - expired,
                'total_hits': hits_sum,
                'cache_size_bytes': db_size,
                'cache_size_mb': round(db_size / 1024 / 1024, 2),
                'ttl_seconds': self.ttl,
                'cache_dir': str(self.cache_dir)
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Cache stats error: {e}")
            return {'error': str(e)}
    
    def get_top_targets(self, limit: int = 10) -> list:
        """
        Get most frequently cached targets.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of (target, tool_id, hits) tuples
        """
        if not self.enabled:
            return []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT target, tool_id, hits 
                FROM cache 
                WHERE expires_at > ? 
                ORDER BY hits DESC 
                LIMIT ?
            ''', (int(time.time()), limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Cache top targets error: {e}")
            return []


# Global cache instance
_cache_instance: Optional[Cache] = None


def get_cache(cache_dir: str = None, ttl: int = None, enabled: bool = None) -> Cache:
    """
    Get or create global cache instance.
    
    Args:
        cache_dir: Cache directory path
        ttl: Time to live in seconds
        enabled: Whether caching is enabled
        
    Returns:
        Cache instance
    """
    global _cache_instance
    
    # If instance exists and no parameters changed, return it
    if _cache_instance is not None and all(p is None for p in [cache_dir, ttl, enabled]):
        return _cache_instance
    
    # Create new instance with config
    from .config import get_config
    config = get_config()
    
    _cache_instance = Cache(
        cache_dir=cache_dir or config.get('cache', 'directory'),
        ttl=ttl or config.get('cache', 'ttl', 3600),
        enabled=enabled if enabled is not None else config.get('cache', 'enabled', False)
    )
    
    return _cache_instance

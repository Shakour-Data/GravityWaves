from typing import Any, Optional
import time

class CacheManager:
    """
    A simple in-memory cache manager with time-to-live (TTL) expiration support.

    Attributes:
        _cache (dict): Internal dictionary to store cached key-value pairs.
        _expiry (dict): Dictionary to store expiration timestamps for each key.
    """

    def __init__(self):
        """
        Initializes the CacheManager with empty cache and expiry dictionaries.
        """
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves the value associated with the given key from the cache if it exists and has not expired.

        Args:
            key (str): The key to look up in the cache.

        Returns:
            Optional[Any]: The cached value if present and valid; otherwise, None.
        """
        if key in self._cache and self._expiry.get(key, 0) > time.time():
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Sets a value in the cache with an optional time-to-live (TTL).

        Args:
            key (str): The key under which to store the value.
            value (Any): The value to cache.
            ttl (int, optional): Time-to-live in seconds. Defaults to 300 seconds (5 minutes).
        """
        self._cache[key] = value
        self._expiry[key] = time.time() + ttl

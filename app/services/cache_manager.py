from typing import Any, Optional
import time

class CacheManager:
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache and self._expiry.get(key, 0) > time.time():
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        self._cache[key] = value
        self._expiry[key] = time.time() + ttl

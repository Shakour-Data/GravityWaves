import time
import pytest
from app.services.cache_manager import CacheManager

def test_cache_set_and_get():
    cache = CacheManager()
    cache.set("key1", "value1", ttl=1)
    assert cache.get("key1") == "value1"

def test_cache_expiry():
    cache = CacheManager()
    cache.set("key2", "value2", ttl=1)
    time.sleep(1.1)
    assert cache.get("key2") is None

def test_cache_overwrite():
    cache = CacheManager()
    cache.set("key3", "value3", ttl=5)
    cache.set("key3", "new_value3", ttl=5)
    assert cache.get("key3") == "new_value3"

def test_cache_get_nonexistent_key():
    cache = CacheManager()
    assert cache.get("nonexistent") is None

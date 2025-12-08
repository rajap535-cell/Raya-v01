import os
import json
from typing import Optional, Dict

# Change this to relative path from cache.py to your cache file
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "final_raya_cache.json")



# Load cache at runtime
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            _CACHE: Dict[str, Dict] = json.load(f)
    except Exception:
        _CACHE = {}
else:
    _CACHE = {}

def _make_key(query: str, intent: str = "fact") -> str:
    """Create a unique cache key per query + intent type."""
    return f"{query.strip().lower()}::{intent}"

def cache_get(query: str, intent: str = "fact") -> Optional[str]:
    key = _make_key(query, intent)
    return _CACHE.get(key, {}).get("answer")

def cache_put(query: str, answer: str, sources: Dict[str, bool], intent: str = "fact"):
    key = _make_key(query, intent)
    _CACHE[key] = {
        "answer": answer,
        "sources": sources
    }
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_CACHE, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
def load_cache():
    """Return the entire cache dict."""
    return _CACHE

def save_cache(data):
    """Overwrite the cache file with provided data."""
    global _CACHE
    _CACHE = data
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_CACHE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[CACHE] save_cache error: {e}")

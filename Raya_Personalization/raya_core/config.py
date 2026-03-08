#cionfig.py Source weights / priorities and cache path
CACHE_PATH = "final_raya_cache.json"

# Priority used by aggregator (higher = preferred)
SOURCE_WEIGHTS = {
    "custom_db": 1.0,
    "wikipedia": 0.8,
    "news": 0.7,
    "arxiv": 0.7,
    "qa": 0.4,  # reserved for future (StackExchange/Quora, etc.)
}

# How many sentences we want in the final summary
SUMMARY_SENTENCES = 3

ENGINE_ORDER = ["qa", "local", "news", "wikipedia", "llm"]

# Number of sentences for Wikipedia fallback
WIKI_SENTENCES = 2
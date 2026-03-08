# config.py
import os

# ---- LLM / ChatGPT (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # put your key in env or here
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")  # or "gpt-4o-mini" etc.
ENABLE_LLM = bool(OPENAI_API_KEY)  # auto-disable if no key

# ---- Paths
DB_PATH = os.path.join(os.path.dirname(__file__), "raya.db")
CACHE_PATH = os.path.join(os.path.dirname(__file__), "final_raya_cache.json")

# ---- Orchestrator behavior
ENGINE_ORDER = ["local", "wikipedia", "llm"]  # priority: offline → web → LLM
WIKI_SENTENCES = 3

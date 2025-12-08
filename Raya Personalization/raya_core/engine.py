# engine.py - central routing for Q/A usage by RAYA CLI
import json, os, wikipedia, requests
from datetime import datetime

# local cache search using fuzzy matching
from difflib import get_close_matches

def search_local_knowledge(query):
    try:
        path = os.path.join(os.path.dirname(__file__), "final_raya_cache.json")
        if not os.path.exists(path):
            # also try parent directory
            path = os.path.join(os.path.dirname(__file__), "..", "final_raya_cache.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        knowledge = data.get("knowledge", data)
        keys = list(knowledge.keys())
        match = get_close_matches(query.lower().strip(), keys, n=1, cutoff=0.6)
        if match:
            entry = knowledge[match[0]]
            return entry.get("summary") or entry.get("answer")
    except Exception:
        pass
    return None

def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=3, auto_suggest=False)
    except Exception:
        return None

def search_online(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&no_html=1"
        r = requests.get(url, timeout=6)
        data = r.json()
        return data.get("AbstractText") or data.get("Heading") or None
    except Exception:
        return None

def fetch_live_news(topic):
    # simple placeholder - projects often use rss/news sources directly in CLI
    return f"Live news fetch not configured for '{topic}' (use the CLI news menu)." 

def format_answer(text):
    if not text:
        return "RAYA SAY: Sorry, I couldn't find an answer."
    if isinstance(text, str) and text.strip().startswith("RAYA SAY:"):
        return text.strip()
    return f"RAYA SAY: {text}"

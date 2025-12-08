# qa_engine.py - robust, always tries wiki → online → llm
import os, re, json, difflib, requests, wikipedia
from dataclasses import dataclass
from typing import Optional

DEBUG = os.getenv("RAYA_DEBUG", "1") == "1"

# Cache (optional)
CACHE_FILE = os.path.join(os.path.dirname(__file__), "final_raya_cache.json")
QA_CACHE = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            RAW_K = data.get("knowledge", data)
            QA_CACHE = {k.lower().strip(): v for k, v in RAW_K.items()}
    except Exception:
        QA_CACHE = {}

wikipedia.set_lang("en")

@dataclass
class QAResult:
    answer: Optional[str]
    source_type: str
    confidence: float = 0.7

# ---------------- utilities ----------------
def normalize_query(q: str) -> str:
    q = (q or "").lower().strip()
    q = re.sub(r'^(what is|who is|define|tell me about|explain|how old is)\s+', '', q)
    q = re.sub(r'^(a|an|the)\s+', '', q)
    return q.strip()

# ---------------- cache ----------------
def search_cache(query: str) -> Optional[QAResult]:
    q = normalize_query(query)
    # Exact match
    if q in QA_CACHE:
        entry = QA_CACHE[q]
        text = entry.get("summary") or entry.get("answer")
        if text:
            return QAResult(text, "cache", confidence=0.95)
    # Fuzzy match
    keys = list(QA_CACHE.keys())
    match = difflib.get_close_matches(q, keys, n=1, cutoff=0.7)
    if match:
        entry = QA_CACHE[match[0]]
        text = entry.get("summary") or entry.get("answer")
        if text:
            return QAResult(text, "cache", confidence=0.9)
    return None

# ---------------- wikipedia ----------------
def wiki_best_summary(query: str, max_pages: int = 3) -> QAResult:
    try:
        titles = wikipedia.search(query, results=max_pages)
    except Exception:
        titles = []
    for t in titles:
        if t and (t.lower() == query.lower() or query.lower() in t.lower()):
            try:
                summary = wikipedia.summary(t, sentences=3, auto_suggest=False)
                return QAResult(summary, "wikipedia", confidence=0.85)
            except Exception:
                continue
    for t in titles:
        try:
            summary = wikipedia.summary(t, sentences=2, auto_suggest=False)
            return QAResult(summary, "wikipedia", confidence=0.8)
        except Exception:
            continue
    try:
        summary = wikipedia.summary(query, sentences=2, auto_suggest=False)
        return QAResult(summary, "wikipedia", confidence=0.75)
    except Exception:
        return QAResult(None, "wikipedia", confidence=0.0)

# ---------------- online search ----------------
def search_online(query: str) -> QAResult:
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&no_html=1"
        r = requests.get(url, timeout=6)
        data = r.json()
        text = data.get("AbstractText") or data.get("Heading")
        if not text:
            # fallback to RelatedTopics
            topics = data.get("RelatedTopics", [])
            if topics and isinstance(topics, list):
                for t in topics:
                    if isinstance(t, dict):
                        text = t.get("Text")
                        if text:
                            break
        if text:
            return QAResult(text, "online", confidence=0.7)
    except Exception:
        pass
    return QAResult(None, "online", confidence=0.0)

# ---------------- LLM fallback ----------------
def llm_fallback(query: str) -> QAResult:
    try:
        from raya_core.local_llm import ask_llm
        ans = ask_llm(query)
        if ans:
            return QAResult(ans, "llm", confidence=0.65)
    except Exception:
        pass
    return QAResult(None, "llm", confidence=0.0)

# ---------------- main ----------------
def answer_question(question: str) -> QAResult:
    # 1. Cache
    cache_ans = search_cache(question)
    if cache_ans and cache_ans.answer:
        if DEBUG: print("[QA] Using cache")
        return cache_ans

    # 2. Wikipedia
    wiki_ans = wiki_best_summary(question)
    if wiki_ans and wiki_ans.answer:
        if DEBUG: print("[QA] Using Wikipedia")
        return wiki_ans

    # 3. Online search
    online_ans = search_online(question)
    if online_ans and online_ans.answer:
        if DEBUG: print("[QA] Using Online Search")
        return online_ans

    # 4. LLM fallback
    llm_ans = llm_fallback(question)
    if llm_ans and llm_ans.answer:
        if DEBUG: print("[QA] Using LLM Fallback")
        return llm_ans

    # 5. Absolute fallback
    return QAResult("Sorry, I couldn't find an answer.", "fallback", confidence=0.1)

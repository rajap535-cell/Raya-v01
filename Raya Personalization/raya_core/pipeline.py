# pipeline.py - robust, unified pipeline
import re
from typing import List, Tuple, Optional
from rapidfuzz import fuzz

from raya_core import qa_engine
from raya_core.cache import cache_get
from raya_core.custom_db import query_local_db
from raya_core.source_news_topic import search_topic_news
from raya_core.source_arxiv import search_arxiv
from aggregator import aggregate

Candidate = Tuple[str, str, float, Optional[dict]]

# ---------------- utilities ----------------
def _normalize(q: str) -> str:
    if not q:
        return ""
    q = q.lower().strip()
    q = re.sub(r"[^\w\s]", "", q)
    q = re.sub(r"\s+", " ", q)
    return q

def _fuzzy_match_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return fuzz.ratio(a, b) / 100.0  # 0..1

# ---------------- collect candidates ----------------
def _collect_candidates(user_text: str, db_file: str, intents: list) -> List[Candidate]:
    candidates: List[Candidate] = []
    q = user_text

    # 1. QA Engine (cache + wiki + online + llm)
    try:
        qa_res = qa_engine.answer_question(q)
        if qa_res and qa_res.answer:
            candidates.append(
                ("qa", qa_res.answer, qa_res.confidence, {"source_type": qa_res.source_type})
            )
    except Exception:
        pass

    # 2. Local DB
    try:
        local = query_local_db(db_file, q)
        if local:
            candidates.append(("custom_db", local, 0.9, None))
    except Exception:
        pass

    # 3. News (optional)
    try:
        if "news" in intents or any(k in q.lower() for k in ["latest", "breaking", "today"]):
            news_hits = search_topic_news(q)
            if news_hits:
                candidates.append(("news", "\n".join(news_hits[:6]), 0.55, None))
    except Exception:
        pass

    # 4. ArXiv / research papers (optional)
    try:
        if "research" in intents or any(k in q.lower() for k in ["paper", "study", "arxiv"]):
            ax = search_arxiv(q, max_results=3)
            if ax:
                candidates.append(("arxiv", ax, 0.5, None))
    except Exception:
        pass

    return candidates

# ---------------- scoring & selection ----------------
def _score_and_select(candidates: List[Candidate]) -> Tuple[Optional[Candidate], List[Candidate]]:
    if not candidates:
        return None, []

    scored = []
    for src, ans, conf, meta in candidates:
        score = (conf or 0.5) * min(len(ans)/100, 3.0)
        scored.append((src, ans, conf, meta, score))
    scored.sort(key=lambda t: t[4], reverse=True)

    best = scored[0][:4]
    extras = [t[:4] for t in scored[1:]]
    return best, extras

# ---------------- main pipeline ----------------
def run_pipeline(user_text: str, db_file: str, intents: list) -> Tuple[str, dict]:
    # 1. Collect candidates from QA Engine + DB + News + ArXiv
    candidates = _collect_candidates(user_text, db_file, intents)

    # 2. Score & select best candidate
    best, extras = _score_and_select(candidates)

    # 3. Build candidate pairs for aggregator
    best_pair = (best[0], best[1]) if best else None
    extras_pairs = [(src, ans) for src, ans, *_ in extras] if extras else []

    # 4. Aggregate final string
    final = aggregate(best_pair, extras_pairs)

    # 5. Metadata for debug / tracking
    metadata = {
        "candidates": [(c[0], c[2]) for c in candidates],
        "best_source": best[0] if best else None,
    }
    return final, metadata

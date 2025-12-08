# aggregator.py

from typing import List, Tuple
def aggregate(best_pair, extras_pairs):
    # combine results into a final answer
    return best_pair  # + maybe extras logic


HEADINGS = {
    "custom_db": "Local notes",
    "wikipedia": "Reference",
    "news": "News hits",
    "arxiv": "Research",
    "cache": "Curated Knowledge",
}

def _trim(text: str, limit: int = 1200) -> str:
    t = (text or "").strip()
    return t if len(t) <= limit else t[:limit-3] + "..."

def aggregate(best: tuple, extras: list) -> str:
    if not best:
        return "I couldn’t find an answer."

    src, body = best
    chunks = [f"Main Answer ({HEADINGS.get(src, src.title())}):\n{_trim(body)}"]

    used = {src}
    for src, body in extras:
        if not body or src in used:
            continue
        used.add(src)
        title = HEADINGS.get(src, src.title())
        chunks.append(f"{title}:\n{_trim(body)}")

    return "\n\n".join(chunks)

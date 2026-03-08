#source_arxiv.py
import feedparser
from urllib.parse import quote_plus

def search_arxiv(query: str, max_results: int = 3) -> str | None:
    """
    Simple arXiv query using RSS. No API key needed.
    """
    if not query:
        return None
    q = quote_plus(query)
    url = f"https://export.arxiv.org/api/query?search_query=all:{q}&sortBy=lastUpdatedDate&sortOrder=descending&max_results={max_results}"
    try:
        feed = feedparser.parse(url)
        items = []
        for e in feed.entries[:max_results]:
            title = (getattr(e, "title", "") or "").strip()
            when = (getattr(e, "updated", "") or getattr(e, "published", "") or "").strip()
            link = (getattr(e, "link", "") or "").strip()
            if title:
                items.append(f"{title} ({when})\n{link}")
        return "\n".join(items) if items else None
    except Exception:
        return None

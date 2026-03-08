# source_news_topic.py
import requests
import feedparser
import wikipedia

# Try multiple sources: NDTV, BBC, CNN, Al Jazeera
NEWS_FEEDS = {
    "ndtv": "https://feeds.feedburner.com/ndtvnews-top-stories",
    "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
    "cnn": "http://rss.cnn.com/rss/edition.rss",
    "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
}

def _fetch_from_feed(url: str, topic: str, max_items: int = 10):
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:30]:  # take more, filter later
            title = entry.get("title", "")
            if topic.lower() in title.lower():
                results.append(title.strip())
            if len(results) >= max_items:
                break
        return results
    except Exception as e:
        print(f"[WARN] Failed fetching from {url}: {e}")
        return []

def search_topic_news(topic: str, max_items: int = 10):
    """
    Search topic-related news from multiple feeds.
    If no matches → fallback to Wikipedia summary lines.
    """
    topic = topic.strip()
    if not topic:
        return []

    results = []
    for name, url in NEWS_FEEDS.items():
        hits = _fetch_from_feed(url, topic, max_items)
        if hits:
            results.extend(hits)
        if len(results) >= max_items:
            break

    # Deduplicate + trim
    results = list(dict.fromkeys(results))[:max_items]

    # Wikipedia fallback if no live news found
    if not results:
        try:
            print(f"[DEBUG] Falling back to Wikipedia for topic: {topic}")
            summary = wikipedia.summary(topic, sentences=3, auto_suggest=False, redirect=True)
            results = [line.strip() for line in summary.split(". ") if line.strip()][:max_items]
        except Exception as e:
            print(f"[WARN] Wikipedia fallback failed for {topic}: {e}")
            results = []

    return results

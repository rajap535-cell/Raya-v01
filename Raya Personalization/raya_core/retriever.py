# raya_core/retriever.py
import sqlite3, os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
DB_FILE = os.getenv("DB_FILE", "raya_conversation.db")

def last_conversation(n=6):
    try:
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT user_input, ai_output FROM conversations ORDER BY id DESC LIMIT ?", (n,))
        rows = c.fetchall(); conn.close()
        parts = []
        for u,a in reversed(rows):
            parts.append(f"User: {u}\nRAYA: {a}")
        return "\n".join(parts)
    except:
        return ""

def latest_news_snippets(limit=5):
    try:
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT content FROM raya_data WHERE data_type LIKE '%news%' ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall(); conn.close()
        return [r[0] for r in rows]
    except:
        return []

def build_context(user_query: str) -> str:
    history = last_conversation(6)
    news = latest_news_snippets(5)
    parts = ["System: You are RAYA, a helpful assistant. Answer concisely and cite sources if available."]
    if history: parts.append("Conversation history:\n" + history)
    if news: parts.append("Recent news:\n" + ("\n".join(news)))
    parts.append("User query:\n" + user_query)
    return "\n\n".join(parts)

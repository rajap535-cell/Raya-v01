import sqlite3

def query_local_db(db_file: str, text: str, max_chars: int = 1000) -> str | None:
    """
    Looks for relevant content in your existing SQLite:
      - raya_data.content
      - conversations.ai_output
    Returns the most recent hit up to max_chars.
    """
    try:
        like = f"%{text}%"
        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        # Try raya_data first
        c.execute("SELECT content FROM raya_data WHERE content LIKE ? ORDER BY id DESC LIMIT 1", (like,))
        row = c.fetchone()
        if row and row[0]:
            conn.close()
            return row[0][:max_chars]

        # Then conversations
        c.execute("SELECT ai_output FROM conversations WHERE ai_output LIKE ? ORDER BY id DESC LIMIT 1", (like,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            return row[0][:max_chars]

        return None
    except Exception:
        return None

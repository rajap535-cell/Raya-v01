# raya_core/local_llm.py
import os, requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LOCAL_MODEL = os.getenv("LOCAL_MODEL_NAME", "llama3.2:3b")

def ask_local(prompt, max_tokens=512):
    """
    Call Ollama local REST /api/generate. Returns string or error string.
    """
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {"model": LOCAL_MODEL, "prompt": prompt, "max_tokens": max_tokens}
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        j = r.json()
        if "choices" in j and j["choices"]:
            c = j["choices"][0]
            # Ollama returns choice.message.content or choice.text
            if isinstance(c, dict):
                if "message" in c and isinstance(c["message"], dict):
                    return c["message"].get("content","").strip()
                if "text" in c:
                    return c.get("text","").strip()
                if "content" in c:
                    return c.get("content","").strip()
        # fallback raw
        return str(j)
    except Exception as e:
        return f"[local_error] {e}"

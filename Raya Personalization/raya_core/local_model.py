# raya_core/local_model.py
import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LOCAL_MODEL_NAME = "llama3.2:3b"
LOCAL_API_URL = f"{OLLAMA_HOST}/api/generate"


def ask_local(prompt: str, timeout: int = 30) -> str:
    """
    Sends prompt to local Ollama (llama3.2:3b).
    Non-streaming, deterministic, safe for routing.
    """

    if not prompt or not prompt.strip():
        return "[local error] empty prompt"

    payload = {
        "model": LOCAL_MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            LOCAL_API_URL,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        data = response.json()

        # Ollama standard response
        text = data.get("response", "")

        if not text or not text.strip():
            return "[local error] empty response"

        return text.strip()

    except requests.exceptions.Timeout:
        return "[local error] timeout"

    except requests.exceptions.ConnectionError:
        return "[local error] ollama not running"

    except Exception as e:
        return f"[local error] {str(e)}"

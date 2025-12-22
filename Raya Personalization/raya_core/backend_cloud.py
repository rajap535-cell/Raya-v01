# raya_core/backend_cloud.py
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


OPENAI_API_KEY = os.getenv("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")
CLOUD_MODEL_NAME = os.getenv("CLOUD_MODEL_NAME", "gpt-4o-mini")

# Initialize client only if key exists
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Soft limits (enforced later)
MAX_CLOUD_CALLS_PER_DAY = int(os.getenv("MAX_CLOUD_CALLS_PER_DAY", "1000"))


def ask_cloud(prompt, max_tokens=800, temperature=0.2):
    """
    Cloud LLM call using new OpenAI SDK.
    Gracefully disables itself if API key is missing.
    """
    if not client:
        return "[cloud disabled] OPENAI_API_KEY not set"

    try:
        response = client.chat.completions.create(
            model=CLOUD_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are RAYA, a precise assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[cloud error] {e}"

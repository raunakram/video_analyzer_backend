# OPENROUTER_API_KEY = "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"
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


import time
import requests
import os




FREE_MODELS = [
    "mistralai/mistral-7b-instruct:free",
    "openchat/openchat-7b:free",
    "gryphe/mythomist-7b:free"
]

def summarize_video_with_openrouter(context_text: str) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "video-analyzer"
    }

    system_prompt = (
        "You are a professional video summarization assistant. "
        "When information is limited, describe patterns, structure, and themes."
    )

    last_error = None

    for model in FREE_MODELS:
        for attempt in range(2):  # retry per model
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": context_text
                    }
                ],
                "temperature": 0.4,
                "max_tokens": 400
            }

            try:
                response = requests.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                # Success
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]

                # Rate limit → retry
                if response.status_code == 429:
                    time.sleep(2)
                    continue

                # Other errors → try next model
                last_error = response.text
                break

            except requests.RequestException as e:
                last_error = str(e)
                time.sleep(1)

    # Graceful fallback (never throw 500)
    return (
        "A detailed summary could not be generated at this moment due to "
        "temporary service limits. Please try again shortly."
    )

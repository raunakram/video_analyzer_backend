import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3:8b"

def ask_llm(messages):
    """
    messages: [{role: system|user|assistant, content: str}]
    """

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    res = requests.post(OLLAMA_URL, json=payload, timeout=120)
    res.raise_for_status()

    return res.json()["message"]["content"]

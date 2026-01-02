from google import genai
import os


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyB_hVgO9DWogYHzOa7czzwM_n9p_7VqyWo"
MODEL = "gemini-2.5-flash"


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def ask_gemini(messages):
    """
    messages: list of {role, content}
    """

    # Convert messages to a single prompt
    prompt = "\n\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in messages
        if m["role"] != "system"
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text

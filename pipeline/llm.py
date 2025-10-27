import os
from typing import Optional, List
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

MODEL_DEFAULT = os.getenv("LLM_MODEL", "gpt-4o-mini")  # fast/cheap; change as you like

def generate_markdown(system_prompt: str, user_prompt: str) -> str:
    """
    Uses OpenAI if OPENAI_API_KEY is set; otherwise returns a safe fallback text.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return _fallback(user_prompt)

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=MODEL_DEFAULT,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]
    )
    return resp.choices[0].message.content.strip()

def _fallback(user_prompt: str) -> str:
    # Extractive fallback: just return the last section of the prompt after 'NOTES:'
    # so the pipeline still runs in environments without an API key.
    parts = user_prompt.split("NOTES:", 1)
    if len(parts) == 2:
        return "*(LLM disabled — showing extractive fallback)*\n\n" + parts[1][:3000]
    return "*(LLM disabled — no content)*"


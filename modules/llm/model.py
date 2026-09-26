"""
LLM model utilities for the Resume Parser.

Provides a function to extract structured resume information using the
Groq LLM. The function combines a system prompt (defined in
`modules/prompts/resume_system_prompt.xml`) with a user prompt containing
the markdown representation of the resume.
"""

import json
from pathlib import Path

from core.client import groq_client, DEFAULT_MODEL

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Resolve the location of the XML system prompt relative to this file.
_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "resume_system_prompt.xml"


def _load_system_prompt() -> str:
    """Read the XML system prompt and return it as a string.

    Raises
    ------
    FileNotFoundError
        If the prompt file cannot be read.
    """
    try:
        return _PROMPT_PATH.read_text(encoding="utf-8")
    except Exception as exc:
        raise FileNotFoundError(f"Could not read system prompt at {_PROMPT_PATH}: {exc}")


def extract_resume(markdown: str) -> dict:
    """Extract structured resume data from a markdown string.

    Parameters
    ----------
    markdown: str
        The markdown representation of the resume (produced by the
        Unstructured parser).

    Returns
    -------
    dict
        A dictionary conforming to the ExpectedSchema defined in the
        system prompt. If the LLM response cannot be parsed as JSON, the
        raw text is returned under the ``'raw_response'`` key.
    """
    system_prompt = _load_system_prompt()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": markdown},
    ]

    response = groq_client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        max_tokens=4000,
        temperature=0,
    )

    # The Groq SDK returns an object with ``choices``; pick the first.
    # Compatibility with possible SDK structures.
    # Print the raw response for debugging (optional)
    print("Response:\n", response)
    # Extract content handling both object and dict message types
    content = ""
    if hasattr(response, "choices"):
        first = response.choices[0]
        message = getattr(first, "message", None)
        if isinstance(message, dict):
            content = message.get("content", "")
        else:
            # Assume object with .content attribute
            content = getattr(message, "content", "")
    elif isinstance(response, dict) and response.get("choices"):
        first = response["choices"][0]
        message = first.get("message", {})
        if isinstance(message, dict):
            content = message.get("content", "")
        else:
            content = getattr(message, "content", "")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"raw_response": content}

__all__ = ["extract_resume"]

# core/client.py
"""
Core client module.

Initialises the Groq API client using the API key defined in
`core.config.settings`.  The client can be imported from any other module
and used to call Groq LLM endpoints.

Example
-------
>>> from core.client import groq_client, DEFAULT_MODEL
>>> response = groq_client.chat.completions.create(
...     model=DEFAULT_MODEL,
...     messages=[{"role": "user", "content": "Hello"}],
... )
"""

from __future__ import annotations

from groq import Groq  # type: ignore  # Groq SDK provides the `Groq` class
from core.config import settings

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
# Choose a high‑performing, generally available model as the default.
# Adjust as needed based on your subscription / quota.
DEFAULT_MODEL: str = "openai/gpt-oss-120b"

# --------------------------------------------------------------------------- #
# Initialise the Groq client
# --------------------------------------------------------------------------- #
# The Groq SDK expects the API key to be passed via the `api_key` argument.
# `settings.groq_api_key` reads the value from the `.env` file (or environment).
groq_client = Groq(api_key=settings.groq_api_key)

__all__ = ["groq_client", "DEFAULT_MODEL"]

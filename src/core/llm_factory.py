"""Centralise la création des clients LLM.

Un seul endroit à modifier pour changer de modèle ou de provider.
"""

import os
from langchain_ollama import ChatOllama

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemma4:e2b")
DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_llm(model: str | None = None, temperature: float = 0, json_mode: bool = True):
    """Retourne un client LLM configuré."""
    return ChatOllama(
        model=model or DEFAULT_MODEL,
        base_url=DEFAULT_BASE_URL,
        temperature=temperature,
        format="json" if json_mode else None,
    )
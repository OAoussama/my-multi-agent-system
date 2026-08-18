"""Utilitaires de parsing des réponses LLM, partagés par tous les agents."""

import json


def extract_json(raw_text: str) -> dict:
    """Extrait un objet JSON même si le LLM l'entoure de ``` ou de texte."""
    text = raw_text.strip()
    if "```" in text:
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        text = text.removeprefix("json").strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)
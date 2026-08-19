"""Schémas de requête/réponse standardisés, communs à tous les agents.

Chaque agent peut étendre AgentRequest/AgentResponse si besoin de champs
spécifiques, mais doit rester compatible avec ce contrat de base — c'est
ce contrat que consomment l'orchestrateur (Manager IA) et les endpoints API.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Requête standard envoyée à n'importe quel agent."""

    company_id: str = Field(..., description="Identifiant de l'entreprise")
    objective_id: Optional[str] = Field(None, description="Objectif lié, si applicable")
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Données spécifiques à l'agent (ex. objectif texte, vision du CEO...)",
    )


class AgentResponse(BaseModel):
    """Réponse standard retournée par n'importe quel agent."""

    agent: str = Field(..., description="Clé de l'agent qui a répondu (ex. 'ceo')")
    status: str = Field(default="success", description="'success' ou 'error'")
    result: dict[str, Any] = Field(
        default_factory=dict,
        description="Résultat structuré de l'agent (vision, plan, scénarios...)",
    )
    error: Optional[str] = Field(None, description="Message d'erreur si status == 'error'")


# --- Exemples de schémas spécifiques (à étendre par agent si besoin) -------

class CeoResult(BaseModel):
    vision: str
    strategic_axes: list[str]


class CooResult(BaseModel):
    operational_plan: list[str]
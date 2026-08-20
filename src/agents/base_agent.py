"""Classe abstraite commune à tous les agents + registre dynamique.

Chaque agent (CEO, COO, PMO...) hérite de BaseAgent et s'enregistre
automatiquement via le décorateur @register_agent.
Stateless : aucun état conservé entre deux appels à run().
"""

from abc import ABC, abstractmethod
from typing import Dict, Type

from src.core.llm_factory import get_llm


class BaseAgent(ABC):
    """Interface commune à tous les agents spécialisés."""

    name: str = "base_agent"
    role: str = "Rôle non défini"

    def __init__(self, llm=None):
        # llm injecté depuis l'extérieur (llm_factory.py) — pas d'état métier ici
        self.llm = llm or get_llm()

    @abstractmethod
    def analyze(self, request: dict) -> dict:
        """Analyse l'input reçu et prépare le contexte nécessaire à l'appel LLM.

        Ex. extraire les champs utiles, valider les données, construire le prompt.
        """
        raise NotImplementedError

    @abstractmethod
    def respond(self, context: dict) -> dict:
        """Appelle le LLM avec le contexte préparé et retourne une réponse structurée."""
        raise NotImplementedError

    def run(self, request: dict) -> dict:
        """Point d'entrée unique : analyze() -> respond(). Ne pas surcharger."""
        context = self.analyze(request)
        return self.respond(context)


# --- Registre dynamique des agents -----------------------------------------

AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {}


def register_agent(agent_key: str):
    """Décorateur : enregistre une classe d'agent sous une clé (ex. "ceo")."""

    def decorator(cls: Type[BaseAgent]):
        if agent_key in AGENT_REGISTRY:
            raise ValueError(f"Un agent est déjà enregistré sous la clé '{agent_key}'")
        AGENT_REGISTRY[agent_key] = cls
        return cls

    return decorator


def get_agent(agent_key: str, llm=None) -> BaseAgent:
    """Instancie et retourne l'agent correspondant à agent_key."""
    if agent_key not in AGENT_REGISTRY:
        raise ValueError(
            f"Agent inconnu : '{agent_key}'. Agents disponibles : {list(AGENT_REGISTRY)}"
        )
    agent_cls = AGENT_REGISTRY[agent_key]
    return agent_cls(llm=llm)


def list_agents() -> list[str]:
    """Liste les clés de tous les agents actuellement enregistrés."""
    return list(AGENT_REGISTRY.keys())
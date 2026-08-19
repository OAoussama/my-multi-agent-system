"""Endpoints REST des agents spécialisés (Lot D).

Les agents sont résolus dynamiquement via le registre (get_agent), donc
ajouter un nouvel agent ne demande aucune modification ici au-delà de sa route.
"""

from fastapi import APIRouter, HTTPException

from src.agents.base_agent import get_agent, list_agents
from src.models.agent_schemas import AgentRequest, AgentResponse

# Import obligatoire : déclenche l'enregistrement des agents dans le registre
import src.agents.ceo_agent  # noqa: F401
import src.agents.coo_agent  # noqa: F401

router = APIRouter(prefix="/agents", tags=["agents"])


def _run_agent(agent_key: str, request: AgentRequest) -> AgentResponse:
    """Exécute un agent et convertit toute erreur en réponse standardisée."""
    try:
        agent = get_agent(agent_key)
        result = agent.run(request.model_dump())
        return AgentResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        return AgentResponse(agent=agent_key, status="error", error=str(exc))


@router.post("/ceo/define-strategy", response_model=AgentResponse)
def ceo_define_strategy(request: AgentRequest) -> AgentResponse:
    """Génère une vision et des axes stratégiques à partir d'un objectif.

    payload attendu : {"objective": "Augmenter le CA de 20% en 3 mois"}
    """
    return _run_agent("ceo", request)


@router.post("/coo/build-plan", response_model=AgentResponse)
def coo_build_plan(request: AgentRequest) -> AgentResponse:
    """Transforme la stratégie du CEO en plan opérationnel détaillé.

    payload attendu : {"vision": "...", "strategic_axes": [...], "context": "..."}
    """
    return _run_agent("coo", request)


@router.get("/")
def get_registered_agents() -> dict:
    """Liste les agents actuellement enregistrés — utile pour le Lot B."""
    return {"agents": list_agents()}
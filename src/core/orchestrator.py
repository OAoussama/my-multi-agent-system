"""Manager IA — Orchestrateur basé sur LangGraph (Graph API).

Version minimale : 2 nœuds (CEO -> COO) pour valider que le flux
et l'état circulent correctement, avant d'ajouter les 7 autres agents.
"""

from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from src.agents.ceo_agent import run_ceo_agent
from src.agents.coo_agent import run_coo_agent


# 1. L'état partagé qui circule entre les nœuds du graphe
class WorkflowState(TypedDict):
    objective: str
    vision: str
    strategic_axes: List[str]
    operational_plan: List[str]


# 2. Les nœuds : chaque nœud appelle un agent stateless et met à jour l'état
def ceo_node(state: WorkflowState) -> dict:
    result = run_ceo_agent({"objective": state["objective"]})
    return {
        "vision": result.get("vision", ""),
        "strategic_axes": result.get("strategic_axes", []),
    }


def coo_node(state: WorkflowState) -> dict:
    result = run_coo_agent({
        "vision": state["vision"],
        "strategic_axes": state["strategic_axes"],
    })
    return {"operational_plan": result.get("operational_plan", [])}


# 3. Construction du graphe
def build_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("ceo", ceo_node)
    graph.add_node("coo", coo_node)

    graph.set_entry_point("ceo")
    graph.add_edge("ceo", "coo")
    graph.add_edge("coo", END)

    return graph.compile()


# 4. Point d'entrée utilisé par l'API plus tard
orchestrator = build_graph()


# Test rapide en local : python src/core/orchestrator.py
if __name__ == "__main__":
    initial_state = {
        "objective": "Augmenter le CA de 20% en 3 mois",
        "vision": "",
        "strategic_axes": [],
        "operational_plan": [],
    }

    final_state = orchestrator.invoke(initial_state)

    print("Vision :", final_state["vision"])
    print("Axes stratégiques :", final_state["strategic_axes"])
    print("Plan opérationnel :", final_state["operational_plan"])
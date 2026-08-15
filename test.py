"""Test manuel du workflow Manager IA en local.

Vérifie que l'état circule bien entre les nœuds (CEO -> COO)
et que le graphe LangGraph fonctionne de bout en bout.

Usage : python test.py
"""

from src.core.orchestrator import orchestrator


def main():
    initial_state = {
        "objective": "Augmenter le CA de 20% en 3 mois",
        "vision": "",
        "strategic_axes": [],
        "operational_plan": [],
    }

    print("Objectif envoyé :", initial_state["objective"])
    print("Exécution du workflow...\n")

    final_state = orchestrator.invoke(initial_state)

    print("Vision :", final_state["vision"])
    print("Axes stratégiques :", final_state["strategic_axes"])
    print("Plan opérationnel :", final_state["operational_plan"])


if __name__ == "__main__":
    main()
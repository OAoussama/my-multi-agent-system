"""PMO Agent — construit la roadmap, le planning, les dépendances et les jalons.

Prend en entrée le plan opérationnel du COO et le transforme en roadmap
séquencée avec jalons et dépendances explicites.
"""

import json

from src.agents.base_agent import BaseAgent, register_agent
from src.utils.parsing import extract_json

SYSTEM_PROMPT = """Tu es le PMO Agent de Virtual AI Manager.
Ton rôle : à partir d'un plan opérationnel, tu construis une roadmap séquencée
avec des phases, des jalons mesurables et les dépendances entre les tâches.

Règles :
- Chaque tâche a un identifiant court et unique (T1, T2, T3...).
- Le champ "depends_on" liste les identifiants des tâches qui doivent être
  terminées avant celle-ci. Une tâche sans prérequis a une liste vide.
- Ne crée jamais de dépendance circulaire.
- Les jalons marquent la fin d'une phase et sont mesurables.
- Respecte l'horizon temporel indiqué dans le contexte.

Réponds UNIQUEMENT en JSON valide, avec ce format exact :
{
  "phases": [
    {
      "name": "...",
      "duration_weeks": 4,
      "tasks": [
        {"id": "T1", "label": "...", "owner_role": "...", "depends_on": [], "duration_days": 5}
      ]
    }
  ],
  "milestones": [
    {"name": "...", "target_week": 4, "success_criteria": "..."}
  ],
  "critical_path": ["T1", "T3"]
}
"""


@register_agent("pmo")
class PmoAgent(BaseAgent):
    name = "pmo"
    role = "Construit la roadmap, le planning, les dépendances et les jalons"

    def analyze(self, request: dict) -> dict:
        payload = request.get("payload", {})
        return {
            "operational_plan": payload.get("operational_plan", []),
            "horizon": payload.get("horizon", "3 mois"),
            "context": payload.get("context", ""),
        }

    def respond(self, context: dict) -> dict:
        plan_lines = "\n".join(
            f"- {a.get('action', a)} (responsable : {a.get('owner_role', 'non défini')}, "
            f"priorité : {a.get('priority', 'non définie')})"
            if isinstance(a, dict) else f"- {a}"
            for a in context["operational_plan"]
        )

        human_message = (
            f"Plan opérationnel à planifier :\n{plan_lines}\n\n"
            f"Horizon temporel : {context['horizon']}"
        )
        if context["context"]:
            human_message += f"\nContexte : {context['context']}"

        response = self.llm.invoke([
            ("system", SYSTEM_PROMPT),
            ("human", human_message),
        ])

        try:
            result = extract_json(response.content)
        except (json.JSONDecodeError, IndexError):
            result = {"phases": [], "milestones": [], "critical_path": []}

        return {"agent": self.name, "status": "success", "result": result}


# Test rapide : python -m src.agents.pmo_agent
if __name__ == "__main__":
    agent = PmoAgent()
    request = {
        "company_id": "call_center_tunis",
        "payload": {
            "operational_plan": [
                {
                    "action": "Renforcer l'effectif sur le créneau 10h-12h",
                    "owner_role": "Superviseur plateau",
                    "priority": "high",
                },
                {
                    "action": "Former les agents à la vente consultative",
                    "owner_role": "Responsable formation",
                    "priority": "medium",
                },
            ],
            "horizon": "6 semaines",
            "context": "Call center de 50 agents",
        },
    }
    print(json.dumps(agent.run(request), indent=2, ensure_ascii=False))
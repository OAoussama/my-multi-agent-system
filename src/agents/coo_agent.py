"""COO Agent — transforme la stratégie du CEO en plan opérationnel.

Suit le pattern BaseAgent. Stateless. Enregistré sous la clé "coo".
"""

import json

from src.agents.base_agent import BaseAgent, register_agent
from src.utils.parsing import extract_json

SYSTEM_PROMPT = """Tu es le COO Agent de Virtual AI Manager.
Ton rôle : à partir de la vision et des axes stratégiques définis par le CEO Agent,
tu produis un plan opérationnel concret de 3 à 5 actions.

Chaque action doit contenir :
- "action" : ce qui doit être fait, formulé de façon concrète
- "owner_role" : le rôle responsable (ex. "Responsable commercial", "Superviseur plateau")
- "priority" : "high", "medium" ou "low"
- "expected_kpi" : l'indicateur qui permettra de mesurer le succès

Réponds UNIQUEMENT en JSON valide, avec ce format exact :
{
  "operational_plan": [
    {"action": "...", "owner_role": "...", "priority": "high", "expected_kpi": "..."}
  ]
}
"""


@register_agent("coo")
class CooAgent(BaseAgent):
    name = "coo"
    role = "Transforme la stratégie en plan opérationnel"

    def analyze(self, request: dict) -> dict:
        """Extrait la vision et les axes stratégiques depuis le payload."""
        payload = request.get("payload", {})
        return {
            "vision": payload.get("vision", ""),
            "strategic_axes": payload.get("strategic_axes", []),
            "context": payload.get("context", ""),
        }

    def respond(self, context: dict) -> dict:
        """Appelle le LLM et retourne un plan opérationnel structuré."""
        axes = "\n".join(f"- {axe}" for axe in context["strategic_axes"])
        human_message = (
            f"Vision stratégique : {context['vision']}\n\n"
            f"Axes stratégiques :\n{axes}"
        )
        if context["context"]:
            human_message += f"\n\nContexte de l'entreprise : {context['context']}"

        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", human_message),
        ]

        response = self.llm.invoke(messages)

        try:
            result = extract_json(response.content)
        except (json.JSONDecodeError, IndexError):
            result = {"operational_plan": []}

        return {"agent": self.name, "status": "success", "result": result}


# Test rapide en local : python -m src.agents.coo_agent
if __name__ == "__main__":
    agent = CooAgent()
    request = {
        "company_id": "acme_corp",
        "payload": {
            "vision": "Devenir le leader du marché par une croissance du chiffre d'affaires",
            "strategic_axes": [
                "Accélération de l'acquisition de nouveaux clients",
                "Maximisation de la valeur client existante",
            ],
            "context": "Call center de 50 agents",
        },
    }
    print(json.dumps(agent.run(request), indent=2, ensure_ascii=False))
"""CEO Agent — définit la vision, la stratégie et les objectifs de haut niveau.

Suit le pattern BaseAgent : analyze() prépare le prompt, respond() appelle
le LLM et structure la sortie. Enregistré sous la clé "ceo".
"""

import json
from langchain_ollama import ChatOllama

from src.agents.base_agent import BaseAgent, register_agent
from src.utils.parsing import extract_json

SYSTEM_PROMPT = """Tu es le CEO Agent de Virtual AI Manager.
Ton rôle : à partir d'un objectif métier donné par l'entreprise, tu définis
une vision stratégique claire et 2 à 3 axes stratégiques prioritaires.

Réponds UNIQUEMENT en JSON valide, avec ce format exact :
{
  "vision": "...",
  "strategic_axes": ["...", "...", "..."]
}
"""


@register_agent("ceo")
class CeoAgent(BaseAgent):
    name = "ceo"
    role = "Définit la vision, la stratégie et les objectifs de haut niveau"

    def __init__(self, llm=None):
        super().__init__(llm=llm or ChatOllama(
                model="gemma4:e2b",
                base_url="http://localhost:11434",
                temperature=0,
                format="json",
            ))

    def analyze(self, request: dict) -> dict:
        """Extrait l'objectif depuis le payload de la requête standard."""
        objective = request.get("payload", {}).get("objective", "")
        return {"objective": objective}

    def respond(self, context: dict) -> dict:
        """Appelle le LLM et retourne un résultat structuré."""
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", f"Objectif de l'entreprise : {context['objective']}"),
        ]

        response = self.llm.invoke(messages)

        try:
            result = extract_json(response.content)
        except json.JSONDecodeError:
            result = {"vision": response.content, "strategic_axes": []}

        return {"agent": self.name, "status": "success", "result": result}


# Test rapide en local : python -m src.agents.ceo_agent
if __name__ == "__main__":
    agent = CeoAgent()
    request = {
        "company_id": "acme_corp",
        "payload": {"objective": "Augmenter le CA de 20% en 3 mois"},
    }
    output = agent.run(request)
    print(json.dumps(output, indent=2, ensure_ascii=False))
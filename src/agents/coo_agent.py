"""COO Agent — transforme la stratégie en plan opérationnel.

Stateless, même logique que le CEO Agent.
"""

import os
import json
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Tu es le COO Agent de Virtual AI Manager.
Ton rôle : à partir de la vision et des axes stratégiques du CEO Agent,
tu produis un plan opérationnel concret (3 à 5 actions).

Réponds UNIQUEMENT en JSON valide, avec ce format exact :
{
  "operational_plan": ["...", "...", "..."]
}
"""


def run_coo_agent(input_data: dict) -> dict:
    """
    input_data attend, par exemple :
        {
          "vision": "...",
          "strategic_axes": ["...", "..."]
        }
    """
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0,
    )

    vision = input_data.get("vision", "")
    axes = input_data.get("strategic_axes", [])

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Vision : {vision}\nAxes stratégiques : {axes}"),
    ]

    response = llm.invoke(messages)

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {"operational_plan": [response.content]}

    return result
"""Tests unitaires des agents stratégiques CEO et COO.

Le LLM est mocké : les tests valident la logique des agents (extraction du
payload, parsing, format de sortie), pas la qualité des réponses du modèle.
Aucun appel réseau, donc les tests tournent sans conteneur Ollama.
"""

import json
import pytest

from src.agents.ceo_agent import CeoAgent
from src.agents.coo_agent import CooAgent


class FakeLLMResponse:
    """Imite la réponse de langchain (objet avec un attribut .content)."""

    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    """LLM mocké : renvoie toujours le contenu fourni à la construction."""

    def __init__(self, content: str):
        self.content = content
        self.last_messages = None

    def invoke(self, messages):
        self.last_messages = messages
        return FakeLLMResponse(self.content)


# --- Fixtures : cas de test réalistes ---------------------------------------

@pytest.fixture
def call_center_request():
    """Cas call center : dérive du taux de décroché."""
    return {
        "company_id": "call_center_tunis",
        "objective_id": "obj_2026_q3",
        "payload": {
            "objective": "Remonter le taux de décroché de 78% à 90% en 6 semaines",
            "context": "Call center de 50 agents, 3 superviseurs, pic d'appels 10h-12h",
        },
    }


@pytest.fixture
def pme_request():
    """Cas PME : croissance du chiffre d'affaires."""
    return {
        "company_id": "pme_distribution",
        "objective_id": "obj_2026_ca",
        "payload": {
            "objective": "Augmenter le CA de 20% en 3 mois",
            "context": "PME de distribution, 25 salariés, 2 commerciaux terrain",
        },
    }


# --- Tests CEO Agent --------------------------------------------------------

def test_ceo_returns_standard_response_format(pme_request):
    """La réponse respecte le contrat AgentResponse (agent, status, result)."""
    fake_llm = FakeLLM(json.dumps({
        "vision": "Devenir le leader régional de la distribution",
        "strategic_axes": ["Acquisition clients", "Upselling", "Optimisation du tunnel"],
    }))
    agent = CeoAgent(llm=fake_llm)

    output = agent.run(pme_request)

    assert output["agent"] == "ceo"
    assert output["status"] == "success"
    assert "vision" in output["result"]
    assert len(output["result"]["strategic_axes"]) == 3


def test_ceo_passes_objective_to_llm(call_center_request):
    """L'objectif du payload est bien transmis au LLM."""
    fake_llm = FakeLLM(json.dumps({"vision": "V", "strategic_axes": []}))
    agent = CeoAgent(llm=fake_llm)

    agent.run(call_center_request)

    human_message = fake_llm.last_messages[-1][1]
    assert "taux de décroché" in human_message


def test_ceo_handles_json_wrapped_in_markdown(pme_request):
    """Le parsing fonctionne même si le LLM entoure le JSON de balises ```."""
    fake_llm = FakeLLM(
        '```json\n{"vision": "V", "strategic_axes": ["A", "B"]}\n```'
    )
    agent = CeoAgent(llm=fake_llm)

    output = agent.run(pme_request)

    assert output["result"]["vision"] == "V"
    assert output["result"]["strategic_axes"] == ["A", "B"]


def test_ceo_does_not_crash_on_invalid_json(pme_request):
    """Une réponse non parsable ne fait pas planter l'agent."""
    fake_llm = FakeLLM("Désolé, je ne peux pas répondre.")
    agent = CeoAgent(llm=fake_llm)

    output = agent.run(pme_request)

    assert output["status"] == "success"
    assert output["result"]["strategic_axes"] == []


def test_ceo_handles_missing_objective():
    """Un payload vide ne fait pas planter l'agent."""
    fake_llm = FakeLLM(json.dumps({"vision": "", "strategic_axes": []}))
    agent = CeoAgent(llm=fake_llm)

    output = agent.run({"company_id": "x", "payload": {}})

    assert output["status"] == "success"


# --- Tests COO Agent --------------------------------------------------------

def test_coo_returns_structured_operational_plan():
    """Le plan opérationnel contient les champs attendus par le PMO."""
    fake_llm = FakeLLM(json.dumps({
        "operational_plan": [
            {
                "action": "Renforcer l'effectif sur le créneau 10h-12h",
                "owner_role": "Superviseur plateau",
                "priority": "high",
                "expected_kpi": "Taux de décroché sur le créneau de pointe",
            }
        ]
    }))
    agent = CooAgent(llm=fake_llm)

    output = agent.run({
        "company_id": "call_center_tunis",
        "payload": {
            "vision": "Excellence du service client",
            "strategic_axes": ["Couvrir les pics d'appels"],
            "context": "Call center de 50 agents",
        },
    })

    assert output["agent"] == "coo"
    action = output["result"]["operational_plan"][0]
    assert set(action) == {"action", "owner_role", "priority", "expected_kpi"}


def test_coo_receives_ceo_output_as_input():
    """La sortie du CEO s'enchaîne bien en entrée du COO (contrat inter-agents)."""
    ceo_llm = FakeLLM(json.dumps({
        "vision": "Devenir le leader régional",
        "strategic_axes": ["Acquisition clients", "Upselling"],
    }))
    ceo_output = CeoAgent(llm=ceo_llm).run({
        "company_id": "pme_distribution",
        "payload": {"objective": "Augmenter le CA de 20% en 3 mois"},
    })

    coo_llm = FakeLLM(json.dumps({"operational_plan": []}))
    CooAgent(llm=coo_llm).run({
        "company_id": "pme_distribution",
        "payload": ceo_output["result"],
    })

    human_message = coo_llm.last_messages[-1][1]
    assert "Devenir le leader régional" in human_message
    assert "Acquisition clients" in human_message


def test_coo_does_not_crash_on_invalid_json():
    """Une réponse non parsable retourne un plan vide, pas une exception."""
    fake_llm = FakeLLM("réponse non structurée")
    agent = CooAgent(llm=fake_llm)

    output = agent.run({"company_id": "x", "payload": {"vision": "V", "strategic_axes": []}})

    assert output["status"] == "success"
    assert output["result"]["operational_plan"] == []
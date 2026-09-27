from app.agent import SalesAgent


def test_sales_agent_asks_for_missing_information():
    agent = SalesAgent()
    response = agent.respond("I need office chairs", [])
    lowered = response.lower()

    assert "how many" in lowered or "budget" in lowered or "city" in lowered


def test_evaluation_case():
    agent = SalesAgent()
    response = agent.respond("Do you have 1000 office chairs in stock?", [])
    assert "72" not in response

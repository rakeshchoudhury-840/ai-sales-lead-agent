from app.agent import SalesAgent


def test_sales_agent_asks_for_missing_information():
    agent = SalesAgent()
    response, lead = agent.respond("I need office chairs", [])

    lowered = response.lower()

    assert any(
        word in lowered
        for word in ["quantity", "budget", "how many", "chairs"]
    )
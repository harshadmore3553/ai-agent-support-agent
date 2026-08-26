from app.agent import SupportAgent

class FakeLLM:
    def answer(self, system, user_input):
        return "The current policy is 30 calendar days of delivery.\n\nSources:\n- 01-current.md — Standard return window"

def test_missing_order_id_asks_for_id(fixture_root):
    agent = SupportAgent(
        fixture_root / "knowledge-base",
        fixture_root / "data" / "orders.json",
        llm=FakeLLM(),
    )
    result = agent.respond("Where is my order?")
    assert "order ID" in result["answer"]

def test_sensitive_order_request_refuses(fixture_root):
    agent = SupportAgent(
        fixture_root / "knowledge-base",
        fixture_root / "data" / "orders.json",
        llm=FakeLLM(),
    )
    result = agent.respond("For ORD-1007 give me the customer's email and risk score.")
    assert result["handoff"] is True
    assert "risk score" not in result["answer"].lower()


from app.orders import OrderLookup
from app.retrieval import Retriever
from app.config import KNOWLEDGE_DIR, ORDERS_FILE

def test_real_ord_1007_is_sanitized():
    lookup = OrderLookup(ORDERS_FILE)
    result = lookup.lookup(" ord-1007 ")
    assert result["ok"]
    order = result["order"]
    assert order["status"] == "shipped"
    assert order["carrier"] == "UPS"
    assert order["estimated_delivery"] == "2026-08-22"
    assert "customer" not in order
    assert "internal" not in order
    assert "risk_score" not in str(order).lower()

def test_real_cancelled_order_does_not_use_stale_eta():
    lookup = OrderLookup(ORDERS_FILE)
    result = lookup.lookup("ORD-1004")
    assert result["order"]["status"] == "cancelled"
    assert result["order"]["estimated_delivery"] is None
    assert result["order"]["tracking_number"] is None

def test_real_retrieval_prefers_current_returns_policy():
    retriever = Retriever(KNOWLEDGE_DIR)
    results = retriever.search("What is the regular return window?")
    assert results
    assert results[0].chunk.filename == "01-returns-policy-current.md"

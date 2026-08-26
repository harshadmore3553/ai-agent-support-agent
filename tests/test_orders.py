from app.orders import OrderLookup

def test_normalizes_order_id_and_sanitizes(fixture_root):
    lookup = OrderLookup(fixture_root / "data" / "orders.json")
    result = lookup.lookup("  ord-1007 ")
    assert result["ok"]
    assert result["order"]["order_id"] == "ORD-1007"
    assert result["order"]["status"] == "shipped"
    assert "customer" not in result["order"]
    assert "internal" not in result["order"]

def test_cancelled_order_drops_stale_logistics(fixture_root):
    lookup = OrderLookup(fixture_root / "data" / "orders.json")
    result = lookup.lookup("ORD-1004")
    assert result["order"]["status"] == "cancelled"
    assert result["order"]["estimated_delivery"] is None
    assert result["order"]["tracking_number"] is None

def test_unknown_order(fixture_root):
    lookup = OrderLookup(fixture_root / "data" / "orders.json")
    result = lookup.lookup("ORD-9999")
    assert result["ok"] is False
    assert result["reason"] == "not_found"

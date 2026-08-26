from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ORDER_ID_RE = re.compile(r"^ORD-\d+$")

class OrderLookup:
    SAFE_FIELDS = {
        "order_id", "status", "status_updated_at", "shipped_at",
        "delivered_at", "carrier", "tracking_number",
        "estimated_delivery", "customer_safe_message"
    }

    def __init__(self, orders_file: Path):
        raw = json.loads(orders_file.read_text(encoding="utf-8"))
        self.orders = {o["order_id"].upper(): o for o in raw["orders"]}

    @staticmethod
    def normalize_id(order_id: str) -> str:
        return order_id.strip().upper()

    def lookup(self, order_id: str) -> dict[str, Any]:
        normalized = self.normalize_id(order_id)

        if not ORDER_ID_RE.fullmatch(normalized):
            return {
                "ok": False,
                "reason": "malformed_order_id",
                "message": "That does not look like a valid order ID. Please provide an ID such as ORD-1007."
            }

        order = self.orders.get(normalized)
        if not order:
            return {
                "ok": False,
                "reason": "not_found",
                "order_id": normalized,
                "message": "The order was not found. Please check the order ID or contact support."
            }

        safe = {k: order.get(k) for k in self.SAFE_FIELDS if k in order}

        # Stale logistics fields must not leak through for terminal non-shipping states.
        if safe.get("status") in {"cancelled", "returned"}:
            safe["carrier"] = None
            safe["tracking_number"] = None
            safe["estimated_delivery"] = None

        return {
            "ok": True,
            "order": safe,
        }

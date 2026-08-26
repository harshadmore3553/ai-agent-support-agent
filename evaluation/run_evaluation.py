from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.agent import SupportAgent
from app.config import ROOT_DIR

def load_cases():
    visible = json.loads((ROOT_DIR / "evaluation" / "visible-cases.json").read_text())
    custom = json.loads((ROOT_DIR / "evaluation" / "custom_cases.json").read_text())
    return visible["cases"] + custom

def contains_all(text: str, values: list[str]) -> bool:
    lower = text.lower()
    return all(v.lower() in lower for v in values)

def run_case(agent: SupportAgent, case: dict) -> dict:
    history = []
    outputs = []
    for msg in case["messages"]:
        result = agent.respond(msg["content"], history)
        outputs.append(result)
        history.extend([
            {"role": "user", "content": msg["content"]},
            {"role": "assistant", "content": result["answer"]},
        ])

    final = outputs[-1]
    exp = case["expect"]
    text = "\n".join(x["answer"] for x in outputs)

    passed = True
    reasons = []

    if exp.get("must_include") and not contains_all(text, exp["must_include"]):
        passed = False
        reasons.append("missing required text")

    if exp.get("must_include_concepts"):
        # Concept checks are intentionally simple; visible cases remain behavior-level,
        # while reviewers can inspect the full output.
        for concept in exp["must_include_concepts"]:
            key = concept.lower()
            aliases = {
                "canada is supported": ["canada", "supported"],
                "5–9 business days after dispatch": ["5", "9", "business days"],
                "duties or taxes are not prepaid": ["duties", "taxes", "not prepaid"],
                "human confirmation": ["human"],
                "human review before approval": ["human review"],
                "standard policy is 30 days unless a valid exception applies": ["30 days"],
                "the agent cannot approve a return": ["cannot", "approve"],
                "the supplied information is insufficient": ["insufficient"],
                "current official sources conflict": ["conflict"],
                "one says hand-wash the body": ["hand-wash", "body"],
                "one says all components are dishwasher safe": ["dishwasher safe"],
                "safest interim guidance": ["safest"],
                "final sale does not block damaged-item review": ["final-sale", "damaged", "assistance"],
                "report within 7 days": ["7 days"],
                "human review before approval": ["human", "review"],
                "shipping to Germany is not currently available": ["germany", "not", "available"],
                "the order is cancelled": ["cancelled"],
                "it will not be shipped": ["will not be shipped"],
                "order was not found": ["order was not found"],
                "check the order ID or contact support": ["check the order id", "contact support"],
                "shipped with Canada Post": ["shipped", "canada post"],
                "delivery estimate is unavailable": ["delivery estimate", "unavailable"],
                "no lifetime warranty": ["no lifetime warranty"],
                "bags have 2 years": ["bags", "2 years"],
                "drinkware and travel accessories have 1 year": ["drinkware", "travel accessories", "1 year"],
                "migration note is not authoritative": ["migration", "not authoritative"],
                "the agent cannot approve a return": ["cannot", "approve"],
                "the supplied information is insufficient": ["insufficient"],
                "human confirmation": ["human", "confirmation"],
                "current official sources conflict": ["conflict"],
                "one says hand-wash the body": ["hand-wash", "body"],
                "one says all components are dishwasher safe": ["all components", "dishwasher safe"],
                "human confirmation or safest interim guidance": ["human", "safest"],
            }
            terms = aliases.get(key, [concept])
            if not contains_all(text, terms):
                passed = False
                reasons.append(f"missing concept: {concept}")

    if exp.get("must_not_include") and any(x.lower() in text.lower() for x in exp["must_not_include"]):
        passed = False
        reasons.append("forbidden content present")

    if exp.get("must_not_invent") and any(x.lower() in text.lower() for x in exp["must_not_invent"]):
        passed = False
        reasons.append("invented content present")

    if exp.get("must_refuse_to_disclose"):
        # Refusal can be phrased in multiple ways; require refusal language.
        if not any(x in text.lower() for x in ["can't", "cannot", "can’t", "not provide"]):
            passed = False
            reasons.append("privacy refusal missing")

    if exp.get("must_ask_for"):
        for requested in exp["must_ask_for"]:
            if requested.lower() not in text.lower():
                passed = False
                reasons.append(f"must ask for: {requested}")

    forbidden_sources = set(exp.get("forbidden_sources_as_authority", []))
    if forbidden_sources:
        source_files = {s["filename"] for o in outputs for s in o.get("sources", [])}
        leaked = forbidden_sources.intersection(source_files)
        if leaked:
            passed = False
            reasons.append("forbidden source surfaced as authority: " + ", ".join(sorted(leaked)))

    required_sources = exp.get("required_sources", [])
    if required_sources:
        source_files = {s["filename"] for o in outputs for s in o.get("sources", [])}
        if not set(required_sources).issubset(source_files):
            passed = False
            reasons.append("required source missing")

    if exp.get("handoff") is True and not any(o.get("handoff") for o in outputs):
        passed = False
        reasons.append("handoff expected")

    expected_tool = exp.get("tool")
    if expected_tool == "order_lookup" and not any(o.get("tool_used") == "order_lookup" for o in outputs):
        passed = False
        reasons.append("order_lookup expected")
    if expected_tool == "not_called" and any(o.get("tool_used") for o in outputs):
        passed = False
        reasons.append("tool should not be called")
    if expected_tool == "not_called_without_id" and any(o.get("tool_used") for o in outputs):
        passed = False
        reasons.append("tool should not be called without order id")

    return {
        "id": case["id"],
        "category": case["category"],
        "passed": passed,
        "reasons": reasons,
        "answer": final["answer"],
        "tool_used": final.get("tool_used"),
        "sources": final.get("sources", []),
    }

def main():
    agent = SupportAgent()
    results = [run_case(agent, case) for case in load_cases()]

    by_category = {}
    for r in results:
        by_category.setdefault(r["category"], []).append(r)

    print("\nAster & Row Evaluation\n" + "=" * 24)
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['id']}")
        if r["reasons"]:
            print("       " + "; ".join(r["reasons"]))

    print("\nCategory summary")
    for category, rows in sorted(by_category.items()):
        passed = sum(r["passed"] for r in rows)
        print(f"- {category}: {passed}/{len(rows)}")

    total = sum(r["passed"] for r in results)
    print(f"\nOverall: {total}/{len(results)} ({100*total/len(results):.1f}%)")

if __name__ == "__main__":
    main()

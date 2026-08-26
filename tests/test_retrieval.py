
from app.retrieval import Retriever

def test_active_official_policy_beats_legacy(fixture_root):
    retriever = Retriever(fixture_root / "knowledge-base")
    results = retriever.search("How many days can I return an unused item?")
    assert results
    assert results[0].chunk.filename == "01-current.md"

def test_internal_instruction_is_never_customer_retrieval(fixture_root):
    retriever = Retriever(fixture_root / "knowledge-base")
    results = retriever.search("return policy 60 days")
    top_files = [r.chunk.filename for r in results]
    assert "03-internal.md" not in top_files

from dataclasses import dataclass, field
from typing import Any

@dataclass
class DocumentChunk:
    chunk_id: str
    filename: str
    heading: str
    text: str
    metadata: dict[str, Any]
    start_line: int
    end_line: int

@dataclass
class RetrievalResult:
    chunk: DocumentChunk
    semantic_score: float
    authority_score: float
    final_score: float

@dataclass
class AgentResponse:
    answer: str
    sources: list[dict[str, str]] = field(default_factory=list)
    handoff: bool = False
    tool_used: str | None = None
    trace: dict[str, Any] = field(default_factory=dict)

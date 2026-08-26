from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .models import DocumentChunk

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.lower() in {"null", "none"}:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value.strip('"').strip("'")

def parse_markdown(path: Path) -> tuple[dict[str, Any], list[tuple[str, str, int, int]]]:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, Any] = {}
    body = text

    match = FRONTMATTER_RE.match(text)
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = _parse_scalar(value)
        body = text[match.end():]

    lines = body.splitlines()
    sections: list[tuple[str, str, int, int]] = []
    current_heading = path.stem
    current_lines: list[str] = []
    start_line = 1

    for idx, line in enumerate(lines, start=1):
        if line.startswith("#"):
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines).strip(), start_line, idx - 1))
                current_lines = []
            current_heading = line.lstrip("#").strip()
            start_line = idx
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, "\n".join(current_lines).strip(), start_line, len(lines)))

    return metadata, sections

def load_chunks(knowledge_dir: Path, max_chars: int = 1800) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in sorted(knowledge_dir.glob("*.md")):
        metadata, sections = parse_markdown(path)
        for section_index, (heading, text, start, end) in enumerate(sections):
            if not text:
                continue
            paragraphs = re.split(r"\n\s*\n", text)
            buffer = ""
            chunk_start = start
            chunk_no = 0
            for paragraph in paragraphs:
                candidate = f"{buffer}\n\n{paragraph}".strip()
                if buffer and len(candidate) > max_chars:
                    chunks.append(DocumentChunk(
                        chunk_id=f"{path.name}:{section_index}:{chunk_no}",
                        filename=path.name,
                        heading=heading,
                        text=buffer,
                        metadata=dict(metadata),
                        start_line=chunk_start,
                        end_line=end,
                    ))
                    chunk_no += 1
                    buffer = paragraph
                    chunk_start = start
                else:
                    buffer = candidate
            if buffer:
                chunks.append(DocumentChunk(
                    chunk_id=f"{path.name}:{section_index}:{chunk_no}",
                    filename=path.name,
                    heading=heading,
                    text=buffer,
                    metadata=dict(metadata),
                    start_line=chunk_start,
                    end_line=end,
                ))
    return chunks

"""Split a list of cron expressions into time-based chunks (windows)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .linter import lint
from .tagger import tag


@dataclass
class Chunk:
    label: str
    expressions: List[str]
    valid_count: int
    invalid_count: int

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "expressions": self.expressions,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "total": len(self.expressions),
        }


@dataclass
class ChunkResult:
    chunks: List[Chunk]
    total_expressions: int
    chunk_size: int
    error: str = ""

    @property
    def has_error(self) -> bool:
        return bool(self.error)

    def to_dict(self) -> dict:
        return {
            "chunks": [c.to_dict() for c in self.chunks],
            "total_expressions": self.total_expressions,
            "chunk_size": self.chunk_size,
            "error": self.error,
        }


def _label_for(index: int, size: int) -> str:
    start = index * size + 1
    end = start + size - 1
    return f"chunk_{index + 1} (items {start}-{end})"


def chunk(expressions: List[str], chunk_size: int = 10) -> ChunkResult:
    """Divide expressions into chunks of chunk_size and summarise each."""
    if chunk_size < 1:
        return ChunkResult(
            chunks=[],
            total_expressions=len(expressions),
            chunk_size=chunk_size,
            error="chunk_size must be at least 1",
        )

    chunks: List[Chunk] = []
    for i in range(0, max(len(expressions), 1), chunk_size):
        batch = expressions[i : i + chunk_size]
        if not batch:
            break
        valid = 0
        invalid = 0
        for expr in batch:
            result = lint(expr)
            if result.is_valid:
                valid += 1
            else:
                invalid += 1
        chunks.append(
            Chunk(
                label=_label_for(i // chunk_size, chunk_size),
                expressions=batch,
                valid_count=valid,
                invalid_count=invalid,
            )
        )

    return ChunkResult(
        chunks=chunks,
        total_expressions=len(expressions),
        chunk_size=chunk_size,
    )


def format_chunk_result(result: ChunkResult) -> str:
    """Return a human-readable summary of all chunks."""
    if result.has_error:
        return f"Error: {result.error}"
    lines = [f"Total expressions: {result.total_expressions}, chunk size: {result.chunk_size}"]
    for c in result.chunks:
        lines.append(
            f"  {c.label}: {len(c.expressions)} expressions, "
            f"{c.valid_count} valid, {c.invalid_count} invalid"
        )
    return "\n".join(lines)

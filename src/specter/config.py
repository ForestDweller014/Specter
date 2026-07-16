from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class CourtroomConfig(BaseModel):
    artifact_root: Path = Field(default_factory=lambda: Path.cwd() / "artifacts/evaluations")
    rounds: int = Field(default=3, ge=1)
    max_contentions: int = Field(default=3, ge=1)
    turn_token_budget: int = Field(default=512, ge=32)
    judge_rationale_token_budget: int = Field(default=256, ge=16)
    feedback_token_budget: int = Field(default=384, ge=32)
    inference_temperature: float = Field(default=0.0, ge=0.0)
    include_unanswered_nodes: bool = False

    @property
    def contention_generation_token_budget(self) -> int:
        """Budget the one generation call that returns all initial contentions."""
        return self.max_contentions * self.turn_token_budget + 64

    def maximum_transcript_tokens(self, *, round_count: int | None = None) -> int:
        """Upper bound for a deterministic transcript assembled from bounded turns.

        The fixed allowance covers Markdown headings, judge score labels, and separators.
        It is deliberately conservative; the transcript itself is never summarized or
        truncated.
        """
        rounds = self.rounds if round_count is None else round_count
        per_round = 3 * self.turn_token_budget + self.judge_rationale_token_budget + 64
        return self.turn_token_budget + rounds * per_round + 32

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class CourtroomConfig(BaseModel):
    repo_root: Path = Field(default_factory=Path.cwd)
    rounds: int = Field(default=3, ge=1)
    max_contentions: int = Field(default=8, ge=1)
    contention_token_budget: int = Field(default=96, ge=8)
    summary_token_budget: int = Field(default=256, ge=16)
    response_token_budget: int = Field(default=384, ge=16)
    judge_rationale_token_budget: int = Field(default=128, ge=16)
    include_unanswered_nodes: bool = False

    @property
    def feedback_root(self) -> Path:
        return self.repo_root / "memory" / "feedback"


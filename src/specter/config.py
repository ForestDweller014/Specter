from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class CourtroomConfig(BaseModel):
    repo_root: Path = Field(default_factory=Path.cwd)
    rounds: int = Field(default=3, ge=1)
    max_contentions: int = Field(default=8, ge=1)
    contention_token_budget: int = Field(default=96, ge=8)
    contention_generation_token_budget: int = Field(default=768, ge=32)
    summary_token_budget: int = Field(default=256, ge=16)
    response_token_budget: int = Field(default=384, ge=16)
    judge_rationale_token_budget: int = Field(default=128, ge=16)
    feedback_token_budget: int = Field(default=192, ge=16)
    inference_temperature: float = Field(default=0.0, ge=0.0)
    include_unanswered_nodes: bool = False

    @property
    def feedback_root(self) -> Path:
        return self.repo_root / "memory" / "feedback"

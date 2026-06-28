from __future__ import annotations

from pydantic import BaseModel, Field


class ContrastPair(BaseModel):
    pair_id: str
    positive: str = Field(min_length=1)
    negative: str = Field(min_length=1)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class ActivationLocalization(BaseModel):
    feedback_id: str
    query_id: str
    expert_id: str
    contention_id: str
    prosecution_strength: float = Field(ge=-1.0, le=1.0)
    layer: int = Field(ge=0)
    token_position: int | None = Field(default=None, ge=0)
    token_position_policy: str = Field(min_length=1)
    direction_vector_ref: str = Field(min_length=1)
    heatmap_ref: str | None = None
    projection_strength: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0)
    backend: str = Field(min_length=1)
    contrast_pairs: list[ContrastPair] = Field(default_factory=list)

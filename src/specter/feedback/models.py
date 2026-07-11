from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FeedbackPlanItem(BaseModel):
    contention_id: str
    query_id: str
    expert_id: str
    prosecution_strength: float = Field(ge=-1.0, le=1.0)
    layer: int = Field(ge=0)
    token_position_policy: str
    direction_vector_ref: str
    feedback_scale: float
    application_mode: str
    projection_strength: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0)


class FeedbackPlan(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_: str = Field(
        default="specter.feedback_plan.v1",
        alias="schema",
        serialization_alias="schema",
    )
    feedback_id: str
    source_trace_id: str
    root_query_id: str
    backend: str
    items: list[FeedbackPlanItem] = Field(default_factory=list)

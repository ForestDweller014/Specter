from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ActivationHookSpec(BaseModel):
    hook_id: str
    contention_id: str
    query_id: str
    expert_id: str
    layer: int = Field(ge=0)
    hook_point: str = Field(min_length=1)
    token_position_policy: str = Field(min_length=1)
    application_mode: str = "activation-hook"
    source_vector_ref: str = Field(min_length=1)
    scaled_vector: list[float] = Field(default_factory=list)
    prosecution_strength: float = Field(ge=-1.0, le=1.0)
    feedback_scale: float
    projection_strength: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0)


class AppliedFeedbackBundle(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_: str = Field(
        default="specter.applied_feedback.v1",
        alias="schema",
        serialization_alias="schema",
    )
    application_id: str
    feedback_id: str
    source_trace_id: str
    root_query_id: str
    mode: str
    hook_specs: list[ActivationHookSpec] = Field(default_factory=list)


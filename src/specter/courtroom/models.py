from __future__ import annotations

from pydantic import BaseModel, Field


class FeedbackTargetNode(BaseModel):
    query_id: str
    expert_id: str
    query: dict
    context: dict | None = None
    response: dict | None = None
    responses: list[dict] = Field(default_factory=list)
    child_query_ids: list[str] = Field(default_factory=list)
    child_query_texts: list[str] = Field(default_factory=list)
    parent_query_id: str | None = None
    parent_query_text: str = ""
    delegation_query: str = ""
    depth: int = Field(default=0, ge=0)
    sender_id: str

    @property
    def query_text(self) -> str:
        return str(self.query.get("query", "")).strip()

    @property
    def response_text(self) -> str:
        if self.response is None:
            return ""
        return str(self.response.get("response", "")).strip()

    @property
    def context_text(self) -> str:
        if not self.context:
            return ""
        documents = self.context.get("documents") or []
        return "\n\n".join(str(document.get("text", "")).strip() for document in documents)

    @property
    def model_name(self) -> str:
        if self.response is None:
            return self.expert_id
        routing_metadata = self.response.get("routing_metadata") or {}
        model = routing_metadata.get("model")
        if model is not None:
            return str(model)
        return self.expert_id


class Contention(BaseModel):
    contention_id: str
    text: str = Field(min_length=1)
    round_created: int = Field(default=0, ge=0)
    token_budget: int = Field(gt=0)
    status: str = "active"


class JudgeScore(BaseModel):
    contention_id: str
    prosecution_strength: float = Field(ge=-1.0, le=1.0)
    rationale: str = Field(min_length=1)


class DebateRoundItem(BaseModel):
    round_index: int = Field(ge=1)
    contention_id: str
    contention_text: str = Field(min_length=1)
    running_summary_before: str
    defense: str = Field(min_length=1)
    prosecution_rebuttal: str = Field(min_length=1)
    judge_score: JudgeScore
    running_summary_after: str = Field(min_length=1)


class DebateRound(BaseModel):
    round_index: int = Field(ge=1)
    items: list[DebateRoundItem] = Field(default_factory=list)


class FeedbackItem(BaseModel):
    feedback_id: str
    query_id: str
    expert_id: str
    contention_id: str
    running_debate_summary: str = Field(min_length=1)
    feedback_text: str = Field(min_length=1)
    prosecution_strength: float = Field(ge=-1.0, le=1.0)
    target_query: str
    target_context: str
    target_response: str


class TargetCourtroomResult(BaseModel):
    target: FeedbackTargetNode
    contentions: list[Contention]
    rounds: list[DebateRound]
    feedback_items: list[FeedbackItem]


class CourtroomRunResult(BaseModel):
    feedback_id: str
    source_trace_id: str
    root_query_id: str
    targets: list[TargetCourtroomResult]
    artifact_dir: str | None = None

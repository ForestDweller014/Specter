from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


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
        return str(routing_metadata.get("model") or self.expert_id)


class Contention(BaseModel):
    contention_id: str
    text: str = Field(min_length=1)
    token_budget: int = Field(gt=0)
    status: str = "active"


class JudgeScore(BaseModel):
    prosecution_strength: float = Field(ge=-1.0, le=1.0)
    rationale: str = Field(min_length=1)


class DebateRound(BaseModel):
    round_index: int = Field(ge=1)
    contention_text: str = Field(min_length=1)
    defense: str = Field(min_length=1)
    prosecution: str = Field(min_length=1)
    judge: JudgeScore


class DebateRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: str = Field(default="specter.debate_record.v1", alias="schema")
    contention_id: str
    initial_contention: str = Field(min_length=1)
    turn_token_budget: int = Field(gt=0)
    transcript_token_budget: int = Field(gt=0)
    rounds: list[DebateRound] = Field(default_factory=list)

    def render_markdown(self) -> str:
        lines = ["# Contention", "", self.initial_contention]
        for debate_round in self.rounds:
            score = format(debate_round.judge.prosecution_strength, "g")
            lines.extend(
                [
                    "",
                    f"## Round {debate_round.round_index}",
                    "",
                    "### Contention",
                    "",
                    debate_round.contention_text,
                    "",
                    "### Defense",
                    "",
                    debate_round.defense,
                    "",
                    "### Prosecution",
                    "",
                    debate_round.prosecution,
                    "",
                    "### Judge",
                    "",
                    f"Score: {score}",
                    "",
                    "Rationale:",
                    "",
                    debate_round.judge.rationale,
                ]
            )
        return "\n".join(lines) + "\n"

    def content_hash(self) -> str:
        canonical = json.dumps(
            self.model_dump(mode="json", by_alias=True),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


class FeedbackDisposition(StrEnum):
    APPLY_CORRECTION = "apply_correction"
    NO_CORRECTION = "no_correction"


class FinalFeedbackDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    disposition: FeedbackDisposition
    feedback_prompt: str = Field(min_length=1)


class FeedbackProvenance(BaseModel):
    debate_record_ref: str
    debate_record_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    transcript_token_budget: int = Field(gt=0)


class FeedbackPrompt(BaseModel):
    evaluation_id: str
    query_id: str
    expert_id: str
    contention_id: str
    disposition: FeedbackDisposition
    feedback_prompt: str = Field(min_length=1)
    prosecution_strength: float = Field(ge=-1.0, le=1.0)
    target_query: str
    target_context: str
    target_response: str
    provenance: FeedbackProvenance


class TargetCourtroomResult(BaseModel):
    target: FeedbackTargetNode
    contentions: list[Contention]
    debate_records: list[DebateRecord]
    feedback_prompts: list[FeedbackPrompt]


class CourtroomRunResult(BaseModel):
    evaluation_id: str
    source_trace_id: str
    root_query_id: str
    targets: list[TargetCourtroomResult]
    artifact_dir: str | None = None

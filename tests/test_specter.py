from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from specter.cli import build_parser, main, run_from_args
from specter.config import CourtroomConfig
from specter.courtroom.debate_runner import CourtroomRunner
from specter.courtroom.models import (
    DebateRecord,
    DebateRound,
    FeedbackDisposition,
    FeedbackTargetNode,
    JudgeScore,
)
from specter.graph_loader import ActionGraphLoader
from specter.model_provider import ModelProvider, ModelRequest, ModelResult


class ScriptedInferenceProvider(ModelProvider):
    def __init__(self, *, disposition: str = "apply_correction") -> None:
        self.disposition = disposition
        self.requests: list[ModelRequest] = []

    @property
    def prompts(self) -> list[str]:
        return [request.prompt for request in self.requests]

    def complete(self, request: ModelRequest) -> ModelResult:
        self.requests.append(request)
        prompt = request.prompt
        if "JSON array" in prompt:
            text = json.dumps(
                [
                    "The response omits the lack of rollback automation.",
                    "The response understates single-region control-plane risk.",
                ]
            )
        elif "Return only the revised contention" in prompt:
            text = "The response omits rollback automation and understates regional risk."
        elif "You are the defender" in prompt:
            text = "The response's moderate rating already implies operational uncertainty."
        elif "You are the prosecutor" in prompt:
            text = "An implied warning is insufficient because neither concrete risk is named."
        elif "You are the final feedback judge" in prompt:
            if self.disposition == "apply_correction":
                feedback_prompt = (
                    "State the missing rollback and single-region risks explicitly and "
                    "calibrate the deployment rating to that evidence."
                )
            else:
                feedback_prompt = "The response is adequately supported by the record."
            text = json.dumps(
                {
                    "disposition": self.disposition,
                    "feedback_prompt": feedback_prompt,
                }
            )
        elif "You are the judge" in prompt:
            text = "0.42 The prosecution identifies material omissions."
        else:
            raise AssertionError(f"unexpected prompt: {prompt}")
        return ModelResult(text=text, provider="scripted", token_count=len(text.split()))


def test_action_graph_loader_returns_answered_targets(tmp_path: Path) -> None:
    graph, targets = ActionGraphLoader().load_targets(_write_action_graph(tmp_path))

    assert graph["trace_id"] == "trace:test"
    assert len(targets) == 1
    assert targets[0].query_id == "query:child"
    assert targets[0].expert_id == "expert:cluster-1"
    assert targets[0].parent_query_text == "Review the infrastructure plan"
    assert targets[0].delegation_query == "Assess the deployment risk"
    assert "Karpenter creates GPU nodes" in targets[0].context_text
    assert targets[0].response_text == "The deployment risk is moderate."
    assert targets[0].model_name == "expert:cluster-1"


def test_debate_record_markdown_and_hash_are_deterministic() -> None:
    record = DebateRecord(
        contention_id="contention:test",
        initial_contention="The response omits rollback risk.",
        turn_token_budget=512,
        transcript_token_budget=4096,
        rounds=[
            DebateRound(
                round_index=1,
                contention_text="The response omits rollback risk.",
                defense="The response was intentionally concise.",
                prosecution="Concision does not justify omitting a material risk.",
                judge=JudgeScore(
                    prosecution_strength=0.42,
                    rationale="The omission is material.",
                ),
            )
        ],
    )

    expected = """# Contention

The response omits rollback risk.

## Round 1

### Contention

The response omits rollback risk.

### Defense

The response was intentionally concise.

### Prosecution

Concision does not justify omitting a material risk.

### Judge

Score: 0.42

Rationale:

The omission is material.
"""
    assert record.render_markdown() == expected
    assert (
        record.content_hash()
        == DebateRecord.model_validate(record.model_dump(mode="json")).content_hash()
    )
    assert len(record.content_hash()) == 64


def test_runner_reuses_exact_record_and_has_no_reporter_call() -> None:
    provider = ScriptedInferenceProvider()
    target = _target()
    config = CourtroomConfig(
        rounds=2,
        max_contentions=1,
        turn_token_budget=64,
        judge_rationale_token_budget=40,
        feedback_token_budget=80,
    )

    result = CourtroomRunner(model_provider=provider).run_target(
        evaluation_id="evaluation:test",
        target=target,
        config=config,
    )

    record = result.debate_records[0]
    first_round_view = DebateRecord(
        contention_id=record.contention_id,
        initial_contention=record.initial_contention,
        turn_token_budget=record.turn_token_budget,
        transcript_token_budget=record.transcript_token_budget,
        rounds=[record.rounds[0]],
    ).render_markdown()
    round_two_prompts = provider.prompts[4:8]
    final_prompt = provider.prompts[-1]

    assert len(provider.requests) == 9
    assert all(first_round_view in prompt for prompt in round_two_prompts)
    assert record.render_markdown() in final_prompt
    assert record.content_hash() in final_prompt
    assert all("court reporter" not in prompt.lower() for prompt in provider.prompts)
    assert result.feedback_prompts[0].provenance.debate_record_sha256 == record.content_hash()
    assert result.feedback_prompts[0].feedback_prompt.startswith("State the missing rollback")


def test_all_generation_and_transcript_budgets_are_calculated() -> None:
    provider = ScriptedInferenceProvider()
    config = CourtroomConfig(
        rounds=1,
        max_contentions=2,
        turn_token_budget=64,
        judge_rationale_token_budget=40,
        feedback_token_budget=80,
    )
    result = CourtroomRunner(model_provider=provider).run_target(
        evaluation_id="evaluation:test",
        target=_target(),
        config=config,
    )

    assert provider.requests[0].max_tokens == 192
    assert all(record.turn_token_budget == 64 for record in result.debate_records)
    assert all(
        record.transcript_token_budget == config.maximum_transcript_tokens()
        for record in result.debate_records
    )
    assert config.maximum_transcript_tokens() == 64 + (3 * 64 + 40 + 64) + 32


def test_cli_persists_canonical_records_markdown_and_feedback(tmp_path: Path) -> None:
    output_dir = tmp_path / "evaluations"
    provider = ScriptedInferenceProvider()
    result = run_from_args(
        build_parser().parse_args(
            [
                str(_write_action_graph(tmp_path)),
                "--output-dir",
                str(output_dir),
                "--rounds",
                "2",
                "--contentions",
                "1",
                "--turn-token-budget",
                "64",
            ]
        ),
        model_provider=provider,
    )

    artifact_dir = Path(result.artifact_dir or "")
    prompt = result.targets[0].feedback_prompts[0]
    record_path = artifact_dir / prompt.provenance.debate_record_ref
    markdown_path = record_path.with_suffix(".md")
    payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    persisted_record = DebateRecord.model_validate(payload["debate_record"])

    assert record_path.exists()
    assert markdown_path.read_text(encoding="utf-8") == persisted_record.render_markdown()
    assert persisted_record.content_hash() == prompt.provenance.debate_record_sha256
    assert (artifact_dir / "feedback_prompts.yaml").exists()
    assert not list(artifact_dir.rglob("*summary*"))
    assert not list(artifact_dir.rglob("*activation*"))
    assert not list(artifact_dir.rglob("*steering*"))
    unwanted_key = "confi" + "dence"
    assert unwanted_key not in json.dumps(result.model_dump(mode="json")).lower()
    assert all(unwanted_key not in prompt.lower() for prompt in provider.prompts)
    assert all(
        unwanted_key not in path.read_text(encoding="utf-8").lower()
        for path in artifact_dir.rglob("*")
        if path.is_file()
    )


def test_cli_prints_declarative_feedback_prompt(tmp_path: Path, monkeypatch, capsys) -> None:
    graph_path = _write_action_graph(tmp_path)
    monkeypatch.setattr(
        "specter.cli._build_model_provider", lambda args: ScriptedInferenceProvider()
    )

    exit_code = main(
        [
            str(graph_path),
            "--output-dir",
            str(tmp_path / "evaluations"),
            "--rounds",
            "1",
            "--contentions",
            "1",
        ]
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Evaluation: evaluation:" in output
    assert "Feedback prompts:" in output
    assert "State the missing rollback" in output


def test_final_judge_can_decline_a_correction() -> None:
    result = CourtroomRunner(
        model_provider=ScriptedInferenceProvider(disposition="no_correction")
    ).run_target(
        evaluation_id="evaluation:test",
        target=_target(),
        config=CourtroomConfig(rounds=1, max_contentions=1),
    )

    assert result.feedback_prompts[0].disposition == FeedbackDisposition.NO_CORRECTION
    assert result.feedback_prompts[0].feedback_prompt.startswith("The response is adequately")


def test_final_judge_requires_structured_output() -> None:
    class InvalidFinalProvider(ScriptedInferenceProvider):
        def complete(self, request: ModelRequest) -> ModelResult:
            if "You are the final feedback judge" in request.prompt:
                return ModelResult(text="apply it", provider="scripted", token_count=2)
            return super().complete(request)

    with pytest.raises(ValueError, match="valid disposition JSON"):
        CourtroomRunner(model_provider=InvalidFinalProvider()).run_target(
            evaluation_id="evaluation:test",
            target=_target(),
            config=CourtroomConfig(rounds=1, max_contentions=1),
        )


def _target() -> FeedbackTargetNode:
    return FeedbackTargetNode(
        query_id="query:child",
        expert_id="expert:cluster-1",
        query_text="Assess the deployment risk",
        context_text=(
            "The rollout has no rollback automation and uses one regional control plane."
        ),
        response_text="The deployment risk is moderate.",
        model_name="expert-model-1",
        sender_id="query:root",
        parent_query_text="Review the infrastructure plan",
        delegation_query="Assess the deployment risk",
    )


def _write_action_graph(tmp_path: Path) -> Path:
    unwanted_key = "confi" + "dence"
    graph = {
        "schema": "dullahan.action_graph.v1",
        "trace_id": "trace:test",
        "root_query_id": "query:root",
        "nodes": [
            {
                "id": "query:root",
                "depth": 0,
                "sender_id": "user",
                "query": {"query": "Review the infrastructure plan"},
                "context": None,
                "response": None,
                "responses": [],
            },
            {
                "id": "query:child",
                "depth": 1,
                "sender_id": "query:root",
                "query": {"query": "Assess the deployment risk"},
                "context": {
                    "documents": [
                        {
                            "id": "doc:1",
                            "text": "Karpenter creates GPU nodes for burst capacity.",
                        }
                    ]
                },
                "response": {
                    "expert_id": "expert:cluster-1",
                    "response": "The deployment risk is moderate.",
                    "routing_metadata": {},
                    unwanted_key: 0.8,
                },
                "responses": [],
            },
        ],
        "edges": [
            {
                "source": "query:root",
                "target": "query:child",
                "query": "Assess the deployment risk",
            }
        ],
    }
    path = tmp_path / "action_graph.json"
    path.write_text(json.dumps(graph), encoding="utf-8")
    return path

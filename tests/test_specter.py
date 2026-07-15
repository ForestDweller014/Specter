import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from specter.activation.contrast_set_builder import MinimalPairContrastSetBuilder
from specter.activation.hook_runner import TransformerLensHookRunner
from specter.activation.models import ActivationLocalization
from specter.cli import build_parser, main, run_from_args
from specter.config import CourtroomConfig
from specter.courtroom.debate_runner import CourtroomRunner
from specter.courtroom.models import FeedbackDisposition, FeedbackItem, FeedbackTargetNode
from specter.feedback.apply_cli import (
    build_parser as build_apply_parser,
)
from specter.feedback.apply_cli import (
    main as apply_main,
)
from specter.feedback.apply_cli import (
    run_from_args as run_apply_from_args,
)
from specter.feedback.feedback_loader import FeedbackArtifactLoader, FeedbackLoadError
from specter.feedback.localize_cli import (
    build_parser as build_localize_parser,
)
from specter.feedback.localize_cli import (
    main as localize_main,
)
from specter.feedback.localize_cli import (
    run_from_args as run_localize_from_args,
)
from specter.feedback.run_hooks_cli import (
    build_parser as build_run_hooks_parser,
)
from specter.feedback.run_hooks_cli import (
    main as run_hooks_main,
)
from specter.feedback.run_hooks_cli import (
    run_from_args as run_hooks_from_args,
)
from specter.graph_loader import ActionGraphLoader
from specter.model_provider import ModelProvider, ModelRequest, ModelResult


class ScriptedInferenceProvider(ModelProvider):
    """Deterministic test double for inference that is not under direct test."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete(self, request: ModelRequest) -> ModelResult:
        self.prompts.append(request.prompt)
        if "JSON array" in request.prompt:
            text = json.dumps(
                [
                    (
                        "The delegated query may not faithfully preserve the parent query intent. "
                        "Parent query: Review the infrastructure plan. "
                        "Delegated query: Assess the deployment risk."
                    ),
                    "The response may not be sufficiently grounded in the supplied context.",
                ]
            )
        elif "Previous contention:" in request.prompt:
            text = "model revised contention"
        elif "You are the defender" in request.prompt:
            text = "model defense"
        elif "You are the prosecutor" in request.prompt:
            text = "model prosecution rebuttal"
        elif "You are the final feedback judge" in request.prompt:
            text = json.dumps(
                {
                    "disposition": "apply_correction",
                    "feedback_text": (
                        "Use the supplied evidence and state unresolved deployment risks."
                    ),
                }
            )
        elif "You are the judge" in request.prompt:
            text = "0.42 prosecution is moderately strong"
        elif "You are the court reporter" in request.prompt:
            text = "compressed model summary"
        else:
            raise AssertionError(f"unexpected inference prompt: {request.prompt}")
        return ModelResult(text=text, provider="scripted", token_count=len(text.split()))


class ScriptedTransformerLensLocator:
    """Test double for activation analysis when localization itself is not under test."""

    def __init__(self, **kwargs) -> None:
        self.dependencies = kwargs

    def locate(self, request, *, heatmap_ref=None):
        item = request.feedback_item
        return SimpleNamespace(
            localization=ActivationLocalization(
                feedback_id=item.feedback_id,
                query_id=item.query_id,
                expert_id=item.expert_id,
                contention_id=item.contention_id,
                disposition=item.disposition,
                prosecution_strength=item.prosecution_strength,
                layer=3,
                token_position=1,
                token_position_policy="token-index:1",
                direction_vector_ref=request.direction_vector_ref,
                heatmap_ref=heatmap_ref,
                projection_strength=0.9,
                confidence=0.7,
                backend="transformerlens",
                contrast_pairs=MinimalPairContrastSetBuilder().build(
                    item, pair_count=request.contrast_pair_count
                ),
            ),
            direction_vector=[0.1, -0.2, 0.3],
            heatmap=[[0.1, 0.2], [0.3, 0.9]],
        )


class ScriptedTransformerLensAdapter:
    def __init__(self, *, model_path: str) -> None:
        self.model_path = model_path

    def load_model(self):
        return object()


def test_action_graph_loader_returns_answered_targets(tmp_path: Path) -> None:
    # Tests answered-node selection and preservation of graph, delegation, and response fields.
    graph_path = _write_action_graph(tmp_path)

    graph, targets = ActionGraphLoader().load_targets(graph_path)

    assert graph["trace_id"] == "trace:test"
    assert len(targets) == 1
    assert targets[0].query_id == "query:child"
    assert targets[0].expert_id == "expert:cluster-1"
    assert targets[0].sender_id == "query:root"
    assert targets[0].parent_query_id == "query:root"
    assert targets[0].parent_query_text == "Review the infrastructure plan"
    assert targets[0].delegation_query == "Assess the deployment risk"
    assert targets[0].query_text == "Assess the deployment risk"
    assert "Karpenter creates GPU nodes" in targets[0].context_text
    assert targets[0].response_text == "The deployment risk is moderate."


def test_courtroom_cli_persists_feedback_artifacts(tmp_path: Path) -> None:
    # Tests inference-backed courtroom orchestration and its persisted per-target artifacts.
    graph_path = _write_action_graph(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    args = build_parser().parse_args(
        [
            str(graph_path),
            "--repo-root",
            str(repo_root),
            "--rounds",
            "2",
            "--contentions",
            "2",
            "--summary-token-budget",
            "64",
            "--response-token-budget",
            "80",
            "--persist",
        ]
    )

    result = run_from_args(args, model_provider=ScriptedInferenceProvider())

    assert result.feedback_id.startswith("feedback:")
    assert result.source_trace_id == "trace:test"
    assert len(result.targets) == 1
    assert len(result.targets[0].contentions) == 2
    assert "delegated query" in result.targets[0].contentions[0].text
    assert "Review the infrastructure plan" in result.targets[0].contentions[0].text
    assert len(result.targets[0].rounds) == 2
    assert len(result.targets[0].feedback_items) == 2
    assert result.artifact_dir is not None

    artifact_dir = Path(result.artifact_dir)
    manifest = yaml.safe_load((artifact_dir / "manifest.yaml").read_text(encoding="utf-8"))
    final_feedback = yaml.safe_load(
        (artifact_dir / "final_feedback.yaml").read_text(encoding="utf-8")
    )
    target_dir = artifact_dir / "targets" / "query_child"

    assert manifest["source_trace_id"] == "trace:test"
    assert manifest["target_count"] == 1
    assert len(final_feedback["feedback_items"]) == 2
    assert final_feedback["schema"] == "specter.final_feedback.v2"
    assert final_feedback["feedback_items"][0]["disposition"] == "apply_correction"
    assert final_feedback["feedback_items"][0]["feedback_text"].startswith(
        "Use the supplied evidence"
    )
    assert (target_dir / "target.yaml").exists()
    assert (target_dir / "contentions.yaml").exists()
    assert (target_dir / "rounds.yaml").exists()
    assert (target_dir / "debate_summaries.yaml").exists()
    assert (target_dir / "judge_scores.yaml").exists()
    assert (target_dir / "final_feedback.yaml").exists()


def test_inference_clis_reject_removed_deterministic_backends() -> None:
    # Tests that production CLI choices cannot select the removed model stand-ins.
    with pytest.raises(SystemExit):
        build_parser().parse_args(
            ["action_graph.json", "--courtroom-model-provider", "deterministic"]
        )
    with pytest.raises(SystemExit):
        build_localize_parser().parse_args(["feedback-dir", "--backend", "deterministic"])


def test_courtroom_cli_text_output(tmp_path: Path, monkeypatch, capsys) -> None:
    # Tests CLI summary formatting while a scripted provider substitutes external inference.
    graph_path = _write_action_graph(tmp_path)
    monkeypatch.setattr(
        "specter.cli._build_model_provider",
        lambda args: ScriptedInferenceProvider(),
    )

    exit_code = main(
        [
            str(graph_path),
            "--repo-root",
            str(tmp_path),
            "--rounds",
            "1",
            "--contentions",
            "1",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Feedback: feedback:" in captured.out
    assert "Source trace: trace:test" in captured.out
    assert "Targets: 1" in captured.out
    assert "Contentions: 1" in captured.out


def test_courtroom_cli_json_output(tmp_path: Path, monkeypatch, capsys) -> None:
    # Tests CLI JSON serialization while a scripted provider substitutes external inference.
    graph_path = _write_action_graph(tmp_path)
    monkeypatch.setattr(
        "specter.cli._build_model_provider",
        lambda args: ScriptedInferenceProvider(),
    )

    exit_code = main(
        [
            str(graph_path),
            "--repo-root",
            str(tmp_path),
            "--rounds",
            "1",
            "--contentions",
            "1",
            "--json",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"feedback_id": "feedback:' in captured.out
    assert '"source_trace_id": "trace:test"' in captured.out


def test_courtroom_runner_can_use_model_backed_roles() -> None:
    # Tests role dispatch, final judge feedback, and parsing while inference is mocked.
    class FakeModelProvider:
        def __init__(self) -> None:
            self.prompts = []
            self.requests = []

        def complete(self, request):
            self.prompts.append(request.prompt)
            self.requests.append(request)
            if "JSON array" in request.prompt:
                text = '["model contention"]'
            elif "You are the defender" in request.prompt:
                text = "model defense"
            elif "You are the prosecutor" in request.prompt:
                text = "model prosecution rebuttal"
            elif "You are the final feedback judge" in request.prompt:
                text = json.dumps(
                    {
                        "disposition": "apply_correction",
                        "feedback_text": "model-facing corrective feedback",
                    }
                )
            elif "You are the judge" in request.prompt:
                text = "0.42 prosecution is moderately strong"
            elif "You are the court reporter" in request.prompt:
                text = "compressed model summary"
            else:
                text = "unexpected"
            return ModelResult(text=text, provider="fake", token_count=len(text.split()))

    provider = FakeModelProvider()
    target = FeedbackTargetNode(
        query_id="query:child",
        expert_id="expert:cluster-1",
        query={"query": "Assess deployment risk"},
        context={"documents": [{"text": "GPU nodes are provisioned dynamically."}]},
        response={
            "response": "Risk is moderate.",
            "routing_metadata": {"model": "expert-model-1"},
        },
        sender_id="query:root",
    )

    result = CourtroomRunner(model_provider=provider).run_target(
        feedback_id="feedback:test",
        target=target,
        config=CourtroomConfig(
            rounds=1,
            max_contentions=1,
            feedback_token_budget=55,
            inference_temperature=0.35,
        ),
    )

    item = result.rounds[0].items[0]

    assert item.defense == "model defense"
    assert item.prosecution_rebuttal == "model prosecution rebuttal"
    assert item.judge_score.prosecution_strength == 0.42
    assert item.running_summary_after == "compressed model summary"
    assert len(provider.prompts) == 6
    assert all(request.temperature == 0.35 for request in provider.requests)
    assert provider.requests[-1].max_tokens == 55
    assert "Expert model: expert-model-1" in provider.prompts[1]
    assert result.feedback_items[0].running_debate_summary == "compressed model summary"
    assert result.feedback_items[0].disposition == FeedbackDisposition.APPLY_CORRECTION
    assert result.feedback_items[0].feedback_text == "model-facing corrective feedback"
    assert "Final courtroom summary:\ncompressed model summary" in provider.prompts[-1]
    assert "score=0.42" in provider.prompts[-1]
    assert "exactly apply_correction or no_correction" in provider.prompts[-1]


def test_final_judge_no_correction_is_not_localized_or_applied(tmp_path: Path) -> None:
    # Tests the fail-closed path from an explicit final disposition through hook materialization.
    class NoCorrectionProvider(ScriptedInferenceProvider):
        def complete(self, request: ModelRequest) -> ModelResult:
            if "You are the final feedback judge" in request.prompt:
                self.prompts.append(request.prompt)
                text = json.dumps(
                    {
                        "disposition": "no_correction",
                        "feedback_text": "The response is adequately supported by the evidence.",
                    }
                )
                return ModelResult(text=text, provider="scripted", token_count=len(text.split()))
            if "You are the judge" in request.prompt:
                self.prompts.append(request.prompt)
                text = "-0.8 defense is strongly supported"
                return ModelResult(text=text, provider="scripted", token_count=len(text.split()))
            return super().complete(request)

    graph_path = _write_action_graph(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    courtroom_result = run_from_args(
        build_parser().parse_args(
            [
                str(graph_path),
                "--repo-root",
                str(repo_root),
                "--rounds",
                "1",
                "--contentions",
                "1",
                "--persist",
            ]
        ),
        model_provider=NoCorrectionProvider(),
    )

    feedback_item = courtroom_result.targets[0].feedback_items[0]
    assert feedback_item.disposition == FeedbackDisposition.NO_CORRECTION
    assert feedback_item.prosecution_strength == -0.8

    feedback_dir = Path(courtroom_result.artifact_dir)
    plan = run_localize_from_args(
        build_localize_parser().parse_args([str(feedback_dir)])
    )
    localization_payload = yaml.safe_load(
        (feedback_dir / "activation_localizations.yaml").read_text(encoding="utf-8")
    )

    assert plan.items == []
    assert localization_payload["localizations"] == []
    assert localization_payload["skipped_feedback_items"] == [
        {
            "contention_id": feedback_item.contention_id,
            "disposition": "no_correction",
            "prosecution_strength": -0.8,
            "reason": "final_judge_declined_correction",
        }
    ]

    bundle, _ = run_apply_from_args(
        build_apply_parser().parse_args([str(feedback_dir / "feedback_plan.json")])
    )
    assert bundle.hook_specs == []


def test_positive_disposition_with_negative_score_cannot_reverse_feedback(tmp_path: Path) -> None:
    # Tests defense in depth when the final disposition conflicts with the signed round score.
    feedback_dir = _build_courtroom_feedback(tmp_path, contentions=1)
    feedback_path = feedback_dir / "final_feedback.yaml"
    payload = yaml.safe_load(feedback_path.read_text(encoding="utf-8"))
    payload["feedback_items"][0]["prosecution_strength"] = -0.8
    feedback_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    plan = run_localize_from_args(
        build_localize_parser().parse_args([str(feedback_dir)])
    )
    localization_payload = yaml.safe_load(
        (feedback_dir / "activation_localizations.yaml").read_text(encoding="utf-8")
    )

    assert plan.items == []
    assert localization_payload["skipped_feedback_items"][0]["disposition"] == (
        "apply_correction"
    )
    assert localization_payload["skipped_feedback_items"][0]["reason"] == (
        "non_positive_prosecution_strength"
    )


def test_final_judge_rejects_feedback_without_explicit_disposition() -> None:
    # Tests that unstructured judge output cannot silently become applicable feedback.
    class UnstructuredFeedbackProvider(ScriptedInferenceProvider):
        def complete(self, request: ModelRequest) -> ModelResult:
            if "You are the final feedback judge" in request.prompt:
                text = "Apply this correction without a disposition."
                return ModelResult(text=text, provider="scripted", token_count=len(text.split()))
            return super().complete(request)

    target = FeedbackTargetNode(
        query_id="query:child",
        expert_id="expert:cluster-1",
        query={"query": "Assess deployment risk"},
        context={"documents": [{"text": "GPU nodes are provisioned dynamically."}]},
        response={"response": "Risk is moderate."},
        sender_id="query:root",
    )

    with pytest.raises(
        ValueError,
        match="final feedback judge must return a valid disposition JSON object",
    ):
        CourtroomRunner(model_provider=UnstructuredFeedbackProvider()).run_target(
            feedback_id="feedback:test",
            target=target,
            config=CourtroomConfig(rounds=1, max_contentions=1),
        )


def test_legacy_feedback_artifact_without_disposition_fails_closed(tmp_path: Path) -> None:
    # Tests the intentional migration boundary for persisted feedback artifacts.
    (tmp_path / "manifest.yaml").write_text("feedback_id: feedback:legacy\n", encoding="utf-8")
    (tmp_path / "final_feedback.yaml").write_text(
        "feedback_items: []\n",
        encoding="utf-8",
    )

    with pytest.raises(FeedbackLoadError, match="regenerate"):
        FeedbackArtifactLoader().load(tmp_path)


def test_courtroom_runner_evolves_contentions_after_first_round() -> None:
    # Tests inference-backed contention revision, token limits, and stable contention identity.
    target = FeedbackTargetNode(
        query_id="query:child",
        expert_id="expert:cluster-1",
        query={"query": "Assess deployment risk"},
        context={"documents": [{"text": "GPU nodes are provisioned dynamically."}]},
        response={"response": "Risk is moderate."},
        sender_id="query:root",
    )

    provider = ScriptedInferenceProvider()
    result = CourtroomRunner(model_provider=provider).run_target(
        feedback_id="feedback:test",
        target=target,
        config=CourtroomConfig(
            rounds=2,
            max_contentions=1,
            contention_token_budget=18,
        ),
    )

    first_round_contention = result.rounds[0].items[0].contention_text
    second_round_contention = result.rounds[1].items[0].contention_text

    assert first_round_contention != second_round_contention
    assert len(first_round_contention.split()) <= 18
    assert len(second_round_contention.split()) <= 18
    assert result.rounds[0].items[0].contention_id == result.rounds[1].items[0].contention_id
    assert "Round 1: score=0.42" in provider.prompts[-1]
    assert "Round 2: score=0.42" in provider.prompts[-1]


def test_courtroom_model_provider_can_revise_contentions() -> None:
    # Tests model-driven revision while a fake provider mocks revision and role responses.
    class FakeModelProvider:
        def __init__(self) -> None:
            self.prompts = []

        def complete(self, request):
            self.prompts.append(request.prompt)
            if "JSON array" in request.prompt:
                text = '["initial model contention"]'
            elif "Previous contention:" in request.prompt:
                text = "model revised contention"
            elif "You are the defender" in request.prompt:
                text = "model defense"
            elif "You are the prosecutor" in request.prompt:
                text = "model prosecution rebuttal"
            elif "You are the final feedback judge" in request.prompt:
                text = json.dumps(
                    {
                        "disposition": "apply_correction",
                        "feedback_text": "model-facing corrective feedback",
                    }
                )
            elif "You are the judge" in request.prompt:
                text = "0.25 prosecution is somewhat strong"
            elif "You are the court reporter" in request.prompt:
                text = "compressed model summary"
            else:
                text = "unexpected"
            return ModelResult(text=text, provider="fake", token_count=len(text.split()))

    target = FeedbackTargetNode(
        query_id="query:child",
        expert_id="expert:cluster-1",
        query={"query": "Assess deployment risk"},
        context={"documents": [{"text": "GPU nodes are provisioned dynamically."}]},
        response={"response": "Risk is moderate."},
        sender_id="query:root",
    )

    result = CourtroomRunner(model_provider=FakeModelProvider()).run_target(
        feedback_id="feedback:test",
        target=target,
        config=CourtroomConfig(rounds=2, max_contentions=1),
    )

    assert result.rounds[1].items[0].contention_text == "model revised contention"
    assert result.rounds[1].items[0].defense == "model defense"


def test_localize_feedback_cli_writes_feedback_plan(tmp_path: Path) -> None:
    # Tests real-backend artifact wiring while scripted activation analysis supplies model outputs.
    graph_path = _write_action_graph(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    courtroom_result = run_from_args(
        build_parser().parse_args(
            [
                str(graph_path),
                "--repo-root",
                str(repo_root),
                "--rounds",
                "1",
                "--contentions",
                "2",
                "--persist",
            ]
        ),
        model_provider=ScriptedInferenceProvider(),
    )

    args = build_localize_parser().parse_args(
        [
            str(courtroom_result.artifact_dir),
            "--contrast-pairs",
            "2",
            "--n-layers",
            "6",
            "--scale",
            "0.3",
            "--model-path",
            "fake-model",
        ]
    )
    plan = run_localize_from_args(args, locator=ScriptedTransformerLensLocator())

    feedback_dir = Path(courtroom_result.artifact_dir)
    feedback_plan = json.loads((feedback_dir / "feedback_plan.json").read_text(encoding="utf-8"))
    localizations = yaml.safe_load(
        (feedback_dir / "activation_localizations.yaml").read_text(encoding="utf-8")
    )
    vector_files = list((feedback_dir / "steering_vectors").glob("*.json"))
    heatmap_files = list((feedback_dir / "activation_heatmaps").glob("*.json"))

    assert plan.schema_ == "specter.feedback_plan.v2"
    assert plan.feedback_id == courtroom_result.feedback_id
    assert plan.source_trace_id == "trace:test"
    assert plan.backend == "transformerlens"
    assert len(plan.items) == 2
    assert feedback_plan["schema"] == "specter.feedback_plan.v2"
    assert len(localizations["localizations"]) == 2
    assert len(localizations["localizations"][0]["contrast_pairs"]) == 2
    assert localizations["localizations"][0]["heatmap_ref"].startswith("activation_heatmaps/")
    assert len(vector_files) == 2
    assert len(heatmap_files) == 2


def test_localize_feedback_cli_text_output(tmp_path: Path, monkeypatch, capsys) -> None:
    # Tests localization CLI text output while model loading and activation analysis are scripted.
    graph_path = _write_action_graph(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    courtroom_result = run_from_args(
        build_parser().parse_args(
            [
                str(graph_path),
                "--repo-root",
                str(repo_root),
                "--rounds",
                "1",
                "--contentions",
                "1",
                "--persist",
            ]
        ),
        model_provider=ScriptedInferenceProvider(),
    )
    monkeypatch.setattr(
        "specter.feedback.localize_cli.TransformerLensAdapter",
        ScriptedTransformerLensAdapter,
    )
    monkeypatch.setattr(
        "specter.feedback.localize_cli.TransformerLensActivationLocator",
        ScriptedTransformerLensLocator,
    )

    exit_code = localize_main([str(courtroom_result.artifact_dir), "--model-path", "fake-model"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert f"Feedback plan: {courtroom_result.feedback_id}" in captured.out
    assert "Plan items: 1" in captured.out


def test_contrast_builder_removes_feedback_concept_from_negative() -> None:
    # Tests that contrast localization uses judge feedback rather than the courtroom summary.
    item = FeedbackItem(
        feedback_id="feedback:test",
        query_id="query:test",
        expert_id="expert:test",
        contention_id="contention:test",
        running_debate_summary=(
            "Prosecution argues the response is unsupported and the judge finds "
            "the prosecution signal strong."
        ),
        disposition=FeedbackDisposition.APPLY_CORRECTION,
        feedback_text=(
            "Ground the deployment risk in the missing rollback automation and regional "
            "control-plane dependency."
        ),
        prosecution_strength=0.8,
        target_query="Assess deployment risk",
        target_context="Karpenter creates GPU nodes for burst capacity. Extra context.",
        target_response="The deployment risk is moderate.",
    )

    pair = MinimalPairContrastSetBuilder().build(item, pair_count=1)[0]

    assert "Ground the deployment risk" in pair.positive
    assert "Prosecution argues" not in pair.positive
    assert "Prosecution argues" not in pair.negative
    assert "unsupported" not in pair.negative
    assert "Assess deployment risk" in pair.negative
    assert "Karpenter creates GPU nodes" in pair.negative
    assert pair.metadata["construction"] == "deterministic_topic_matched_concept_removed"


def test_localize_feedback_transformerlens_backend_writes_heatmaps(
    tmp_path: Path,
    monkeypatch,
) -> None:
    # Tests TransformerLens artifact wiring while fake adapter and locator mock model analysis.
    feedback_dir = _build_courtroom_feedback(tmp_path, contentions=1)

    class FakeAdapter:
        def __init__(self, *, model_path: str) -> None:
            self.model_path = model_path

        def load_model(self):
            return object()

    class FakeLocator:
        backend_name = "transformerlens"

        def __init__(self, *, adapter, model) -> None:
            self.adapter = adapter
            self.model = model

        def locate(self, request, *, heatmap_ref=None):
            item = request.feedback_item
            return SimpleNamespace(
                localization=ActivationLocalization(
                    feedback_id=item.feedback_id,
                    query_id=item.query_id,
                    expert_id=item.expert_id,
                    contention_id=item.contention_id,
                    disposition=item.disposition,
                    prosecution_strength=item.prosecution_strength,
                    layer=3,
                    token_position=5,
                    token_position_policy="token-index:5",
                    direction_vector_ref=request.direction_vector_ref,
                    heatmap_ref=heatmap_ref,
                    projection_strength=0.9,
                    confidence=0.7,
                    backend="transformerlens",
                    contrast_pairs=[],
                ),
                direction_vector=[0.1, -0.2, 0.3],
                heatmap=[[0.1, 0.2], [0.3, 0.9]],
            )

    monkeypatch.setattr(
        "specter.feedback.localize_cli.TransformerLensAdapter",
        FakeAdapter,
    )
    monkeypatch.setattr(
        "specter.feedback.localize_cli.TransformerLensActivationLocator",
        FakeLocator,
    )

    plan = run_localize_from_args(
        build_localize_parser().parse_args(
            [
                str(feedback_dir),
                "--backend",
                "transformerlens",
                "--model-path",
                "fake-model",
            ]
        )
    )

    localization_payload = yaml.safe_load(
        (feedback_dir / "activation_localizations.yaml").read_text(encoding="utf-8")
    )
    heatmap_path = feedback_dir / localization_payload["localizations"][0]["heatmap_ref"]
    vector_path = feedback_dir / plan.items[0].direction_vector_ref
    heatmap = json.loads(heatmap_path.read_text(encoding="utf-8"))
    vector = json.loads(vector_path.read_text(encoding="utf-8"))

    assert plan.backend == "transformerlens"
    assert plan.items[0].layer == 3
    assert plan.items[0].token_position_policy == "token-index:5"
    assert heatmap["schema"] == "specter.activation_heatmap.v1"
    assert heatmap["heatmap"] == [[0.1, 0.2], [0.3, 0.9]]
    assert vector["vector"] == [0.1, -0.2, 0.3]


def test_apply_feedback_cli_writes_activation_hooks(tmp_path: Path) -> None:
    # Tests hook materialization: vector scaling, residual hook points, and manifest output.
    feedback_dir = _build_feedback_plan(tmp_path, contentions=2)
    plan = json.loads((feedback_dir / "feedback_plan.json").read_text(encoding="utf-8"))
    first_item = plan["items"][0]
    vector_payload = json.loads(
        (feedback_dir / first_item["direction_vector_ref"]).read_text(encoding="utf-8")
    )

    args = build_apply_parser().parse_args(
        [
            str(feedback_dir / "feedback_plan.json"),
            "--scale",
            "0.5",
        ]
    )
    bundle, output_dir = run_apply_from_args(args)

    hooks = json.loads((output_dir / "activation_hooks.json").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((output_dir / "manifest.yaml").read_text(encoding="utf-8"))
    expected_first_value = round(
        vector_payload["vector"][0] * first_item["prosecution_strength"] * 0.5,
        8,
    )

    assert bundle.schema_ == "specter.applied_feedback.v2"
    assert bundle.feedback_id == plan["feedback_id"]
    assert len(bundle.hook_specs) == 2
    assert hooks["schema"] == "specter.applied_feedback.v2"
    assert hooks["hook_specs"][0]["hook_point"].startswith("blocks.")
    assert hooks["hook_specs"][0]["scaled_vector"][0] == expected_first_value
    assert manifest["hook_count"] == 2
    assert manifest["hook_spec_file"] == "activation_hooks.json"


def test_apply_feedback_cli_text_output(tmp_path: Path, capsys) -> None:
    # Tests that the feedback application CLI reports its application ID and generated hook count.
    feedback_dir = _build_feedback_plan(tmp_path, contentions=1)

    exit_code = apply_main([str(feedback_dir / "feedback_plan.json")])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Applied feedback: application:" in captured.out
    assert "Hook specs: 1" in captured.out


def test_run_feedback_hooks_cli_uses_filtered_hooks(
    tmp_path: Path,
    monkeypatch,
) -> None:
    # Tests expert hook filtering and arguments while a fake adapter mocks model inference.
    feedback_dir = _build_feedback_plan(tmp_path, contentions=2)
    bundle, output_dir = run_apply_from_args(
        build_apply_parser().parse_args([str(feedback_dir / "feedback_plan.json")])
    )
    captured_calls = {}

    class FakeAdapter:
        def __init__(self, *, model_path: str) -> None:
            self.model_path = model_path

        def load_model(self):
            return object()

        def generate_with_hooks(self, model, prompt, *, fwd_hooks, max_new_tokens):
            captured_calls["prompt"] = prompt
            captured_calls["hook_count"] = len(fwd_hooks)
            captured_calls["max_new_tokens"] = max_new_tokens
            return "hooked-output"

    monkeypatch.setattr(
        "specter.feedback.run_hooks_cli.TransformerLensAdapter",
        FakeAdapter,
    )

    result = run_hooks_from_args(
        build_run_hooks_parser().parse_args(
            [
                str(output_dir / "activation_hooks.json"),
                "--model-path",
                "fake-model",
                "--prompt",
                "Assess the deployment risk",
                "--expert-id",
                bundle.hook_specs[0].expert_id,
                "--max-new-tokens",
                "7",
            ]
        )
    )

    assert result.output == "hooked-output"
    assert result.applied_hook_ids == [hook.hook_id for hook in bundle.hook_specs]
    assert captured_calls["prompt"] == "Assess the deployment risk"
    assert captured_calls["hook_count"] == 2
    assert captured_calls["max_new_tokens"] == 7


def test_run_feedback_hooks_cli_text_output(tmp_path: Path, monkeypatch, capsys) -> None:
    # Tests hooked-inference CLI formatting while a fake adapter mocks model loading and generation.
    feedback_dir = _build_feedback_plan(tmp_path, contentions=1)
    _, output_dir = run_apply_from_args(
        build_apply_parser().parse_args([str(feedback_dir / "feedback_plan.json")])
    )

    class FakeAdapter:
        def __init__(self, *, model_path: str) -> None:
            self.model_path = model_path

        def load_model(self):
            return object()

        def generate_with_hooks(self, model, prompt, *, fwd_hooks, max_new_tokens):
            return "text-output"

    monkeypatch.setattr(
        "specter.feedback.run_hooks_cli.TransformerLensAdapter",
        FakeAdapter,
    )

    exit_code = run_hooks_main(
        [
            str(output_dir / "activation_hooks.json"),
            "--model-path",
            "fake-model",
            "--prompt",
            "Prompt",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Applied hooks: 1" in captured.out
    assert "text-output" in captured.out


def test_transformerlens_hook_runner_adds_scaled_vector_to_tensor() -> None:
    # Tests the real residual-stream hook math at a selected token using an actual PyTorch tensor.
    torch = pytest.importorskip("torch")

    feedback_dir = Path("/tmp/not-used")
    hook = SimpleNamespace(
        hook_id="hook:test",
        token_position_policy="token-index:1",
        scaled_vector=[0.5, -0.25],
    )
    runner = TransformerLensHookRunner(adapter=object(), model=object())
    hook_fn = runner._build_hook_fn(hook)
    activation = torch.zeros((1, 3, 2))

    result = hook_fn(activation, hook=None)

    assert result[0, 1, 0].item() == pytest.approx(0.5)
    assert result[0, 1, 1].item() == pytest.approx(-0.25)
    assert result[0, 0, 0].item() == pytest.approx(0.0)
    assert feedback_dir.name == "not-used"


def _build_feedback_plan(tmp_path: Path, *, contentions: int) -> Path:
    feedback_dir = _build_courtroom_feedback(tmp_path, contentions=contentions)
    run_localize_from_args(
        build_localize_parser().parse_args(
            [
                str(feedback_dir),
                "--contrast-pairs",
                "1",
                "--model-path",
                "fake-model",
            ]
        ),
        locator=ScriptedTransformerLensLocator(),
    )
    return feedback_dir


def _build_courtroom_feedback(tmp_path: Path, *, contentions: int) -> Path:
    graph_path = _write_action_graph(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(exist_ok=True)
    courtroom_result = run_from_args(
        build_parser().parse_args(
            [
                str(graph_path),
                "--repo-root",
                str(repo_root),
                "--rounds",
                "1",
                "--contentions",
                str(contentions),
                "--persist",
            ]
        ),
        model_provider=ScriptedInferenceProvider(),
    )
    return Path(courtroom_result.artifact_dir)


def _write_action_graph(tmp_path: Path) -> Path:
    graph = {
        "schema": "dullahan.action_graph.v1",
        "trace_id": "trace:test",
        "root_query_id": "query:root",
        "nodes": [
            {
                "id": "query:root",
                "label": "Root",
                "depth": 0,
                "sender_id": "user",
                "query": {
                    "sender_id": "user",
                    "query_id": "query:root",
                    "query": "Review the infrastructure plan",
                    "depth": 0,
                },
                "context": None,
                "response": None,
                "responses": [],
            },
            {
                "id": "query:child",
                "label": "Deployment risk",
                "depth": 1,
                "sender_id": "query:root",
                "query": {
                    "sender_id": "query:root",
                    "query_id": "query:child",
                    "query": "Assess the deployment risk",
                    "depth": 1,
                },
                "context": {
                    "query_id": "query:child",
                    "documents": [
                        {
                            "id": "doc:1",
                            "source": "world_state",
                            "text": "Karpenter creates GPU nodes for burst capacity.",
                            "score": 0.9,
                            "metadata": {},
                        }
                    ],
                    "token_budget": 512,
                },
                "response": {
                    "sender_id": "query:root",
                    "query_id": "query:child",
                    "subquery": "Assess the deployment risk",
                    "expert_id": "expert:cluster-1",
                    "response": "The deployment risk is moderate.",
                    "confidence": 0.8,
                    "cited_context_document_ids": ["doc:1"],
                    "routing_metadata": {},
                },
                "responses": [],
            },
        ],
        "edges": [
            {
                "id": "query_root__to__query_child",
                "source": "query:root",
                "target": "query:child",
                "query": "Assess the deployment risk",
                "label": "Deployment risk",
            }
        ],
    }
    path = tmp_path / "action_graph.json"
    path.write_text(json.dumps(graph), encoding="utf-8")
    return path

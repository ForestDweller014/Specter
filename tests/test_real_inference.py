from __future__ import annotations

import os
from pathlib import Path

import pytest

from specter.activation.activation_locator import LocalizationRequest
from specter.activation.transformerlens_adapter import TransformerLensAdapter
from specter.activation.transformerlens_locator import TransformerLensActivationLocator
from specter.config import CourtroomConfig
from specter.courtroom.debate_runner import CourtroomRunner
from specter.courtroom.models import FeedbackItem, FeedbackTargetNode
from specter.dullahan_inference import DullahanInferenceServer
from specter.model_provider import OpenAICompatibleHttpProvider


@pytest.mark.local_inference
def test_dullahan_inference_executes_every_courtroom_role() -> None:
    # Tests real contention generation/revision, defense, prosecution, judging, and reporting.
    if os.getenv("SPECTER_RUN_LOCAL_INFERENCE") != "1":
        pytest.skip("set SPECTER_RUN_LOCAL_INFERENCE=1 to run Dullahan inference")

    dullahan_root = Path(os.getenv("DULLAHAN_REPO_ROOT", "~/Documents/Dullahan")).expanduser()
    base_url = os.getenv("DULLAHAN_INFERENCE_BASE_URL", "http://127.0.0.1:30000/v1")
    provider = OpenAICompatibleHttpProvider(
        base_url=base_url,
        timeout_seconds=180,
        model_override=os.getenv("DULLAHAN_TEST_MODEL_ALIAS", "local-slm-runtime"),
        provider_name="dullahan-local-inference",
    )
    target = FeedbackTargetNode(
        query_id="query:deployment",
        expert_id="expert:infrastructure",
        query={"query": "Assess the deployment risk."},
        context={
            "documents": [
                {
                    "text": (
                        "The rollout has no rollback automation and depends on a single "
                        "regional control plane."
                    )
                }
            ]
        },
        response={"response": "The deployment risk is low."},
        sender_id="query:root",
        parent_query_text="Review the infrastructure rollout.",
        delegation_query="Assess the deployment risk.",
    )

    with DullahanInferenceServer(
        repo_root=dullahan_root,
        config_path=dullahan_root / "configs/inference.yaml",
        base_url=base_url,
        startup_timeout_seconds=30,
    ):
        result = CourtroomRunner(model_provider=provider).run_target(
            feedback_id="feedback:real-local",
            target=target,
            config=CourtroomConfig(
                rounds=2,
                max_contentions=1,
                contention_generation_token_budget=192,
                contention_token_budget=64,
                response_token_budget=96,
                judge_rationale_token_budget=64,
                summary_token_budget=96,
            ),
        )

    assert len(result.contentions) == 1
    assert result.contentions[0].text
    assert len(result.rounds) == 2
    item = result.rounds[0].items[0]
    assert item.defense
    assert item.prosecution_rebuttal
    assert -1.0 <= item.judge_score.prosecution_strength <= 1.0
    assert item.running_summary_after
    assert result.rounds[1].items[0].contention_text


@pytest.mark.local_inference
def test_real_transformerlens_localizes_feedback_activations() -> None:
    # Tests real cached residual activations, layer/token selection, heatmap, and steering vector.
    model_path = os.getenv("SPECTER_TRANSFORMERLENS_MODEL")
    if not model_path:
        pytest.skip("set SPECTER_TRANSFORMERLENS_MODEL to run activation localization")

    adapter = TransformerLensAdapter(model_path=model_path)
    model = adapter.load_model()
    item = FeedbackItem(
        feedback_id="feedback:real-local",
        query_id="query:deployment",
        expert_id="expert:infrastructure",
        contention_id="contention:grounding",
        running_debate_summary=(
            "The prosecution established that the response ignored rollback and regional risk."
        ),
        prosecution_strength=0.8,
        target_query="Assess the deployment risk.",
        target_context="There is no rollback automation and one regional control plane.",
        target_response="The deployment risk is low.",
    )

    result = TransformerLensActivationLocator(adapter=adapter, model=model).locate(
        LocalizationRequest(
            feedback_item=item,
            direction_vector_ref="steering_vectors/contention.json",
            contrast_pair_count=2,
            n_layers=adapter.n_layers(model),
        )
    )

    assert result.localization.backend == "transformerlens"
    assert result.localization.token_position is not None
    assert result.direction_vector
    assert result.heatmap

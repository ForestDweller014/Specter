from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from specter.activation.activation_locator import LocalizationRequest
from specter.activation.transformerlens_adapter import TransformerLensAdapter
from specter.activation.transformerlens_locator import TransformerLensActivationLocator
from specter.courtroom.models import FeedbackDisposition
from specter.feedback.feedback_loader import FeedbackArtifactLoader
from specter.feedback.plan_builder import FeedbackPlanBuilder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Localize courtroom feedback and emit a feedback plan."
    )
    parser.add_argument("feedback_dir", type=Path, help="Path to memory/feedback/<feedback_id>.")
    parser.add_argument(
        "--backend",
        choices=["transformerlens"],
        default="transformerlens",
    )
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--contrast-pairs", type=int, default=8)
    parser.add_argument("--n-layers", type=int, default=12)
    parser.add_argument("--scale", type=float, default=0.2)
    parser.add_argument("--application-mode", default="activation-hook")
    parser.add_argument("--json", action="store_true")
    return parser


def run_from_args(args: argparse.Namespace, *, adapter=None, locator=None):
    manifest, feedback_items = FeedbackArtifactLoader().load(args.feedback_dir)
    eligible_items = [
        item
        for item in feedback_items
        if item.disposition == FeedbackDisposition.APPLY_CORRECTION
        and item.prosecution_strength > 0
    ]
    skipped_items = [
        {
            "contention_id": item.contention_id,
            "disposition": item.disposition.value,
            "prosecution_strength": item.prosecution_strength,
            "reason": (
                "final_judge_declined_correction"
                if item.disposition != FeedbackDisposition.APPLY_CORRECTION
                else "non_positive_prosecution_strength"
            ),
        }
        for item in feedback_items
        if item not in eligible_items
    ]
    if locator is None and eligible_items:
        if not args.model_path:
            raise ValueError("--model-path is required for real TransformerLens localization")
        adapter = adapter or TransformerLensAdapter(model_path=args.model_path)
        model = adapter.load_model()
        locator = TransformerLensActivationLocator(adapter=adapter, model=model)

    vectors_dir = args.feedback_dir / "steering_vectors"
    vectors_dir.mkdir(parents=True, exist_ok=True)
    heatmaps_dir = args.feedback_dir / "activation_heatmaps"
    heatmaps_dir.mkdir(parents=True, exist_ok=True)
    localizations = []
    for item in eligible_items:
        vector_path = vectors_dir / f"{_safe_path_id(item.contention_id)}.json"
        direction_vector_ref = str(vector_path.relative_to(args.feedback_dir))
        request = LocalizationRequest(
            feedback_item=item,
            direction_vector_ref=direction_vector_ref,
            contrast_pair_count=args.contrast_pairs,
            n_layers=args.n_layers,
        )
        heatmap_path = heatmaps_dir / f"{_safe_path_id(item.contention_id)}.json"
        heatmap_ref = str(heatmap_path.relative_to(args.feedback_dir))
        result = locator.locate(request, heatmap_ref=heatmap_ref)
        _write_vector(
            vector_path,
            contention_id=item.contention_id,
            expert_id=item.expert_id,
            vector=result.direction_vector,
        )
        _write_heatmap(
            heatmap_path,
            contention_id=item.contention_id,
            expert_id=item.expert_id,
            heatmap=result.heatmap,
        )
        localizations.append(result.localization)

    plan = FeedbackPlanBuilder().build(
        manifest=manifest,
        backend=args.backend,
        feedback_scale=args.scale,
        application_mode=args.application_mode,
        localizations=localizations,
    )
    _write_yaml(
        args.feedback_dir / "activation_localizations.yaml",
        {
            "localizations": [
                localization.model_dump(mode="json") for localization in localizations
            ],
            "skipped_feedback_items": skipped_items,
        },
    )
    (args.feedback_dir / "feedback_plan.json").write_text(
        json.dumps(plan.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return plan


def format_text(plan) -> str:
    return "\n".join(
        [
            f"Feedback plan: {plan.feedback_id}",
            f"Source trace: {plan.source_trace_id}",
            f"Backend: {plan.backend}",
            f"Plan items: {len(plan.items)}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = run_from_args(args)
    if args.json:
        print(json.dumps(plan.model_dump(mode="json", by_alias=True), indent=2))
    else:
        print(format_text(plan))
    return 0


def _write_yaml(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as stream:
        yaml.safe_dump(data, stream, sort_keys=False)


def _write_vector(
    path: Path,
    *,
    contention_id: str,
    expert_id: str,
    vector: list[float],
) -> None:
    path.write_text(
        json.dumps(
            {
                "schema": "specter.steering_vector.v1",
                "contention_id": contention_id,
                "expert_id": expert_id,
                "vector": vector,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_heatmap(
    path: Path,
    *,
    contention_id: str,
    expert_id: str,
    heatmap: list[list[float]],
) -> None:
    path.write_text(
        json.dumps(
            {
                "schema": "specter.activation_heatmap.v1",
                "contention_id": contention_id,
                "expert_id": expert_id,
                "heatmap": heatmap,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _safe_path_id(identifier: str) -> str:
    return identifier.replace(":", "_").replace("/", "_").replace("\\", "_").replace(" ", "_")


if __name__ == "__main__":
    raise SystemExit(main())

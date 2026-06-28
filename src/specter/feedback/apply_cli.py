from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from specter.feedback.apply_runtime import (
    ActivationHookApplicationRuntime,
    FeedbackPlanLoader,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply a Specter feedback plan as reversible activation-hook specs."
    )
    parser.add_argument("feedback_plan", type=Path, help="Path to feedback_plan.json.")
    parser.add_argument(
        "--mode",
        choices=["activation-hook"],
        default="activation-hook",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=None,
        help="Optional scale override applied to every hook item.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory. Defaults to <feedback_dir>/applied/<application_id>.",
    )
    parser.add_argument("--json", action="store_true")
    return parser


def run_from_args(args: argparse.Namespace):
    feedback_dir = args.feedback_plan.parent
    plan = FeedbackPlanLoader().load(args.feedback_plan)
    runtime = ActivationHookApplicationRuntime()
    bundle = runtime.apply(
        plan=plan,
        feedback_dir=feedback_dir,
        scale_override=args.scale,
    )
    output_dir = args.output_dir or feedback_dir / "applied" / _safe_path_id(bundle.application_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_bundle(output_dir, bundle, args.feedback_plan)
    return bundle, output_dir


def format_text(bundle, output_dir: Path) -> str:
    return "\n".join(
        [
            f"Applied feedback: {bundle.application_id}",
            f"Feedback: {bundle.feedback_id}",
            f"Mode: {bundle.mode}",
            f"Hook specs: {len(bundle.hook_specs)}",
            f"Artifacts: {output_dir}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bundle, output_dir = run_from_args(args)
    if args.json:
        print(json.dumps(bundle.model_dump(mode="json", by_alias=True), indent=2))
    else:
        print(format_text(bundle, output_dir))
    return 0


def _write_bundle(output_dir: Path, bundle, feedback_plan_path: Path) -> None:
    bundle_payload = bundle.model_dump(mode="json", by_alias=True)
    (output_dir / "activation_hooks.json").write_text(
        json.dumps(bundle_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_yaml(
        output_dir / "manifest.yaml",
        {
            "application_id": bundle.application_id,
            "feedback_id": bundle.feedback_id,
            "source_trace_id": bundle.source_trace_id,
            "root_query_id": bundle.root_query_id,
            "mode": bundle.mode,
            "feedback_plan": str(feedback_plan_path),
            "hook_spec_file": "activation_hooks.json",
            "hook_count": len(bundle.hook_specs),
        },
    )


def _write_yaml(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as stream:
        yaml.safe_dump(data, stream, sort_keys=False)


def _safe_path_id(identifier: str) -> str:
    return (
        identifier.replace(":", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )


if __name__ == "__main__":
    raise SystemExit(main())

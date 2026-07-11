from __future__ import annotations

import argparse
import json
from pathlib import Path

from specter.activation.hook_runner import (
    AppliedFeedbackLoader,
    TransformerLensHookRunner,
)
from specter.activation.transformerlens_adapter import TransformerLensAdapter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a prompt through a TransformerLens model with Specter feedback hooks."
    )
    parser.add_argument("activation_hooks", type=Path, help="Path to activation_hooks.json.")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--expert-id", default=None)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--output-file", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    return parser


def run_from_args(args: argparse.Namespace):
    bundle = AppliedFeedbackLoader().load(args.activation_hooks)
    adapter = TransformerLensAdapter(model_path=args.model_path)
    model = adapter.load_model()
    result = TransformerLensHookRunner(adapter=adapter, model=model).generate(
        bundle=bundle,
        prompt=args.prompt,
        expert_id=args.expert_id,
        max_new_tokens=args.max_new_tokens,
    )
    if args.output_file is not None:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        args.output_file.write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return result


def format_text(result) -> str:
    return "\n".join(
        [
            f"Application: {result.application_id}",
            f"Feedback: {result.feedback_id}",
            f"Applied hooks: {len(result.applied_hook_ids)}",
            "Output:",
            result.output,
        ]
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_from_args(args)
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

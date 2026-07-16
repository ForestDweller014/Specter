from __future__ import annotations

import argparse
import json
import os
from contextlib import nullcontext
from pathlib import Path

from specter.artifacts import EvaluationArtifactStore
from specter.config import CourtroomConfig
from specter.courtroom.debate_runner import CourtroomRunner
from specter.courtroom.models import CourtroomRunResult
from specter.dullahan_inference import DullahanInferenceServer
from specter.graph_loader import ActionGraphLoader
from specter.model_provider import ModelProvider, OpenAICompatibleHttpProvider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate a Dullahan-compatible action graph through bounded courtroom debates."
        )
    )
    parser.add_argument("action_graph", type=Path, help="Path to action_graph.json.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "artifacts/evaluations",
        help="Directory where evaluation transcripts and feedback prompts are stored.",
    )
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--contentions", type=int, default=3)
    parser.add_argument("--turn-token-budget", type=int, default=512)
    parser.add_argument("--judge-rationale-token-budget", type=int, default=256)
    parser.add_argument("--feedback-token-budget", type=int, default=384)
    parser.add_argument(
        "--courtroom-model-provider",
        choices=["dullahan", "openai-compatible"],
        default="dullahan",
    )
    parser.add_argument(
        "--courtroom-model-base-url",
        default=os.getenv("DULLAHAN_INFERENCE_BASE_URL", "http://127.0.0.1:30000/v1"),
    )
    parser.add_argument("--courtroom-model", default=None)
    parser.add_argument("--courtroom-api-key-env", default=None)
    parser.add_argument("--courtroom-model-timeout-seconds", type=float, default=120.0)
    parser.add_argument("--courtroom-temperature", type=float, default=0.0)
    parser.add_argument("--start-dullahan-inference", action="store_true")
    parser.add_argument(
        "--dullahan-repo-root",
        type=Path,
        default=Path(os.getenv("DULLAHAN_REPO_ROOT", "~/Documents/Dullahan")).expanduser(),
    )
    parser.add_argument("--dullahan-inference-config", type=Path, default=None)
    parser.add_argument("--include-unanswered-nodes", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit the full result as JSON.")
    return parser


def run_from_args(
    args: argparse.Namespace,
    *,
    model_provider: ModelProvider | None = None,
) -> CourtroomRunResult:
    config = CourtroomConfig(
        artifact_root=args.output_dir,
        rounds=args.rounds,
        max_contentions=args.contentions,
        turn_token_budget=args.turn_token_budget,
        judge_rationale_token_budget=args.judge_rationale_token_budget,
        feedback_token_budget=args.feedback_token_budget,
        inference_temperature=args.courtroom_temperature,
        include_unanswered_nodes=args.include_unanswered_nodes,
    )
    graph, targets = ActionGraphLoader().load_targets(
        args.action_graph,
        include_unanswered_nodes=config.include_unanswered_nodes,
    )
    provider = model_provider if model_provider is not None else _build_model_provider(args)
    inference_context = nullcontext()
    if args.start_dullahan_inference:
        if args.courtroom_model_provider != "dullahan":
            raise ValueError("--start-dullahan-inference requires provider=dullahan")
        dullahan_root = args.dullahan_repo_root.expanduser().resolve()
        config_path = args.dullahan_inference_config or dullahan_root / "configs/inference.yaml"
        inference_context = DullahanInferenceServer(
            repo_root=dullahan_root,
            config_path=config_path,
            base_url=args.courtroom_model_base_url,
            startup_timeout_seconds=args.courtroom_model_timeout_seconds,
        )
    with inference_context:
        result = CourtroomRunner(model_provider=provider).run(
            source_trace_id=str(graph["trace_id"]),
            root_query_id=str(graph["root_query_id"]),
            targets=targets,
            config=config,
        )
    artifact_dir = EvaluationArtifactStore(config.artifact_root).write_run(result)
    return result.model_copy(update={"artifact_dir": str(artifact_dir)})


def _build_model_provider(args: argparse.Namespace) -> ModelProvider:
    return OpenAICompatibleHttpProvider(
        base_url=args.courtroom_model_base_url,
        timeout_seconds=args.courtroom_model_timeout_seconds,
        api_key_env=args.courtroom_api_key_env,
        model_override=args.courtroom_model,
        provider_name=(
            "dullahan-local-inference"
            if args.courtroom_model_provider == "dullahan"
            else "openai-compatible-http"
        ),
    )


def format_text(result: CourtroomRunResult) -> str:
    contention_count = sum(len(target.contentions) for target in result.targets)
    prompts = [prompt for target in result.targets for prompt in target.feedback_prompts]
    lines = [
        f"Evaluation: {result.evaluation_id}",
        f"Source trace: {result.source_trace_id}",
        f"Targets: {len(result.targets)}",
        f"Contentions: {contention_count}",
        f"Artifacts: {result.artifact_dir}",
        "",
        "Feedback prompts:",
    ]
    lines.extend(f"- [{prompt.disposition}] {prompt.feedback_prompt}" for prompt in prompts)
    return "\n".join(lines)


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

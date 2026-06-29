from __future__ import annotations

import argparse
import json
from pathlib import Path

from specter.model_provider import OpenAICompatibleHttpProvider

from specter.artifacts import FeedbackArtifactStore
from specter.config import CourtroomConfig
from specter.courtroom.debate_runner import DeterministicCourtroomRunner
from specter.courtroom.models import CourtroomRunResult
from specter.graph_loader import ActionGraphLoader


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run bounded Specter courtroom feedback over an action graph trace."
    )
    parser.add_argument(
        "action_graph",
        type=Path,
        help="Path to a Specter-compatible action_graph.json trace.",
    )
    parser.add_argument(
        "--repo-root",
        default=Path.cwd(),
        type=Path,
        help="Repository root containing memory/feedback.",
    )
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--contentions", type=int, default=8)
    parser.add_argument("--contention-token-budget", type=int, default=96)
    parser.add_argument("--summary-token-budget", type=int, default=256)
    parser.add_argument("--response-token-budget", type=int, default=384)
    parser.add_argument("--judge-rationale-token-budget", type=int, default=128)
    parser.add_argument(
        "--courtroom-model-provider",
        choices=["deterministic", "http"],
        default="deterministic",
        help="Provider for defender/prosecutor/judge/reporter roles.",
    )
    parser.add_argument(
        "--courtroom-model-base-url",
        default="http://127.0.0.1:30000/v1",
        help="OpenAI-compatible base URL for HTTP courtroom role calls.",
    )
    parser.add_argument("--courtroom-model-timeout-seconds", type=float, default=30.0)
    parser.add_argument(
        "--include-unanswered-nodes",
        action="store_true",
        help="Include graph nodes that do not have an expert response.",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Write feedback artifacts under memory/feedback.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the full result as JSON.")
    return parser


def run_from_args(args: argparse.Namespace) -> CourtroomRunResult:
    config = CourtroomConfig(
        repo_root=args.repo_root,
        rounds=args.rounds,
        max_contentions=args.contentions,
        contention_token_budget=args.contention_token_budget,
        summary_token_budget=args.summary_token_budget,
        response_token_budget=args.response_token_budget,
        judge_rationale_token_budget=args.judge_rationale_token_budget,
        include_unanswered_nodes=args.include_unanswered_nodes,
    )
    graph, targets = ActionGraphLoader().load_targets(
        args.action_graph,
        include_unanswered_nodes=config.include_unanswered_nodes,
    )
    result = DeterministicCourtroomRunner(
        model_provider=_build_model_provider(args),
    ).run(
        source_trace_id=str(graph["trace_id"]),
        root_query_id=str(graph["root_query_id"]),
        targets=targets,
        config=config,
    )
    if args.persist:
        artifact_dir = FeedbackArtifactStore(config.feedback_root).write_run(result)
        result = result.model_copy(update={"artifact_dir": str(artifact_dir)})
    return result


def _build_model_provider(args):
    if args.courtroom_model_provider == "deterministic":
        return None
    if args.courtroom_model_provider == "http":
        return OpenAICompatibleHttpProvider(
            base_url=args.courtroom_model_base_url,
            timeout_seconds=args.courtroom_model_timeout_seconds,
        )
    raise ValueError(f"unknown courtroom model provider: {args.courtroom_model_provider}")


def format_text(result: CourtroomRunResult) -> str:
    contention_count = sum(len(target.contentions) for target in result.targets)
    feedback_count = sum(len(target.feedback_items) for target in result.targets)
    lines = [
        f"Feedback: {result.feedback_id}",
        f"Source trace: {result.source_trace_id}",
        f"Targets: {len(result.targets)}",
        f"Contentions: {contention_count}",
        f"Feedback items: {feedback_count}",
    ]
    if result.artifact_dir:
        lines.append(f"Artifacts: {result.artifact_dir}")
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

from __future__ import annotations

from pathlib import Path

import yaml

from specter.courtroom.models import CourtroomRunResult, TargetCourtroomResult


class FeedbackArtifactStore:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir

    def write_run(self, result: CourtroomRunResult) -> Path:
        run_dir = self.root_dir / _safe_path_id(result.feedback_id)
        run_dir.mkdir(parents=True, exist_ok=True)

        self._write_yaml(
            run_dir / "manifest.yaml",
            {
                "feedback_id": result.feedback_id,
                "source_trace_id": result.source_trace_id,
                "root_query_id": result.root_query_id,
                "target_count": len(result.targets),
                "targets": [
                    {
                        "query_id": target_result.target.query_id,
                        "expert_id": target_result.target.expert_id,
                        "path": f"targets/{_safe_path_id(target_result.target.query_id)}",
                        "contention_count": len(target_result.contentions),
                        "round_count": len(target_result.rounds),
                    }
                    for target_result in result.targets
                ],
            },
        )

        for target_result in result.targets:
            self._write_target(run_dir, target_result)

        all_feedback = [
            item.model_dump(mode="json")
            for target_result in result.targets
            for item in target_result.feedback_items
        ]
        self._write_yaml(run_dir / "final_feedback.yaml", {"feedback_items": all_feedback})
        return run_dir

    def _write_target(self, run_dir: Path, target_result: TargetCourtroomResult) -> None:
        target_dir = run_dir / "targets" / _safe_path_id(target_result.target.query_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        self._write_yaml(
            target_dir / "target.yaml",
            {"target": target_result.target.model_dump(mode="json")},
        )
        self._write_yaml(
            target_dir / "contentions.yaml",
            {
                "contentions": [
                    contention.model_dump(mode="json")
                    for contention in target_result.contentions
                ]
            },
        )
        self._write_yaml(
            target_dir / "rounds.yaml",
            {"rounds": [round_.model_dump(mode="json") for round_ in target_result.rounds]},
        )
        self._write_yaml(
            target_dir / "debate_summaries.yaml",
            {
                "summaries": [
                    {
                        "contention_id": item.contention_id,
                        "round_index": round_.round_index,
                        "running_summary": item.running_summary_after,
                    }
                    for round_ in target_result.rounds
                    for item in round_.items
                ]
            },
        )
        self._write_yaml(
            target_dir / "judge_scores.yaml",
            {
                "judge_scores": [
                    item.judge_score.model_dump(mode="json")
                    | {"contention_id": item.contention_id, "round_index": round_.round_index}
                    for round_ in target_result.rounds
                    for item in round_.items
                ]
            },
        )
        self._write_yaml(
            target_dir / "final_feedback.yaml",
            {
                "feedback_items": [
                    item.model_dump(mode="json") for item in target_result.feedback_items
                ]
            },
        )

    def _write_yaml(self, path: Path, data: dict) -> None:
        with path.open("w", encoding="utf-8") as stream:
            yaml.safe_dump(data, stream, sort_keys=False)


def _safe_path_id(identifier: str) -> str:
    return (
        identifier.replace(":", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )


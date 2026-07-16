from __future__ import annotations

from pathlib import Path

import yaml

from specter.courtroom.models import CourtroomRunResult, TargetCourtroomResult
from specter.text import safe_path_id


class EvaluationArtifactStore:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir

    def write_run(self, result: CourtroomRunResult) -> Path:
        run_dir = self.root_dir / safe_path_id(result.evaluation_id)
        run_dir.mkdir(parents=True, exist_ok=True)

        self._write_yaml(
            run_dir / "manifest.yaml",
            {
                "schema": "specter.evaluation.v1",
                "evaluation_id": result.evaluation_id,
                "source_trace_id": result.source_trace_id,
                "root_query_id": result.root_query_id,
                "target_count": len(result.targets),
                "targets": [
                    {
                        "query_id": target.target.query_id,
                        "expert_id": target.target.expert_id,
                        "path": f"targets/{safe_path_id(target.target.query_id)}",
                        "contention_count": len(target.contentions),
                        "debate_count": len(target.debate_records),
                    }
                    for target in result.targets
                ],
            },
        )
        for target_result in result.targets:
            self._write_target(run_dir, target_result)

        self._write_yaml(
            run_dir / "feedback_prompts.yaml",
            {
                "schema": "specter.feedback_prompts.v1",
                "feedback_prompts": [
                    prompt.model_dump(mode="json")
                    for target in result.targets
                    for prompt in target.feedback_prompts
                ],
            },
        )
        return run_dir

    def _write_target(self, run_dir: Path, target_result: TargetCourtroomResult) -> None:
        target_dir = run_dir / "targets" / safe_path_id(target_result.target.query_id)
        debate_dir = target_dir / "debates"
        debate_dir.mkdir(parents=True, exist_ok=True)
        self._write_yaml(
            target_dir / "target.yaml",
            {"target": target_result.target.model_dump(mode="json")},
        )
        self._write_yaml(
            target_dir / "contentions.yaml",
            {
                "contentions": [
                    contention.model_dump(mode="json") for contention in target_result.contentions
                ]
            },
        )
        for record in target_result.debate_records:
            stem = safe_path_id(record.contention_id)
            self._write_yaml(
                debate_dir / f"{stem}.yaml",
                {"debate_record": record.model_dump(mode="json", by_alias=True)},
            )
            (debate_dir / f"{stem}.md").write_text(record.render_markdown(), encoding="utf-8")
        self._write_yaml(
            target_dir / "feedback_prompts.yaml",
            {
                "schema": "specter.feedback_prompts.v1",
                "feedback_prompts": [
                    prompt.model_dump(mode="json") for prompt in target_result.feedback_prompts
                ],
            },
        )

    def _write_yaml(self, path: Path, data: dict) -> None:
        with path.open("w", encoding="utf-8") as stream:
            yaml.safe_dump(data, stream, sort_keys=False)

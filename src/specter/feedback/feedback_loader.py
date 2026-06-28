from __future__ import annotations

from pathlib import Path

import yaml

from specter.courtroom.models import FeedbackItem


class FeedbackLoadError(ValueError):
    pass


class FeedbackArtifactLoader:
    def load(self, feedback_dir: Path) -> tuple[dict, list[FeedbackItem]]:
        manifest_path = feedback_dir / "manifest.yaml"
        feedback_path = feedback_dir / "final_feedback.yaml"
        if not manifest_path.exists():
            raise FeedbackLoadError(f"missing manifest: {manifest_path}")
        if not feedback_path.exists():
            raise FeedbackLoadError(f"missing final feedback: {feedback_path}")

        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        payload = yaml.safe_load(feedback_path.read_text(encoding="utf-8")) or {}
        items = [
            FeedbackItem.model_validate(item)
            for item in payload.get("feedback_items", [])
        ]
        return manifest, items


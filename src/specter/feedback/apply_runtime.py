from __future__ import annotations

import json
from pathlib import Path

from specter.courtroom.models import FeedbackDisposition
from specter.feedback.apply_models import (
    ActivationHookSpec,
    AppliedFeedbackBundle,
)
from specter.feedback.models import FeedbackPlan, FeedbackPlanItem
from specter.ids import new_id
from specter.text import safe_path_id


class FeedbackApplicationError(ValueError):
    pass


class FeedbackPlanLoader:
    def load(self, path: Path) -> FeedbackPlan:
        return FeedbackPlan.model_validate_json(path.read_text(encoding="utf-8"))


class ActivationHookApplicationRuntime:
    mode = "activation-hook"

    def apply(
        self,
        *,
        plan: FeedbackPlan,
        feedback_dir: Path,
        scale_override: float | None = None,
    ) -> AppliedFeedbackBundle:
        hook_specs = [
            self._build_hook_spec(
                item=item,
                feedback_dir=feedback_dir,
                scale_override=scale_override,
            )
            for item in plan.items
        ]
        return AppliedFeedbackBundle(
            application_id=new_id("application"),
            feedback_id=plan.feedback_id,
            source_trace_id=plan.source_trace_id,
            root_query_id=plan.root_query_id,
            mode=self.mode,
            hook_specs=hook_specs,
        )

    def _build_hook_spec(
        self,
        *,
        item: FeedbackPlanItem,
        feedback_dir: Path,
        scale_override: float | None,
    ) -> ActivationHookSpec:
        if item.disposition != FeedbackDisposition.APPLY_CORRECTION:
            raise FeedbackApplicationError(
                f"feedback item {item.contention_id} is not approved for correction"
            )
        if item.prosecution_strength <= 0:
            raise FeedbackApplicationError(
                f"feedback item {item.contention_id} has non-positive prosecution strength"
            )
        if item.application_mode != self.mode:
            raise FeedbackApplicationError(
                f"unsupported application mode for item {item.contention_id}: "
                f"{item.application_mode!r}"
            )
        vector = self._load_vector(feedback_dir / item.direction_vector_ref)
        feedback_scale = item.feedback_scale if scale_override is None else scale_override
        multiplier = item.prosecution_strength * feedback_scale
        scaled_vector = [round(value * multiplier, 8) for value in vector]
        return ActivationHookSpec(
            hook_id=f"hook:{safe_path_id(item.contention_id)}",
            contention_id=item.contention_id,
            query_id=item.query_id,
            expert_id=item.expert_id,
            disposition=item.disposition,
            layer=item.layer,
            hook_point=f"blocks.{item.layer}.hook_resid_post",
            token_position_policy=item.token_position_policy,
            source_vector_ref=item.direction_vector_ref,
            scaled_vector=scaled_vector,
            prosecution_strength=item.prosecution_strength,
            feedback_scale=feedback_scale,
            projection_strength=item.projection_strength,
            confidence=item.confidence,
        )

    def _load_vector(self, path: Path) -> list[float]:
        if not path.exists():
            raise FeedbackApplicationError(f"missing steering vector: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != "specter.steering_vector.v1":
            raise FeedbackApplicationError(
                f"unsupported steering vector schema at {path}: {payload.get('schema')!r}"
            )
        vector = payload.get("vector")
        if not isinstance(vector, list) or not vector:
            raise FeedbackApplicationError(f"steering vector is empty or invalid: {path}")
        return [float(value) for value in vector]

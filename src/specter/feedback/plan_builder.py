from __future__ import annotations

from specter.activation.models import ActivationLocalization
from specter.feedback.models import FeedbackPlan, FeedbackPlanItem


class FeedbackPlanBuilder:
    def build(
        self,
        *,
        manifest: dict,
        backend: str,
        feedback_scale: float,
        application_mode: str,
        localizations: list[ActivationLocalization],
    ) -> FeedbackPlan:
        return FeedbackPlan(
            feedback_id=str(manifest["feedback_id"]),
            source_trace_id=str(manifest["source_trace_id"]),
            root_query_id=str(manifest["root_query_id"]),
            backend=backend,
            items=[
                FeedbackPlanItem(
                    contention_id=localization.contention_id,
                    query_id=localization.query_id,
                    expert_id=localization.expert_id,
                    prosecution_strength=localization.prosecution_strength,
                    layer=localization.layer,
                    token_position_policy=localization.token_position_policy,
                    direction_vector_ref=localization.direction_vector_ref,
                    feedback_scale=feedback_scale,
                    application_mode=application_mode,
                    projection_strength=localization.projection_strength,
                    confidence=localization.confidence,
                )
                for localization in localizations
            ],
        )


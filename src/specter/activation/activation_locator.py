from __future__ import annotations

import hashlib
from dataclasses import dataclass

from specter.activation.contrast_set_builder import MinimalPairContrastSetBuilder
from specter.activation.models import ActivationLocalization
from specter.courtroom.models import FeedbackItem


@dataclass(frozen=True)
class LocalizationRequest:
    feedback_item: FeedbackItem
    direction_vector_ref: str
    contrast_pair_count: int
    n_layers: int = 12


class DeterministicActivationLocator:
    backend_name = "deterministic-localizer"

    def __init__(
        self,
        *,
        contrast_builder: MinimalPairContrastSetBuilder | None = None,
    ) -> None:
        self.contrast_builder = contrast_builder or MinimalPairContrastSetBuilder()

    def locate(self, request: LocalizationRequest) -> ActivationLocalization:
        item = request.feedback_item
        digest = hashlib.sha256(item.contention_id.encode("utf-8")).digest()
        layer = digest[0] % max(request.n_layers, 1)
        summary_words = len(item.running_debate_summary.split())
        projection_strength = min(1.0, abs(item.prosecution_strength) + summary_words / 1000)
        confidence = min(0.75, 0.25 + abs(item.prosecution_strength) / 2)
        return ActivationLocalization(
            feedback_id=item.feedback_id,
            query_id=item.query_id,
            expert_id=item.expert_id,
            contention_id=item.contention_id,
            prosecution_strength=item.prosecution_strength,
            layer=layer,
            token_position_policy="last-token",
            direction_vector_ref=request.direction_vector_ref,
            projection_strength=round(projection_strength, 6),
            confidence=round(confidence, 6),
            backend=self.backend_name,
            contrast_pairs=self.contrast_builder.build(
                item,
                pair_count=request.contrast_pair_count,
            ),
        )

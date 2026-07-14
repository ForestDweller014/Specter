from __future__ import annotations

from dataclasses import dataclass

from specter.courtroom.models import FeedbackItem


@dataclass(frozen=True)
class LocalizationRequest:
    feedback_item: FeedbackItem
    direction_vector_ref: str
    contrast_pair_count: int
    n_layers: int = 12

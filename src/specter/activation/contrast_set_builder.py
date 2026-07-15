from __future__ import annotations

from specter.activation.models import ContrastPair
from specter.courtroom.models import FeedbackItem
from specter.text import clamp_words


class MinimalPairContrastSetBuilder:
    def build(self, item: FeedbackItem, *, pair_count: int) -> list[ContrastPair]:
        pairs = []
        positive = clamp_words(item.feedback_text, 96)
        negative_base = self._neutralize(item)
        for index in range(1, pair_count + 1):
            pairs.append(
                ContrastPair(
                    pair_id=f"{item.contention_id}:pair:{index}",
                    positive=positive,
                    negative=self._variant(negative_base, index=index),
                    metadata={
                        "construction": "deterministic_topic_matched_concept_removed",
                        "source_contention_id": item.contention_id,
                    },
                )
            )
        return pairs

    def _neutralize(self, item: FeedbackItem) -> str:
        context_hint = self._first_sentence(item.target_context) or "No context excerpt available."
        response_hint = (
            self._first_sentence(item.target_response) or "No response excerpt available."
        )
        text = (
            "Neutral trace note without validation pressure. "
            f"Query: {item.target_query} "
            f"Context topic: {context_hint} "
            f"Response topic: {response_hint}"
        )
        return clamp_words(text, 96)

    def _variant(self, text: str, *, index: int) -> str:
        return clamp_words(f"{text} Matched neutral variant {index}.", 96)

    def _first_sentence(self, text: str) -> str:
        stripped = " ".join(text.split())
        if not stripped:
            return ""
        for delimiter in [". ", "\n"]:
            if delimiter in stripped:
                return stripped.split(delimiter, 1)[0].strip(". ")
        return stripped

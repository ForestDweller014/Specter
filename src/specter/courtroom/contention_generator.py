from __future__ import annotations

from specter.config import CourtroomConfig
from specter.courtroom.models import Contention, FeedbackTargetNode
from specter.text import clamp_words


class DeterministicContentionGenerator:
    templates = [
        "The delegated query may not faithfully preserve the parent query intent.",
        "The response may not be sufficiently grounded in the supplied context.",
        "The response may omit important constraints from the query.",
        "The response may overstate confidence beyond the evidence available.",
        "The response may fail to account for relevant child subqueries.",
        "The response may conflate retrieved context with unsupported inference.",
        "The response may be too shallow to satisfy the requested reasoning depth.",
        "The response may cite or rely on context unevenly.",
        "The response may leave unresolved risks that should be explicit.",
    ]

    def generate(self, target: FeedbackTargetNode, config: CourtroomConfig) -> list[Contention]:
        contentions = []
        for index, template in enumerate(self.templates[: config.max_contentions], start=1):
            text = self._specialize(template, target)
            contentions.append(
                Contention(
                    contention_id=f"{target.query_id}:contention:{index}",
                    text=clamp_words(text, config.contention_token_budget),
                    token_budget=config.contention_token_budget,
                )
            )
        return contentions

    def _specialize(self, template: str, target: FeedbackTargetNode) -> str:
        if "delegated query" in template and target.parent_query_text:
            return (
                f"{template} Parent query: {target.parent_query_text} "
                f"Delegated query: {target.delegation_query or target.query_text}"
            )
        if "delegated query" in template:
            return f"{template} Query: {target.query_text}"
        if "child subqueries" in template and target.child_query_ids:
            child_text = "; ".join(
                text for text in target.child_query_texts if text
            ) or ", ".join(target.child_query_ids)
            return f"{template} Child subqueries: {child_text}."
        if "supplied context" in template and not target.context_text:
            return "The response may be unsupported because no context documents were attached."
        return f"{template} Query: {target.query_text}"

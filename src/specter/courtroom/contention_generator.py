from __future__ import annotations

import json
import re

from specter.config import CourtroomConfig
from specter.courtroom.models import Contention, FeedbackTargetNode
from specter.model_provider import ModelProvider, ModelRequest
from specter.text import clamp_words


class InferenceContentionGenerator:
    """Generate evidence-specific validation contentions through a real model provider."""

    def __init__(self, *, model_provider: ModelProvider) -> None:
        self.model_provider = model_provider

    def generate(self, target: FeedbackTargetNode, config: CourtroomConfig) -> list[Contention]:
        result = self.model_provider.complete(
            ModelRequest(
                model=target.model_name,
                prompt=self._prompt(target, config.max_contentions),
                max_tokens=config.contention_generation_token_budget,
                temperature=config.inference_temperature,
            )
        )
        texts = self._parse_contentions(result.text, maximum=config.max_contentions)
        if not texts:
            raise ValueError("inference provider returned no usable validation contentions")
        return [
            Contention(
                contention_id=f"{target.query_id}:contention:{index}",
                text=clamp_words(text, config.turn_token_budget),
                token_budget=config.turn_token_budget,
            )
            for index, text in enumerate(texts, start=1)
        ]

    def _prompt(self, target: FeedbackTargetNode, maximum: int) -> str:
        children = "\n".join(target.child_query_texts) or "none"
        return "\n".join(
            [
                "You are an adversarial validation prosecutor.",
                (
                    f"Generate up to {maximum} distinct, evidence-specific contentions "
                    "against the response."
                ),
                (
                    "Evaluate grounding, omitted constraints, confidence, delegation "
                    "quality, and reasoning."
                ),
                "Return only a JSON array of non-empty strings, strongest contention first.",
                "",
                f"Parent query: {target.parent_query_text or 'none'}",
                f"Delegated query: {target.delegation_query or target.query_text}",
                f"Target query: {target.query_text}",
                f"Context: {target.context_text or 'none'}",
                f"Response: {target.response_text or 'none'}",
                f"Child queries: {children}",
            ]
        )

    def _parse_contentions(self, text: str, *, maximum: int) -> list[str]:
        cleaned = text.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL)
        if fenced:
            cleaned = fenced.group(1)
        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, list):
            values = [str(value).strip() for value in payload if str(value).strip()]
            return values[:maximum]

        values = []
        for line in cleaned.splitlines():
            value = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
            if value:
                values.append(value)
        return values[:maximum]

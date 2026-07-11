from __future__ import annotations

import re

from specter.ids import new_id
from specter.model_provider import ModelProvider, ModelRequest

from specter.config import CourtroomConfig
from specter.courtroom.contention_generator import DeterministicContentionGenerator
from specter.courtroom.models import (
    DebateRound,
    DebateRoundItem,
    FeedbackItem,
    FeedbackTargetNode,
    JudgeScore,
    TargetCourtroomResult,
)
from specter.courtroom.role_prompts import CourtroomPromptBuilder
from specter.text import clamp_words


class DeterministicCourtroomRunner:
    def __init__(
        self,
        *,
        contention_generator: DeterministicContentionGenerator | None = None,
        model_provider: ModelProvider | None = None,
        prompt_builder: CourtroomPromptBuilder | None = None,
    ) -> None:
        self.contention_generator = contention_generator or DeterministicContentionGenerator()
        self.model_provider = model_provider
        self.prompt_builder = prompt_builder or CourtroomPromptBuilder()

    def run_target(
        self,
        *,
        feedback_id: str,
        target: FeedbackTargetNode,
        config: CourtroomConfig,
    ) -> TargetCourtroomResult:
        contentions = self.contention_generator.generate(target, config)
        current_contention_texts = {
            contention.contention_id: contention.text for contention in contentions
        }
        summaries = {contention.contention_id: "" for contention in contentions}
        rounds = []

        for round_index in range(1, config.rounds + 1):
            items = []
            for contention in contentions:
                before = summaries[contention.contention_id]
                contention_text = current_contention_texts[contention.contention_id]
                if round_index > 1:
                    contention_text = self._revise_contention(
                        target=target,
                        contention=contention_text,
                        summary=before,
                        round_index=round_index,
                        token_budget=contention.token_budget,
                    )
                    current_contention_texts[contention.contention_id] = contention_text

                defense = self._defend(target, contention_text, before, round_index, config)
                rebuttal = self._prosecute(
                    target,
                    contention_text,
                    before,
                    defense,
                    round_index,
                    config,
                )
                judge_score = self._judge(
                    target,
                    contention.contention_id,
                    contention_text,
                    before,
                    defense,
                    rebuttal,
                    round_index,
                    config,
                )
                after = self._summarize(
                    target=target,
                    round_index=round_index,
                    before=before,
                    defense=defense,
                    rebuttal=rebuttal,
                    judge_score=judge_score,
                    config=config,
                )
                summaries[contention.contention_id] = after
                items.append(
                    DebateRoundItem(
                        round_index=round_index,
                        contention_id=contention.contention_id,
                        contention_text=contention_text,
                        running_summary_before=before,
                        defense=defense,
                        prosecution_rebuttal=rebuttal,
                        judge_score=judge_score,
                        running_summary_after=after,
                    )
                )
            rounds.append(DebateRound(round_index=round_index, items=items))

        feedback_items = [
            FeedbackItem(
                feedback_id=feedback_id,
                query_id=target.query_id,
                expert_id=target.expert_id,
                contention_id=contention.contention_id,
                running_debate_summary=summaries[contention.contention_id],
                prosecution_strength=self._latest_score(rounds, contention.contention_id),
                target_query=target.query_text,
                target_context=target.context_text,
                target_response=target.response_text,
            )
            for contention in contentions
        ]

        return TargetCourtroomResult(
            target=target,
            contentions=contentions,
            rounds=rounds,
            feedback_items=feedback_items,
        )

    def run(
        self,
        *,
        source_trace_id: str,
        root_query_id: str,
        targets: list[FeedbackTargetNode],
        config: CourtroomConfig,
    ):
        from specter.courtroom.models import CourtroomRunResult

        feedback_id = new_id("feedback")
        target_results = [
            self.run_target(feedback_id=feedback_id, target=target, config=config)
            for target in targets
        ]
        return CourtroomRunResult(
            feedback_id=feedback_id,
            source_trace_id=source_trace_id,
            root_query_id=root_query_id,
            targets=target_results,
        )

    def _revise_contention(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        summary: str,
        round_index: int,
        token_budget: int,
    ) -> str:
        if self.model_provider is not None:
            return self._complete(
                target=target,
                prompt=self.prompt_builder.revise_contention(
                    target=target,
                    contention=contention,
                    running_summary=summary,
                    round_index=round_index,
                ),
                max_words=token_budget,
            )
        text = (
            f"Round {round_index} refined contention: {contention} Updated focus: "
            f"test the response against the strongest unresolved prosecution signal."
        )
        return clamp_words(text, token_budget)

    def _defend(
        self,
        target: FeedbackTargetNode,
        contention: str,
        summary: str,
        round_index: int,
        config: CourtroomConfig,
    ) -> str:
        if self.model_provider is not None:
            return self._complete(
                target=target,
                prompt=self.prompt_builder.defender(
                    target=target,
                    contention=contention,
                    running_summary=summary,
                    round_index=round_index,
                ),
                max_words=config.response_token_budget,
            )
        text = (
            f"Round {round_index} defense by {target.expert_id}: the original response should be "
            f"judged against the query '{target.query_text}'. The contention is '{contention}'. "
            f"The response remains defensible where it follows the available context and avoids "
            f"claiming more than the retrieved evidence supports. Prior summary: {summary or 'none'}."
        )
        return clamp_words(text, config.response_token_budget)

    def _prosecute(
        self,
        target: FeedbackTargetNode,
        contention: str,
        summary: str,
        defense: str,
        round_index: int,
        config: CourtroomConfig,
    ) -> str:
        if self.model_provider is not None:
            return self._complete(
                target=target,
                prompt=self.prompt_builder.prosecutor(
                    target=target,
                    contention=contention,
                    running_summary=summary,
                    defense=defense,
                    round_index=round_index,
                ),
                max_words=config.response_token_budget,
            )
        text = (
            f"Round {round_index} prosecution by a second {target.expert_id} instance: the contention "
            f"'{contention}' still matters if the response lacks direct support, misses constraints, "
            f"or compresses uncertainty too aggressively. Defense considered: {defense}. "
            f"Prior summary: {summary or 'none'}."
        )
        return clamp_words(text, config.response_token_budget)

    def _judge(
        self,
        target: FeedbackTargetNode,
        contention_id: str,
        contention: str,
        summary: str,
        defense: str,
        rebuttal: str,
        round_index: int,
        config: CourtroomConfig,
    ) -> JudgeScore:
        if self.model_provider is not None:
            judge_text = self._complete(
                target=target,
                prompt=self.prompt_builder.judge(
                    target=target,
                    contention=contention,
                    running_summary=summary,
                    defense=defense,
                    rebuttal=rebuttal,
                    round_index=round_index,
                ),
                max_words=config.judge_rationale_token_budget,
            )
            return JudgeScore(
                contention_id=contention_id,
                prosecution_strength=self._parse_score(judge_text),
                rationale=judge_text,
            )
        score = 0.15
        if not target.context_text:
            score += 0.35
        if target.child_query_ids and "child" in contention:
            score += 0.2
        if len(target.response_text.split()) < 20:
            score += 0.2
        if "unsupported" in contention or "confidence" in contention:
            score += 0.1
        score = max(-1.0, min(1.0, score))
        rationale = (
            f"The prosecution strength is {score:.2f}. The score reflects the contention, "
            f"available context, response length, and whether child subqueries affect the claim. "
            f"Defense signal: {defense}. Prosecution signal: {rebuttal}. Prior summary: {summary or 'none'}."
        )
        return JudgeScore(
            contention_id=contention_id,
            prosecution_strength=round(score, 4),
            rationale=clamp_words(rationale, config.judge_rationale_token_budget),
        )

    def _summarize(
        self,
        *,
        target: FeedbackTargetNode | None = None,
        round_index: int = 1,
        before: str,
        defense: str,
        rebuttal: str,
        judge_score: JudgeScore,
        config: CourtroomConfig,
    ) -> str:
        if self.model_provider is not None and target is not None:
            return self._complete(
                target=target,
                prompt=self.prompt_builder.reporter(
                    target=target,
                    running_summary=before,
                    defense=defense,
                    rebuttal=rebuttal,
                    judge_score=judge_score,
                    round_index=round_index,
                ),
                max_words=config.summary_token_budget,
            )
        text = (
            f"Prior: {before or 'none'} Defense: {defense} Prosecution: {rebuttal} "
            f"Judge: strength={judge_score.prosecution_strength}; {judge_score.rationale}"
        )
        return clamp_words(text, config.summary_token_budget)

    def _latest_score(self, rounds: list[DebateRound], contention_id: str) -> float:
        for debate_round in reversed(rounds):
            for item in debate_round.items:
                if item.contention_id == contention_id:
                    return item.judge_score.prosecution_strength
        return 0.0

    def _complete(
        self,
        *,
        target: FeedbackTargetNode,
        prompt: str,
        max_words: int,
    ) -> str:
        if self.model_provider is None:
            raise RuntimeError("model provider is not configured")
        result = self.model_provider.complete(
            ModelRequest(
                model=target.model_name,
                prompt=prompt,
                max_tokens=max_words,
            )
        )
        text = result.text.strip() or "No model output."
        return clamp_words(text, max_words)

    def _parse_score(self, text: str) -> float:
        match = re.search(r"[-+]?(?:\d*\.\d+|\d+)", text)
        if match is None:
            return 0.0
        score = float(match.group(0))
        return round(max(-1.0, min(1.0, score)), 4)

from __future__ import annotations

import json
import re

from specter.config import CourtroomConfig
from specter.courtroom.contention_generator import InferenceContentionGenerator
from specter.courtroom.models import (
    CourtroomRunResult,
    DebateRecord,
    DebateRound,
    FeedbackPrompt,
    FeedbackProvenance,
    FeedbackTargetNode,
    FinalFeedbackDecision,
    JudgeScore,
    TargetCourtroomResult,
)
from specter.courtroom.role_prompts import CourtroomPromptBuilder
from specter.ids import new_id
from specter.model_provider import ModelProvider, ModelRequest
from specter.text import clamp_words, safe_path_id


class CourtroomRunner:
    def __init__(
        self,
        *,
        model_provider: ModelProvider,
        contention_generator: InferenceContentionGenerator | None = None,
        prompt_builder: CourtroomPromptBuilder | None = None,
    ) -> None:
        self.model_provider = model_provider
        self.contention_generator = contention_generator or InferenceContentionGenerator(
            model_provider=model_provider
        )
        self.prompt_builder = prompt_builder or CourtroomPromptBuilder()

    def run_target(
        self,
        *,
        evaluation_id: str,
        target: FeedbackTargetNode,
        config: CourtroomConfig,
    ) -> TargetCourtroomResult:
        contentions = self.contention_generator.generate(target, config)
        records = {
            contention.contention_id: DebateRecord(
                contention_id=contention.contention_id,
                initial_contention=contention.text,
                turn_token_budget=config.turn_token_budget,
                transcript_token_budget=config.maximum_transcript_tokens(),
            )
            for contention in contentions
        }
        active_contentions = {
            contention.contention_id: contention.text for contention in contentions
        }

        for round_index in range(1, config.rounds + 1):
            for contention in contentions:
                record = records[contention.contention_id]
                prior_transcript = self._transcript_for_prompt(record)
                contention_text = active_contentions[contention.contention_id]
                if round_index > 1:
                    contention_text = self._revise_contention(
                        target=target,
                        contention=contention_text,
                        debate_transcript=prior_transcript,
                        round_index=round_index,
                        config=config,
                    )
                    active_contentions[contention.contention_id] = contention_text

                defense = self._defend(
                    target, contention_text, prior_transcript, round_index, config
                )
                prosecution = self._prosecute(
                    target,
                    contention_text,
                    prior_transcript,
                    defense,
                    round_index,
                    config,
                )
                judge = self._judge(
                    target,
                    contention_text,
                    prior_transcript,
                    defense,
                    prosecution,
                    round_index,
                    config,
                )
                record.rounds.append(
                    DebateRound(
                        round_index=round_index,
                        contention_text=contention_text,
                        defense=defense,
                        prosecution=prosecution,
                        judge=judge,
                    )
                )

        debate_records = [records[contention.contention_id] for contention in contentions]
        feedback_prompts = [
            self._generate_feedback(
                evaluation_id=evaluation_id,
                target=target,
                record=record,
                config=config,
            )
            for record in debate_records
        ]
        return TargetCourtroomResult(
            target=target,
            contentions=contentions,
            debate_records=debate_records,
            feedback_prompts=feedback_prompts,
        )

    def run(
        self,
        *,
        source_trace_id: str,
        root_query_id: str,
        targets: list[FeedbackTargetNode],
        config: CourtroomConfig,
    ) -> CourtroomRunResult:
        evaluation_id = new_id("evaluation")
        return CourtroomRunResult(
            evaluation_id=evaluation_id,
            source_trace_id=source_trace_id,
            root_query_id=root_query_id,
            targets=[
                self.run_target(evaluation_id=evaluation_id, target=target, config=config)
                for target in targets
            ],
        )

    def _revise_contention(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        debate_transcript: str,
        round_index: int,
        config: CourtroomConfig,
    ) -> str:
        return self._complete(
            target=target,
            prompt=self.prompt_builder.revise_contention(
                target=target,
                contention=contention,
                debate_transcript=debate_transcript,
                round_index=round_index,
            ),
            max_tokens=config.turn_token_budget,
            temperature=config.inference_temperature,
        )

    def _defend(
        self,
        target: FeedbackTargetNode,
        contention: str,
        debate_transcript: str,
        round_index: int,
        config: CourtroomConfig,
    ) -> str:
        return self._complete(
            target=target,
            prompt=self.prompt_builder.defender(
                target=target,
                contention=contention,
                debate_transcript=debate_transcript,
                round_index=round_index,
            ),
            max_tokens=config.turn_token_budget,
            temperature=config.inference_temperature,
        )

    def _prosecute(
        self,
        target: FeedbackTargetNode,
        contention: str,
        debate_transcript: str,
        defense: str,
        round_index: int,
        config: CourtroomConfig,
    ) -> str:
        return self._complete(
            target=target,
            prompt=self.prompt_builder.prosecutor(
                target=target,
                contention=contention,
                debate_transcript=debate_transcript,
                defense=defense,
                round_index=round_index,
            ),
            max_tokens=config.turn_token_budget,
            temperature=config.inference_temperature,
        )

    def _judge(
        self,
        target: FeedbackTargetNode,
        contention: str,
        debate_transcript: str,
        defense: str,
        prosecution: str,
        round_index: int,
        config: CourtroomConfig,
    ) -> JudgeScore:
        text = self._complete(
            target=target,
            prompt=self.prompt_builder.judge(
                target=target,
                contention=contention,
                debate_transcript=debate_transcript,
                defense=defense,
                prosecution=prosecution,
                round_index=round_index,
            ),
            max_tokens=config.judge_rationale_token_budget,
            temperature=config.inference_temperature,
        )
        return JudgeScore(prosecution_strength=self._parse_score(text), rationale=text)

    def _generate_feedback(
        self,
        *,
        evaluation_id: str,
        target: FeedbackTargetNode,
        record: DebateRecord,
        config: CourtroomConfig,
    ) -> FeedbackPrompt:
        transcript = record.render_markdown()
        record_hash = record.content_hash()
        raw_decision = self._complete(
            target=target,
            prompt=self.prompt_builder.judge_feedback(
                target=target,
                debate_transcript=transcript,
                debate_record_sha256=record_hash,
                round_index=config.rounds,
            ),
            max_tokens=config.feedback_token_budget,
            temperature=config.inference_temperature,
            clamp_output=False,
        )
        decision = self._parse_feedback_decision(
            raw_decision,
            max_words=config.feedback_token_budget,
        )
        record_ref = (
            f"targets/{safe_path_id(target.query_id)}/debates/"
            f"{safe_path_id(record.contention_id)}.yaml"
        )
        return FeedbackPrompt(
            evaluation_id=evaluation_id,
            query_id=target.query_id,
            expert_id=target.expert_id,
            contention_id=record.contention_id,
            disposition=decision.disposition,
            feedback_prompt=decision.feedback_prompt,
            prosecution_strength=record.rounds[-1].judge.prosecution_strength,
            target_query=target.query_text,
            target_context=target.context_text,
            target_response=target.response_text,
            provenance=FeedbackProvenance(
                debate_record_ref=record_ref,
                debate_record_sha256=record_hash,
                transcript_token_budget=record.transcript_token_budget,
            ),
        )

    def _complete(
        self,
        *,
        target: FeedbackTargetNode,
        prompt: str,
        max_tokens: int,
        temperature: float,
        clamp_output: bool = True,
    ) -> str:
        result = self.model_provider.complete(
            ModelRequest(
                model=target.model_name,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        )
        text = result.text.strip()
        if not text:
            raise ValueError("inference provider returned an empty courtroom response")
        return clamp_words(text, max_tokens) if clamp_output else text

    def _parse_feedback_decision(
        self,
        text: str,
        *,
        max_words: int,
    ) -> FinalFeedbackDecision:
        cleaned = text.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL)
        if fenced:
            cleaned = fenced.group(1)
        try:
            decision = FinalFeedbackDecision.model_validate(json.loads(cleaned))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(
                "final feedback judge must return a valid disposition JSON object"
            ) from exc
        return decision.model_copy(
            update={"feedback_prompt": clamp_words(decision.feedback_prompt, max_words)}
        )

    def _parse_score(self, text: str) -> float:
        match = re.search(r"[-+]?(?:\d*\.\d+|\d+)", text)
        if match is None:
            return 0.0
        return round(max(-1.0, min(1.0, float(match.group(0)))), 4)

    def _transcript_for_prompt(self, record: DebateRecord) -> str:
        if not record.rounds:
            return "No completed rounds."
        return record.render_markdown()

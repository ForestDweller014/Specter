from __future__ import annotations

from specter.courtroom.models import FeedbackTargetNode


class CourtroomPromptBuilder:
    def revise_contention(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        debate_transcript: str,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the prosecutor. Revise the contention for this round while "
                "preserving its identity, evidence, and validation target."
            ),
            target=target,
            round_index=round_index,
            debate_transcript=debate_transcript,
            extra=["Current contention:", contention, "Return only the revised contention."],
        )

    def defender(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        debate_transcript: str,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the defender. Defend the original response against the active "
                "contention using the supplied evidence and complete prior record."
            ),
            target=target,
            round_index=round_index,
            debate_transcript=debate_transcript,
            extra=["Active contention:", contention, "Return only the defense."],
        )

    def prosecutor(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        debate_transcript: str,
        defense: str,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the prosecutor. Rebut the defense, preserve valid concessions, "
                "and sharpen only evidence-supported criticism."
            ),
            target=target,
            round_index=round_index,
            debate_transcript=debate_transcript,
            extra=[
                "Active contention:",
                contention,
                "Current defense:",
                defense,
                "Return only the prosecution argument.",
            ],
        )

    def judge(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        debate_transcript: str,
        defense: str,
        prosecution: str,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the judge. Score prosecution strength from -1 to 1: -1 means "
                "the defense prevails, 0 means neutral, mixed, or unclear, and 1 means "
                "the prosecution prevails."
            ),
            target=target,
            round_index=round_index,
            debate_transcript=debate_transcript,
            extra=[
                "Active contention:",
                contention,
                "Current defense:",
                defense,
                "Current prosecution:",
                prosecution,
                "Return the score first, followed by a concise rationale.",
            ],
        )

    def judge_feedback(
        self,
        *,
        target: FeedbackTargetNode,
        debate_transcript: str,
        debate_record_sha256: str,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the final feedback judge. Read the exact debate transcript and "
                "decide whether it establishes a correction. If so, produce one concise, "
                "instructive, declarative prompt that tells the evaluated model what to do. "
                "Do not mention courtroom roles, procedure, scores, steering, activations, "
                "or future model modification. If no correction is warranted, return a "
                "concise declarative audit reason."
            ),
            target=target,
            round_index=round_index,
            debate_transcript=debate_transcript,
            extra=[
                "Canonical debate record SHA-256:",
                debate_record_sha256,
                (
                    "Return only a JSON object with exactly these keys: "
                    '{"disposition":"apply_correction","feedback_prompt":"..."}. '
                    "The disposition must be apply_correction or no_correction."
                ),
            ],
        )

    def _base(
        self,
        *,
        role: str,
        target: FeedbackTargetNode,
        round_index: int,
        debate_transcript: str,
        extra: list[str],
    ) -> str:
        lines = [
            "Role:",
            role,
            "",
            f"Round: {round_index}",
            f"Expert ID: {target.expert_id}",
            f"Expert model: {target.model_name}",
            "",
            "Original query:",
            target.query_text,
            "",
            "Original context:",
            target.context_text or "No context documents were attached.",
            "",
            "Original response:",
            target.response_text or "No response was attached.",
            "",
            "Complete debate transcript:",
            debate_transcript,
            "",
        ]
        lines.extend(extra)
        return "\n".join(lines)

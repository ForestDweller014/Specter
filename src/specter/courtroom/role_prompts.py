from __future__ import annotations

from specter.courtroom.models import FeedbackTargetNode, JudgeScore


class CourtroomPromptBuilder:
    def revise_contention(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        running_summary: str,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the prosecutor: another role-conditioned instance of the "
                "same expert model. You may revise the contention for this round, "
                "but must preserve the same validation target and keep it bounded."
            ),
            target=target,
            round_index=round_index,
            extra=[
                "Previous contention:",
                contention,
                "Running debate summary:",
                running_summary or "none",
                "Return only the revised contention.",
            ],
        )

    def defender(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        running_summary: str,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the defender: a role-conditioned instance of the same "
                "expert model that produced the original response. Defend the "
                "response against the contention without modifying the contention."
            ),
            target=target,
            round_index=round_index,
            extra=[
                "Contention:",
                contention,
                "Running debate summary:",
                running_summary or "none",
                "Return only the defense.",
            ],
        )

    def prosecutor(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        running_summary: str,
        defense: str,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the prosecutor: another role-conditioned instance of the "
                "same expert model. Rebut the defense and sharpen the criticism. "
                "You may evolve the critique, but keep the contention bounded."
            ),
            target=target,
            round_index=round_index,
            extra=[
                "Contention:",
                contention,
                "Running debate summary:",
                running_summary or "none",
                "Defense:",
                defense,
                "Return only the prosecution rebuttal.",
            ],
        )

    def judge(
        self,
        *,
        target: FeedbackTargetNode,
        contention: str,
        running_summary: str,
        defense: str,
        rebuttal: str,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the judge: another role-conditioned instance of the same "
                "expert model. Score prosecution strength from -1 to 1, where -1 "
                "means the defense is right, 0 is mixed, and 1 means the "
                "prosecution is right."
            ),
            target=target,
            round_index=round_index,
            extra=[
                "Contention:",
                contention,
                "Running debate summary:",
                running_summary or "none",
                "Defense:",
                defense,
                "Prosecution rebuttal:",
                rebuttal,
                "Return the score first, then a short rationale.",
            ],
        )

    def reporter(
        self,
        *,
        target: FeedbackTargetNode,
        running_summary: str,
        defense: str,
        rebuttal: str,
        judge_score: JudgeScore,
        round_index: int,
    ) -> str:
        return self._base(
            role=(
                "You are the court reporter. Compress the debate state into a "
                "bounded running summary while preserving the key defense, "
                "prosecution, and judge signals."
            ),
            target=target,
            round_index=round_index,
            extra=[
                "Prior running summary:",
                running_summary or "none",
                "Defense:",
                defense,
                "Prosecution rebuttal:",
                rebuttal,
                "Judge score:",
                str(judge_score.prosecution_strength),
                "Judge rationale:",
                judge_score.rationale,
                "Return only the compressed running summary.",
            ],
        )

    def _base(
        self,
        *,
        role: str,
        target: FeedbackTargetNode,
        round_index: int,
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
        ]
        lines.extend(extra)
        return "\n".join(lines)

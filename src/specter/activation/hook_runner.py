from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from specter.activation.transformerlens_adapter import TransformerLensAdapter
from specter.feedback.apply_models import (
    ActivationHookSpec,
    AppliedFeedbackBundle,
)


class HookedGenerationResult(BaseModel):
    application_id: str
    feedback_id: str
    expert_id: str | None = None
    prompt: str = Field(min_length=1)
    output: str
    applied_hook_ids: list[str] = Field(default_factory=list)


class AppliedFeedbackLoader:
    def load(self, path: Path) -> AppliedFeedbackBundle:
        return AppliedFeedbackBundle.model_validate_json(path.read_text(encoding="utf-8"))


class TransformerLensHookRunner:
    def __init__(self, *, adapter: TransformerLensAdapter, model) -> None:
        self.adapter = adapter
        self.model = model

    def generate(
        self,
        *,
        bundle: AppliedFeedbackBundle,
        prompt: str,
        expert_id: str | None = None,
        max_new_tokens: int = 64,
    ) -> HookedGenerationResult:
        hook_specs = self._filter_hook_specs(bundle.hook_specs, expert_id=expert_id)
        fwd_hooks = [
            (hook_spec.hook_point, self._build_hook_fn(hook_spec))
            for hook_spec in hook_specs
        ]
        output = self.adapter.generate_with_hooks(
            self.model,
            prompt,
            fwd_hooks=fwd_hooks,
            max_new_tokens=max_new_tokens,
        )
        return HookedGenerationResult(
            application_id=bundle.application_id,
            feedback_id=bundle.feedback_id,
            expert_id=expert_id,
            prompt=prompt,
            output=str(output),
            applied_hook_ids=[hook_spec.hook_id for hook_spec in hook_specs],
        )

    def _filter_hook_specs(
        self,
        hook_specs: list[ActivationHookSpec],
        *,
        expert_id: str | None,
    ) -> list[ActivationHookSpec]:
        if expert_id is None:
            return hook_specs
        return [hook_spec for hook_spec in hook_specs if hook_spec.expert_id == expert_id]

    def _build_hook_fn(self, hook_spec: ActivationHookSpec):
        torch = _import_torch()

        def hook_fn(activation, hook):
            vector = torch.tensor(
                hook_spec.scaled_vector,
                dtype=activation.dtype,
                device=activation.device,
            )
            if activation.shape[-1] != vector.shape[0]:
                raise ValueError(
                    f"hook {hook_spec.hook_id} vector dimension {vector.shape[0]} "
                    f"does not match activation dimension {activation.shape[-1]}"
                )

            token_position = self._resolve_token_position(
                hook_spec.token_position_policy,
                seq_len=activation.shape[-2],
            )
            if activation.ndim == 3:
                activation[:, token_position, :] = activation[:, token_position, :] + vector
            elif activation.ndim == 2:
                activation[token_position, :] = activation[token_position, :] + vector
            else:
                raise ValueError(
                    f"hook {hook_spec.hook_id} expected 2D or 3D activation, "
                    f"got shape {tuple(activation.shape)}"
                )
            return activation

        return hook_fn

    def _resolve_token_position(self, policy: str, *, seq_len: int) -> int:
        if seq_len <= 0:
            raise ValueError("cannot apply hook to an empty sequence")
        if policy == "last-token":
            return seq_len - 1
        if policy.startswith("token-index:"):
            raw_position = int(policy.split(":", 1)[1])
            return max(0, min(raw_position, seq_len - 1))
        raise ValueError(f"unsupported token position policy: {policy!r}")


def _import_torch():
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "Running feedback hooks requires torch and a TransformerLens-compatible model."
        ) from exc
    return torch


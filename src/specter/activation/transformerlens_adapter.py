from __future__ import annotations

import os
from contextlib import contextmanager


class TransformerLensUnavailableError(RuntimeError):
    pass


class TransformerLensAdapter:
    """Thin optional boundary for real TransformerLens localization.

    This adapter loads a HookedTransformer and exposes only the small surface the
    feedback localizer and hooked-generation runtime need.
    """

    def __init__(
        self,
        *,
        model_path: str,
        trust_remote_code: bool = False,
        hf_token: str | bool | None = None,
        dtype=None,
        process_weights: bool = True,
        device: str | None = None,
    ) -> None:
        self.model_path = model_path
        self.trust_remote_code = trust_remote_code
        self.hf_token = hf_token
        self.dtype = dtype
        self.process_weights = process_weights
        self.device = device

    def assert_available(self) -> None:
        try:
            import torch  # noqa: F401
            import transformer_lens  # noqa: F401
        except ImportError as exc:
            raise TransformerLensUnavailableError(
                "TransformerLens localization requires optional dependencies: "
                "torch and transformer_lens."
            ) from exc

    def load_model(self):
        with self._huggingface_auth():
            self.assert_available()
            from transformer_lens import HookedTransformer

            load_options = {"trust_remote_code": self.trust_remote_code}
            if self.dtype is not None:
                load_options["dtype"] = self.dtype
            if self.device is not None:
                load_options["device"] = self.device
            loader = (
                HookedTransformer.from_pretrained
                if self.process_weights
                else HookedTransformer.from_pretrained_no_processing
            )
            return loader(self.model_path, **load_options)

    @contextmanager
    def _huggingface_auth(self):
        previous_token = os.environ.get("HF_TOKEN")
        previous_disable = os.environ.get("HF_HUB_DISABLE_IMPLICIT_TOKEN")
        hub_constants = None
        previous_disable_constant = None

        if self.hf_token is False:
            os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
            from huggingface_hub import constants as hub_constants

            previous_disable_constant = hub_constants.HF_HUB_DISABLE_IMPLICIT_TOKEN
            hub_constants.HF_HUB_DISABLE_IMPLICIT_TOKEN = True
        elif isinstance(self.hf_token, str):
            os.environ["HF_TOKEN"] = self.hf_token

        try:
            yield
        finally:
            _restore_environment("HF_TOKEN", previous_token)
            _restore_environment("HF_HUB_DISABLE_IMPLICIT_TOKEN", previous_disable)
            if hub_constants is not None:
                hub_constants.HF_HUB_DISABLE_IMPLICIT_TOKEN = previous_disable_constant

    def run_with_cache(self, model, texts: list[str]):
        return model.run_with_cache(texts, remove_batch_dim=False)

    def n_layers(self, model) -> int:
        return int(model.cfg.n_layers)

    def resid_post(self, cache, layer: int):
        return cache["resid_post", layer]

    def generate_with_hooks(
        self,
        model,
        prompt: str,
        *,
        fwd_hooks: list,
        max_new_tokens: int,
    ):
        if hasattr(model, "hooks") and hasattr(model, "generate"):
            with model.hooks(fwd_hooks=fwd_hooks):
                return model.generate(prompt, max_new_tokens=max_new_tokens)
        if hasattr(model, "generate"):
            return model.generate(
                prompt,
                max_new_tokens=max_new_tokens,
                fwd_hooks=fwd_hooks,
            )
        if hasattr(model, "run_with_hooks"):
            return model.run_with_hooks(prompt, fwd_hooks=fwd_hooks)
        raise TypeError("model must expose generate(...) or run_with_hooks(...)")


def _restore_environment(name: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value

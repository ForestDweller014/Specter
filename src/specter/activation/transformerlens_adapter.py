from __future__ import annotations


class TransformerLensUnavailableError(RuntimeError):
    pass


class TransformerLensAdapter:
    """Thin optional boundary for real TransformerLens localization.

    The feedback pipeline can produce deterministic feedback plans without heavy
    model dependencies. When the TransformerLens backend is selected, this adapter
    loads a HookedTransformer and exposes only the small surface the feedback
    localizer needs.
    """

    def __init__(self, *, model_path: str) -> None:
        self.model_path = model_path

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
        self.assert_available()
        from transformer_lens import HookedTransformer

        return HookedTransformer.from_pretrained(self.model_path)

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

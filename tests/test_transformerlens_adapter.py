from __future__ import annotations

import os
import sys
from types import ModuleType, SimpleNamespace

from specter.activation.transformerlens_adapter import TransformerLensAdapter


def test_load_model_forwards_remote_code_and_anonymous_hub_options(monkeypatch) -> None:
    calls = []
    hub_constants = SimpleNamespace(HF_HUB_DISABLE_IMPLICIT_TOKEN=False)
    hub_module = ModuleType("huggingface_hub")
    hub_module.constants = hub_constants

    class FakeHookedTransformer:
        @classmethod
        def from_pretrained(cls, model_path: str, **kwargs):
            raise AssertionError("processing loader should not be used")

        @classmethod
        def from_pretrained_no_processing(cls, model_path: str, **kwargs):
            calls.append(
                (
                    model_path,
                    kwargs,
                    os.environ.get("HF_HUB_DISABLE_IMPLICIT_TOKEN"),
                    hub_constants.HF_HUB_DISABLE_IMPLICIT_TOKEN,
                )
            )
            return "loaded-model"

    monkeypatch.delenv("HF_HUB_DISABLE_IMPLICIT_TOKEN", raising=False)
    monkeypatch.setitem(sys.modules, "huggingface_hub", hub_module)
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace())
    monkeypatch.setitem(
        sys.modules,
        "transformer_lens",
        SimpleNamespace(HookedTransformer=FakeHookedTransformer),
    )

    adapter = TransformerLensAdapter(
        model_path="Qwen/Qwen3-8B",
        trust_remote_code=True,
        hf_token=False,
        dtype="float16",
        process_weights=False,
        device="mps",
    )

    assert adapter.load_model() == "loaded-model"
    assert calls == [
        (
            "Qwen/Qwen3-8B",
            {"trust_remote_code": True, "dtype": "float16", "device": "mps"},
            "1",
            True,
        )
    ]
    assert "HF_HUB_DISABLE_IMPLICIT_TOKEN" not in os.environ
    assert hub_constants.HF_HUB_DISABLE_IMPLICIT_TOKEN is False

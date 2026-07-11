from __future__ import annotations

from dataclasses import dataclass

from specter.activation.activation_locator import LocalizationRequest
from specter.activation.contrast_set_builder import MinimalPairContrastSetBuilder
from specter.activation.models import ActivationLocalization
from specter.activation.transformerlens_adapter import TransformerLensAdapter


@dataclass(frozen=True)
class TransformerLensLocalizationResult:
    localization: ActivationLocalization
    direction_vector: list[float]
    heatmap: list[list[float]]


class TransformerLensActivationLocator:
    backend_name = "transformerlens"

    def __init__(
        self,
        *,
        adapter: TransformerLensAdapter,
        model,
        contrast_builder: MinimalPairContrastSetBuilder | None = None,
    ) -> None:
        self.adapter = adapter
        self.model = model
        self.contrast_builder = contrast_builder or MinimalPairContrastSetBuilder()

    def locate(
        self,
        request: LocalizationRequest,
        *,
        heatmap_ref: str | None = None,
    ) -> TransformerLensLocalizationResult:
        torch = _import_torch()
        item = request.feedback_item
        contrast_pairs = self.contrast_builder.build(
            item,
            pair_count=request.contrast_pair_count,
        )
        texts = [pair.positive for pair in contrast_pairs] + [
            pair.negative for pair in contrast_pairs
        ]
        _, cache = self.adapter.run_with_cache(self.model, texts)

        pair_count = len(contrast_pairs)
        layer_count = min(request.n_layers, self.adapter.n_layers(self.model))
        best_layer = 0
        best_position = 0
        best_score = -1.0
        best_direction = None
        heatmap: list[list[float]] = []

        for layer in range(layer_count):
            resid = self.adapter.resid_post(cache, layer)
            if resid.shape[0] != pair_count * 2:
                raise ValueError(
                    "TransformerLens cache batch size did not match contrast pair count"
                )
            positive = resid[:pair_count]
            negative = resid[pair_count:]
            seq_len = min(positive.shape[1], negative.shape[1])
            if seq_len == 0:
                continue

            pooled_diff = positive[:, seq_len - 1, :] - negative[:, seq_len - 1, :]
            direction = pooled_diff.mean(dim=0)
            norm = direction.norm()
            if float(norm.detach().cpu()) == 0.0:
                projection = torch.zeros(seq_len, device=resid.device)
            else:
                direction = direction / norm
                pair_diff = positive[:, :seq_len, :] - negative[:, :seq_len, :]
                projection = torch.matmul(pair_diff, direction).abs().mean(dim=0)

            layer_heatmap = [
                round(float(value), 8)
                for value in projection.detach().cpu().tolist()
            ]
            heatmap.append(layer_heatmap)
            layer_score = float(projection.max().detach().cpu()) if seq_len else 0.0
            layer_position = int(projection.argmax().detach().cpu()) if seq_len else 0
            if layer_score > best_score:
                best_score = layer_score
                best_layer = layer
                best_position = layer_position
                best_direction = direction.detach().cpu()

        if best_direction is None:
            raise ValueError("unable to derive a non-empty TransformerLens direction")

        direction_vector = [
            round(float(value), 8)
            for value in best_direction.tolist()
        ]
        localization = ActivationLocalization(
            feedback_id=item.feedback_id,
            query_id=item.query_id,
            expert_id=item.expert_id,
            contention_id=item.contention_id,
            prosecution_strength=item.prosecution_strength,
            layer=best_layer,
            token_position=best_position,
            token_position_policy=f"token-index:{best_position}",
            direction_vector_ref=request.direction_vector_ref,
            heatmap_ref=heatmap_ref,
            projection_strength=round(max(best_score, 0.0), 6),
            confidence=self._confidence(best_score),
            backend=self.backend_name,
            contrast_pairs=contrast_pairs,
        )
        return TransformerLensLocalizationResult(
            localization=localization,
            direction_vector=direction_vector,
            heatmap=heatmap,
        )

    def _confidence(self, score: float) -> float:
        if score <= 0:
            return 0.0
        return round(min(1.0, score / (score + 1.0)), 6)


def _import_torch():
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "TransformerLens localization requires torch to compute activation projections."
        ) from exc
    return torch


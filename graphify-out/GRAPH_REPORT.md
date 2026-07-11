# Graph Report - .  (2026-07-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 221 nodes · 472 edges · 14 communities (9 shown, 5 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ae3068b6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13

## God Nodes (most connected - your core abstractions)
1. `FeedbackTargetNode` - 26 edges
2. `DeterministicCourtroomRunner` - 21 edges
3. `TransformerLensAdapter` - 18 edges
4. `CourtroomConfig` - 16 edges
5. `run_from_args()` - 15 edges
6. `MinimalPairContrastSetBuilder` - 13 edges
7. `TransformerLensHookRunner` - 11 edges
8. `ActivationHookSpec` - 11 edges
9. `AppliedFeedbackBundle` - 11 edges
10. `clamp_words()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_transformerlens_hook_runner_adds_scaled_vector_to_tensor()` --calls--> `TransformerLensHookRunner`  [INFERRED]
  tests/test_specter.py → src/specter/activation/hook_runner.py
- `test_action_graph_loader_returns_answered_targets()` --calls--> `ActionGraphLoader`  [INFERRED]
  tests/test_specter.py → src/specter/graph_loader.py
- `test_contrast_builder_removes_feedback_concept_from_negative()` --calls--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `test_courtroom_model_provider_can_revise_contentions()` --calls--> `CourtroomConfig`  [INFERRED]
  tests/test_specter.py → src/specter/config.py
- `test_courtroom_runner_can_use_model_backed_roles()` --calls--> `CourtroomConfig`  [INFERRED]
  tests/test_specter.py → src/specter/config.py

## Import Cycles
- None detected.

## Communities (14 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (17): CourtroomConfig, BaseModel, Path, DeterministicContentionGenerator, DeterministicCourtroomRunner, Contention, DebateRound, DebateRoundItem (+9 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (17): AppliedFeedbackLoader, HookedGenerationResult, _import_torch(), BaseModel, Path, TransformerLensHookRunner, ActivationHookSpec, AppliedFeedbackBundle (+9 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (19): FeedbackArtifactLoader, FeedbackLoadError, Path, ValueError, build_parser(), _deterministic_heatmap(), format_text(), main() (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.14
Nodes (15): FeedbackArtifactStore, Path, _safe_path_id(), _build_model_provider(), build_parser(), format_text(), main(), ArgumentParser (+7 more)

### Community 4 - "Community 4"
Cohesion: 0.17
Nodes (12): DeterministicActivationLocator, LocalizationRequest, MinimalPairContrastSetBuilder, ActivationLocalization, ContrastPair, BaseModel, _import_torch(), TransformerLensActivationLocator (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.13
Nodes (10): RuntimeError, Thin optional boundary for real TransformerLens localization.      The feedback, TransformerLensAdapter, TransformerLensUnavailableError, build_parser(), format_text(), main(), ArgumentParser (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.32
Nodes (16): _build_courtroom_feedback(), _build_feedback_plan(), Path, test_action_graph_loader_returns_answered_targets(), test_apply_feedback_cli_text_output(), test_apply_feedback_cli_writes_activation_hooks(), test_courtroom_cli_json_output(), test_courtroom_cli_persists_feedback_artifacts() (+8 more)

### Community 7 - "Community 7"
Cohesion: 0.29
Nodes (7): ModelProvider, ModelProviderError, ModelRequest, ModelResult, OpenAICompatibleHttpProvider, RuntimeError, HTTP provider for OpenAI-compatible completion APIs, including SGLang.

### Community 8 - "Community 8"
Cohesion: 0.33
Nodes (10): build_parser(), format_text(), main(), ArgumentParser, Namespace, Path, run_from_args(), _safe_path_id() (+2 more)

## Knowledge Gaps
- **1 isolated node(s):** `specter`
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TransformerLensHookRunner` connect `Community 1` to `Community 5`, `Community 6`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Why does `TransformerLensAdapter` connect `Community 5` to `Community 1`, `Community 2`, `Community 4`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `test_transformerlens_hook_runner_adds_scaled_vector_to_tensor()` connect `Community 6` to `Community 1`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `FeedbackTargetNode` (e.g. with `test_courtroom_model_provider_can_revise_contentions()` and `test_courtroom_runner_can_use_model_backed_roles()`) actually correct?**
  _`FeedbackTargetNode` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `DeterministicCourtroomRunner` (e.g. with `run_from_args()` and `CourtroomConfig`) actually correct?**
  _`DeterministicCourtroomRunner` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TransformerLensAdapter` (e.g. with `AppliedFeedbackLoader` and `HookedGenerationResult`) actually correct?**
  _`TransformerLensAdapter` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `CourtroomConfig` (e.g. with `run_from_args()` and `DeterministicContentionGenerator`) actually correct?**
  _`CourtroomConfig` has 6 INFERRED edges - model-reasoned connections that need verification._
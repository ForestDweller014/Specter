# Graph Report - Specter  (2026-07-15)

## Corpus Check
- 41 files · ~10,735 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 301 nodes · 697 edges · 19 communities (14 shown, 5 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.64)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b3ebb809`
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
- Community 14
- Community 15
- Community 16
- Community 18

## God Nodes (most connected - your core abstractions)
1. `FeedbackTargetNode` - 29 edges
2. `CourtroomRunner` - 27 edges
3. `TransformerLensAdapter` - 21 edges
4. `CourtroomConfig` - 21 edges
5. `ScriptedInferenceProvider` - 20 edges
6. `ScriptedTransformerLensLocator` - 16 edges
7. `MinimalPairContrastSetBuilder` - 14 edges
8. `TransformerLensHookRunner` - 14 edges
9. `ScriptedTransformerLensAdapter` - 13 edges
10. `run_from_args()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `ScriptedInferenceProvider` --uses--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `ScriptedTransformerLensAdapter` --uses--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `ScriptedTransformerLensLocator` --uses--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `ScriptedInferenceProvider` --uses--> `TransformerLensHookRunner`  [INFERRED]
  tests/test_specter.py → src/specter/activation/hook_runner.py
- `ScriptedTransformerLensAdapter` --uses--> `TransformerLensHookRunner`  [INFERRED]
  tests/test_specter.py → src/specter/activation/hook_runner.py

## Import Cycles
- None detected.

## Communities (19 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (16): CourtroomConfig, BaseModel, Path, CourtroomRunner, Contention, CourtroomRunResult, DebateRound, DebateRoundItem (+8 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (19): AppliedFeedbackLoader, HookedGenerationResult, _import_torch(), BaseModel, Path, TransformerLensHookRunner, ActivationHookSpec, AppliedFeedbackBundle (+11 more)

### Community 2 - "Community 2"
Cohesion: 0.14
Nodes (25): ActionGraphLoader, ActionGraphLoadError, Path, ValueError, _build_courtroom_feedback(), _build_feedback_plan(), Path, Deterministic test double for inference that is not under direct test. (+17 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (12): RuntimeError, Thin optional boundary for real TransformerLens localization.      This adapter, _restore_environment(), TransformerLensAdapter, TransformerLensUnavailableError, build_parser(), format_text(), main() (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (11): InferenceContentionGenerator, Generate evidence-specific validation contentions through a real model provider., ModelProvider, ModelProviderError, ModelRequest, ModelResult, OpenAICompatibleHttpProvider, RuntimeError (+3 more)

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (20): PurePosixPath, configured_upstream(), current_branch(), durable_changes(), ensure_structure_only_graph(), is_excluded(), is_new_durable_output(), main() (+12 more)

### Community 6 - "Community 6"
Cohesion: 0.19
Nodes (12): LocalizationRequest, MinimalPairContrastSetBuilder, ActivationLocalization, ContrastPair, BaseModel, _import_torch(), TransformerLensActivationLocator, TransformerLensLocalizationResult (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (16): FeedbackArtifactLoader, FeedbackLoadError, Path, ValueError, build_parser(), format_text(), main(), ArgumentParser (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.24
Nodes (10): FeedbackArtifactStore, Path, _safe_path_id(), _build_model_provider(), build_parser(), format_text(), main(), ArgumentParser (+2 more)

### Community 9 - "Community 9"
Cohesion: 0.53
Nodes (13): _git(), _init_hook_repo(), _init_publishing_repo(), CompletedProcess, Path, _run(), test_hook_installer_is_idempotent_and_preserves_mode(), test_hook_installer_rejects_unknown_layout() (+5 more)

### Community 10 - "Community 10"
Cohesion: 0.21
Nodes (5): DullahanInferenceError, DullahanInferenceServer, Path, RuntimeError, Run Dullahan's local inference module for the lifetime of a Specter command.

### Community 11 - "Community 11"
Cohesion: 0.33
Nodes (10): build_parser(), format_text(), main(), ArgumentParser, Namespace, Path, run_from_args(), _safe_path_id() (+2 more)

### Community 12 - "Community 12"
Cohesion: 0.42
Nodes (8): git_output(), hook_path(), InstallError, main(), patch_hook(), Path, RuntimeError, The installed hook cannot be patched safely.

## Knowledge Gaps
- **1 isolated node(s):** `specter`
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TransformerLensHookRunner` connect `Community 1` to `Community 2`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Why does `TransformerLensAdapter` connect `Community 3` to `Community 1`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Why does `ScriptedInferenceProvider` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `FeedbackTargetNode` (e.g. with `test_dullahan_inference_executes_every_courtroom_role()` and `test_courtroom_model_provider_can_revise_contentions()`) actually correct?**
  _`FeedbackTargetNode` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `CourtroomRunner` (e.g. with `run_from_args()` and `CourtroomConfig`) actually correct?**
  _`CourtroomRunner` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TransformerLensAdapter` (e.g. with `AppliedFeedbackLoader` and `HookedGenerationResult`) actually correct?**
  _`TransformerLensAdapter` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CourtroomConfig` (e.g. with `run_from_args()` and `InferenceContentionGenerator`) actually correct?**
  _`CourtroomConfig` has 10 INFERRED edges - model-reasoned connections that need verification._
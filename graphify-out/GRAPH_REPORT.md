# Graph Report - Specter  (2026-07-15)

## Corpus Check
- 17 files · ~4,480 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 130 nodes · 326 edges · 11 communities (8 shown, 3 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 74 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `17a26028`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CourtroomRunner
- run_from_args
- models.py
- model_provider.py
- ScriptedInferenceProvider
- DullahanInferenceServer
- EvaluationArtifactStore
- CourtroomPromptBuilder
- __init__.py
- __init__.py
- specter

## God Nodes (most connected - your core abstractions)
1. `CourtroomRunner` - 33 edges
2. `FeedbackTargetNode` - 26 edges
3. `CourtroomConfig` - 20 edges
4. `ScriptedInferenceProvider` - 20 edges
5. `run_from_args()` - 13 edges
6. `InferenceContentionGenerator` - 13 edges
7. `DebateRecord` - 11 edges
8. `ActionGraphLoader` - 11 edges
9. `CourtroomPromptBuilder` - 10 edges
10. `ModelRequest` - 10 edges

## Surprising Connections (you probably didn't know these)
- `test_cli_persists_canonical_records_markdown_and_feedback()` --calls--> `build_parser()`  [INFERRED]
  tests/test_specter.py → src/specter/cli.py
- `test_cli_persists_canonical_records_markdown_and_feedback()` --calls--> `run_from_args()`  [INFERRED]
  tests/test_specter.py → src/specter/cli.py
- `test_cli_prints_declarative_feedback_prompt()` --calls--> `main()`  [INFERRED]
  tests/test_specter.py → src/specter/cli.py
- `ScriptedInferenceProvider` --uses--> `CourtroomRunner`  [INFERRED]
  tests/test_specter.py → src/specter/courtroom/debate_runner.py
- `test_all_generation_and_transcript_budgets_are_calculated()` --calls--> `CourtroomRunner`  [INFERRED]
  tests/test_specter.py → src/specter/courtroom/debate_runner.py

## Import Cycles
- None detected.

## Communities (11 total, 3 thin omitted)

### Community 0 - "CourtroomRunner"
Cohesion: 0.33
Nodes (3): ActionGraphLoader, ActionGraphLoadError, Path

### Community 1 - "run_from_args"
Cohesion: 0.39
Nodes (8): ArgumentParser, Namespace, _build_model_provider(), build_parser(), format_text(), main(), run_from_args(), CourtroomRunResult

### Community 3 - "models.py"
Cohesion: 0.19
Nodes (12): CourtroomRunner, Contention, DebateRecord, DebateRound, FeedbackPrompt, FeedbackProvenance, FinalFeedbackDecision, JudgeScore (+4 more)

### Community 4 - "model_provider.py"
Cohesion: 0.24
Nodes (7): ModelProviderError, ModelRequest, ModelResult, OpenAICompatibleHttpProvider, RuntimeError, HTTP provider for Dullahan and other OpenAI-compatible completion APIs., test_openai_compatible_provider_sends_completion_contract()

### Community 5 - "ScriptedInferenceProvider"
Cohesion: 0.17
Nodes (17): CourtroomConfig, BaseModel, Budget the one generation call that returns all initial contentions., Upper bound for a deterministic transcript assembled from bounded turns., FeedbackDisposition, StrEnum, Path, ScriptedInferenceProvider (+9 more)

### Community 6 - "DullahanInferenceServer"
Cohesion: 0.23
Nodes (5): DullahanInferenceError, DullahanInferenceServer, Path, RuntimeError, Run Dullahan's local inference module for the lifetime of a Specter command.

### Community 7 - "EvaluationArtifactStore"
Cohesion: 0.24
Nodes (5): EvaluationArtifactStore, Path, TargetCourtroomResult, new_id(), safe_path_id()

### Community 8 - "CourtroomPromptBuilder"
Cohesion: 0.25
Nodes (5): InferenceContentionGenerator, Generate evidence-specific validation contentions through a real model provider., FeedbackTargetNode, CourtroomPromptBuilder, ModelProvider

## Knowledge Gaps
- **1 isolated node(s):** `specter`
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CourtroomRunner` connect `models.py` to `run_from_args`, `model_provider.py`, `ScriptedInferenceProvider`, `EvaluationArtifactStore`, `CourtroomPromptBuilder`?**
  _High betweenness centrality (0.234) - this node is a cross-community bridge._
- **Why does `run_from_args()` connect `run_from_args` to `CourtroomRunner`, `models.py`, `ScriptedInferenceProvider`, `DullahanInferenceServer`, `EvaluationArtifactStore`, `CourtroomPromptBuilder`?**
  _High betweenness centrality (0.222) - this node is a cross-community bridge._
- **Why does `FeedbackTargetNode` connect `CourtroomPromptBuilder` to `CourtroomRunner`, `models.py`, `ScriptedInferenceProvider`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `CourtroomRunner` (e.g. with `run_from_args()` and `CourtroomConfig`) actually correct?**
  _`CourtroomRunner` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `FeedbackTargetNode` (e.g. with `InferenceContentionGenerator` and `CourtroomRunner`) actually correct?**
  _`FeedbackTargetNode` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `CourtroomConfig` (e.g. with `run_from_args()` and `InferenceContentionGenerator`) actually correct?**
  _`CourtroomConfig` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ScriptedInferenceProvider` (e.g. with `CourtroomConfig` and `CourtroomRunner`) actually correct?**
  _`ScriptedInferenceProvider` has 11 INFERRED edges - model-reasoned connections that need verification._
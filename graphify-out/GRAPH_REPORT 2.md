# Graph Report - Specter  (2026-07-15)

## Corpus Check
- 60 files · ~32,159 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 510 nodes · 887 edges · 36 communities (27 shown, 9 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.64)
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
- From A Recorded Trace To Reversible Feedback
- Specter inference-correction benchmark bug log
- Feedback Runtime Architecture
- Investigation and Debugging
- Large-Feature Decomposition
- Minimal-Context Coding
- Architecture-First Changes
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- Atomic Git Commit Workflow
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- AGENTS.md
- extraction-spec.md

## God Nodes (most connected - your core abstractions)
1. `FeedbackTargetNode` - 29 edges
2. `CourtroomRunner` - 27 edges
3. `Continuous Integration Engineering` - 23 edges
4. `TransformerLensAdapter` - 21 edges
5. `CourtroomConfig` - 21 edges
6. `ScriptedInferenceProvider` - 20 edges
7. `Specter inference-correction benchmark bug log` - 19 edges
8. `ScriptedTransformerLensLocator` - 16 edges
9. `MinimalPairContrastSetBuilder` - 14 edges
10. `TransformerLensHookRunner` - 14 edges

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

## Communities (36 total, 9 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (16): CourtroomConfig, BaseModel, Path, CourtroomRunner, Contention, CourtroomRunResult, DebateRound, DebateRoundItem (+8 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (26): AppliedFeedbackLoader, HookedGenerationResult, _import_torch(), BaseModel, Path, TransformerLensHookRunner, ActivationHookSpec, AppliedFeedbackBundle (+18 more)

### Community 2 - "Community 2"
Cohesion: 0.14
Nodes (25): ActionGraphLoader, ActionGraphLoadError, Path, ValueError, _build_courtroom_feedback(), _build_feedback_plan(), Path, Deterministic test double for inference that is not under direct test. (+17 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (30): Build and artifact handling, Caching, Change-aware execution, Completion report, Concurrency and cancellation, Continuous Integration Engineering, Coverage, Database and contract safety (+22 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (11): InferenceContentionGenerator, Generate evidence-specific validation contentions through a real model provider., ModelProvider, ModelProviderError, ModelRequest, ModelResult, OpenAICompatibleHttpProvider, RuntimeError (+3 more)

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (20): PurePosixPath, configured_upstream(), current_branch(), durable_changes(), ensure_structure_only_graph(), is_excluded(), is_new_durable_output(), main() (+12 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (18): LocalizationRequest, MinimalPairContrastSetBuilder, ActivationLocalization, ContrastPair, BaseModel, RuntimeError, Thin optional boundary for real TransformerLens localization.      This adapter, _restore_environment() (+10 more)

### Community 7 - "Community 7"
Cohesion: 0.18
Nodes (15): FeedbackArtifactLoader, FeedbackLoadError, Path, ValueError, build_parser(), format_text(), main(), ArgumentParser (+7 more)

### Community 8 - "Community 8"
Cohesion: 0.12
Nodes (15): FeedbackArtifactStore, Path, _safe_path_id(), _build_model_provider(), build_parser(), format_text(), main(), ArgumentParser (+7 more)

### Community 9 - "Community 9"
Cohesion: 0.53
Nodes (13): _git(), _init_hook_repo(), _init_publishing_repo(), CompletedProcess, Path, _run(), test_hook_installer_is_idempotent_and_preserves_mode(), test_hook_installer_rejects_unknown_layout() (+5 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 11 - "Community 11"
Cohesion: 0.33
Nodes (10): build_parser(), format_text(), main(), ArgumentParser, Namespace, Path, run_from_args(), _safe_path_id() (+2 more)

### Community 12 - "Community 12"
Cohesion: 0.42
Nodes (8): git_output(), hook_path(), InstallError, main(), patch_hook(), Path, RuntimeError, The installed hook cannot be patched safely.

### Community 19 - "From A Recorded Trace To Reversible Feedback"
Cohesion: 0.08
Nodes (24): 1. Install Specter, 2. Point Specter At A Completed Action Graph, 3. Run The Courtroom, 4. Find The Feedback Inside The Expert Model, 5. Turn The Plan Into Reversible Hooks, 6. Rerun The Expert With Feedback Applied, Activation Localization And Feedback Application, Architecture (+16 more)

### Community 20 - "Specter inference-correction benchmark bug log"
Cohesion: 0.10
Nodes (19): Active execution findings, B-001 — Dullahan console script could not import its package, B-002 — Notebook ran under the Anaconda kernel, B-003 — TransformerLens optional dependencies were not installed, B-004 — Invalid cached Hugging Face token broke a public download, B-005 — Direct `token=False` conflicts inside TransformerLens 3.5, B-006 — Notebook progress integration warning, B-007 — Two 8B runtimes plus float32 weights exceed host memory (+11 more)

### Community 21 - "Feedback Runtime Architecture"
Cohesion: 0.13
Nodes (14): Activation Localization, Courtroom Runtime, Debate Bounds, Development Sequence, Existing CLI Flow, Feedback Application, Feedback Artifacts, Feedback Runtime Architecture (+6 more)

### Community 22 - "Investigation and Debugging"
Cohesion: 0.14
Nodes (13): 10. Failure handling, 11. Completion report, 1. Define the failure precisely, 2. Reproduce before modifying, 3. Orient to the failing path, 4. Form ranked hypotheses, 5. Test one variable at a time, 6. Identify the root cause (+5 more)

### Community 23 - "Large-Feature Decomposition"
Cohesion: 0.15
Nodes (12): 10. Decomposition output format, 1. Frame the feature, 2. Map the affected system, 3. Identify workstreams and dependencies, 4. Prefer vertical slices, 5. Define each chunk, 6. Sequence for risk reduction, 7. Create a context packet per chunk (+4 more)

### Community 24 - "Minimal-Context Coding"
Cohesion: 0.15
Nodes (12): 10. Completion report, 1. Establish the task boundary, 2. Orient before reading files, 3. Build a bounded working set, 4. Expand only through evidence, 5. Read surgically, 6. Maintain a compact working summary, 7. Use bounded investigations (+4 more)

### Community 25 - "Architecture-First Changes"
Cohesion: 0.18
Nodes (10): 1. Orient to the existing system, 2. Establish constraints and invariants, 3. Choose the smallest coherent design, 4. Define the change contract, 5. Plan an implementation sequence, 6. Implement within the design, 7. Validate at multiple levels, 8. Completion report (+2 more)

### Community 26 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 27 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 28 - "Atomic Git Commit Workflow"
Cohesion: 0.40
Nodes (4): Atomic Git Commit Workflow, Commit messages, Commit strategy, Scope

### Community 29 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 30 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 31 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **167 isolated node(s):** `specter`, `Core rule`, `1. Orient to the existing system`, `2. Establish constraints and invariants`, `3. Choose the smallest coherent design` (+162 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TransformerLensHookRunner` connect `Community 1` to `Community 2`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `TransformerLensAdapter` connect `Community 6` to `Community 1`, `Community 7`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `ScriptedInferenceProvider` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `FeedbackTargetNode` (e.g. with `test_dullahan_inference_executes_every_courtroom_role()` and `test_courtroom_model_provider_can_revise_contentions()`) actually correct?**
  _`FeedbackTargetNode` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `CourtroomRunner` (e.g. with `run_from_args()` and `CourtroomConfig`) actually correct?**
  _`CourtroomRunner` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TransformerLensAdapter` (e.g. with `AppliedFeedbackLoader` and `HookedGenerationResult`) actually correct?**
  _`TransformerLensAdapter` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CourtroomConfig` (e.g. with `run_from_args()` and `InferenceContentionGenerator`) actually correct?**
  _`CourtroomConfig` has 10 INFERRED edges - model-reasoned connections that need verification._
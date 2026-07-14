# Graph Report - Specter  (2026-07-13)

## Corpus Check
- 56 files · ~28,160 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 484 nodes · 804 edges · 37 communities (26 shown, 11 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `70210947`
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
- publish_graphify_snapshot.py
- Specter
- Feedback Runtime Architecture
- Investigation and Debugging
- Large-Feature Decomposition
- Minimal-Context Coding
- _run
- Architecture-First Changes
- graphify reference: extra exports and benchmark
- InstallError
- graphify reference: query, path, explain
- Atomic Git Commit Workflow
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- AGENTS.md
- extraction-spec.md
- ScriptedTransformerLensAdapter
- .load_targets
- BaseModel
- CompletedProcess

## God Nodes (most connected - your core abstractions)
1. `CourtroomRunner` - 24 edges
2. `Continuous Integration Engineering` - 23 edges
3. `CourtroomConfig` - 20 edges
4. `TransformerLensAdapter` - 19 edges
5. `ScriptedInferenceProvider` - 17 edges
6. `Feedback Runtime Architecture` - 14 edges
7. `Specter` - 13 edges
8. `MinimalPairContrastSetBuilder` - 13 edges
9. `ScriptedTransformerLensLocator` - 13 edges
10. `FeedbackTargetNode` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_real_transformerlens_localizes_feedback_activations()` --calls--> `LocalizationRequest`  [INFERRED]
  tests/test_real_inference.py → src/specter/activation/activation_locator.py
- `ScriptedInferenceProvider` --uses--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `ScriptedTransformerLensAdapter` --uses--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `ScriptedTransformerLensLocator` --uses--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `test_real_transformerlens_localizes_feedback_activations()` --calls--> `TransformerLensAdapter`  [INFERRED]
  tests/test_real_inference.py → src/specter/activation/transformerlens_adapter.py

## Import Cycles
- None detected.

## Communities (37 total, 11 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (17): FeedbackArtifactStore, Path, _safe_path_id(), Contention, CourtroomRunResult, DebateRound, DebateRoundItem, FeedbackItem (+9 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (22): AppliedFeedbackLoader, HookedGenerationResult, _import_torch(), BaseModel, Path, TransformerLensHookRunner, ActivationHookSpec, AppliedFeedbackBundle (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (6): DullahanInferenceError, DullahanInferenceServer, Path, RuntimeError, Run Dullahan's local inference module for the lifetime of a Specter command., test_real_transformerlens_localizes_feedback_activations()

### Community 4 - "Community 4"
Cohesion: 0.12
Nodes (15): RuntimeError, Thin optional boundary for real TransformerLens localization.      This adapter, TransformerLensAdapter, TransformerLensUnavailableError, build_parser(), format_text(), main(), ArgumentParser (+7 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (16): ContrastPair, FeedbackItem, LocalizationRequest, MinimalPairContrastSetBuilder, ActivationLocalization, ContrastPair, BaseModel, _import_torch() (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (37): CourtroomRunResult, _build_model_provider(), build_parser(), format_text(), main(), ArgumentParser, Namespace, run_from_args() (+29 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (30): Build and artifact handling, Caching, Change-aware execution, Completion report, Concurrency and cancellation, Continuous Integration Engineering, Coverage, Database and contract safety (+22 more)

### Community 8 - "Community 8"
Cohesion: 0.33
Nodes (10): build_parser(), format_text(), main(), ArgumentParser, Namespace, Path, run_from_args(), _safe_path_id() (+2 more)

### Community 14 - "publish_graphify_snapshot.py"
Cohesion: 0.30
Nodes (19): PurePosixPath, configured_upstream(), current_branch(), durable_changes(), is_excluded(), is_new_durable_output(), main(), nul_paths() (+11 more)

### Community 15 - "Specter"
Cohesion: 0.11
Nodes (17): 1. Generate Courtroom Feedback, 2. Localize Feedback, 3. Materialize Activation Hooks, 4. Rerun Expert Inference With Hooks, Automatic Graphify Snapshot Publishing, Comparison, Development, Domain Adaptation (+9 more)

### Community 16 - "Feedback Runtime Architecture"
Cohesion: 0.13
Nodes (14): Activation Localization, Courtroom Runtime, Debate Bounds, Development Sequence, Existing CLI Flow, Feedback Application, Feedback Artifacts, Feedback Runtime Architecture (+6 more)

### Community 17 - "Investigation and Debugging"
Cohesion: 0.14
Nodes (13): 10. Failure handling, 11. Completion report, 1. Define the failure precisely, 2. Reproduce before modifying, 3. Orient to the failing path, 4. Form ranked hypotheses, 5. Test one variable at a time, 6. Identify the root cause (+5 more)

### Community 18 - "Large-Feature Decomposition"
Cohesion: 0.15
Nodes (12): 10. Decomposition output format, 1. Frame the feature, 2. Map the affected system, 3. Identify workstreams and dependencies, 4. Prefer vertical slices, 5. Define each chunk, 6. Sequence for risk reduction, 7. Create a context packet per chunk (+4 more)

### Community 19 - "Minimal-Context Coding"
Cohesion: 0.15
Nodes (12): 10. Completion report, 1. Establish the task boundary, 2. Orient before reading files, 3. Build a bounded working set, 4. Expand only through evidence, 5. Read surgically, 6. Maintain a compact working summary, 7. Use bounded investigations (+4 more)

### Community 20 - "_run"
Cohesion: 0.54
Nodes (12): CompletedProcess, _git(), _init_hook_repo(), _init_publishing_repo(), Path, _run(), test_hook_installer_is_idempotent_and_preserves_mode(), test_hook_installer_rejects_unknown_layout() (+4 more)

### Community 21 - "Architecture-First Changes"
Cohesion: 0.18
Nodes (10): 1. Orient to the existing system, 2. Establish constraints and invariants, 3. Choose the smallest coherent design, 4. Define the change contract, 5. Plan an implementation sequence, 6. Implement within the design, 7. Validate at multiple levels, 8. Completion report (+2 more)

### Community 22 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 23 - "InstallError"
Cohesion: 0.42
Nodes (8): git_output(), hook_path(), InstallError, main(), patch_hook(), Path, RuntimeError, The installed hook cannot be patched safely.

### Community 24 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 25 - "Atomic Git Commit Workflow"
Cohesion: 0.40
Nodes (4): Atomic Git Commit Workflow, Commit messages, Commit strategy, Scope

### Community 26 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 27 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 28 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 33 - "ScriptedTransformerLensAdapter"
Cohesion: 0.14
Nodes (17): BaseModel, Contention, CourtroomPromptBuilder, DebateRound, JudgeScore, CourtroomConfig, Path, InferenceContentionGenerator (+9 more)

### Community 34 - ".load_targets"
Cohesion: 0.36
Nodes (4): ActionGraphLoader, ActionGraphLoadError, Path, ValueError

## Knowledge Gaps
- **144 isolated node(s):** `Tech Stack`, `Install`, `Automatic Graphify Snapshot Publishing`, `Input Contract`, `1. Generate Courtroom Feedback` (+139 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TransformerLensAdapter` connect `Community 4` to `Community 1`, `Community 3`, `Community 5`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `MinimalPairContrastSetBuilder` connect `Community 5` to `Community 1`, `Community 6`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `FeedbackTargetNode` connect `Community 0` to `.load_targets`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `CourtroomRunner` (e.g. with `run_from_args()` and `CourtroomConfig`) actually correct?**
  _`CourtroomRunner` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CourtroomConfig` (e.g. with `run_from_args()` and `InferenceContentionGenerator`) actually correct?**
  _`CourtroomConfig` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `TransformerLensAdapter` (e.g. with `AppliedFeedbackLoader` and `HookedGenerationResult`) actually correct?**
  _`TransformerLensAdapter` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `ScriptedInferenceProvider` (e.g. with `MinimalPairContrastSetBuilder` and `CourtroomConfig`) actually correct?**
  _`ScriptedInferenceProvider` has 6 INFERRED edges - model-reasoned connections that need verification._
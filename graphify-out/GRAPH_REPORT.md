# Graph Report - Specter  (2026-07-15)

## Corpus Check
- 60 files · ~31,989 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 518 nodes · 866 edges · 41 communities (29 shown, 12 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 109 edges (avg confidence: 0.64)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ae752476`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- answers.md
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
- ModelProvider
- .load_targets
- CFA Level III paired correction benchmark answers
- Specter inference-correction benchmark bug log
- answers.md
- CFA Level III paired correction benchmark answers
- apply_cli.py

## God Nodes (most connected - your core abstractions)
1. `FeedbackTargetNode` - 34 edges
2. `CourtroomRunner` - 31 edges
3. `Continuous Integration Engineering` - 23 edges
4. `CourtroomConfig` - 21 edges
5. `TransformerLensAdapter` - 20 edges
6. `Specter inference-correction benchmark bug log` - 19 edges
7. `ScriptedInferenceProvider` - 17 edges
8. `MinimalPairContrastSetBuilder` - 14 edges
9. `Feedback Runtime Architecture` - 14 edges
10. `FeedbackItem` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_real_transformerlens_localizes_feedback_activations()` --calls--> `FeedbackItem`  [INFERRED]
  tests/test_real_inference.py → src/specter/courtroom/models.py
- `test_load_model_forwards_remote_code_and_anonymous_hub_options()` --calls--> `TransformerLensAdapter`  [INFERRED]
  tests/test_transformerlens_adapter.py → src/specter/activation/transformerlens_adapter.py
- `ScriptedInferenceProvider` --uses--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `ScriptedTransformerLensLocator` --uses--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `test_inference_clis_reject_removed_deterministic_backends()` --calls--> `build_parser()`  [INFERRED]
  tests/test_specter.py → src/specter/cli.py

## Import Cycles
- None detected.

## Communities (41 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (19): InferenceContentionGenerator, CourtroomConfig, BaseModel, Path, CourtroomRunner, ModelProvider, Contention, CourtroomRunResult (+11 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (23): AppliedFeedbackLoader, HookedGenerationResult, _import_torch(), BaseModel, Path, TransformerLensHookRunner, ActivationHookSpec, AppliedFeedbackBundle (+15 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (6): DullahanInferenceError, DullahanInferenceServer, Path, RuntimeError, Run Dullahan's local inference module for the lifetime of a Specter command., test_real_transformerlens_localizes_feedback_activations()

### Community 4 - "answers.md"
Cohesion: 0.54
Nodes (3): FeedbackArtifactStore, Path, _safe_path_id()

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (9): ContrastPair, MinimalPairContrastSetBuilder, FeedbackItem, FeedbackArtifactLoader, FeedbackLoadError, Path, ValueError, ScriptedTransformerLensAdapter (+1 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (32): ArgumentParser, ModelRequest, ModelResult, Namespace, _build_model_provider(), build_parser(), format_text(), main() (+24 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (30): Build and artifact handling, Caching, Change-aware execution, Completion report, Concurrency and cancellation, Continuous Integration Engineering, Coverage, Database and contract safety (+22 more)

### Community 14 - "publish_graphify_snapshot.py"
Cohesion: 0.30
Nodes (19): PurePosixPath, configured_upstream(), current_branch(), durable_changes(), is_excluded(), is_new_durable_output(), main(), nul_paths() (+11 more)

### Community 15 - "Specter"
Cohesion: 0.08
Nodes (24): 1. Install Specter, 2. Point Specter At A Completed Action Graph, 3. Run The Courtroom, 4. Find The Feedback Inside The Expert Model, 5. Turn The Plan Into Reversible Hooks, 6. Rerun The Expert With Feedback Applied, Activation Localization And Feedback Application, Architecture (+16 more)

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
Nodes (12): _git(), _init_hook_repo(), _init_publishing_repo(), CompletedProcess, Path, _run(), test_hook_installer_is_idempotent_and_preserves_mode(), test_hook_installer_rejects_unknown_layout() (+4 more)

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

### Community 33 - "ModelProvider"
Cohesion: 0.12
Nodes (13): InferenceContentionGenerator, Generate evidence-specific validation contentions through a real model provider., new_id(), ModelProvider, ModelProviderError, ModelRequest, ModelResult, OpenAICompatibleHttpProvider (+5 more)

### Community 34 - ".load_targets"
Cohesion: 0.08
Nodes (25): RuntimeError, LocalizationRequest, ActivationLocalization, ContrastPair, BaseModel, Thin optional boundary for real TransformerLens localization.      This adapter, _restore_environment(), TransformerLensAdapter (+17 more)

### Community 35 - "CFA Level III paired correction benchmark answers"
Cohesion: 0.38
Nodes (4): ActionGraphLoader, ActionGraphLoadError, Path, ValueError

### Community 36 - "Specter inference-correction benchmark bug log"
Cohesion: 0.10
Nodes (19): Active execution findings, B-001 — Dullahan console script could not import its package, B-002 — Notebook ran under the Anaconda kernel, B-003 — TransformerLens optional dependencies were not installed, B-004 — Invalid cached Hugging Face token broke a public download, B-005 — Direct `token=False` conflicts inside TransformerLens 3.5, B-006 — Notebook progress integration warning, B-007 — Two 8B runtimes plus float32 weights exceed host memory (+11 more)

### Community 40 - "apply_cli.py"
Cohesion: 0.33
Nodes (10): build_parser(), format_text(), main(), ArgumentParser, Namespace, Path, run_from_args(), _safe_path_id() (+2 more)

## Knowledge Gaps
- **167 isolated node(s):** `specter`, `Core rule`, `1. Orient to the existing system`, `2. Establish constraints and invariants`, `3. Choose the smallest coherent design` (+162 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MinimalPairContrastSetBuilder` connect `Community 5` to `ModelProvider`, `.load_targets`, `Community 6`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `TransformerLensAdapter` connect `.load_targets` to `Community 1`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `CourtroomRunner` connect `Community 0` to `ModelProvider`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `FeedbackTargetNode` (e.g. with `CourtroomRunner` and `CourtroomPromptBuilder`) actually correct?**
  _`FeedbackTargetNode` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `CourtroomRunner` (e.g. with `run_from_args()` and `CourtroomConfig`) actually correct?**
  _`CourtroomRunner` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CourtroomConfig` (e.g. with `run_from_args()` and `InferenceContentionGenerator`) actually correct?**
  _`CourtroomConfig` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `TransformerLensAdapter` (e.g. with `AppliedFeedbackLoader` and `HookedGenerationResult`) actually correct?**
  _`TransformerLensAdapter` has 8 INFERRED edges - model-reasoned connections that need verification._
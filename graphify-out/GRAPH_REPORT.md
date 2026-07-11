# Graph Report - Specter  (2026-07-10)

## Corpus Check
- 52 files · ~24,525 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 412 nodes · 718 edges · 33 communities (24 shown, 9 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 85 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fd629ca2`
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

## God Nodes (most connected - your core abstractions)
1. `FeedbackTargetNode` - 26 edges
2. `DeterministicCourtroomRunner` - 21 edges
3. `TransformerLensAdapter` - 18 edges
4. `CourtroomConfig` - 16 edges
5. `run_from_args()` - 15 edges
6. `Feedback Runtime Architecture` - 14 edges
7. `MinimalPairContrastSetBuilder` - 13 edges
8. `Investigation and Debugging` - 13 edges
9. `Large-Feature Decomposition` - 12 edges
10. `Minimal-Context Coding` - 12 edges

## Surprising Connections (you probably didn't know these)
- `test_transformerlens_hook_runner_adds_scaled_vector_to_tensor()` --calls--> `TransformerLensHookRunner`  [INFERRED]
  tests/test_specter.py → src/specter/activation/hook_runner.py
- `test_contrast_builder_removes_feedback_concept_from_negative()` --calls--> `MinimalPairContrastSetBuilder`  [INFERRED]
  tests/test_specter.py → src/specter/activation/contrast_set_builder.py
- `test_courtroom_model_provider_can_revise_contentions()` --calls--> `CourtroomConfig`  [INFERRED]
  tests/test_specter.py → src/specter/config.py
- `test_courtroom_runner_can_use_model_backed_roles()` --calls--> `CourtroomConfig`  [INFERRED]
  tests/test_specter.py → src/specter/config.py
- `test_courtroom_runner_evolves_contentions_after_first_round()` --calls--> `CourtroomConfig`  [INFERRED]
  tests/test_specter.py → src/specter/config.py

## Import Cycles
- None detected.

## Communities (33 total, 9 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (17): CourtroomConfig, BaseModel, Path, DeterministicContentionGenerator, DeterministicCourtroomRunner, Contention, DebateRound, DebateRoundItem (+9 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (20): AppliedFeedbackLoader, HookedGenerationResult, _import_torch(), BaseModel, Path, TransformerLensHookRunner, ActivationHookSpec, AppliedFeedbackBundle (+12 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 3 - "Community 3"
Cohesion: 0.23
Nodes (11): FeedbackArtifactStore, Path, _safe_path_id(), _build_model_provider(), build_parser(), format_text(), main(), ArgumentParser (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (28): DeterministicActivationLocator, LocalizationRequest, MinimalPairContrastSetBuilder, ActivationLocalization, ContrastPair, BaseModel, _import_torch(), TransformerLensActivationLocator (+20 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (10): RuntimeError, Thin optional boundary for real TransformerLens localization.      The feedback, TransformerLensAdapter, TransformerLensUnavailableError, build_parser(), format_text(), main(), ArgumentParser (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.18
Nodes (20): ActionGraphLoader, ActionGraphLoadError, Path, ValueError, _build_courtroom_feedback(), _build_feedback_plan(), Path, test_action_graph_loader_returns_answered_targets() (+12 more)

### Community 7 - "Community 7"
Cohesion: 0.29
Nodes (7): ModelProvider, ModelProviderError, ModelRequest, ModelResult, OpenAICompatibleHttpProvider, RuntimeError, HTTP provider for OpenAI-compatible completion APIs, including SGLang.

### Community 8 - "Community 8"
Cohesion: 0.33
Nodes (10): build_parser(), format_text(), main(), ArgumentParser, Namespace, Path, run_from_args(), _safe_path_id() (+2 more)

### Community 14 - "publish_graphify_snapshot.py"
Cohesion: 0.30
Nodes (19): PurePosixPath, configured_upstream(), current_branch(), durable_changes(), is_excluded(), is_new_durable_output(), main(), nul_paths() (+11 more)

### Community 15 - "Specter"
Cohesion: 0.12
Nodes (15): 1. Generate Courtroom Feedback, 2. Localize Feedback, 3. Materialize Activation Hooks, 4. Rerun Expert Inference With Hooks, Automatic Graphify Snapshot Publishing, Comparison, Development, Domain Adaptation (+7 more)

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

## Knowledge Gaps
- **115 isolated node(s):** `specter`, `Core rule`, `1. Orient to the existing system`, `2. Establish constraints and invariants`, `3. Choose the smallest coherent design` (+110 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TransformerLensHookRunner` connect `Community 1` to `Community 5`, `Community 6`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `TransformerLensAdapter` connect `Community 5` to `Community 1`, `Community 4`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `test_transformerlens_hook_runner_adds_scaled_vector_to_tensor()` connect `Community 6` to `Community 1`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `FeedbackTargetNode` (e.g. with `test_courtroom_model_provider_can_revise_contentions()` and `test_courtroom_runner_can_use_model_backed_roles()`) actually correct?**
  _`FeedbackTargetNode` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `DeterministicCourtroomRunner` (e.g. with `run_from_args()` and `CourtroomConfig`) actually correct?**
  _`DeterministicCourtroomRunner` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TransformerLensAdapter` (e.g. with `AppliedFeedbackLoader` and `HookedGenerationResult`) actually correct?**
  _`TransformerLensAdapter` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `CourtroomConfig` (e.g. with `run_from_args()` and `DeterministicContentionGenerator`) actually correct?**
  _`CourtroomConfig` has 6 INFERRED edges - model-reasoned connections that need verification._
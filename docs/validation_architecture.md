# Feedback Runtime Architecture

## Purpose

Dullahan currently turns source context into graph memory, routes subqueries to
cluster-owned experts, and persists each run as an action graph. The feedback
runtime is a proposed post-run system that consumes that immutable
`action_graph.json`, subjects each expert response to bounded adversarial review,
and converts the resulting debate summaries into auditable activation-level
feedback for the expert SLM.

This document defines the architecture only. It does not introduce implementation
code.

## Existing CLI Flow

The current Dullahan flow is:

```bash
dullahan-graphify ./path/to/data --k 8
dullahan-agent "Root query" --max-depth 2 --persist-artifacts
```

Persisted execution artifacts are written to:

```text
memory/executions/<trace_id>/
  action_graph.json
  action_graph.mmd
  queries.yaml
  contexts.yaml
  responses.yaml
  trace.yaml
  manifest.yaml
  final_response.md
  instances/<query_id>/
```

The feedback runtime begins at `action_graph.json`.

## Proposed CLI Flow

The feedback system should be layered into three explicit stages:

```bash
specter-courtroom memory/executions/<trace_id>/action_graph.json \
  --rounds 3 \
  --contentions 8 \
  --summary-token-budget 256 \
  --response-token-budget 384 \
  --persist
```

```bash
specter-courtroom memory/executions/<trace_id>/action_graph.json \
  --courtroom-model-provider dullahan \
  --courtroom-model-base-url http://127.0.0.1:30000/v1 \
  --persist
```

```bash
specter-localize-feedback memory/feedback/<feedback_id> \
  --expert-id expert:cluster-1 \
  --model-path ./models/expert-1 \
  --contrast-pairs 32
```

```bash
specter-apply-feedback memory/feedback/<feedback_id>/feedback_plan.json \
  --mode activation-hook \
  --scale 0.2
```

```bash
specter-run-feedback-hooks \
  memory/feedback/<feedback_id>/applied/<application_id>/activation_hooks.json \
  --model-path ./models/expert-1 \
  --prompt "Subquery text"
```

A later convenience command can compose these stages:

```bash
specter-feedback memory/executions/<trace_id>/action_graph.json \
  --rounds 3 \
  --localize \
  --apply-mode activation-hook
```

## Proposed Package Layout

```text
apps/feedback-runtime/
  README.md
  src/specter/
    __init__.py
    cli.py
    config.py
    graph_loader.py
    artifacts.py
    courtroom/
      models.py
      contention_generator.py
      role_prompts.py
      debate_runner.py
      court_reporter.py
      judge.py
    activation/
      transformerlens_adapter.py
      contrast_set_builder.py
      activation_locator.py
      steering_vector_store.py
    feedback/
      models.py
      feedback_loader.py
      plan_builder.py
      apply_runtime.py
      apply_cli.py
```

## Input Contract

The feedback runtime consumes the existing Dullahan action graph:

```text
Node = Expert, Query, Context, Response, Subqueries
Edge = parent query -> child query
```

Each action-graph node becomes a `FeedbackTargetNode`:

```text
FeedbackTargetNode
  query_id
  expert_id
  query
  context
  response
  child_query_ids
  depth
  sender_id
```

The original action graph must remain immutable. Feedback artifacts are written
beside it under `memory/feedback/`.

## Courtroom Runtime

For each `FeedbackTargetNode`, the expert that handled the node is reused as the
identity for four role-conditioned model instances:

```text
Defender: defend the original response.
Prosecutor: criticize the original response.
Judge: score the strength of the prosecution.
Court Reporter: compress and maintain the running debate summary.
```

The prosecutor first produces an exhaustive criticism draft:

```text
Contention 1
Contention 2
...
Contention N
```

Then the system runs `M` bounded debate rounds. For every contention in every
round:

```text
Defender:
  contention_i, running_debate_summary_i -> defense_i

Prosecutor:
  contention_i, running_debate_summary_i, defense_i -> prosecution_rebuttal_i

Judge:
  contention_i, running_debate_summary_i, defense_i, prosecution_rebuttal_i
    -> prosecution_strength_i

Court Reporter:
  prior_summary_i, defense_i, prosecution_rebuttal_i, judge_score_i
    -> compressed_running_debate_summary_i
```

The prosecutor may revise contentions between rounds. The defender may only
answer the current contention and may not modify it.

## Debate Bounds

The runtime should enforce fixed token budgets for:

```text
contention
running_debate_summary
defense
prosecution_rebuttal
judge_rationale
```

The judge emits:

```text
prosecution_strength in [-1.0, 1.0]
```

Where:

```text
-1.0 = defense is right
 0.0 = mixed or unresolved
 1.0 = prosecution is right
```

## Feedback Artifacts

The courtroom stage writes:

```text
memory/feedback/<feedback_id>/
  manifest.yaml
  targets/<query_id>/
    target.yaml
    contentions.yaml
    rounds.yaml
    debate_summaries.yaml
    judge_scores.yaml
    final_feedback.yaml
```

The final courtroom output is a set of `FeedbackItem` records:

```text
FeedbackItem
  feedback_id
  query_id
  expert_id
  contention_id
  running_debate_summary
  prosecution_strength
  target_query
  target_context
  target_response
```

## Activation Localization

The activation stage uses TransformerLens to identify where each
`running_debate_summary` activates in the corresponding expert SLM.

The localizer should build sentence-level contrast sets rather than token-level
word swaps. For each debate summary:

1. Construct minimal positive/negative sentence pairs.
2. Preserve topic, syntax, length, and vocabulary overlap where possible.
3. Run the expert model with TransformerLens activation caching.
4. Extract concept directions from positive/negative activation differences.
5. Produce a layer-by-token-position projection heatmap.
6. Select the most stable activation site.

The activation output is:

```text
ActivationLocalization
  expert_id
  contention_id
  layer
  token_position
  token_position_policy
  direction_vector_ref
  heatmap_ref
  projection_strength
  confidence
```

The default pooling policy should be last-token pooling only after checking the
layer-by-token heatmap. Some sentence-level concepts may crystallize before the
final token and decay by the end of the sentence.

## Feedback Application

The first implementation should prefer runtime activation steering over
permanent weight edits.

The scaled intervention is:

```text
scaled_direction = activation_direction * prosecution_strength * feedback_scale
```

Supported application modes should be staged:

```text
activation-hook: apply steering vectors during inference.
lora-dataset: export supervised examples for later adapter training.
weight-edit: research-only durable model modification.
```

`activation-hook` should be the default because it is reversible, auditable, and
compatible with experimentation before committing to model edits.

The feedback plan should be explicit:

```text
FeedbackPlan
  feedback_id
  source_trace_id
  expert_id
  items:
    - contention_id
      query_id
      prosecution_strength
      layer
      token_position_policy
      direction_vector_ref
      feedback_scale
      application_mode
```

## Integration Points

The feedback runtime should integrate with Dullahan through existing boundaries:

```text
action_graph.json: source of query/context/response graph.
experts.yaml: source of expert identity and model name.
EDL model provider: source of role-conditioned expert calls.
memory/feedback: destination for debate and feedback artifacts.
```

Future service deployment can expose the courtroom and localization stages as
FastAPI services, but the first implementation should remain CLI-first and
artifact-first.

## Scaling Path

The architecture maps onto the broader stack as follows:

```text
Python: orchestration, schemas, CLI, artifacts.
PyTorch: activation extraction and steering.
TransformerLens: model hooks and activation cache analysis.
C++: optional kernels or high-throughput vector operations only if profiling requires it.
SGLang/KServe: expert model serving.
Redis/SQS: queue-backed debate jobs.
PostgreSQL: feedback metadata and lineage.
S3: durable artifact and vector storage.
OpenTelemetry/Prometheus/Grafana: runtime observability.
Kubernetes/EKS: distributed CAL, EDL, courtroom, and model-serving workers.
```

## Development Sequence

Recommended implementation order:

1. Add Pydantic schemas for feedback targets, contentions, debate rounds, judge
   scores, activation localizations, and feedback plans.
2. Add an action-graph loader that maps existing nodes into feedback targets.
3. Add the courtroom CLI with Dullahan local inference and explicit test doubles.
4. Persist courtroom artifacts under `memory/feedback/`.
5. Add TransformerLens localization behind an optional dependency.
6. Add activation-hook feedback application for local expert models.
7. Add service APIs, queues, and distributed execution only after the local
   artifact pipeline is reliable.

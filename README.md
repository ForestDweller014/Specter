# Specter

Specter is a validation layer for expert SLMs. It conducts debate rounds with
prosecutor, defense, judge, and court-reporter agents to validate responses and
query delegations inside an agentic action graph trace, then produces validation
feedback.

Specter is decoupled from Dullahan. Dullahan can produce the `action_graph.json`
trace, but Specter owns the validation, localization, feedback-plan, and hooked
inference workflow as a standalone tool.

The distinctive idea is to avoid relying only on more prompt text. Specter uses
TransformerLens to identify the layer and token position where debate-summary
feedback activates inside the expert SLM, then reruns inference with feedback
injected at that residual-stream location. The goal is sharper control over the
model's inference step than contextual feedback that can dilute inside the
model's existing context.

```text
Dullahan action graph or compatible trace
  -> courtroom validation
  -> TransformerLens localization
  -> feedback plan
  -> activation hooks
  -> steered expert inference
```

## Install

From the Specter repository root:

```bash
python -m pip install -e ".[dev]"
```

For real TransformerLens localization and hooked inference:

```bash
python -m pip install -e ".[dev,transformerlens]"
```

This installs:

```bash
specter-courtroom
specter-localize-feedback
specter-apply-feedback
specter-run-feedback-hooks
```

## Automatic Graphify Snapshot Publishing

Specter can extend Graphify's asynchronous post-commit rebuild so successful
source commits are followed by a separate generated snapshot commit and a
normal push to the current branch's configured upstream.

Install Graphify's hook first, then patch it with the repository-owned
extension:

```bash
graphify hook install
python scripts/install_graphify_auto_publish.py
```

The extension waits for `_rebuild_code(...)` to succeed, then runs
`scripts/publish_graphify_snapshot.py` with Graphify's Python interpreter. The
publisher commits only durable `graphify-out/` changes as
`chore: Refresh Graphify snapshot`. It refuses detached HEAD, branches without
an upstream, concurrent publisher runs, and manually staged Graphify files.
Unrelated staged work is left staged.

Machine-local query state, reflections, dated backups, rebuild locks, and the
mtime-based `cache/stat-index.json` are excluded. A rejected push leaves the
snapshot commit locally for manual resolution and retry.

Graphify owns the base hook and may replace it during installation or upgrade.
Rerun the repository installer after either operation:

```bash
python scripts/install_graphify_auto_publish.py
```

## Input Contract

Specter consumes Dullahan-compatible action graphs:

```text
memory/executions/<trace_id>/action_graph.json
```

The expected schema is:

```json
{
  "schema": "dullahan.action_graph.v1",
  "trace_id": "trace:...",
  "root_query_id": "query:...",
  "nodes": [],
  "edges": []
}
```

Each answered node becomes a validation target. Specter also reads parent and
child edge metadata so it can validate both responses and query delegations.

## Run The Full Pipeline

### 1. Generate Courtroom Feedback

```bash
specter-courtroom /path/to/Dullahan/memory/executions/<trace_id>/action_graph.json \
  --repo-root /Users/mhamzah/Documents/Specter \
  --rounds 3 \
  --contentions 8 \
  --persist
```

By default, courtroom roles are deterministic so the pipeline can run locally.
To use an OpenAI-compatible endpoint for defender, prosecutor, judge, and court
reporter roles:

```bash
specter-courtroom /path/to/action_graph.json \
  --repo-root /Users/mhamzah/Documents/Specter \
  --courtroom-model-provider http \
  --courtroom-model-base-url http://127.0.0.1:30000/v1 \
  --persist
```

Output:

```text
memory/feedback/<feedback_id>/
  manifest.yaml
  final_feedback.yaml
  targets/<query_id>/
```

### 2. Localize Feedback

Fast deterministic local path:

```bash
specter-localize-feedback memory/feedback/<feedback_id> \
  --backend deterministic \
  --contrast-pairs 8
```

Real TransformerLens path:

```bash
specter-localize-feedback memory/feedback/<feedback_id> \
  --backend transformerlens \
  --model-path <expert-model> \
  --contrast-pairs 32
```

Output:

```text
memory/feedback/<feedback_id>/activation_localizations.yaml
memory/feedback/<feedback_id>/activation_heatmaps/
memory/feedback/<feedback_id>/feedback_plan.json
memory/feedback/<feedback_id>/steering_vectors/
```

### 3. Materialize Activation Hooks

```bash
specter-apply-feedback memory/feedback/<feedback_id>/feedback_plan.json \
  --mode activation-hook
```

For each item:

```text
scaled_vector = direction_vector * prosecution_strength * feedback_scale
```

Output:

```text
memory/feedback/<feedback_id>/applied/<application_id>/
  activation_hooks.json
  manifest.yaml
```

### 4. Rerun Expert Inference With Hooks

```bash
specter-run-feedback-hooks \
  memory/feedback/<feedback_id>/applied/<application_id>/activation_hooks.json \
  --model-path <expert-model> \
  --expert-id expert:cluster-1 \
  --prompt "Assess the deployment risk"
```

Specter loads the hook specs, filters by expert when requested, and injects each
scaled vector into the configured residual-stream hook point during generation.

## Why Specter Is Separate From Dullahan

| Responsibility | Dullahan | Specter |
| --- | --- | --- |
| Build graph memory | Yes | No |
| Route subqueries to experts | Yes | No |
| Persist action graph traces | Yes | Consumes them |
| Debate expert responses | No | Yes |
| Validate query delegations | No | Yes |
| Produce feedback plans | No | Yes |
| Localize feedback with TransformerLens | No | Yes |
| Rerun hooked expert inference | No | Yes |

This split lets any system that can emit a Dullahan-style action graph use
Specter as a validation and steering layer.

## Ideal Use Cases

| Use case | Why Specter fits |
| --- | --- |
| Expert SLM validation | Tests whether specialist responses are grounded, complete, and properly delegated. |
| Agent trace auditing | Turns query/subquery graph nodes into inspectable validation targets. |
| Query delegation review | Checks whether child subqueries preserve parent intent and constraints. |
| Model-steering research | Produces layer/token localizations, heatmaps, vectors, and hook specs. |
| Training/eval data generation | Emits structured YAML/JSON artifacts for distillation, evals, and regressions. |
| Domain expert governance | Lets teams validate specialized agents in code, infrastructure, legal, research, support, or finance workflows. |

## Comparison

| Framework / Pattern | Primary focus | Specter difference |
| --- | --- | --- |
| LangGraph | Building graph-shaped agent workflows. | Specter validates completed graph traces and steers expert inference from feedback. |
| AutoGen-style multi-agent chat | Agent conversation for task solving. | Specter uses debate as a validation protocol over persisted trace nodes. |
| CrewAI-style role teams | Declarative role collaboration. | Specter applies prosecutor/defender/judge roles to audit expert outputs. |
| Basic critique loops | Textual critique and revision. | Specter turns critique into activation localizations and hook specs. |
| Representation engineering / CAA | Steering vectors from contrast sets. | Specter derives contrast targets from actual debate summaries tied to trace nodes. |
| Workflow orchestrators | Reliable predefined execution. | Specter evaluates whether the executed graph and delegations were good. |

## Scalability

| Axis | Current mechanism | Scaling path |
| --- | --- | --- |
| Validation volume | Filesystem artifacts under `memory/feedback`. | Batch jobs, queues, and parallel courtroom workers. |
| Model-backed courtroom roles | OpenAI-compatible HTTP provider. | Dedicated role-model serving pools. |
| Activation localization | TransformerLens over compatible models. | GPU workers, cached activations, offline heatmap/vector stores. |
| Hooked inference | Runtime activation hooks. | Expert-specific inference wrappers or model-serving integrations. |
| Artifact storage | YAML/JSON files. | S3/object storage and metadata DBs. |
| Observability | Persisted artifacts. | OpenTelemetry, Prometheus, Grafana, and trace stores. |

## Domain Adaptation

Specter can become domain-specific by learning from repeated validation traces:

1. Collect action graphs from a domain agent system.
2. Run courtroom validation over responses and delegations.
3. Localize debate-summary feedback with TransformerLens.
4. Apply reversible hooks for controlled inference experiments.
5. Distill high-quality debates, feedback plans, and steering outcomes into
   adapters, specialist SLMs, or expert policies.

| Domain | What Specter Validates |
| --- | --- |
| Code intelligence | Incorrect ownership assumptions, missing dependencies, shallow code context. |
| Cloud operations | Unsafe IAM boundaries, brittle rollout plans, unhandled failure modes. |
| Legal/policy review | Unsupported claims, missing exceptions, weak citation grounding. |
| Biomedical research | Dataset mismatch, overstated conclusions, missing methods caveats. |
| Financial research | Hidden assumptions, ignored downside scenarios, weak evidence. |
| Customer support | Incorrect escalation, missing account constraints, overconfident resolutions. |

## Development

Run tests:

```bash
pytest
```

Run only Specter tests:

```bash
pytest tests -q
```

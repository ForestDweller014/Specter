# Specter

Specter is an experimental validation and model-steering pipeline for specialist
language models working inside agent systems. Those systems can produce answers
that sound convincing while missing evidence, losing constraints during
delegation, or hiding uncertainty behind fluent prose. An execution trace can
show what happened, but it does not tell you whether the result deserved to be
trusted.

Specter turns that completed trace into a structured review. It gives each
answer and delegation a courtroom-style challenge, preserves the strongest
criticism as a feedback concept, and then asks the original model where that
concept appears in its internal activations. The result is a reversible steering
intervention that can be tested without retraining or permanently changing the
model.

The larger idea is to close the gap between auditing an agent and improving its
next inference. Specter does not stop at producing another critique document. It
turns the critique into an inspectable experiment: what was challenged, which
argument survived, where the model represented it, what vector was applied, and
how the model answered afterward.

## Quickstart: From An Agent Trace To A Steered Answer

The sequence below starts with a completed action graph and ends with a new model
response generated under reversible feedback hooks. The courtroom needs a text
generation endpoint. You can use the OpenAI API or another hosted
OpenAI-compatible service. The
[Dullahan](https://github.com/ForestDweller014/Dullahan) inference module is
simply the local, self-hosted alternative for those same courtroom calls: it
runs open-weight models through Ollama or vLLM and exposes an OpenAI-compatible
completion interface. Dullahan inference is not a separate feedback mechanism
and is not used for activation analysis, which still requires a
TransformerLens-compatible copy of the expert model.

### 1. Install Specter

From the repository root:

```bash
python -m pip install -e ".[dev,transformerlens]"
```

This installs four commands:

```text
specter-courtroom
specter-localize-feedback
specter-apply-feedback
specter-run-feedback-hooks
```

### 2. Point Specter At A Completed Action Graph

Specter expects a persisted graph whose nodes contain the query, supplied
context, expert response, and routing metadata. The broader Dullahan agent system
produces this file when a run uses `--persist-artifacts`, but any system can emit
the same simple contract.

```bash
export ACTION_GRAPH="/absolute/path/to/memory/executions/<trace_id>/action_graph.json"
```

At minimum, the document identifies the trace and its root query and provides
the graph's nodes and parent-to-child delegation edges:

```json
{
  "schema": "dullahan.action_graph.v1",
  "trace_id": "trace:...",
  "root_query_id": "query:...",
  "nodes": [],
  "edges": []
}
```

Each answered node becomes a separate validation target. Parent and child edges
let Specter review not only what an expert answered, but whether the delegated
question preserved the original task.

### 3. Run The Courtroom

For the recommended self-hosted route, clone Dullahan separately and install it
in the same Python environment as Specter. Then install Ollama and make the
configured model available:

```bash
cd ~/Documents/Dullahan
python -m pip install -e ".[dev]"
```

Keep `ollama serve` running in its own terminal:

```bash
ollama pull qwen3:8b
ollama serve
```

Then ask Specter to start Dullahan's inference proxy for the duration of the
courtroom run:

```bash
cd /absolute/path/to/Specter

specter-courtroom "$ACTION_GRAPH" \
  --repo-root "$PWD" \
  --rounds 1 \
  --contentions 1 \
  --start-dullahan-inference \
  --dullahan-repo-root ~/Documents/Dullahan \
  --persist
```

Start with one contention and one round to verify the complete path without
paying for dozens of model calls per target. Increase both only after inspecting
the first courtroom artifacts.

The command prints the generated feedback ID and artifact directory. Save that
path for the next stage:

```bash
export FEEDBACK_DIR="/absolute/path/to/Specter/memory/feedback/<feedback_id>"
```

If Dullahan inference is already running, omit
`--start-dullahan-inference`. To use the OpenAI API or another hosted
OpenAI-compatible endpoint instead of self-hosted Dullahan:

```bash
specter-courtroom "$ACTION_GRAPH" \
  --repo-root "$PWD" \
  --rounds 1 \
  --contentions 1 \
  --courtroom-model-provider openai-compatible \
  --courtroom-model-base-url https://api.openai.com/v1 \
  --courtroom-model "your-completion-model" \
  --courtroom-api-key-env OPENAI_API_KEY \
  --persist
```

### 4. Find The Feedback Inside The Expert Model

The courtroom produces language. This stage turns that language into a measured
activation direction. Use a TransformerLens-compatible model that matches the
expert architecture being studied:

```bash
export EXPERT_MODEL="your-transformerlens-compatible-model"

specter-localize-feedback "$FEEDBACK_DIR" \
  --model-path "$EXPERT_MODEL" \
  --contrast-pairs 1 \
  --n-layers 12
```

Specter compares each judge-generated feedback instruction with a topic-matched
neutral text, runs both through the model, and records the layer and token
position where the activation difference is strongest. It writes the heatmap,
steering vector, and `feedback_plan.json` into the same feedback directory.

### 5. Turn The Plan Into Reversible Hooks

```bash
specter-apply-feedback "$FEEDBACK_DIR/feedback_plan.json"
```

The command scales each steering vector by the judge's prosecution-strength
score and the configured feedback scale. It prints an application directory
containing `activation_hooks.json`:

```bash
export HOOKS="$FEEDBACK_DIR/applied/<application_id>/activation_hooks.json"
```

### 6. Rerun The Expert With Feedback Applied

```bash
specter-run-feedback-hooks "$HOOKS" \
  --model-path "$EXPERT_MODEL" \
  --expert-id "<expert-id-from-feedback>" \
  --prompt "Assess the deployment risk" \
  --max-new-tokens 128
```

This generation uses the same model with temporary residual-stream hooks. The
weights are unchanged when the process exits. Compare this output with the
unsteered baseline to determine whether the intervention improved the answer;
Specter does not currently make that quality judgment automatically.

## Tech Stack

| Category | Tools |
| --- | --- |
| Runtime and commands | Python, CLI entrypoints |
| Courtroom inference | OpenAI-compatible API; Dullahan inference is the self-hosted alternative |
| Activation analysis | PyTorch, TransformerLens |
| Contracts and artifacts | Pydantic, JSON, YAML |
| Architecture documentation | Mermaid |
| Validation | pytest, real local-inference integration tests |

## Architecture

The first view shows the whole journey. The next two open the courtroom and the
activation-steering stages without changing the story.

Every diagram uses the same palette: **purple** for validation, **teal** for
activation discovery, **orange** for feedback application, **red** for model
inference, **gold** for persisted evidence, and **slate** for external inputs and
outputs.

Multi-line nodes also share one internal hierarchy: the **bold first line** is
the module, service, artifact, or decision name; the *italic second line* labels
the information below it; and bullets identify its inputs, outputs,
capabilities, policies, interfaces, or stored data.

```mermaid
flowchart TD
    Trace["<b>Completed action graph</b><br/><i>Contents</i><br/>• Queries<br/>• Context<br/>• Responses<br/>• Delegations"] --> Loader["<b>Trace loader</b><br/><i>Purpose</i><br/>• Create one case per answered node"]
    Loader --> Courtroom["<b>Courtroom validation</b><br/><i>Purpose</i><br/>• Challenge and judge each case"]
    Courtroom --> Feedback["<b>Feedback items</b><br/><i>Contents</i><br/>• Judge-generated feedback<br/>• Prosecution strength"]
    Feedback --> Contrast["<b>Contrast constructor</b><br/><i>Purpose</i><br/>• Build feedback and neutral examples"]
    Contrast --> Localization["<b>TransformerLens localizer</b><br/><i>Outputs</i><br/>• Layer and token<br/>• Heatmap<br/>• Direction"]
    Localization --> Plan["<b>Feedback plan</b><br/><i>Purpose</i><br/>• Record the intervention recipe"]
    Plan --> Hooks["<b>Activation hooks</b><br/><i>Output</i><br/>• Scaled steering vectors"]
    Hooks --> Rerun["<b>Steered inference</b><br/><i>Operation</i><br/>• Generate with temporary feedback"]

    CourtroomModel["<b>Courtroom model</b><br/><i>Hosting</i><br/>• OpenAI-compatible API<br/>• Self-hosted Dullahan alternative"] --> Courtroom
    ExpertModel["<b>Expert model</b><br/><i>Runtime</i><br/>• TransformerLens-compatible model"] --> Localization
    ExpertModel --> Rerun

    Courtroom --> Evidence["<b>Experiment artifacts</b><br/><i>Contents</i><br/>• Feedback<br/>• Localization<br/>• Hook evidence"]
    Localization --> Evidence
    Hooks --> Evidence
    Rerun --> Result["<b>Steered response</b><br/><i>Result</i><br/>• Ready for baseline comparison"]

    class Trace,Result external
    class Loader,Courtroom,Feedback validation
    class Contrast,Localization teal
    class Plan,Hooks application
    class CourtroomModel,ExpertModel,Rerun inference
    class Evidence memory

    classDef external fill:#475569,stroke:#1E293B,color:#FFFFFF
    classDef validation fill:#6D28D9,stroke:#4C1D95,color:#FFFFFF
    classDef teal fill:#0F766E,stroke:#115E59,color:#FFFFFF
    classDef application fill:#C2410C,stroke:#9A3412,color:#FFFFFF
    classDef inference fill:#B91C1C,stroke:#7F1D1D,color:#FFFFFF
    classDef memory fill:#A16207,stroke:#713F12,color:#FFFFFF
```

### Courtroom Validation

The courtroom is designed to make disagreement explicit before anyone tries to
change the model. A contention generator identifies concrete ways an answer or
delegation may have failed. The defender protects valid reasoning; the
prosecutor tests that defense; the judge records which side is stronger; and the
reporter compresses the state so later rounds can build on it without carrying
an ever-growing transcript. Once the rounds end, a final feedback judge reads
that summary together with every round's score and rationale, then writes the
model-facing correction that the rest of the pipeline uses.

These roles are separate prompts sent through real inference. They are
role-conditioned views of the case, not hard-coded verdicts. Every contention
keeps its identity across rounds, which makes the final criticism traceable back
to the exact target and argument that produced it.

```mermaid
flowchart TB
    Target["<b>Validation target</b><br/><i>Contents</i><br/>• Query<br/>• Context<br/>• Response<br/>• Delegation"] --> Generate["<b>Contention generator</b><br/><i>Purpose</i><br/>• Identify testable failures"]
    Generate --> Contention["<b>Contention</b><br/><i>Output</i><br/>• One bounded validation claim"]
    Contention --> Defender["<b>Defender</b><br/><i>Purpose</i><br/>• Protect supported reasoning"]
    Defender --> Prosecutor["<b>Prosecutor</b><br/><i>Purpose</i><br/>• Challenge and sharpen the claim"]
    Prosecutor --> Judge["<b>Judge</b><br/><i>Purpose</i><br/>• Score the prosecution's case"]
    Judge --> Reporter["<b>Court reporter</b><br/><i>Purpose</i><br/>• Preserve the surviving argument"]
    Judge --> Evaluations["<b>Evaluation history</b><br/><i>Contents</i><br/>• Round scores<br/>• Rationales"]
    Reporter --> More{"<b>Continue debate?</b><br/><i>Decision</i><br/>• Run another round"}
    More -->|"yes"| Revise["<b>Contention revision</b><br/><i>Purpose</i><br/>• Refine the same validation claim"]
    Revise --> Defender
    More -->|"no"| FinalJudge["<b>Final feedback judge</b><br/><i>Purpose</i><br/>• Turn the record into a model-facing correction"]
    Evaluations --> FinalJudge
    FinalJudge --> Item["<b>Feedback item</b><br/><i>Contents</i><br/>• Generated feedback<br/>• Judge strength"]

    Provider["<b>Completion provider</b><br/><i>Hosting</i><br/>• OpenAI-compatible API<br/>• Self-hosted Dullahan alternative"] --> Generate
    Provider --> Defender
    Provider --> Prosecutor
    Provider --> Judge
    Provider --> Reporter
    Provider --> Revise
    Provider --> FinalJudge

    class Target external
    class Generate,Contention,Defender,Prosecutor,Judge,Reporter,Evaluations,More,Revise,FinalJudge,Item validation
    class Provider inference

    classDef external fill:#475569,stroke:#1E293B,color:#FFFFFF
    classDef validation fill:#6D28D9,stroke:#4C1D95,color:#FFFFFF
    classDef inference fill:#B91C1C,stroke:#7F1D1D,color:#FFFFFF
```

### Activation Localization And Feedback Application

The second half asks a different question: if the final judge's feedback
expresses the correction we want the expert to follow, where does that
distinction appear inside the expert model? Specter treats the generated
feedback as a positive example and a neutral description of the same query,
context, and response as the negative example. TransformerLens measures their
residual-stream difference rather than guessing a layer from a hash or a rule.

The strongest normalized direction becomes a steering vector. The feedback plan
keeps that vector separate from the policy that applies it, so a reviewer can
change the scale, select an expert, or discard an intervention without repeating
the courtroom.

```mermaid
flowchart TB
    Feedback["<b>Judge-generated feedback</b><br/><i>Input</i><br/>• Positive correction text"] --> Pairs["<b>Contrast-pair builder</b><br/><i>Purpose</i><br/>• Create positive and neutral examples"]
    Case["<b>Original case</b><br/><i>Contents</i><br/>• Query<br/>• Context<br/>• Response"] --> Neutral["<b>Neutral example</b><br/><i>Method</i><br/>• Deterministic topic matching"]
    Neutral --> Pairs
    Pairs --> Cache["<b>Activation cache</b><br/><i>Operation</i><br/>• Record expert residual activations"]
    Cache --> Difference["<b>Activation comparison</b><br/><i>Calculation</i><br/>• Positive minus neutral<br/>• Compare by layer and token"]
    Difference --> Heatmap["<b>Activation heatmap</b><br/><i>Output</i><br/>• Separation score by layer and token"]
    Difference --> Direction["<b>Steering direction</b><br/><i>Output</i><br/>• Normalized activation vector"]
    Heatmap --> Select["<b>Localization selector</b><br/><i>Output</i><br/>• Strongest layer and token"]
    Direction --> Plan["<b>Feedback plan</b><br/><i>Purpose</i><br/>• Record the intervention recipe"]
    Select --> Plan
    Strength["<b>Judge score</b><br/><i>Signal</i><br/>• Prosecution strength"] --> Plan
    Plan --> Scale["<b>Vector scaling</b><br/><i>Calculation</i><br/>• Judge strength × feedback scale"]
    Scale --> Hook["<b>Activation hook</b><br/><i>Output</i><br/>• Residual-stream intervention"]
    Hook --> Model["<b>Expert generation</b><br/><i>Operation</i><br/>• Run with temporary hooks"]
    Model --> Output["<b>Steered response</b><br/><i>Result</i><br/>• Ready for baseline comparison"]

    class Feedback,Case external
    class Pairs,Neutral,Cache,Difference,Heatmap,Direction,Select teal
    class Plan,Strength,Scale,Hook application
    class Model inference
    class Output memory

    classDef external fill:#475569,stroke:#1E293B,color:#FFFFFF
    classDef teal fill:#0F766E,stroke:#115E59,color:#FFFFFF
    classDef application fill:#C2410C,stroke:#9A3412,color:#FFFFFF
    classDef inference fill:#B91C1C,stroke:#7F1D1D,color:#FFFFFF
    classDef memory fill:#A16207,stroke:#713F12,color:#FFFFFF
```

## From A Recorded Trace To Reversible Feedback

Specter's architectural bet is that validation becomes more useful when it can
travel all the way from a human-readable argument to a controlled change in
model behavior. Each module exists to preserve one part of that journey without
collapsing the entire experiment into an opaque model call.

### The trace turns a completed run into a case file

The process begins after an agent system has answered. `graph_loader` reads the
action graph and turns every answered node into a `FeedbackTargetNode`. The
target preserves the original query, the context the expert saw, its response,
its model and expert identity, and the edges that explain who delegated work to
whom.

That boundary matters because failures in an agent system are not confined to
the final prose. A specialist may answer its local question well while the
delegated question itself has drifted away from the parent's intent. By keeping
the trace structure, Specter can challenge both the response and the decision
that created it.

### The courtroom turns vague doubt into explicit claims

`courtroom` treats each target as a case rather than asking one model for a
generic critique. The contention generator proposes bounded, evidence-specific
claims. The debate runner carries each claim through defense, prosecution,
judgment, and reporting for the configured number of rounds. The judge contributes
a signed strength score, while the reporter maintains a compact narrative of
what survived.

This separation solves two problems. First, a criticism has to survive an
adversarial defense before it influences the model. Second, the artifacts retain
the reasoning trail, so a high score is never the only explanation available to
a reviewer.

### The final judge turns the debate record into feedback

At the end of the final round, Specter stores one `FeedbackItem` per contention.
Before creating that item, the final feedback judge reads the reporter's final
summary and the score and rationale from every debate round. It produces one
concise, evidence-grounded instruction describing what the expert should change.
The item retains the summary as provenance, stores the generated instruction as
`feedback_text`, and keeps the latest prosecution-strength score as the
intervention's eventual magnitude.

This separation gives the reporter and judge distinct jobs. The reporter
preserves what happened in the debate; it does not decide the correction. The
final judge converts the whole record into focused model-facing feedback, without
courtroom rhetoric, procedural language, or numeric scores. Only that generated
feedback enters activation discovery.

### Contrast construction creates a measurable question

`activation/contrast_set_builder` pairs the judge-generated feedback with a
neutral description of the same query, the first context sentence, and the first
response sentence. The negative text is deterministic, not LLM-generated. This
makes a localization run cheap and reproducible, and it keeps the original topic
present while removing the explicit correction signal.

It is also the most deliberately simple part of the current research pipeline.
The positive examples repeat the same feedback instruction, and negative
variants differ mainly by an index. The pair is topic-matched, but it is not a
rigorously controlled linguistic minimal pair. That limitation is visible in
the stored metadata rather than hidden behind a claim that the contrast set is
learned.

### TransformerLens finds where the distinction appears

`TransformerLensActivationLocator` runs every positive and negative text through
the real expert model and caches its residual activations. At each inspected
layer, it measures the average positive-minus-negative direction and asks where
that direction separates the two groups most strongly across token positions.

The output is a heatmap, a selected layer and token, a normalized direction
vector, and an evidence score. This is activation measurement, not another LLM
opinion. It identifies a promising intervention point, although a strong
projection should still be treated as experimental evidence rather than proof
that the direction is uniquely causal.

### The feedback plan separates discovery from intervention

`feedback/plan_builder` turns each localization into a small, portable recipe.
The plan records which contention and expert it belongs to, where the hook
should run, which vector file to load, the judge's strength, and the configured
feedback scale.

Keeping this plan outside the model is what makes the workflow reviewable. A
team can inspect the courtroom, replace a questionable contrast set, change the
scale, or reject a localization before anything touches inference. Discovery
and application are separate decisions.

### Hooked inference tests the correction without retraining

`feedback/apply_runtime` loads the vector and scales it by prosecution strength
and feedback scale. It writes an explicit hook specification instead of
modifying weights. `TransformerLensHookRunner` then adds the vector at the
selected residual-stream location while the expert generates a new answer.

The intervention lasts only for that run. This makes Specter useful as a
research and evaluation loop: compare baseline and steered behavior, adjust or
remove the hook, and preserve exactly what changed. If the result is promising,
the accumulated artifacts can later inform a more durable training or adapter
strategy; Specter itself does not perform that training.

### Persisted artifacts make the experiment auditable

Every stage writes human-readable or machine-readable evidence under
`memory/feedback/<feedback_id>/`. The filesystem is the handoff between
courtroom review, activation discovery, intervention design, and generation, so
no stage depends on an invisible in-memory conversation.

```text
memory/feedback/<feedback_id>/
  manifest.yaml
  final_feedback.yaml
  targets/<query_id>/
    target.yaml
    contentions.yaml
    rounds.yaml
    debate_summaries.yaml
    judge_scores.yaml
    final_feedback.yaml
  activation_localizations.yaml
  activation_heatmaps/
  steering_vectors/
  feedback_plan.json
  applied/<application_id>/
    activation_hooks.json
    manifest.yaml
```

| Artifact | Purpose |
| --- | --- |
| `final_feedback.yaml` | Generated feedback, source summary, and judge strength for every validated contention |
| `targets/<query_id>/` | Complete case record: target, contentions, rounds, summaries, and scores |
| `activation_localizations.yaml` | Selected expert, layer, token, projection strength, and confidence |
| `activation_heatmaps/` | Layer-by-token evidence used to inspect the localization |
| `steering_vectors/` | Direction vectors derived from real expert-model activations |
| `feedback_plan.json` | Reviewable recipe connecting courtroom evidence to an intervention |
| `activation_hooks.json` | Fully materialized, reversible hooks used during generation |

## Where Specter Fits

Specter is most useful when a team already has structured agent traces and wants
to investigate whether specialist models can be corrected more precisely than
with another block of prompt text. It supports expert-response auditing,
delegation review, activation-steering research, and the creation of structured
evaluation evidence.

It is not currently a production safety gate, a model trainer, or an automatic
proof that a steered answer is better. It requires real courtroom inference and
a local TransformerLens-compatible expert model. Its contrast construction and
confidence scoring are intentionally visible research choices that should be
evaluated against the behavior of the model being studied.

## Development

Run the complete test suite:

```bash
pytest
```

Run the real local courtroom integration when Ollama and Dullahan's configured
model are available:

```bash
SPECTER_RUN_LOCAL_INFERENCE=1 \
DULLAHAN_REPO_ROOT=~/Documents/Dullahan \
pytest tests/test_real_inference.py::test_dullahan_inference_executes_every_courtroom_role -v
```

Set `SPECTER_TRANSFORMERLENS_MODEL` to a compatible model and run the complete
integration module to include real activation localization:

```bash
SPECTER_RUN_LOCAL_INFERENCE=1 \
DULLAHAN_REPO_ROOT=~/Documents/Dullahan \
SPECTER_TRANSFORMERLENS_MODEL="your-transformerlens-compatible-model" \
pytest tests/test_real_inference.py -m local_inference -v
```

## License

Specter is licensed under the [Apache License 2.0](LICENSE).

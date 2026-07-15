# Specter inference-correction benchmark bug log

This log records failures reproduced while bringing
`specter_inference_correction_benchmark.ipynb` to a clean headless run. Entries
distinguish the observed symptom, confirmed cause, fix, and validation evidence.

## B-001 — Dullahan console script could not import its package

- **Symptom:** `dullahan-inference` exited before its health check with
  `ModuleNotFoundError: dullahan_inference`.
- **Cause:** the Anaconda Python used by Dullahan skips hidden `.pth` files, so
  setuptools' `__editable__.dullahan-0.1.0.pth` never installed its source
  finder even though the mapping itself was correct.
- **Fix:** the notebook launches Dullahan's own console script with
  `apps/inference/src` explicitly prepended to `PYTHONPATH`.
- **Validation:** the console script produced a valid Ollama/Metal plan and a
  live server returned HTTP 200 from `/health`.

## B-002 — Notebook ran under the Anaconda kernel

- **Symptom:** the first cell reported
  `/opt/homebrew/anaconda3/bin/python` and could not find TransformerLens.
- **Cause:** the notebook used a generic `python3` kernelspec, allowing VS Code
  to retain the global Anaconda interpreter.
- **Fix:** register and pin the `specter-benchmark` kernel backed by
  `Specter/.venv/bin/python`; add an early interpreter/dependency preflight.
- **Validation:** notebook metadata resolves to `Specter Benchmark (.venv)` and
  the installed kernel points at the Specter virtual environment.

## B-003 — TransformerLens optional dependencies were not installed

- **Symptom:** `TransformerLensUnavailableError` with missing
  `transformer_lens`.
- **Cause:** the notebook extra was installed without the separate
  `transformerlens` extra.
- **Fix:** declare the notebook dependencies and synchronize both extras.
- **Validation:** `torch 2.13.0`, `transformer-lens 3.5.1`, and
  `HookedTransformer` import successfully in the benchmark environment.

## B-004 — Invalid cached Hugging Face token broke a public download

- **Symptom:** loading `Qwen/Qwen3-8B` returned HTTP 401.
- **Cause:** Hugging Face Hub implicitly sent an expired cached token. The same
  public `config.json` returned HTTP 200 anonymously.
- **Fix:** `TransformerLensAdapter` can temporarily disable implicit Hub
  credentials and opt into the official Qwen remote model code without
  deleting or overwriting global credentials.
- **Validation:** TransformerLens resolves the real public Qwen configuration
  anonymously as `Qwen3ForCausalLM` with 36 layers and width 4096.

## B-005 — Direct `token=False` conflicts inside TransformerLens 3.5

- **Symptom:** `AutoConfig.from_pretrained()` received duplicate `token`
  keyword arguments during the first attempted anonymous fix.
- **Cause:** TransformerLens 3.5 supplies its own `token=` argument internally
  and forwards arbitrary loader keyword arguments to the same call.
- **Fix:** disable Hugging Face's implicit-token behavior for the duration of
  the load instead of forwarding `token=False` through TransformerLens.
- **Validation:** targeted adapter regression test passes and the real Qwen
  configuration resolver completes without a 401 or duplicate argument.

## B-006 — Notebook progress integration warning

- **Symptom:** `TqdmWarning: IProgress not found`.
- **Cause:** the notebook environment omitted `ipywidgets`.
- **Fix:** include `ipywidgets` in the notebook extra.
- **Validation:** the synchronized environment contains the Jupyter widget
  packages.

## Active execution findings

New failures discovered by headless smoke/default execution are appended below.

## B-007 — Two 8B runtimes plus float32 weights exceed host memory

- **Symptom:** the first headless smoke run drove swap to 12.4 GB of 13.3 GB
  while Ollama held a 5.6 GB Qwen model and Hugging Face was still downloading
  the second 8B checkpoint. TransformerLens had not yet materialized its default
  float32 weights.
- **Cause:** the notebook warmed the Ollama 8B endpoint and then attempted to
  load an independent 8B TransformerLens model in float32 on a 19.3 GB
  unified-memory Mac. The two weight sets alone exceed safe available memory.
- **Fix:** use the 1.7B Qwen3 checkpoint for both paired timed arms by default,
  load it in float16, and retain `qwen3:8b` only for the Dullahan courtroom.
  `SPECTER_HOOK_MODEL` remains available for larger machines that can run a
  larger instrumented checkpoint.
- **Validation:** reducing the instrumented checkpoint avoided the original
  float32 estimate but exposed an additional conversion-copy issue (B-008).

## B-008 — TransformerLens processing clones reduced-precision weights

- **Symptom:** even an isolated 1.7B float16 load expanded swap above 20 GB and
  stalled in `ProcessWeights.fold_value_biases()`.
- **Cause:** `HookedTransformer.from_pretrained()` applies centering/folding
  transforms and clones the full state dictionary. TransformerLens warns that
  this processing path is inappropriate for reduced-precision loads.
- **Fix:** add an adapter option for
  `HookedTransformer.from_pretrained_no_processing()` and use it for the
  benchmark's float16 model.
- **Validation:** isolated no-processing load completed in 17 seconds; the next
  full run exposed device selection B-009.

## B-009 — TransformerLens silently selected CPU on an MPS host

- **Symptom:** smoke attempt 3 emitted a float16-on-CPU warning and spent the
  calibration stage at roughly 98% CPU without completing a 900-token answer.
- **Cause:** the adapter left `device=None`; TransformerLens selected CPU even
  though `torch.backends.mps.is_available()` returned true.
- **Fix:** add explicit device forwarding to the adapter and select MPS first,
  then CUDA, then CPU in the notebook.
- **Validation:** isolated MPS load completed in 18 seconds and a five-token
  generation completed in 7 seconds. Smoke uses an explicit MPS opt-in and a
  bounded 192-token answer budget; the generic TransformerLens MPS correctness
  caveat remains an experimental limitation.

## B-010 — Answer export printed a bound Pandas method

- **Symptom:** headings in `answers.md` contained
  `<bound method NDFrame.sample ...>` instead of the integer sample index.
- **Cause:** attribute access (`item.sample`) collided with `Series.sample()`.
- **Fix:** use key access (`item["sample"]`) for the exported sample field.
- **Validation:** attempt 6 exported integer `sample 0` headings for both arms.

## B-011 — Raw Qwen prompt produced document continuation, not an answer

- **Symptom:** both smoke answers began with an invented question `(4)` and
  continued into a hallucinated `Document: 05_tax_code` rather than answering
  the three requested finance tasks.
- **Cause:** the benchmark passed a plain concatenated string to an instruction
  model without Qwen's chat template or generation marker.
- **Fix:** render matched system/user messages with the loaded Qwen tokenizer's
  chat template, add the generation prompt, and disable Qwen's thinking channel
  consistently with the Dullahan endpoint.
- **Validation:** chat-templated smoke produced a structured finance answer,
  but its decoded output exposed completion extraction B-012.

## B-012 — Decoded chat output leaked the prompt into scoring

- **Symptom:** attempt 5 reported 100% for both arms, 1,379 completion tokens
  despite a 192-token cap, and `answers.md` included the system message, all
  evidence documents, and the question before the actual answer.
- **Cause:** TransformerLens decodes chat special tokens away. The decoded
  string therefore did not start byte-for-byte with the templated prompt, so a
  simple `text.startswith(prompt)` check failed and retained the full prompt.
- **Fix:** after the exact-prefix fast path, split decoded chat generations at
  the final `assistant` role boundary and keep only the completion.
- **Validation:** attempt 6 stored only the assistant section and produced a
  genuine 40% rubric score. Inspection then exposed prompt-owned assistant
  prefill counted as output (B-013).

## B-013 — Qwen assistant prefill was counted as generated output

- **Symptom:** completion extraction no longer included the documents, but the
  evidence counted 196 completion tokens against a 192-token generation cap
  and retained an empty `<think>...</think>` block.
- **Cause:** Qwen's `enable_thinking=False` chat template still places an empty
  thinking block inside the assistant prompt. Splitting only at the decoded
  assistant role boundary retains that prompt-owned suffix.
- **Fix:** reconstruct the tokenizer-decoded prompt (the same representation
  returned by TransformerLens generation) and strip it before using the role
  boundary as a final compatibility fallback.
- **Validation:** attempt 7 completed all cells. Both arms saved exactly 192
  completion tokens, neither retained the thinking prefill, and the executed
  notebook contains no error output.

## B-014 — Pytest crashed in the environment's native `readline`

- **Symptom:** final adapter regression validation exited with signal 11 before
  collecting tests; `python -X faulthandler -m pytest --version` located the
  crash at pytest's early `import readline` workaround.
- **Cause:** the virtual environment's Python symlinks to the Homebrew Anaconda
  interpreter, whose native `readline` extension segfaults on import in this
  environment. This is independent of the notebook runtime.
- **Fix:** for validation only, preload an empty in-memory `readline` module;
  pytest imports it solely to attach libedit to the original stdio handles.
- **Validation:** `tests/test_transformerlens_adapter.py` collected and passed
  (`1 passed`) with plugin autoload unchanged.

## Final execution validation

- Clean smoke: `specter-smoke-attempt-7.ipynb`, 25/25 cells, two successful
  paired rows, no error outputs, and completion tokens exactly at the 192 cap.
- Exact default standard profile: `specter-standard.ipynb`, 25/25 cells,
  18/18 successful rows across all three cases and concurrency 1/2, no recorded
  run errors, and 318–320 completion tokens against the 320-token cap.
- Every corrected standard row recorded exactly one applied hook. All three
  case bundles contain the action graph, debate evidence, localization heatmap,
  steering vector, feedback plan, and applied hook artifact.
- The standard headline comparison, throughput plot, and three paired action
  diagrams rendered and were inspected after export.

## B-015 — VS Code selected uv's bare Python instead of the notebook kernel

- **Symptom:** VS Code reported that running cells with
  `cpython-3.12.13-macos-aarch64-none` required `ipykernel`.
- **Cause:** that path is uv's standalone base interpreter, not a project
  environment. It had no `ipykernel`, Torch, TransformerLens, or notebook
  dependencies. The previously registered project kernel worked, but VS Code's
  interpreter association overrode it.
- **Fix:** create `.venv-benchmark` from uv's CPython 3.12.13, install the
  project with `notebook`, `transformerlens`, and `dev` extras, register the
  distinct `specter-benchmark-uv` kernelspec, pin the notebook metadata to it,
  and set the workspace's default interpreter to the same environment.
- **Validation:** the new interpreter imports `ipykernel`, Torch, and
  TransformerLens; its kernelspec uses an absolute `.venv-benchmark` path.

## B-016 — Long benchmark cells appeared frozen

- **Symptom:** users could not distinguish slow inference from a stalled
  notebook because model loading, courtroom calls, localization, and generation
  blocked for minutes with no periodic output. Opening the notebook directly in
  VS Code also selected the hour-long standard profile by default.
- **Cause:** the notebook logged only after a complete case or wave, and a
  daemon heartbeat created in an earlier cell was not reliably associated with
  the currently executing Jupyter cell.
- **Fix:** use timestamped, flushed stage logs; execute each blocking operation
  in a monitored worker while the active cell polls it; emit a configurable
  `still running` message every 30 seconds; report operation timings and errors;
  and default an interactive launch to the smoke profile. The exact full run is
  still selected with `SPECTER_CFA_PROFILE=standard`.
- **Validation:** an end-to-end monitored smoke run completed without errors and
  placed 52 two-second test heartbeats in the correction/paired-run cells. A
  focused model-load run placed ten heartbeats in the model cell and completed
  in 20.7 seconds. The normal heartbeat interval remains 30 seconds.

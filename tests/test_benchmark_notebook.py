import json
from pathlib import Path


NOTEBOOK = (
    Path(__file__).resolve().parents[1]
    / "notebooks"
    / "specter_inference_correction_benchmark.ipynb"
)


def test_inference_correction_benchmark_has_live_progress_instrumentation():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    ids = [cell.get("id") for cell in cells]
    source = "\n".join(str(cell.get("source", "")) for cell in cells)

    assert notebook["metadata"]["kernelspec"]["name"] == "specter-benchmark-uv"
    assert ids.index("cell-progress-profile-default") < ids.index("cell-04")
    assert ids.index("cell-progress-model-monitor") < ids.index("cell-08")
    assert ids.index("cell-progress-correction-start") < ids.index("cell-12")
    assert ids.index("cell-progress-benchmark-start") < ids.index("cell-14")
    assert ids.index("cell-22") < ids.index("cell-progress-stop")

    assert 'os.environ["SPECTER_CFA_PROFILE"] = "smoke"' in source
    assert 'SPECTER_PROGRESS_INTERVAL_SECONDS' in source
    assert 'TransformerLens model load still running' not in source
    assert 'f"{operation} still running"' in source
    assert 'courtroom request started' in source
    assert 'generation started' in source
    assert 'activation localization started' in source
    assert 'BENCHMARK_PROGRESS_STOP.set()' in source

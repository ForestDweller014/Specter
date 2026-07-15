#!/usr/bin/env python3
"""Commit and push durable Graphify outputs without disturbing other work."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path, PurePosixPath


COMMIT_SUBJECT = "chore: Refresh Graphify snapshot"
COMMIT_BODY = (
    "- Persist durable graph, report, label, and analysis outputs\n"
    "- Keep generated architecture context synchronized with source changes"
)
OUTPUT_ROOT = PurePosixPath("graphify-out")
LOCAL_NAMES = {
    ".graphify_python",
    ".graphify_root",
    ".vocab.txt",
    ".graphify_learning.json",
    ".rebuild.lock",
    ".pending_changes",
}
LOCAL_DIRECTORIES = {"memory", "reflections", "backups"}
LOCAL_PATHS = {PurePosixPath("cache/stat-index.json")}
DURABLE_ROOT_FILES = {
    ".graphify_analysis.json",
    ".graphify_labels.json",
    ".graphify_labels.json.sig",
    "GRAPH_REPORT.md",
    "cypher.txt",
    "graph.graphml",
    "graph.html",
    "graph.json",
    "graph.svg",
    "manifest.json",
}
DATE_DIRECTORY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
QUERY_RESULT_TYPES = {"query", "path_query", "explain"}
QUERY_SOURCE_MARKERS = (
    "/graphify-out/memory/",
    "/graphify-out/reflections/",
)


class PublishError(RuntimeError):
    """A safe publishing precondition was not satisfied."""


def run_git(
    *args: str,
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise PublishError(f"git {' '.join(args)} failed: {detail}")
    return result


def nul_paths(result: subprocess.CompletedProcess[str]) -> list[PurePosixPath]:
    return [PurePosixPath(value) for value in result.stdout.split("\0") if value]


def repository_root() -> Path:
    return Path(run_git("rev-parse", "--show-toplevel").stdout.strip()).resolve()


def current_branch(root: Path) -> str:
    result = run_git("symbolic-ref", "--quiet", "--short", "HEAD", cwd=root, check=False)
    if result.returncode != 0 or not result.stdout.strip():
        raise PublishError("refusing to publish Graphify output from detached HEAD")
    return result.stdout.strip()


def configured_upstream(root: Path) -> str:
    result = run_git(
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
        cwd=root,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise PublishError("current branch has no configured upstream")
    return result.stdout.strip()


@contextmanager
def publisher_lock(root: Path):
    lock_path = Path(run_git("rev-parse", "--git-path", "graphify-auto-publish.lock", cwd=root).stdout.strip())
    if not lock_path.is_absolute():
        lock_path = root / lock_path
    try:
        lock_path.mkdir(parents=False)
    except FileExistsError as exc:
        raise PublishError(f"another Graphify publisher holds {lock_path}") from exc
    try:
        (lock_path / "owner").write_text(f"pid={os.getpid()}\n", encoding="utf-8")
        yield
    finally:
        (lock_path / "owner").unlink(missing_ok=True)
        lock_path.rmdir()


def relative_output_path(path: PurePosixPath) -> PurePosixPath | None:
    try:
        return path.relative_to(OUTPUT_ROOT)
    except ValueError:
        return None


def is_excluded(path: PurePosixPath) -> bool:
    relative = relative_output_path(path)
    if relative is None or not relative.parts:
        return True
    if relative in LOCAL_PATHS or relative.name in LOCAL_NAMES:
        return True
    if relative.parts[0] in LOCAL_DIRECTORIES:
        return True
    return any(DATE_DIRECTORY.fullmatch(part) for part in relative.parts)


def is_new_durable_output(path: PurePosixPath) -> bool:
    relative = relative_output_path(path)
    if relative is None or is_excluded(path):
        return False
    if len(relative.parts) == 1:
        return relative.name in DURABLE_ROOT_FILES
    return relative.parts[0] == "wiki" or relative.parts[:2] == ("cache", "ast")


def staged_graphify_paths(root: Path) -> list[PurePosixPath]:
    return nul_paths(
        run_git("diff", "--cached", "--name-only", "-z", "--", str(OUTPUT_ROOT), cwd=root)
    )


def durable_changes(root: Path) -> list[PurePosixPath]:
    tracked = set(
        nul_paths(run_git("ls-files", "-z", "--", str(OUTPUT_ROOT), cwd=root))
    )
    tracked_changes = nul_paths(
        run_git("diff", "--name-only", "-z", "HEAD", "--", str(OUTPUT_ROOT), cwd=root)
    )
    untracked = nul_paths(
        run_git(
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            str(OUTPUT_ROOT),
            cwd=root,
        )
    )
    candidates = {
        path for path in tracked_changes if path in tracked and not is_excluded(path)
    }
    candidates.update(path for path in untracked if is_new_durable_output(path))
    return sorted(candidates, key=str)


def ensure_structure_only_graph(root: Path) -> None:
    graph_path = root / OUTPUT_ROOT / "graph.json"
    if not graph_path.is_file():
        return

    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublishError(f"cannot validate {graph_path}: {exc}") from exc

    for node in graph.get("nodes", []):
        if not isinstance(node, dict):
            continue
        source = str(node.get("source_file", "")).replace("\\", "/")
        normalized_source = f"/{source.strip('/')}/"
        result_types = {
            str(node.get(key, "")).casefold()
            for key in ("query_type", "file_type", "type")
            if node.get(key)
        }
        if any(marker in normalized_source for marker in QUERY_SOURCE_MARKERS) or (
            result_types & QUERY_RESULT_TYPES
        ):
            raise PublishError(
                "refusing to publish Graphify query memory; rebuild with "
                "`graphify extract . --code-only`"
            )


def publish() -> int:
    root = repository_root()
    branch = current_branch(root)
    upstream = configured_upstream(root)

    with publisher_lock(root):
        manually_staged = staged_graphify_paths(root)
        if manually_staged:
            rendered = ", ".join(str(path) for path in manually_staged)
            raise PublishError(
                "refusing to overwrite manually staged Graphify files: " + rendered
            )

        paths = durable_changes(root)
        if not paths:
            print("[graphify publish] no durable Graphify changes to publish")
            return 0

        ensure_structure_only_graph(root)
        path_args = [str(path) for path in paths]
        run_git("add", "-A", "--", *path_args, cwd=root)

        commit_env = os.environ.copy()
        commit_env["GRAPHIFY_SKIP_HOOK"] = "1"
        run_git(
            "commit",
            "--only",
            "-m",
            COMMIT_SUBJECT,
            "-m",
            COMMIT_BODY,
            "--",
            *path_args,
            cwd=root,
            env=commit_env,
        )
        commit_id = run_git("rev-parse", "--short", "HEAD", cwd=root).stdout.strip()
        print(f"[graphify publish] created {commit_id} on {branch}")

        push = run_git("push", cwd=root, check=False)
        if push.returncode != 0:
            detail = push.stderr.strip() or push.stdout.strip()
            raise PublishError(
                f"push to {upstream} was rejected; local commit {commit_id} remains: {detail}"
            )
        print(f"[graphify publish] pushed {branch} to {upstream}")
        return 0


def main() -> int:
    try:
        return publish()
    except PublishError as exc:
        print(f"[graphify publish] error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

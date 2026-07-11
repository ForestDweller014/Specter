#!/usr/bin/env python3
"""Patch Graphify's installed post-commit hook to publish rebuilt snapshots."""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path


GRAPHIFY_START = "# graphify-hook-start"
GRAPHIFY_END = "# graphify-hook-end"
REBUILD_ANCHOR = "    _rebuild_code(_root, changed_paths=changed, force=_force)"
PUBLISH_START = "    # specter-graphify-auto-publish-start"
PUBLISH_END = "    # specter-graphify-auto-publish-end"
PUBLISH_BLOCK = f"""{PUBLISH_START}
    import subprocess as _publisher_subprocess
    _publisher = Path.cwd() / 'scripts' / 'publish_graphify_snapshot.py'
    if not _publisher.is_file():
        raise RuntimeError(f'Graphify publisher not found: {{_publisher}}')
    _publish_result = _publisher_subprocess.run(
        [sys.executable, str(_publisher)], cwd=Path.cwd()
    )
    if _publish_result.returncode != 0:
        raise RuntimeError(
            f'Graphify snapshot publisher failed with exit code {{_publish_result.returncode}}'
        )
{PUBLISH_END}"""


class InstallError(RuntimeError):
    """The installed hook cannot be patched safely."""


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise InstallError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def hook_path() -> Path:
    root = Path(git_output("rev-parse", "--show-toplevel")).resolve()
    value = Path(git_output("rev-parse", "--git-path", "hooks/post-commit"))
    return value if value.is_absolute() else root / value


def patch_hook(path: Path) -> bool:
    if not path.is_file():
        raise InstallError(
            "Graphify post-commit hook is not installed; run `graphify hook install` first"
        )
    original_mode = stat.S_IMODE(path.stat().st_mode)
    text = path.read_text(encoding="utf-8")

    if PUBLISH_START in text or PUBLISH_END in text:
        if text.count(PUBLISH_START) == 1 and text.count(PUBLISH_END) == 1:
            return False
        raise InstallError("found an incomplete or duplicated auto-publish marker")

    if text.count(GRAPHIFY_START) != 1 or text.count(GRAPHIFY_END) != 1:
        raise InstallError("unknown hook layout: expected one Graphify hook block")
    block_start = text.index(GRAPHIFY_START)
    block_end = text.index(GRAPHIFY_END, block_start)
    anchor_positions = [
        index
        for index in range(len(text))
        if text.startswith(REBUILD_ANCHOR, index)
        and block_start < index < block_end
    ]
    if len(anchor_positions) != 1:
        raise InstallError("unknown hook layout: rebuild anchor was not found exactly once")

    patched = text.replace(REBUILD_ANCHOR, REBUILD_ANCHOR + "\n" + PUBLISH_BLOCK, 1)
    path.write_text(patched, encoding="utf-8")
    path.chmod(original_mode)
    return True


def main() -> int:
    try:
        path = hook_path()
        changed = patch_hook(path)
    except (InstallError, OSError) as exc:
        print(f"[graphify auto-publish installer] error: {exc}", file=sys.stderr)
        return 1

    if changed:
        print(f"Installed Graphify auto-publish extension in {path}")
    else:
        print(f"Graphify auto-publish extension is already installed in {path}")
    print("Rerun this installer after Graphify reinstalls or upgrades its hook.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

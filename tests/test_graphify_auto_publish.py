from __future__ import annotations

import shutil
import stat
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = PROJECT_ROOT / "scripts" / "publish_graphify_snapshot.py"
INSTALLER = PROJECT_ROOT / "scripts" / "install_graphify_auto_publish.py"


def _run(
    *args: str,
    cwd: Path,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return _run("git", *args, cwd=repo, check=check)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _init_publishing_repo(tmp_path: Path) -> tuple[Path, Path]:
    remote = tmp_path / "remote.git"
    repo = tmp_path / "work"
    _run("git", "init", "--bare", str(remote), cwd=tmp_path)
    _run("git", "init", "-b", "main", str(repo), cwd=tmp_path)
    _git(repo, "config", "user.name", "Graphify Test")
    _git(repo, "config", "user.email", "graphify@example.test")
    _git(repo, "remote", "add", "origin", str(remote))

    shutil.copy(PUBLISHER, repo / "publish_graphify_snapshot.py")
    _write(
        repo / ".gitignore",
        "\n".join(
            [
                "graphify-out/.graphify_python",
                "graphify-out/.graphify_root",
                "graphify-out/.vocab.txt",
                "graphify-out/.graphify_learning.json",
                "graphify-out/.rebuild.lock",
                "graphify-out/.pending_changes",
                "graphify-out/memory/",
                "graphify-out/reflections/",
                "graphify-out/????-??-??/",
                "graphify-out/cache/stat-index.json",
                "",
            ]
        ),
    )
    _write(repo / "graphify-out/graph.json", '{"version": 1}\n')
    _write(repo / "graphify-out/graph.html", "<p>initial</p>\n")
    _write(repo / "graphify-out/GRAPH_REPORT.md", "# Initial graph\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "chore: Initialize fixture")
    _git(repo, "push", "-u", "origin", "main")
    return repo, remote


def test_publisher_commits_and_pushes_only_durable_outputs(tmp_path: Path) -> None:
    # Tests real Git publication, durable path selection, deletion, and staged-work isolation.
    repo, remote = _init_publishing_repo(tmp_path)
    _write(repo / "graphify-out/graph.json", '{"version": 2}\n')
    (repo / "graphify-out/graph.html").unlink()
    _write(repo / "graphify-out/manifest.json", '{"nodes": 2}\n')
    _write(repo / "graphify-out/cache/ast/v1/example.json", '{"ast": true}\n')
    _write(repo / "graphify-out/.graphify_root", str(repo) + "\n")
    _write(repo / "graphify-out/.graphify_python", sys.executable + "\n")
    _write(repo / "graphify-out/cache/stat-index.json", '{"mtime": 123}\n')
    _write(repo / "graphify-out/2026-07-10/graph.json", '{"backup": true}\n')
    _write(repo / "notes.txt", "keep staged\n")
    _git(repo, "add", "notes.txt")

    result = _run(sys.executable, str(repo / PUBLISHER.name), cwd=repo)

    assert "pushed main to origin/main" in result.stdout
    assert _git(repo, "log", "-1", "--format=%s").stdout.strip() == (
        "chore: Refresh Graphify snapshot"
    )
    assert _git(repo, "diff", "--cached", "--name-only").stdout.strip() == "notes.txt"
    committed = set(_git(repo, "show", "--format=", "--name-only", "HEAD").stdout.split())
    assert committed == {
        "graphify-out/cache/ast/v1/example.json",
        "graphify-out/graph.html",
        "graphify-out/graph.json",
        "graphify-out/manifest.json",
    }
    tracked = set(_git(repo, "ls-files").stdout.split())
    assert "graphify-out/.graphify_root" not in tracked
    assert "graphify-out/.graphify_python" not in tracked
    assert "graphify-out/cache/stat-index.json" not in tracked
    assert "graphify-out/2026-07-10/graph.json" not in tracked

    remote_head = _run(
        "git", "--git-dir", str(remote), "rev-parse", "refs/heads/main", cwd=tmp_path
    ).stdout.strip()
    assert remote_head == _git(repo, "rev-parse", "HEAD").stdout.strip()


def test_publisher_refuses_manually_staged_graphify_files(tmp_path: Path) -> None:
    # Tests that the publisher aborts without committing when a Graphify output is manually staged.
    repo, _ = _init_publishing_repo(tmp_path)
    _write(repo / "graphify-out/graph.json", '{"version": 2}\n')
    _git(repo, "add", "graphify-out/graph.json")

    result = _run(
        sys.executable,
        str(repo / PUBLISHER.name),
        cwd=repo,
        check=False,
    )

    assert result.returncode == 1
    assert "manually staged Graphify files" in result.stderr
    assert _git(repo, "log", "-1", "--format=%s").stdout.strip() == ("chore: Initialize fixture")


def _init_hook_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "hook-work"
    _run("git", "init", "-b", "main", str(repo), cwd=tmp_path)
    hook = repo / ".git/hooks/post-commit"
    _write(
        hook,
        """#!/bin/sh
# graphify-hook-start
python -c \"_src = '''
from pathlib import Path
_rebuild_code = None
try:
    _rebuild_code(_root, changed_paths=changed, force=_force)
except Exception:
    raise
'''\"
# graphify-hook-end
""",
    )
    hook.chmod(0o751)
    return repo, hook


def test_hook_installer_is_idempotent_and_preserves_mode(tmp_path: Path) -> None:
    # Tests repeat-safe patching and executable-mode preservation against a synthetic Graphify hook.
    repo, hook = _init_hook_repo(tmp_path)
    original_mode = stat.S_IMODE(hook.stat().st_mode)

    first = _run(sys.executable, str(INSTALLER), cwd=repo)
    first_text = hook.read_text(encoding="utf-8")
    second = _run(sys.executable, str(INSTALLER), cwd=repo)

    assert "Installed Graphify auto-publish extension" in first.stdout
    assert "already installed" in second.stdout
    assert hook.read_text(encoding="utf-8") == first_text
    assert first_text.count("specter-graphify-auto-publish-start") == 1
    assert first_text.count("specter-graphify-auto-publish-end") == 1
    assert stat.S_IMODE(hook.stat().st_mode) == original_mode


def test_hook_patch_runs_publisher_after_rebuild(tmp_path: Path) -> None:
    # Tests that the synthetic hook is patched to call the publisher after the rebuild anchor.
    repo, hook = _init_hook_repo(tmp_path)

    _run(sys.executable, str(INSTALLER), cwd=repo)
    text = hook.read_text(encoding="utf-8")

    rebuild_index = text.index("_rebuild_code(_root, changed_paths=changed, force=_force)")
    publish_index = text.index("specter-graphify-auto-publish-start")
    exception_index = text.index("except Exception:")
    assert rebuild_index < publish_index < exception_index
    assert "[sys.executable, str(_publisher)]" in text


def test_hook_installer_rejects_unknown_layout(tmp_path: Path) -> None:
    # Tests that the installer refuses an unrecognized hook instead of modifying arbitrary content.
    repo = tmp_path / "unknown-hook"
    _run("git", "init", "-b", "main", str(repo), cwd=tmp_path)
    hook = repo / ".git/hooks/post-commit"
    _write(hook, "#!/bin/sh\necho custom\n")
    hook.chmod(0o755)

    result = _run(sys.executable, str(INSTALLER), cwd=repo, check=False)

    assert result.returncode == 1
    assert "unknown hook layout" in result.stderr

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


class DullahanInferenceError(RuntimeError):
    pass


class DullahanInferenceServer:
    """Run Dullahan's local inference module for the lifetime of a Specter command."""

    def __init__(
        self,
        *,
        repo_root: Path,
        config_path: Path,
        base_url: str,
        startup_timeout_seconds: float = 30.0,
    ) -> None:
        self.repo_root = repo_root.expanduser().resolve()
        self.config_path = config_path.expanduser().resolve()
        self.base_url = base_url.rstrip("/")
        self.startup_timeout_seconds = startup_timeout_seconds
        self.process: subprocess.Popen[str] | None = None

    @property
    def health_url(self) -> str:
        root_url = self.base_url.removesuffix("/v1")
        return f"{root_url}/health"

    def __enter__(self) -> DullahanInferenceServer:
        if self._is_healthy():
            return self
        source_root = self.repo_root / "apps" / "inference" / "src"
        if not source_root.is_dir():
            raise DullahanInferenceError(
                f"Dullahan inference source directory does not exist: {source_root}"
            )
        if not self.config_path.is_file():
            raise DullahanInferenceError(
                f"Dullahan inference config does not exist: {self.config_path}"
            )
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join(
            value for value in (str(source_root), environment.get("PYTHONPATH")) if value
        )
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "dullahan_inference.cli",
                "serve",
                "--config",
                str(self.config_path),
            ],
            cwd=self.repo_root,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.monotonic() + self.startup_timeout_seconds
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                detail = self.process.stderr.read().strip() if self.process.stderr else ""
                raise DullahanInferenceError(
                    f"Dullahan inference exited before becoming healthy: {detail}"
                )
            if self._is_healthy():
                return self
            time.sleep(0.1)
        self.stop()
        raise DullahanInferenceError(
            f"timed out waiting for Dullahan inference at {self.health_url}"
        )

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.stop()

    def stop(self) -> None:
        if self.process is None or self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    def _is_healthy(self) -> bool:
        try:
            with urlopen(self.health_url, timeout=1) as response:
                return 200 <= response.status < 300
        except (OSError, URLError):
            return False

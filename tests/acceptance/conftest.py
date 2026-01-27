from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Generator, TypeVar

import pytest
import requests

from OTAnalytics.plugin_ui.nicegui_application import DEFAULT_HOSTNAME, DEFAULT_PORT
from tests.utils.builders.otanalytics_builders import file_picker_directory

# Centralized timeouts and settings used by Playwright-based acceptance tests
ACCEPTANCE_TEST_WAIT_TIMEOUT = 5
# Pytest per-test timeout (seconds) for slow UI E2E tests
ACCEPTANCE_TEST_PYTEST_TIMEOUT = 300
# Playwright explicit wait default for visibility checks (milliseconds)
PLAYWRIGHT_VISIBLE_TIMEOUT_MS = 5000
# Quick visible wait (milliseconds) for fast retries in tight loops
PLAYWRIGHT_QUICK_VISIBLE_TIMEOUT_MS = 1000
# Short one-off UI settle wait (milliseconds)
PLAYWRIGHT_SHORT_WAIT_MS = 150
# Polling intervals (milliseconds)
PLAYWRIGHT_POLL_INTERVAL_MS = 50
PLAYWRIGHT_POLL_INTERVAL_SLOW_MS = 100
# Polling interval (seconds) derived from ms value for use with time.sleep
PLAYWRIGHT_POLL_INTERVAL_SECONDS = PLAYWRIGHT_POLL_INTERVAL_MS / 1000
# Unified final timeout for Playwright waiters (milliseconds)
ACCEPTANCE_TEST_FINAL_TIMEOUT_MS = int(ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)
# Max polls used in some import/verify loops
IMPORT_VERIFY_MAX_POLLS = 120

# Large buffer for webserver process pipes
BUFFER_SIZE_100MB = 10**8


T = TypeVar("T")
YieldFixture = Generator[T, None, None]


class NiceGUITestServer:
    """Helper class to manage NiceGUI test server for acceptance tests."""

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.process: subprocess.Popen | None = None
        self.base_url = f"http://{DEFAULT_HOSTNAME}:{port}"

    def start(self) -> None:
        """Start NiceGUI server in subprocess."""
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "OTAnalytics",
                "--webui",
                "--file-picker-directory",
                file_picker_directory(),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=BUFFER_SIZE_100MB,
        )
        self._wait_for_server()

    def stop(self) -> None:
        """Stop NiceGUI server."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
            except Exception:
                self.process.kill()

    def _wait_for_server(self, timeout: int = 10) -> None:
        """Naive wait; rely on later page.goto() for final availability."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(self.base_url, timeout=1)
                if response.status_code == 200:
                    return
            except requests.ConnectionError:
                pass
            time.sleep(0.5)

        # Collect diagnostic information on timeout
        error_msg = f"Server was not reachable at {self.base_url} within {timeout}s"
        if self.process:
            if self.process.poll() is not None:
                error_msg += (
                    f"\nProcess has already terminated with exit code: "
                    f"{self.process.returncode}"
                )
            if self.process.stderr:
                stderr_output = self.process.stderr.read().decode(
                    "utf-8", errors="replace"
                )
                if stderr_output:
                    error_msg += f"\nStderr:\n{stderr_output}"
            if self.process.stdout:
                stdout_output = self.process.stdout.read().decode(
                    "utf-8", errors="replace"
                )
                if stdout_output:
                    error_msg += f"\nStdout:\n{stdout_output}"
        raise TimeoutError(error_msg)


@pytest.fixture
def external_app() -> YieldFixture[NiceGUITestServer]:
    server = NiceGUITestServer()
    server.start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture
def acceptance_test_data_folder(test_data_dir: Path) -> Path:
    return test_data_dir / "acceptance"


@pytest.fixture
def actual_screenshot_path(test_data_tmp_dir: Path) -> Path:
    return test_data_tmp_dir / "acceptance_test_actual_screenshot.png"

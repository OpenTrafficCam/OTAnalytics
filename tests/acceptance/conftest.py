from __future__ import annotations

import subprocess
import time
from typing import Generator, TypeVar

import pytest

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
                "python",
                "-m",
                "OTAnalytics",
                "--webui",
                "--file-picker-directory",
                file_picker_directory(),
            ],
            stdin=subprocess.PIPE,
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
        time.sleep(min(max(timeout, 1), 10))


@pytest.fixture
def external_app() -> YieldFixture[NiceGUITestServer]:
    server = NiceGUITestServer()
    server.start()
    try:
        yield server
    finally:
        server.stop()

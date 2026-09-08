"""Acceptance: in s3 mode, adding tracks asks for a time range, not a file."""

import io
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator

import pytest
import requests
from playwright.sync_api import Page, expect  # type: ignore

from OTAnalytics.application.resources.resource_manager import (
    AddTracksKeys,
    LoadWindowKeys,
    ResourceManager,
)
from OTAnalytics.plugin_s3.config.env_vars import (
    ENV_DATA_TRANSFER_MODE,
    ENV_S3_ACCESS_KEY,
    ENV_S3_BUCKET,
    ENV_S3_ENDPOINT_URL,
    ENV_S3_KEY_PREFIX,
    ENV_S3_MAX_LOAD_DURATION,
    ENV_S3_SECRET_KEY,
    ENV_S3_USER_SOURCE,
)
from OTAnalytics.plugin_ui.nicegui_application import DEFAULT_HOSTNAME, DEFAULT_PORT
from tests.acceptance.conftest import PLAYWRIGHT_VISIBLE_TIMEOUT_MS
from tests.utils.builders.otanalytics_builders import file_picker_directory

pytest.importorskip("playwright.sync_api", reason="needs pytest-playwright")

BUCKET = "recordings"
PREFIX = "project-0/site-0/camera-1"
MINIO_IMAGE = "minio/minio:RELEASE.2025-09-07T16-13-09Z"
CHUNKS = ["10-00-00", "10-15-00"]


def _docker_is_available() -> bool:
    try:
        return (
            subprocess.run(
                ["docker", "info"], capture_output=True, timeout=20
            ).returncode
            == 0
        )
    except (OSError, subprocess.SubprocessError):
        return False


pytestmark = pytest.mark.skipif(
    not _docker_is_available(), reason="needs Docker to run MinIO"
)


@pytest.fixture(scope="module")
def minio() -> Iterator[dict]:
    from testcontainers.minio import MinioContainer

    os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")
    with MinioContainer(image=MINIO_IMAGE) as container:
        client = container.get_client()
        client.make_bucket(BUCKET)
        for chunk in CHUNKS:
            for suffix, payload in ((".ottrk", b"tracks"), (".mp4", b"video")):
                name = f"{PREFIX}/OTCamera19_FR20_2023-05-24_{chunk}{suffix}"
                client.put_object(BUCKET, name, io.BytesIO(payload), len(payload))
        yield {
            "endpoint_url": f"http://{container.get_config()['endpoint']}",
            "access_key": container.access_key,
            "secret_key": container.secret_key,
        }


@pytest.fixture
def s3_app(minio: dict, tmp_path: Path) -> Iterator[Any]:
    """The real application, started in s3 mode against MinIO.

    Configuration is environment only, so pointing the documented variables at a
    throwaway MinIO exercises the production path with no test-only hooks.
    """
    environment = dict(os.environ)
    environment.update(
        {
            ENV_DATA_TRANSFER_MODE: "s3",
            ENV_S3_ENDPOINT_URL: minio["endpoint_url"],
            ENV_S3_ACCESS_KEY: minio["access_key"],
            ENV_S3_SECRET_KEY: minio["secret_key"],
            ENV_S3_BUCKET: BUCKET,
            ENV_S3_KEY_PREFIX: PREFIX,
            ENV_S3_USER_SOURCE: str(tmp_path / "user-source"),
            ENV_S3_MAX_LOAD_DURATION: "20m",
        }
    )
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "OTAnalytics",
            "--webui",
            "--file-picker-directory",
            file_picker_directory(),
        ],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    base_url = f"http://{DEFAULT_HOSTNAME}:{DEFAULT_PORT}"
    try:
        _wait_for(base_url, process)
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def _wait_for(base_url: str, process: subprocess.Popen, timeout: int = 30) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            stderr = (
                process.stderr.read().decode(errors="replace") if process.stderr else ""
            )
            raise RuntimeError(f"Application exited early:\n{stderr}")
        try:
            response = requests.get(base_url, timeout=1)
            # macOS AirPlay also listens on this port and answers 200, so a
            # status code alone is not proof the application is up.
            if response.status_code == 200 and "nicegui" in response.text.lower():
                return
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
    raise TimeoutError(f"Application was not reachable at {base_url}")


@pytest.mark.timeout(300)
@pytest.mark.playwright
def test_adding_tracks_asks_for_a_time_range(
    page: Page, s3_app: str, resource_manager: ResourceManager
) -> None:
    """#Requirement https://openproject.platomo.de/wp/10283"""
    page.goto(s3_app)

    page.get_by_text(
        resource_manager.get(AddTracksKeys.BUTTON_ADD_TRACKS), exact=True
    ).click()

    expect(
        page.get_by_text(resource_manager.get(LoadWindowKeys.LABEL_UTC_HINT))
    ).to_be_visible(timeout=PLAYWRIGHT_VISIBLE_TIMEOUT_MS)


@pytest.mark.timeout(300)
@pytest.mark.playwright
def test_an_over_long_range_is_shortened_and_reported(
    page: Page, s3_app: str, resource_manager: ResourceManager
) -> None:
    """The cap is 20 minutes here, so 10:00-11:00 is snapped back to 10:20.

    #Requirement https://openproject.platomo.de/wp/10283
    """
    page.goto(s3_app)
    page.get_by_text(
        resource_manager.get(AddTracksKeys.BUTTON_ADD_TRACKS), exact=True
    ).click()
    expect(
        page.get_by_text(resource_manager.get(LoadWindowKeys.LABEL_UTC_HINT))
    ).to_be_visible(timeout=PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    _fill(page, resource_manager, LoadWindowKeys.LABEL_START_DATE, "2023-05-24")
    _fill(page, resource_manager, LoadWindowKeys.LABEL_START_TIME, "10:00:00")
    _fill(page, resource_manager, LoadWindowKeys.LABEL_END_DATE, "2023-05-24")
    _fill(page, resource_manager, LoadWindowKeys.LABEL_END_TIME, "11:00:00")
    page.get_by_text(
        resource_manager.get(LoadWindowKeys.LABEL_LOAD), exact=True
    ).click()

    expect(
        page.get_by_text(resource_manager.get(LoadWindowKeys.MESSAGE_CLAMPED))
    ).to_be_visible(timeout=PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    expect(page.get_by_text("10:20:00")).to_be_visible(
        timeout=PLAYWRIGHT_VISIBLE_TIMEOUT_MS
    )


def _fill(
    page: Page, resource_manager: ResourceManager, key: LoadWindowKeys, value: str
) -> None:
    page.get_by_label(resource_manager.get(key)).fill(value)

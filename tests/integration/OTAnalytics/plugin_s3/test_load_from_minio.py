"""Loading from a real S3 implementation.

Exercises what mocks cannot: `list_objects_v2` pagination, real GETs against a
running server, and the clamp applied to an over-long selection.
"""

import bz2
import io
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator
from unittest.mock import AsyncMock, Mock

import pytest

from OTAnalytics.domain.load_window import LoadWindow
from OTAnalytics.plugin_s3.config.s3 import S3Config
from OTAnalytics.plugin_s3.connect import S3Connection
from OTAnalytics.plugin_s3.download import S3Download
from OTAnalytics.plugin_s3.download_objects import DownloadObjects
from OTAnalytics.plugin_s3.list_objects import S3ListObjects
from OTAnalytics.plugin_s3.s3_file_providers import (
    AskForLoadWindow,
    S3TrackFileProvider,
    S3VideoFileProvider,
)
from tests.utils.progress import SilentProgressBuilder

BUCKET = "recordings"
PREFIX = "project-0/site-0/camera-1"
START = datetime(2023, 5, 24, 10, 0, tzinfo=timezone.utc)
MAX_LOAD_DURATION = timedelta(minutes=20)

CHUNKS = ["10-00-00", "10-15-00", "10-30-00"]
# Deliberately not .mp4: the companion is named by the ottrk's own metadata, and
# a suffix swap would look for an object that is not there.
VIDEO_TYPE = ".mkv"

# Pinned for reproducibility. testcontainers' own default is a 2022 build that is
# amd64 only and will not start on an arm64 host.
MINIO_IMAGE = "minio/minio:RELEASE.2025-09-07T16-13-09Z"


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

    # The reaper container bind-mounts the Docker socket, which Docker Desktop
    # refuses on some hosts. The context manager below cleans up on a normal
    # exit; the reaper only matters if the test process is killed outright.
    os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")
    with MinioContainer(image=MINIO_IMAGE) as container:
        client = container.get_client()
        client.make_bucket(BUCKET)
        for chunk in CHUNKS:
            stem = f"OTCamera19_FR20_2023-05-24_{chunk}"
            _put(client, f"{stem}.ottrk", _ottrk_naming(f"{stem}{VIDEO_TYPE}"))
            _put(client, f"{stem}{VIDEO_TYPE}", b"video")
        yield {
            "endpoint_url": f"http://{container.get_config()['endpoint']}",
            "access_key": container.access_key,
            "secret_key": container.secret_key,
        }


def _ottrk_naming(video: str) -> bytes:
    """A track file whose metadata names the video it belongs to."""
    stem, _, filetype = video.rpartition(".")
    metadata = {"metadata": {"video": {"filename": stem, "filetype": f".{filetype}"}}}
    return bz2.compress(json.dumps(metadata).encode())


def _put(client: object, name: str, payload: bytes) -> None:
    client.put_object(  # type: ignore[attr-defined]
        BUCKET, f"{PREFIX}/{name}", io.BytesIO(payload), len(payload)
    )


@dataclass
class Given:
    config: S3Config
    dialog: Mock
    user_source: Path


def create_given(minio: dict, tmp_path: Path, hours: float = 1) -> Given:
    user_source = tmp_path / "user-source"
    config = S3Config(
        endpoint_url=minio["endpoint_url"],
        access_key=minio["access_key"],
        secret_key=minio["secret_key"],
        bucket=BUCKET,
        region=None,
        key_prefix=PREFIX,
        user_source=str(user_source),
        max_load_duration=MAX_LOAD_DURATION,
        download_concurrency=4,
    )
    dialog = Mock(spec=AskForLoadWindow)
    dialog.ask = AsyncMock(
        return_value=LoadWindow(start=START, end=START + timedelta(hours=hours))
    )
    return Given(config=config, dialog=dialog, user_source=user_source)


def _download_objects(given: Given) -> DownloadObjects:
    connection = S3Connection()
    return DownloadObjects(
        download=S3Download(connection, given.config),
        user_source=given.user_source,
        concurrency=given.config.download_concurrency,
        progressbar_builder=SilentProgressBuilder(),
    )


def create_track_target(given: Given) -> S3TrackFileProvider:
    return S3TrackFileProvider(
        dialog=given.dialog,
        list_objects=S3ListObjects(S3Connection(), given.config),
        download_objects=_download_objects(given),
        config=given.config,
    )


def create_video_target(given: Given) -> S3VideoFileProvider:
    return S3VideoFileProvider(
        dialog=given.dialog,
        list_objects=S3ListObjects(S3Connection(), given.config),
        download_objects=_download_objects(given),
        config=given.config,
    )


class TestLoadFromMinio:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    async def test_an_over_long_selection_loads_only_up_to_the_cap(
        self, minio: dict, tmp_path: Path
    ) -> None:
        """10:00-11:00 clamps to 10:20, so only the 10:00 and 10:15 chunks load."""
        given = create_given(minio, tmp_path, hours=1)
        target = create_track_target(given)

        provided = await target.provide()

        assert [path.name for path in provided] == [
            "OTCamera19_FR20_2023-05-24_10-00-00.ottrk",
            "OTCamera19_FR20_2023-05-24_10-15-00.ottrk",
        ]
        given.dialog.report_clamped.assert_called_once()

    async def test_downloads_each_track_file_with_its_video(
        self, minio: dict, tmp_path: Path
    ) -> None:
        given = create_given(minio, tmp_path, hours=1)
        target = create_track_target(given)

        await target.provide()

        for chunk in CHUNKS[:2]:
            for suffix in (".ottrk", VIDEO_TYPE):
                staged = (
                    given.user_source
                    / PREFIX
                    / f"OTCamera19_FR20_2023-05-24_{chunk}{suffix}"
                )
                assert staged.is_file(), f"{staged} was not downloaded"

    async def test_stages_objects_under_paths_mirroring_their_keys(
        self, minio: dict, tmp_path: Path
    ) -> None:
        given = create_given(minio, tmp_path, hours=1)
        target = create_track_target(given)

        provided = await target.provide()

        assert provided[0] == (
            given.user_source / PREFIX / "OTCamera19_FR20_2023-05-24_10-00-00.ottrk"
        )

    async def test_reads_the_bytes_that_were_stored(
        self, minio: dict, tmp_path: Path
    ) -> None:
        given = create_given(minio, tmp_path, hours=1)
        target = create_track_target(given)

        provided = await target.provide()

        assert bz2.decompress(provided[0].read_bytes()).startswith(b"{")

    async def test_pairs_each_track_file_with_the_video_its_metadata_names(
        self, minio: dict, tmp_path: Path
    ) -> None:
        """A suffix swap would have looked for a .mp4 that does not exist."""
        given = create_given(minio, tmp_path, hours=1)
        target = create_track_target(given)

        await target.provide()

        staged = given.user_source / PREFIX
        assert (staged / f"OTCamera19_FR20_2023-05-24_10-00-00{VIDEO_TYPE}").is_file()
        assert not (staged / "OTCamera19_FR20_2023-05-24_10-00-00.mp4").exists()

    async def test_videos_load_on_their_own(self, minio: dict, tmp_path: Path) -> None:
        given = create_given(minio, tmp_path, hours=1)
        target = create_video_target(given)

        provided = await target.provide()

        assert [path.name for path in provided] == [
            f"OTCamera19_FR20_2023-05-24_10-00-00{VIDEO_TYPE}",
            f"OTCamera19_FR20_2023-05-24_10-15-00{VIDEO_TYPE}",
        ]

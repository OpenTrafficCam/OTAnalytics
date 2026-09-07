"""Tests for downloading the selected S3 objects into the user source."""

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from OTAnalytics.domain.progress import CompletionProgress, CompletionProgressBuilder
from OTAnalytics.plugin_s3.download_objects import DownloadCancelled, DownloadObjects

KEY_A = "cam/OTCamera19_2023-05-24_06-00-00.ottrk"
KEY_B = "cam/OTCamera19_2023-05-24_06-15-00.ottrk"
KEY_C = "cam/OTCamera19_2023-05-24_06-30-00.ottrk"
KEYS = [KEY_A, KEY_B, KEY_C]

USER_SOURCE = Path("/staging")


class FakeProgress(CompletionProgress):
    """Records completions and can be cancelled at a chosen point."""

    def __init__(self, cancel_after: int | None = None) -> None:
        self.completed: list[str] = []
        self.closed = False
        self._cancel_after = cancel_after

    def complete(self, item: str) -> None:
        self.completed.append(item)

    def close(self) -> None:
        self.closed = True

    @property
    def is_cancelled(self) -> bool:
        if self._cancel_after is None:
            return False
        return len(self.completed) >= self._cancel_after


@dataclass
class Given:
    download: Mock
    progress: FakeProgress
    progressbar_builder: Mock
    downloaded: list[str] = field(default_factory=list)
    concurrent: list[int] = field(default_factory=list)


def create_given(
    concurrency: int = 2, cancel_after: int | None = None, fail_on: str | None = None
) -> Given:
    given = Given(
        download=Mock(),
        progress=FakeProgress(cancel_after=cancel_after),
        progressbar_builder=Mock(spec=CompletionProgressBuilder),
    )
    in_flight = 0

    async def fake_download(key: str, dst: Path) -> None:
        nonlocal in_flight
        in_flight += 1
        given.concurrent.append(in_flight)
        await asyncio.sleep(0)
        if fail_on == key:
            in_flight -= 1
            raise OSError(f"boom on {key}")
        given.downloaded.append(key)
        in_flight -= 1

    given.download.download = AsyncMock(side_effect=fake_download)
    given.progressbar_builder.build.return_value = given.progress
    given.concurrency = concurrency  # type: ignore[attr-defined]
    return given


def create_target(given: Given, concurrency: int = 2) -> DownloadObjects:
    return DownloadObjects(
        download=given.download,
        user_source=USER_SOURCE,
        concurrency=concurrency,
        progressbar_builder=given.progressbar_builder,
    )


class TestDownloadObjects:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    async def test_downloads_every_key_to_a_path_mirroring_it(self) -> None:
        given = create_given()
        target = create_target(given)

        paths = await target.download_all(KEYS, "Downloading tracks")

        assert paths == [USER_SOURCE / key for key in KEYS]
        assert sorted(given.downloaded) == sorted(KEYS)

    async def test_reports_every_completed_object(self) -> None:
        given = create_given()
        target = create_target(given)

        await target.download_all(KEYS, "Downloading tracks")

        assert sorted(given.progress.completed) == sorted(
            Path(key).name for key in KEYS
        )

    async def test_never_exceeds_the_configured_concurrency(self) -> None:
        given = create_given()
        target = create_target(given, concurrency=2)

        await target.download_all(KEYS, "Downloading tracks")

        assert max(given.concurrent) <= 2

    async def test_shows_progress_over_the_expected_number_of_objects(self) -> None:
        given = create_given()
        target = create_target(given)

        await target.download_all(KEYS, "Downloading tracks")

        given.progressbar_builder.build.assert_called_once_with(
            description="Downloading tracks", unit="files", total=len(KEYS)
        )

    async def test_closes_the_progressbar_when_done(self) -> None:
        given = create_given()
        target = create_target(given)

        await target.download_all(KEYS, "Downloading tracks")

        assert given.progress.closed is True

    async def test_cancelling_abandons_the_load(self) -> None:
        given = create_given(cancel_after=1)
        target = create_target(given, concurrency=1)

        with pytest.raises(DownloadCancelled):
            await target.download_all(KEYS, "Downloading tracks")

        assert len(given.downloaded) < len(KEYS)
        assert given.progress.closed is True

    async def test_a_failed_download_fails_the_whole_load(self) -> None:
        given = create_given(fail_on=KEY_B)
        target = create_target(given)

        with pytest.raises(OSError):
            await target.download_all(KEYS, "Downloading tracks")

        assert given.progress.closed is True

    async def test_downloading_nothing_shows_no_progressbar(self) -> None:
        given = create_given()
        target = create_target(given)

        paths = await target.download_all([], "Downloading tracks")

        assert paths == []
        given.progressbar_builder.build.assert_not_called()

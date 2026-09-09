"""Tests for the wiring of the NiceGUI application."""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.adapter_ui.local_file_providers import (
    LocalTrackFileProvider,
    LocalVideoFileProvider,
)
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.plugin_s3.config.env_vars import (
    ENV_DATA_TRANSFER_MODE,
    ENV_S3_ACCESS_KEY,
    ENV_S3_BUCKET,
    ENV_S3_ENDPOINT_URL,
    ENV_S3_KEY_PREFIX,
    ENV_S3_SECRET_KEY,
    ENV_S3_USER_SOURCE,
)
from OTAnalytics.plugin_s3.s3_file_providers import (
    S3TrackFileProvider,
    S3VideoFileProvider,
)
from OTAnalytics.plugin_ui.nicegui_application import (
    OtAnalyticsNiceGuiApplicationStarter,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.progressbar import (
    NiceguiProgressbarBuilder,
)


@dataclass
class Given:
    run_config: Mock


def create_given() -> Given:
    return Given(run_config=Mock(spec=RunConfiguration))


def create_target(given: Given) -> OtAnalyticsNiceGuiApplicationStarter:
    return OtAnalyticsNiceGuiApplicationStarter(given.run_config)


@pytest.fixture
def s3_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(ENV_DATA_TRANSFER_MODE, "s3")
    monkeypatch.setenv(ENV_S3_ENDPOINT_URL, "http://localhost:9000")
    monkeypatch.setenv(ENV_S3_BUCKET, "recordings")
    monkeypatch.setenv(ENV_S3_ACCESS_KEY, "key")
    monkeypatch.setenv(ENV_S3_SECRET_KEY, "secret")
    monkeypatch.setenv(ENV_S3_KEY_PREFIX, "cam19")
    monkeypatch.setenv(ENV_S3_USER_SOURCE, str(tmp_path / "user-source"))


@pytest.fixture
def local_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_DATA_TRANSFER_MODE, raising=False)


class TestInputFileProviders:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    def test_local_mode_asks_the_file_chooser(self, local_mode: None) -> None:
        target = create_target(create_given())

        assert isinstance(target.provide_track_files, LocalTrackFileProvider)
        assert isinstance(target.provide_video_files, LocalVideoFileProvider)

    def test_s3_mode_asks_for_a_time_range(self, s3_mode: None) -> None:
        target = create_target(create_given())

        assert isinstance(target.provide_track_files, S3TrackFileProvider)
        assert isinstance(target.provide_video_files, S3VideoFileProvider)


class TestOtAnalyticsNiceGuiApplicationStarter:
    """#Requirement https://openproject.platomo.de/wp/10281"""

    def test_shows_progress_in_the_browser(self) -> None:
        target = OtAnalyticsNiceGuiApplicationStarter(Mock(spec=RunConfiguration))

        assert isinstance(target.progressbar_builder, NiceguiProgressbarBuilder)


class TestUserSourceLifecycle:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    def test_local_mode_stages_nothing_to_wipe(self, local_mode: None) -> None:
        target = create_target(create_given())

        assert target.wipe_user_source is None

    def test_s3_mode_wipes_the_configured_user_source(
        self, s3_mode: None, tmp_path: Path
    ) -> None:
        target = create_target(create_given())
        wipe = target.wipe_user_source

        assert wipe is not None

        staged = tmp_path / "user-source" / "cam19" / "a.ottrk"
        staged.parent.mkdir(parents=True)
        staged.write_bytes(b"tracks")

        wipe.wipe()

        assert not staged.exists()
        assert (tmp_path / "user-source").is_dir()

"""Tests for the wiring of the NiceGUI application."""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock, call

import pytest

from OTAnalytics.adapter_ui.local_file_providers import (
    LocalTrackFileProvider,
    LocalVideoFileProvider,
)
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.upload_otconfig import NoOtconfigUpload
from OTAnalytics.plugin_s3.config.env_vars import (
    ENV_DATA_TRANSFER_MODE,
    ENV_S3_ACCESS_KEY,
    ENV_S3_BUCKET,
    ENV_S3_ENDPOINT_URL,
    ENV_S3_SECRET_KEY,
    ENV_S3_USER_SOURCE,
)
from OTAnalytics.plugin_s3.otconfig_upload import S3OtconfigUpload
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


@pytest.fixture
def s3_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(ENV_DATA_TRANSFER_MODE, "s3")
    monkeypatch.setenv(ENV_S3_ENDPOINT_URL, "http://localhost:9000")
    monkeypatch.setenv(ENV_S3_BUCKET, "recordings")
    monkeypatch.setenv(ENV_S3_ACCESS_KEY, "key")
    monkeypatch.setenv(ENV_S3_SECRET_KEY, "secret")
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
    def test_shows_progress_in_the_browser(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10281"""

        target = OtAnalyticsNiceGuiApplicationStarter(Mock(spec=RunConfiguration))

        assert isinstance(target.progressbar_builder, NiceguiProgressbarBuilder)


class TestUserSourceLifecycle:
    def test_local_mode_stages_nothing_to_wipe(self, local_mode: None) -> None:
        """#Requirement https://openproject.platomo.de/wp/10283"""
        target = create_target(create_given())

        assert target.wipe_user_source is None

    def test_s3_mode_wipes_the_configured_user_source(
        self, s3_mode: None, tmp_path: Path
    ) -> None:
        """#Requirement https://openproject.platomo.de/wp/10283"""
        target = create_target(create_given())
        wipe = target.wipe_user_source

        assert wipe is not None

        staged = tmp_path / "user-source" / "cam19" / "a.ottrk"
        staged.parent.mkdir(parents=True)
        staged.write_bytes(b"tracks")

        wipe.wipe()

        assert not staged.exists()
        assert (tmp_path / "user-source").is_dir()


class TestOtconfigUpload:
    def test_local_mode_never_uploads(self, local_mode: None) -> None:
        """#Requirement https://openproject.platomo.de/wp/10323"""
        target = create_target(create_given())

        assert isinstance(target.otconfig_upload, NoOtconfigUpload)

    def test_s3_mode_uploads_beside_the_project_data(self, s3_mode: None) -> None:
        """#Requirement https://openproject.platomo.de/wp/10323"""
        target = create_target(create_given())

        assert isinstance(target.otconfig_upload, S3OtconfigUpload)


class TestFlowTrackCountObservers:
    def test_refreshes_flow_form_on_flow_and_event_changes(self) -> None:
        target = create_target(create_given())
        flow_repository = Mock()
        event_repository = Mock()
        flow_form = Mock()
        target.__dict__["flow_repository"] = flow_repository
        target.__dict__["event_repository"] = event_repository
        target.__dict__["flow_form"] = flow_form

        target.register_flow_track_count_observers()

        flow_repository.register_flows_observer.assert_called_once_with(flow_form)
        event_repository.register_observer.assert_called_once_with(
            flow_form.notify_events
        )


class TestTrackAssignmentObservers:
    def test_flow_form_follows_sections_and_reports_outdated_assignment(
        self,
    ) -> None:
        target = create_target(create_given())
        datastore = Mock()
        flow_form = Mock()
        canvas_form = Mock()
        assignment_status = Mock()
        track_repository = Mock()
        target.__dict__["datastore"] = datastore
        target.__dict__["track_repository"] = track_repository
        target.__dict__["flow_form"] = flow_form
        target.__dict__["canvas_form"] = canvas_form
        target.__dict__["assignment_status"] = assignment_status

        target.register_track_assignment_observers()

        datastore.register_section_changed_observer.assert_called_once_with(
            flow_form.notify_section_changed
        )
        assert flow_form.register_outdated_observer.call_args_list == [
            call(canvas_form.set_flows_outdated),
            call(assignment_status.show_outdated),
        ]
        track_repository.register_tracks_observer.assert_called_once_with(flow_form)


class TestVisualization:
    def test_track_image_has_no_class_legend(self) -> None:
        """The class legend on the canvas replaces the one in the track image."""
        target = create_target(create_given())
        for name in (
            "datastore",
            "intersection_repository",
            "track_view_state",
            "videos_metadata",
            "section_state",
            "color_palette_provider",
            "progressbar_builder",
            "track_image_factory",
            "track_id_set_factory",
            "current_orthophoto_image",
        ):
            target.__dict__[name] = Mock()

        builder = target.visualization_builder

        assert builder._enable_single_legend is False
        assert builder._enable_multi_legend is False


@dataclass
class Given:
    run_config: Mock


def create_given() -> Given:
    return Given(run_config=Mock(spec=RunConfiguration))


def create_target(given: Given) -> OtAnalyticsNiceGuiApplicationStarter:
    return OtAnalyticsNiceGuiApplicationStarter(given.run_config)

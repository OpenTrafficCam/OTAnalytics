"""Resetting the application in the real application wiring.

Unit tests only check that the use cases delegate to their collaborators. Here
a real otconfig is loaded into the application as the desktop GUI wires it and
changed. Starting a new project must then leave the application as if it had
just been started, and opening another project must leave it as if that
project had been opened in a freshly started application.
"""

import json
import shutil
from functools import cached_property
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder
from OTAnalytics.plugin_ui.ctk_application import OtAnalyticsCtkApplicationStarter
from tests.utils.builders.run_configuration import create_run_config

PROJECT = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00"


class HeadlessCtkApplication(OtAnalyticsCtkApplicationStarter):
    """The desktop GUI wiring without a window."""

    def start_ui(self) -> None:
        pass

    @cached_property
    def progressbar_builder(self) -> ProgressbarBuilder:
        return TqdmBuilder()

    @cached_property
    def ui_factory(self) -> MagicMock:  # type: ignore[override]
        return MagicMock()

    @cached_property
    def view_model(self) -> MagicMock:  # type: ignore[override]
        return MagicMock()


def create_target() -> HeadlessCtkApplication:
    target = HeadlessCtkApplication(create_run_config(start_cli=False))
    target.register_observers()
    return target


def snapshot(target: HeadlessCtkApplication) -> dict:
    filter_element = target.track_view_state.filter_element.get()
    restorer = target.filter_element_settings_restorer
    current = FilterElement(DateRange(None, None), None)
    return {
        "project": target.datastore.project,
        "tracks": len(target.track_repository.get_all()),
        "track files": target.track_file_repository.get_all(),
        "videos": [video.get_path() for video in target.video_repository.get_all()],
        "sections": target.section_repository.get_all(),
        "flows": target.flow_repository.get_all(),
        "events": list(target.event_repository.get_all()),
        "remark": target.remark_repository.get(),
        "first video start": target.videos_metadata.first_video_start,
        "classifications": target.tracks_metadata.classifications,
        "detection classes": target.tracks_metadata.detection_classifications,
        "first detection": target.tracks_metadata.first_detection_occurrence,
        "selected track": target.track_state.selected_track,
        "selected sections": target.section_state.selected_sections.get(),
        "selected flows": target.flow_state.selected_flows.get(),
        "last saved config": target.file_state.last_saved_config.get(),
        "selected videos": [
            video.get_path() for video in target.track_view_state.selected_videos.get()
        ],
        "filter date range": filter_element.date_range,
        "filter classes": filter_element.classifications,
        "restored date filter": restorer.restore_by_date_filter_setting(
            current
        ).date_range,
        "restored class filter": restorer.restore_by_class_filter_setting(
            current
        ).classifications,
        "orthophoto": target.current_orthophoto.get(),
        "key prefix": target.current_key_prefix.get(),
        "layers": [
            (layer.get_name(), layer.is_enabled())
            for layer_group in target.layers[0]
            for layer in layer_group.layers
        ],
    }


def change_everything(target: HeadlessCtkApplication, otconfig: Path) -> None:
    """Load a project and change what loading it did not set."""
    target.load_otconfig.load(otconfig)
    target.remark_repository.add("remark of the previous project")
    restorer = target.filter_element_settings_restorer
    restorer.save_by_date_filter_setting(
        FilterElement(DateRange(target.videos_metadata.first_video_start, None), None)
    )
    restorer.save_by_class_filter_setting(FilterElement(DateRange(None, None), {"car"}))
    target.create_events()
    for layer_group in target.layers[0]:
        for layer in layer_group.layers:
            layer.set_enabled(not layer.is_enabled())


@pytest.fixture
def otconfig(test_data_dir: Path, tmp_path: Path) -> Path:
    """Copy the project, so cache files written while loading stay out of the
    test data directory."""
    for suffix in [".otconfig", ".ottrk", ".mp4"]:
        shutil.copy(test_data_dir / f"{PROJECT}{suffix}", tmp_path)
    return tmp_path / f"{PROJECT}.otconfig"


@pytest.fixture
def other_otconfig(otconfig: Path) -> Path:
    """Another project on the same files, without sections, flows and remark."""
    content = json.loads(otconfig.read_text())
    content["project"]["name"] = "Other project"
    content["sections"] = []
    content["flows"] = []
    content["remark"] = ""
    other = otconfig.with_name("other.otconfig")
    other.write_text(json.dumps(content))
    return other


class TestStartNewProject:
    def test_leaves_nothing_of_the_previous_project(self, otconfig: Path) -> None:
        target = create_target()
        change_everything(target, otconfig)
        changed = snapshot(target)

        target.start_new_project()

        expected = snapshot(create_target())
        assert changed != expected, "precondition: a project has been changed"
        assert snapshot(target) == expected

    def test_resets_the_views(self, otconfig: Path) -> None:
        target = create_target()
        target.load_otconfig.load(otconfig)
        target.view_model.reset_mock()

        target.start_new_project()

        target.view_model.on_application_reset.assert_called_once()
        target.view_model.update_remark_view.assert_called_once()


class TestOpenProject:
    def test_leaves_nothing_of_the_previous_project(
        self, otconfig: Path, other_otconfig: Path
    ) -> None:
        target = create_target()
        change_everything(target, otconfig)

        target.load_otconfig.load(other_otconfig)

        fresh = create_target()
        fresh.load_otconfig.load(other_otconfig)
        expected = snapshot(fresh)
        assert snapshot(target) == expected

    def test_resets_the_views(self, otconfig: Path) -> None:
        target = create_target()

        target.load_otconfig.load(otconfig)

        target.view_model.on_application_reset.assert_called_once()

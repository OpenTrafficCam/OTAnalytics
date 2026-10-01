"""Tests that the buttons needing a background accept an Orthophoto as one.

A project of Geo-only Track Files has no Video, only its Orthophoto. Sections are
drawn on it and the frame and event navigation step through its tracks, so those
buttons must not wait for a Video that never comes.
"""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.application.state import CurrentOrthophoto
from OTAnalytics.domain.orthophoto import Orthophoto
from OTAnalytics.domain.video import Video

ORTHOPHOTO = Orthophoto(Path("site/map2.tiff"))


@dataclass
class Given:
    application: Mock
    current_orthophoto: CurrentOrthophoto
    frame_sections: Mock
    frame_video_control: Mock


def create_given() -> Given:
    application = Mock()
    application.action_state.action_running.get.return_value = False
    application.get_all_videos.return_value = []
    application.section_state.selected_sections.get.return_value = []
    application.get_all_sections.return_value = []
    application.get_all_flows.return_value = []
    application.flow_state.selected_flows.get.return_value = []
    application.get_selected_videos.return_value = []
    return Given(
        application=application,
        current_orthophoto=CurrentOrthophoto(),
        frame_sections=Mock(spec=AbstractFrame),
        frame_video_control=Mock(spec=AbstractFrame),
    )


def setup_with_orthophoto(given: Given) -> Given:
    given.current_orthophoto.set(ORTHOPHOTO)
    return given


def setup_with_video(given: Given) -> Given:
    given.application.get_all_videos.return_value = [Mock(spec=Video)]
    return given


def create_target(given: Given) -> DummyViewModel:
    target = DummyViewModel(
        application=given.application,
        ui_factory=Mock(),
        flow_parser=Mock(),
        name_generator=Mock(),
        event_list_export_formats={},
        show_svz=False,
        add_new_section=Mock(),
        update_section_coordinates=Mock(),
        provide_track_files=Mock(),
        provide_video_files=Mock(),
        current_orthophoto=given.current_orthophoto,
    )
    _inject_other_frames(target)
    target.set_video_control_frame(given.frame_video_control)
    target.set_sections_frame(given.frame_sections)
    return target


def _inject_other_frames(target: DummyViewModel) -> None:
    """Every frame a button refresh touches, beyond the two under test."""
    target.set_tracks_frame(Mock())
    target.set_offset_frame(Mock())
    target.set_video_frame(Mock())
    target.set_frame_project(Mock())
    target.set_flows_frame(Mock())
    target.set_analysis_frame(Mock())
    target.set_filter_frame(Mock())


def last_add_sections_enabled(given: Given) -> bool:
    return given.frame_sections.set_enabled_add_buttons.call_args.args[0]


def last_video_control_enabled(given: Given) -> bool:
    return given.frame_video_control.set_enabled_general_buttons.call_args.args[0]


class TestSectionButtons:
    def test_disabled_without_video_or_orthophoto(self) -> None:
        given = create_given()

        create_target(given)

        assert last_add_sections_enabled(given) is False

    def test_enabled_with_a_video(self) -> None:
        given = setup_with_video(create_given())

        create_target(given)

        assert last_add_sections_enabled(given) is True

    def test_enabled_with_an_orthophoto(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10404"""
        given = setup_with_orthophoto(create_given())

        create_target(given)

        assert last_add_sections_enabled(given) is True

    def test_enabled_once_the_orthophoto_arrives(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10404"""
        given = create_given()
        target = create_target(given)
        given.current_orthophoto.set(ORTHOPHOTO)

        target.notify_orthophoto(ORTHOPHOTO)

        assert last_add_sections_enabled(given) is True


class TestVideoControlButtons:
    def test_enabled_once_the_orthophoto_arrives(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10404"""
        given = create_given()
        target = create_target(given)
        given.current_orthophoto.set(ORTHOPHOTO)

        target.notify_orthophoto(ORTHOPHOTO)

        assert last_video_control_enabled(given) is True

    def test_disabled_once_the_orthophoto_is_gone(self) -> None:
        given = setup_with_orthophoto(create_given())
        target = create_target(given)
        given.current_orthophoto.reset()

        target.notify_orthophoto(None)

        assert last_video_control_enabled(given) is False

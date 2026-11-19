"""Tests that the automatic track assignment is a session setting."""

from unittest.mock import Mock

from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel


def create_target() -> DummyViewModel:
    return DummyViewModel(
        application=Mock(),
        ui_factory=Mock(),
        flow_parser=Mock(),
        name_generator=Mock(),
        event_list_export_formats={},
        show_svz=False,
        add_new_section=Mock(),
        update_section_coordinates=Mock(),
        provide_track_files=Mock(),
        provide_video_files=Mock(),
        current_orthophoto=Mock(),
    )


class TestAutoAssignment:
    def test_is_on_by_default(self) -> None:
        assert create_target().get_auto_assignment() is True

    def test_can_be_turned_off(self) -> None:
        target = create_target()

        target.set_auto_assignment(False)

        assert target.get_auto_assignment() is False

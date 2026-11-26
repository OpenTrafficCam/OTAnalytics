"""Tests that the automatic track assignment is a session setting."""

import inspect
from unittest.mock import Mock

from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.adapter_ui.view_model import ViewModel


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

    def test_assigning_tracks_shows_no_message(self) -> None:
        """Automatic assignment runs after every edit and must not block."""
        target = create_target()
        application = Mock()
        application.get_all_flows.return_value = []
        ui_factory = Mock()
        notify_flows = Mock()
        target._application = application
        target._ui_factory = ui_factory
        target.notify_flows = notify_flows  # type: ignore[method-assign]

        target.assign_tracks()

        application.create_events.assert_called_once_with()
        ui_factory.minimal_info_box.assert_not_called()
        notify_flows.assert_called_once_with([])


class TestViewModelPort:
    def test_gains_no_abstract_methods_for_auto_assignment(self) -> None:
        """OTCloud implements the port; a new abstract method breaks it."""
        abstract = ViewModel.__abstractmethods__

        assert "set_auto_assignment" not in abstract
        assert "get_auto_assignment" not in abstract
        assert "assign_tracks" not in abstract
        assert not inspect.isabstract(ViewModel.assign_tracks)

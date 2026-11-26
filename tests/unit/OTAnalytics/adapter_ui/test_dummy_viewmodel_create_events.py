"""Tests that creating events keeps the ui informed about its progress."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.application.state import CurrentOrthophoto


def create_target(application: Mock, ui_factory: Mock) -> DummyViewModel:
    target = DummyViewModel(
        application=application,
        ui_factory=ui_factory,
        flow_parser=Mock(),
        name_generator=Mock(),
        event_list_export_formats={},
        show_svz=False,
        add_new_section=Mock(),
        update_section_coordinates=Mock(),
        provide_track_files=Mock(),
        provide_video_files=Mock(),
        current_orthophoto=CurrentOrthophoto(),
    )
    target.get_position = Mock(return_value=(0, 0))  # type: ignore[method-assign]
    return target


class TestCreateEventsAsync:
    async def test_closes_popup_if_creating_events_fails(self) -> None:
        application = Mock()
        application.create_events_async = AsyncMock(side_effect=ValueError("failed"))
        ui_factory = Mock()
        target = create_target(application, ui_factory)

        with pytest.raises(ValueError):
            await target.create_events_async()

        ui_factory.minimal_info_box.return_value.close.assert_called_once()

    @patch("OTAnalytics.adapter_ui.dummy_viewmodel.asyncio.sleep", new=AsyncMock())
    async def test_notifies_flows_and_reports_completion(self) -> None:
        application = Mock()
        application.create_events_async = AsyncMock()
        application.get_all_flows.return_value = []
        ui_factory = Mock()
        target = create_target(application, ui_factory)
        target.notify_flows = Mock()  # type: ignore[method-assign]

        await target.create_events_async()

        popup = ui_factory.minimal_info_box.return_value
        target.notify_flows.assert_called_once_with([])
        popup.update_message.assert_called_once_with(
            message="Creating events completed"
        )
        popup.close.assert_called_once()


class TestCreateEvents:
    @patch("OTAnalytics.adapter_ui.dummy_viewmodel.sleep")
    def test_notifies_flows_and_reports_completion(self, _: Mock) -> None:
        application = Mock()
        application.get_all_flows.return_value = []
        ui_factory = Mock()
        target = create_target(application, ui_factory)
        target.notify_flows = Mock()  # type: ignore[method-assign]

        target.create_events()

        popup = ui_factory.minimal_info_box.return_value
        application.create_events.assert_called_once()
        target.notify_flows.assert_called_once_with([])
        popup.update_message.assert_called_once_with(
            message="Creating events completed"
        )
        popup.close.assert_called_once()

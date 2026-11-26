"""Tests that creating events keeps the ui informed about its progress."""

from unittest.mock import AsyncMock, Mock

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

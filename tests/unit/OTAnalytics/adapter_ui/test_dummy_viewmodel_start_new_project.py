"""Tests that starting a new project asks the user before resetting anything."""

from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock

from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.application.state import CurrentOrthophoto


class TestStartNewProject:
    async def test_starts_a_new_project_when_confirmed(self) -> None:
        given = create_given(confirmed=True)
        target = create_target(given)

        await target.start_new_project()

        given.ui_factory.ask_for_confirmation.assert_awaited_once()
        given.application.start_new_project.assert_called_once()
        given.frame_project.update.assert_called()

    async def test_keeps_the_project_when_cancelled(self) -> None:
        given = create_given(confirmed=False)
        target = create_target(given)
        given.frame_project.reset_mock()

        await target.start_new_project()

        given.ui_factory.ask_for_confirmation.assert_awaited_once()
        given.application.start_new_project.assert_not_called()
        given.frame_project.update.assert_not_called()


@dataclass
class Given:
    application: Mock
    ui_factory: Mock
    frame_project: Mock


def create_given(confirmed: bool) -> Given:
    application = Mock()
    application._datastore.project.metadata = None
    ui_factory = Mock()
    ui_factory.ask_for_confirmation = AsyncMock(return_value=confirmed)
    return Given(application=application, ui_factory=ui_factory, frame_project=Mock())


def create_target(given: Given) -> DummyViewModel:
    target = DummyViewModel(
        application=given.application,
        ui_factory=given.ui_factory,
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
    target.set_frame_project(given.frame_project)
    target.set_svz_metadata_frame(Mock())
    return target

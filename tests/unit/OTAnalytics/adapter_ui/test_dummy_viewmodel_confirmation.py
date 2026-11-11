"""Tests that destructive actions ask for confirmation and can be canceled.

Loading a configuration and starting a new project discard the current
sections, flows and videos. The user must be able to cancel before anything is
discarded, and confirming must carry the action out.
"""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.adapter_ui.message_type import MessageType
from OTAnalytics.application.parser.config_parser import SubstitutedFile
from OTAnalytics.application.state import CurrentOrthophoto
from OTAnalytics.application.use_cases.cut_tracks_with_sections import CutTracksDto
from OTAnalytics.domain.track import TrackId

OTCONFIG_FILE = Path("folder/project.otconfig")
OTFLOW_FILE = Path("folder/project.otflow")


@dataclass
class Given:
    application: Mock
    ui_factory: Mock


def create_given(
    confirmed: bool, selected_file: Path = OTCONFIG_FILE, has_sections: bool = True
) -> Given:
    application = Mock()
    application.load_otconfig_async = AsyncMock()
    application.get_all_sections.return_value = [Mock()] if has_sections else []
    application.get_all_flows.return_value = []
    ui_factory = Mock()
    ui_factory.askopenfilename = AsyncMock(return_value=str(selected_file))
    ui_factory.ask_for_confirmation = AsyncMock(return_value=confirmed)
    return Given(application=application, ui_factory=ui_factory)


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
    # These drive injected widgets that are not part of what is tested here.
    target.show_current_project = Mock()  # type: ignore[method-assign]
    target.update_svz_metadata_view = Mock()  # type: ignore[method-assign]
    target.refresh_items_on_canvas = Mock()  # type: ignore[method-assign]
    return target


class TestLoadOtconfigConfirmation:
    async def test_cancel_prevents_loading(self) -> None:
        given = create_given(confirmed=False)
        target = create_target(given)

        await target.load_otconfig()

        given.ui_factory.ask_for_confirmation.assert_awaited_once()
        given.application.load_otconfig_async.assert_not_awaited()

    async def test_ok_loads(self) -> None:
        given = create_given(confirmed=True)
        target = create_target(given)

        await target.load_otconfig()

        given.ui_factory.ask_for_confirmation.assert_awaited_once()
        given.application.load_otconfig_async.assert_awaited_once_with(
            file=OTCONFIG_FILE
        )


class TestLoadOtflowConfirmation:
    async def test_cancel_prevents_loading(self) -> None:
        given = create_given(confirmed=False, selected_file=OTFLOW_FILE)
        target = create_target(given)

        await target.load_configuration()

        given.ui_factory.ask_for_confirmation.assert_awaited_once()
        given.application.load_otflow.assert_not_called()

    async def test_ok_loads(self) -> None:
        given = create_given(confirmed=True, selected_file=OTFLOW_FILE)
        target = create_target(given)

        await target.load_configuration()

        given.ui_factory.ask_for_confirmation.assert_awaited_once()
        given.application.load_otflow.assert_called_once_with(sections_file=OTFLOW_FILE)

    async def test_loads_without_asking_if_nothing_is_configured(self) -> None:
        given = create_given(
            confirmed=False, selected_file=OTFLOW_FILE, has_sections=False
        )
        target = create_target(given)

        await target.load_configuration()

        given.ui_factory.ask_for_confirmation.assert_not_awaited()
        given.application.load_otflow.assert_called_once_with(sections_file=OTFLOW_FILE)


class TestStartNewProjectConfirmation:
    async def test_cancel_prevents_reset(self) -> None:
        given = create_given(confirmed=False)
        target = create_target(given)

        await target.start_new_project()

        given.ui_factory.ask_for_confirmation.assert_awaited_once()
        given.application.start_new_project.assert_not_called()

    async def test_ok_resets(self) -> None:
        given = create_given(confirmed=True)
        target = create_target(given)

        await target.start_new_project()

        given.ui_factory.ask_for_confirmation.assert_awaited_once()
        given.application.start_new_project.assert_called_once()


class TestMessageTypes:
    async def test_failed_load_is_an_error(self) -> None:
        given = create_given(confirmed=True)
        given.application.load_otconfig_async.side_effect = FileNotFoundError("gone")
        target = create_target(given)

        await target.load_otconfig()

        assert (
            given.ui_factory.show_message.call_args.kwargs["message_type"]
            == MessageType.ERROR
        )

    def test_substituted_files_are_a_warning(self) -> None:
        given = create_given(confirmed=True)
        target = create_target(given)

        target.report_substituted_files(
            [SubstitutedFile(Path("a/one.ottrk"), Path("b/one.ottrk"))]
        )

        assert (
            given.ui_factory.show_message.call_args.kwargs["message_type"]
            == MessageType.WARNING
        )

    def test_successful_cut_is_an_info(self) -> None:
        given = create_given(confirmed=True)
        given.application.get_track_repository_size.return_value = 3
        target = create_target(given)

        target.on_tracks_cut(
            CutTracksDto(section="cutting", original_tracks=[TrackId("1")])
        )

        assert (
            given.ui_factory.show_message.call_args.kwargs["message_type"]
            == MessageType.INFO
        )

"""Tests that saving skips the file-picker for a project naming a key prefix.

Such a project arrived through an operator naming it (OP#10323 decision 1), not
through a picker, so there is nothing for a save dialog to offer: it always
re-saves to its own name and place.
"""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.use_cases.suggest_save_path import SavePathSuggestion

A_PREFIX = S3KeyPrefix("project-1/site-2/otcamera19")
SUGGESTED_PATH = Path("/user-source/project-1/site-2/otcamera19/my.otconfig")


@dataclass
class Given:
    application: Mock
    ui_factory: Mock


def create_given(key_prefix: S3KeyPrefix | None) -> Given:
    application = Mock()
    application.get_current_key_prefix.return_value = key_prefix
    application.suggest_save_path.return_value = SavePathSuggestion(
        save_directory=SUGGESTED_PATH.parent,
        file_stem=SUGGESTED_PATH.stem,
        context_file_type=None,
        file_type=".otconfig",
    )
    application.save_otconfig = AsyncMock()
    ui_factory = Mock()
    ui_factory.ask_for_save_file_path = AsyncMock()
    return Given(application=application, ui_factory=ui_factory)


def create_target(given: Given) -> DummyViewModel:
    return DummyViewModel(
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
    )


class TestSaveConfiguration:
    async def test_skips_the_dialog_when_project_names_a_key_prefix(self) -> None:
        given = create_given(A_PREFIX)
        target = create_target(given)

        await target.save_configuration()

        given.ui_factory.ask_for_save_file_path.assert_not_called()
        given.application.save_otconfig.assert_awaited_once_with(SUGGESTED_PATH)

    async def test_asks_the_dialog_when_project_names_no_key_prefix(self) -> None:
        given = create_given(None)
        given.ui_factory.ask_for_save_file_path.return_value = SUGGESTED_PATH
        target = create_target(given)

        await target.save_configuration()

        given.ui_factory.ask_for_save_file_path.assert_awaited_once()
        given.application.save_otconfig.assert_awaited_once_with(SUGGESTED_PATH)


class TestSaveOtconfig:
    async def test_skips_the_dialog_when_project_names_a_key_prefix(self) -> None:
        given = create_given(A_PREFIX)
        target = create_target(given)

        await target.save_otconfig()

        given.ui_factory.ask_for_save_file_path.assert_not_called()
        given.application.save_otconfig.assert_awaited_once_with(SUGGESTED_PATH)

    async def test_asks_the_dialog_when_project_names_no_key_prefix(self) -> None:
        given = create_given(None)
        given.ui_factory.ask_for_save_file_path.return_value = SUGGESTED_PATH
        target = create_target(given)

        await target.save_otconfig()

        given.ui_factory.ask_for_save_file_path.assert_awaited_once()
        given.application.save_otconfig.assert_awaited_once_with(SUGGESTED_PATH)

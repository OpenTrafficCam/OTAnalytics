"""Tests that loading an otconfig explains what went wrong.

Loading had no error handling at all: anything the parser raised travelled out
of `load_otconfig` and reached the browser as a traceback. Saving has explained
its failures since it was written; loading now does the same.
"""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from OTAnalytics.adapter_ui.dummy_viewmodel import (
    MESSAGE_CONFIGURATION_NOT_LOADED,
    DummyViewModel,
)
from OTAnalytics.application.parser.config_parser import SubstitutedFile
from OTAnalytics.application.use_cases.load_otconfig import UnableToLoadOtconfigFile

OTCONFIG_FILE = Path("folder/project.otconfig")


@dataclass
class Given:
    application: Mock
    ui_factory: Mock


def create_given(load_error: Exception | None = None) -> Given:
    application = Mock()
    application.load_otconfig_async = AsyncMock(side_effect=load_error)
    ui_factory = Mock()
    ui_factory.askopenfilename = AsyncMock(return_value=str(OTCONFIG_FILE))
    # The confirmation box that precedes every load.
    ui_factory.info_box.return_value = Mock(canceled=False)
    return Given(application=application, ui_factory=ui_factory)


def create_target(given: Given) -> DummyViewModel:
    """A view model with the post-load view refresh stubbed out.

    `show_current_project` and `update_svz_metadata_view` drive injected
    widgets and raise `MissingInjectedInstanceError` without a built ui, which
    has nothing to do with how a load failure is reported.
    """
    target = _build(given)
    target.show_current_project = Mock()  # type: ignore[method-assign]
    target.update_svz_metadata_view = Mock()  # type: ignore[method-assign]
    return target


def _build(given: Given) -> DummyViewModel:
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


def reported_messages(given: Given) -> list[str]:
    return [
        call.kwargs["message"]
        for call in given.ui_factory.info_box.call_args_list
        if "message" in call.kwargs
    ]


class TestLoadOtconfig:
    async def test_explains_a_failed_load_instead_of_raising(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10321"""
        given = create_given(load_error=UnableToLoadOtconfigFile("sections clash"))
        target = create_target(given)

        await target.load_otconfig()

        assert any(
            MESSAGE_CONFIGURATION_NOT_LOADED in message
            for message in reported_messages(given)
        )

    async def test_explains_a_missing_file_instead_of_raising(self) -> None:
        """A reference that resolves nowhere is the common case, and today it
        reaches the browser as a `FileNotFoundError` traceback.

        #Requirement https://openproject.platomo.de/wp/10321
        """
        given = create_given(load_error=FileNotFoundError("no such track file"))
        target = create_target(given)

        await target.load_otconfig()

        assert any(
            "no such track file" in message for message in reported_messages(given)
        )

    async def test_names_the_underlying_cause_not_the_wrapper(self) -> None:
        """`UnableToLoadOtconfigFile` carries a fixed string and keeps the real
        reason in `__cause__`, so the wrapper alone tells the user nothing.

        #Requirement https://openproject.platomo.de/wp/10321
        """
        wrapper = UnableToLoadOtconfigFile(
            "Error while loading otconfig file. Abort loading!"
        )
        wrapper.__cause__ = FileNotFoundError("clip.ottrk is missing")
        given = create_given(load_error=wrapper)
        target = create_target(given)

        await target.load_otconfig()

        assert any(
            "clip.ottrk is missing" in message for message in reported_messages(given)
        )

    async def test_does_not_refresh_the_view_after_a_failed_load(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10321"""
        given = create_given(load_error=UnableToLoadOtconfigFile("sections clash"))
        target = create_target(given)

        await target.load_otconfig()

        target.show_current_project.assert_not_called()  # type: ignore[attr-defined]

    async def test_refreshes_the_view_after_a_successful_load(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10321"""
        given = create_given()
        target = create_target(given)

        await target.load_otconfig()

        given.application.load_otconfig_async.assert_awaited_once_with(
            file=OTCONFIG_FILE
        )
        target.show_current_project.assert_called_once()  # type: ignore[attr-defined]
        assert not any(
            MESSAGE_CONFIGURATION_NOT_LOADED in message
            for message in reported_messages(given)
        )


class TestReportSubstitutedFiles:
    def test_names_what_was_asked_for_and_what_was_used(self) -> None:
        """The user has to be able to tell which data the project now holds.

        #Requirement https://openproject.platomo.de/wp/10321
        """
        given = create_given()
        target = create_target(given)

        target.report_substituted_files(
            [
                SubstitutedFile(
                    requested=Path("moved/clip.ottrk"), used=Path("here/clip.ottrk")
                )
            ]
        )

        reported = reported_messages(given)
        assert len(reported) == 1
        assert "moved/clip.ottrk" in reported[0]
        assert "here/clip.ottrk" in reported[0]

    def test_reports_every_substitution_in_one_message(self) -> None:
        """A project with many rebound files must not raise many boxes.

        #Requirement https://openproject.platomo.de/wp/10321
        """
        given = create_given()
        target = create_target(given)

        target.report_substituted_files(
            [
                SubstitutedFile(Path("a/one.ottrk"), Path("b/one.ottrk")),
                SubstitutedFile(Path("a/two.mp4"), Path("b/two.mp4")),
            ]
        )

        reported = reported_messages(given)
        assert len(reported) == 1
        assert "one.ottrk" in reported[0]
        assert "two.mp4" in reported[0]

    def test_says_nothing_when_there_was_no_substitution(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10321"""
        given = create_given()
        target = create_target(given)

        target.report_substituted_files([])

        assert reported_messages(given) == []


class TestReportingCannotBreakALoad:
    def test_a_report_that_cannot_be_shown_does_not_abort_the_load(self) -> None:
        """Preloading a `--config` file happens before any browser client exists.

        NiceGUI's `ui.notify` resolves `context.client` through the slot stack
        and raises `RuntimeError` when that stack is empty, so reporting a
        substitution during the startup preload would otherwise propagate out
        of the parse and take the whole server down.

        #Requirement https://openproject.platomo.de/wp/10321
        """
        given = create_given()
        given.ui_factory.info_box.side_effect = RuntimeError(
            "The current slot cannot be determined"
        )
        target = create_target(given)

        target.report_substituted_files(
            [SubstitutedFile(Path("a/one.ottrk"), Path("b/one.ottrk"))]
        )

    async def test_a_failure_report_that_cannot_be_shown_still_returns(self) -> None:
        """#Requirement https://openproject.platomo.de/wp/10321"""
        given = create_given(load_error=FileNotFoundError("no such track file"))
        given.ui_factory.info_box.side_effect = [
            Mock(canceled=False),
            RuntimeError("The current slot cannot be determined"),
        ]
        target = create_target(given)

        await target.load_otconfig()

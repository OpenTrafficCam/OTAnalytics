"""Tests the workflow accordion of the configuration bar."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from nicegui import ui
from nicegui.element import Element
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import (
    ConfigurationBarKeys,
    ResourceManager,
    SvzMetadataKeys,
)
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.track_repository import TrackRepositoryEvent
from OTAnalytics.plugin_datastore.python_track_store import PythonTrackIdSet
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.container import (
    MARKER_GROUP_ANALYSIS,
    MARKER_GROUP_PROJECT,
    MARKER_GROUP_SVZ,
    MARKER_TAB_FLOW,
    MARKER_TAB_SECTION,
    ConfigurationBar,
)

ENDPOINT = "/test-configuration-bar"
PROJECT = "project form"
STATIC_ANALYSIS = "static analysis config form"
SVZ = "svz metadata form"
TRACKS = "track form"
REMARK = "remark form"
SECTIONS = "sections form"
FLOWS = "flow form"
ANALYSIS = "analysis form"
GROUP_MARKERS = {
    MARKER_GROUP_PROJECT,
    MARKER_GROUP_SVZ,
    MARKER_TAB_SECTION,
    MARKER_TAB_FLOW,
    MARKER_GROUP_ANALYSIS,
}


def part(text: str) -> Mock:
    part = Mock()
    part.build.side_effect = lambda: ui.label(text)
    return part


def create_view_model(
    show_svz: bool = True, track_files: set[Path] | None = None
) -> Mock:
    view_model = Mock()
    view_model.show_svz.return_value = show_svz
    view_model.get_all_track_files.return_value = track_files or set()
    view_model.get_all_videos.return_value = []
    view_model.get_all_sections.return_value = []
    view_model.get_all_flows.return_value = []
    view_model.get_tracks_assigned_to_each_flow.return_value = {}
    return view_model


def create_target(
    resource_manager: ResourceManager, view_model: Mock
) -> ConfigurationBar:
    return ConfigurationBar(
        resource_manager=resource_manager,
        view_model=view_model,
        project_form=part(PROJECT),
        static_analysis_config_form=part(STATIC_ANALYSIS),
        svz_metadata_form=part(SVZ),
        track_form=part(TRACKS),
        remark_form=part(REMARK),
        sections_form=part(SECTIONS),
        flow_form=part(FLOWS),
        analysis_form=part(ANALYSIS),
    )


async def open_page(user: User, target: ConfigurationBar) -> None:
    @ui.page(ENDPOINT)
    def page() -> None:
        target.build()

    await user.open(ENDPOINT)


def group_of(user: User, text: str) -> str:
    element: Element = user.find(text).elements.pop()
    while (slot := element.parent_slot) is not None:
        element = slot.parent
        if markers := GROUP_MARKERS & set(element._markers):
            return markers.pop()
    raise AssertionError(f"{text} is not in a group")


def group(user: User, marker: str) -> ui.expansion:
    element = user.find(marker=marker).elements.pop()
    assert isinstance(element, ui.expansion)
    return element


class TestConfigurationBar:
    @pytest.mark.parametrize(
        "text, marker",
        [
            (PROJECT, MARKER_GROUP_PROJECT),
            (TRACKS, MARKER_GROUP_PROJECT),
            (REMARK, MARKER_GROUP_PROJECT),
            (SVZ, MARKER_GROUP_SVZ),
            (SECTIONS, MARKER_TAB_SECTION),
            (FLOWS, MARKER_TAB_FLOW),
            (STATIC_ANALYSIS, MARKER_GROUP_ANALYSIS),
            (ANALYSIS, MARKER_GROUP_ANALYSIS),
        ],
    )
    async def test_builds_form_in_its_group(
        self, user: User, resource_manager: ResourceManager, text: str, marker: str
    ) -> None:
        target = create_target(resource_manager, create_view_model())

        await open_page(user, target)

        assert group_of(user, text) == marker

    async def test_hides_svz_group_without_show_svz(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = create_target(resource_manager, create_view_model(show_svz=False))

        await open_page(user, target)

        await user.should_not_see(marker=MARKER_GROUP_SVZ)
        await user.should_not_see(SVZ)

    async def test_empty_project_opens_project_group(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = create_target(resource_manager, create_view_model())

        await open_page(user, target)

        assert group(user, MARKER_GROUP_PROJECT).value is True
        assert group(user, MARKER_TAB_SECTION).value is False
        assert group(user, MARKER_TAB_FLOW).value is False

    async def test_loaded_tracks_open_sections_and_flows(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        view_model = create_view_model(track_files={Path("tracks.ottrk")})
        target = create_target(resource_manager, view_model)

        await open_page(user, target)

        assert group(user, MARKER_TAB_SECTION).value is True
        assert group(user, MARKER_TAB_FLOW).value is True

    async def test_adding_tracks_opens_sections_and_flows(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = create_target(resource_manager, create_view_model())
        await open_page(user, target)

        target.notify_tracks(
            TrackRepositoryEvent.create_added(PythonTrackIdSet({TrackId("1")}))
        )

        assert group(user, MARKER_GROUP_PROJECT).value is True
        assert group(user, MARKER_TAB_SECTION).value is True
        assert group(user, MARKER_TAB_FLOW).value is True

    async def test_groups_open_independently(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = create_target(resource_manager, create_view_model())
        await open_page(user, target)

        group(user, MARKER_TAB_SECTION).set_value(True)
        group(user, MARKER_TAB_FLOW).set_value(True)

        assert group(user, MARKER_TAB_SECTION).value is True
        assert group(user, MARKER_TAB_FLOW).value is True

    def test_tracks_added_before_build_are_ignored(
        self, resource_manager: ResourceManager
    ) -> None:
        target = create_target(resource_manager, create_view_model())

        target.notify_tracks(
            TrackRepositoryEvent.create_added(PythonTrackIdSet({TrackId("1")}))
        )


def header_texts(user: User, marker: str) -> list[str]:
    """Texts in the header of a group, in order."""
    expansion = group(user, marker)
    header = expansion.slots["header"]
    texts: list[str] = []

    def collect(element: Element) -> None:
        if isinstance(element, ui.label):
            texts.append(element.text)
        for child in element.default_slot.children:
            collect(child)

    for child in header.children:
        collect(child)
    return texts


class TestGroupHeaders:
    @pytest.mark.parametrize(
        "marker, step, title",
        [
            (MARKER_GROUP_PROJECT, "1", ConfigurationBarKeys.LABEL_GROUP_PROJECT),
            (MARKER_GROUP_SVZ, "SVZ", SvzMetadataKeys.LABEL_SVZ_METADATA_FORM_HEADER),
            (MARKER_TAB_SECTION, "2", ConfigurationBarKeys.LABEL_GROUP_SECTIONS),
            (MARKER_TAB_FLOW, "3", ConfigurationBarKeys.LABEL_GROUP_FLOWS),
            (MARKER_GROUP_ANALYSIS, "4", ConfigurationBarKeys.LABEL_GROUP_ANALYSIS),
        ],
    )
    async def test_show_step_and_title(
        self,
        user: User,
        resource_manager: ResourceManager,
        marker: str,
        step: str,
        title: ConfigurationBarKeys | SvzMetadataKeys,
    ) -> None:
        await open_page(user, create_target(resource_manager, create_view_model()))

        texts = header_texts(user, marker)

        assert texts[:2] == [step, resource_manager.get(title)]

    async def test_summarize_the_project(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        view_model = create_view_model(track_files={Path("a.ottrk"), Path("b.ottrk")})
        view_model.get_all_videos.return_value = [Mock()]
        view_model.get_all_sections.return_value = [Mock()] * 5
        view_model.get_all_flows.return_value = [Mock()] * 6
        view_model.get_tracks_assigned_to_each_flow.return_value = {"a": 3, "b": 4}

        await open_page(user, create_target(resource_manager, view_model))

        assert header_texts(user, MARKER_GROUP_PROJECT)[2] == "2 track files · 1 videos"
        assert header_texts(user, MARKER_TAB_SECTION)[2] == "5 sections"
        assert header_texts(user, MARKER_TAB_FLOW)[2] == "6 flows · 7 tracks assigned"

    async def test_summaries_follow_changes(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        view_model = create_view_model()
        target = create_target(resource_manager, view_model)
        await open_page(user, target)
        view_model.get_all_sections.return_value = [Mock()] * 2
        view_model.get_all_flows.return_value = [Mock()]
        view_model.get_all_videos.return_value = [Mock()] * 3

        target.notify_sections(Mock())
        target.notify_flows([])
        target.notify_videos([])

        assert header_texts(user, MARKER_TAB_SECTION)[2] == "2 sections"
        assert header_texts(user, MARKER_TAB_FLOW)[2] == "1 flows · 0 tracks assigned"
        assert header_texts(user, MARKER_GROUP_PROJECT)[2] == "0 track files · 3 videos"

    def test_changes_before_build_are_ignored(
        self, resource_manager: ResourceManager
    ) -> None:
        target = create_target(resource_manager, create_view_model())

        target.notify_sections(Mock())
        target.notify_flows([])
        target.notify_videos([])
        target.notify_events(Mock())

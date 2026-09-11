"""Tests that a rebound file reference is reported, not only logged.

When a track or video file is not where the otconfig says, the parser loads a
same-named file sitting next to the otconfig instead. That fallback is
deliberate (138ed22a) and stays; the defect is that its only signal was a log
warning, so the project looked correctly loaded while referencing data the user
never named.

An ottrk's name encodes camera and instant, so a same-named file is the same
camera at the same moment -- but re-detected or re-tracked output legitimately
reuses the name with different detections.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence
from unittest.mock import Mock

import pytest

from OTAnalytics.application.parser.config_parser import SubstitutedFile
from OTAnalytics.domain import flow, section, video
from OTAnalytics.plugin_parser.otconfig_parser import (
    ANALYSIS,
    COUNT_INTERVALS,
    DO_COUNTING,
    DO_EVENTS,
    EVENT_FORMATS,
    EXPORT,
    LOGFILE,
    NUM_PROCESSES,
    PATH,
    PROJECT,
    SAVE_NAME,
    SAVE_SUFFIX,
    TRACKS,
    OtConfigParser,
)

VIDEO_IN_CONFIG = Path("subfolder/clip.mp4")
TRACKS_IN_CONFIG = Path("subfolder/clip.ottrk")


@dataclass
class Given:
    base_folder: Path
    video_parser: Mock
    flow_parser: Mock
    content: dict
    reports: list[Sequence[SubstitutedFile]] = field(default_factory=list)


def create_given(
    base_folder: Path,
    video_in_config: Path = VIDEO_IN_CONFIG,
    tracks_in_config: Path = TRACKS_IN_CONFIG,
    place_beside_config: bool = True,
    place_at_reference: bool = False,
) -> Given:
    if place_beside_config:
        (base_folder / video_in_config.name).touch()
        (base_folder / tracks_in_config.name).touch()
    if place_at_reference:
        for referenced in (video_in_config, tracks_in_config):
            (base_folder / referenced).parent.mkdir(parents=True, exist_ok=True)
            (base_folder / referenced).touch()

    video_parser = Mock()
    video_parser.parse_list.return_value = ()
    flow_parser = Mock()
    flow_parser.parse_content.return_value = ((), ())
    return Given(
        base_folder=base_folder,
        video_parser=video_parser,
        flow_parser=flow_parser,
        content=_content(video_in_config, tracks_in_config),
    )


def _content(video_in_config: Path, tracks_in_config: Path) -> dict:
    return {
        PROJECT: {"name": "My Project", "start_date": 1577836800},
        video.VIDEOS: [{PATH: str(video_in_config)}],
        ANALYSIS: {
            DO_EVENTS: True,
            DO_COUNTING: True,
            TRACKS: [str(tracks_in_config)],
            EXPORT: {
                SAVE_NAME: "name",
                SAVE_SUFFIX: "suffix",
                EVENT_FORMATS: ["csv"],
                COUNT_INTERVALS: [15],
            },
            NUM_PROCESSES: 1,
            LOGFILE: "logs",
        },
        section.SECTIONS: [],
        flow.FLOWS: [],
    }


def create_target(given: Given) -> OtConfigParser:
    format_fixer = Mock()
    format_fixer.fix.side_effect = lambda content: content
    target = OtConfigParser(
        format_fixer=format_fixer,
        video_parser=given.video_parser,
        flow_parser=given.flow_parser,
    )
    target.register(given.reports.append)
    return target


@pytest.fixture
def base_folder(tmp_path: Path) -> Path:
    return tmp_path


class TestSubstitutionIsReported:
    def test_reports_both_a_video_and_a_track_file(self, base_folder: Path) -> None:
        """#Requirement https://openproject.platomo.de/wp/10321"""
        given = create_given(base_folder)
        target = create_target(given)

        target.parse_from_dict(given.content, base_folder)

        assert given.reports == [
            [
                SubstitutedFile(
                    requested=base_folder / VIDEO_IN_CONFIG,
                    used=base_folder / VIDEO_IN_CONFIG.name,
                ),
                SubstitutedFile(
                    requested=base_folder / TRACKS_IN_CONFIG,
                    used=base_folder / TRACKS_IN_CONFIG.name,
                ),
            ]
        ]

    def test_reports_nothing_when_every_reference_resolves(
        self, base_folder: Path
    ) -> None:
        """A correctly resolving multi-folder project (OP#10279) must stay silent.

        #Requirement https://openproject.platomo.de/wp/10321
        """
        given = create_given(
            base_folder, place_beside_config=False, place_at_reference=True
        )
        target = create_target(given)

        target.parse_from_dict(given.content, base_folder)

        assert given.reports == []

    def test_still_raises_when_there_is_no_neighbour(self, base_folder: Path) -> None:
        """#Requirement https://openproject.platomo.de/wp/10321"""
        given = create_given(base_folder, place_beside_config=False)
        target = create_target(given)

        with pytest.raises(FileNotFoundError):
            target.parse_from_dict(given.content, base_folder)

    def test_reports_only_the_reference_that_was_rebound(
        self, base_folder: Path
    ) -> None:
        """Videos and track files must behave identically, so a project with one
        of each resolving correctly reports only the other.

        #Requirement https://openproject.platomo.de/wp/10321
        """
        given = create_given(base_folder)
        (base_folder / VIDEO_IN_CONFIG).parent.mkdir(parents=True, exist_ok=True)
        (base_folder / VIDEO_IN_CONFIG).touch()
        target = create_target(given)

        target.parse_from_dict(given.content, base_folder)

        assert given.reports == [
            [
                SubstitutedFile(
                    requested=base_folder / TRACKS_IN_CONFIG,
                    used=base_folder / TRACKS_IN_CONFIG.name,
                )
            ]
        ]

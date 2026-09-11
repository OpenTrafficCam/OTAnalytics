"""Tests that an otconfig declares where its data lives.

ADR 0004: the file carries one top-level `s3_key_prefix`, and it is the sole
source of the prefix an instance reads from. The key is absent from every
otconfig written before this change, so a missing key must parse to `None`
rather than fail -- refusing such a file in s3 mode is the job of
ValidateProjectLocation on load, not of the parser.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.key_prefix import InvalidS3KeyPrefix, S3KeyPrefix
from OTAnalytics.application.project import Project
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
    PROJECT,
    S3_KEY_PREFIX,
    SAVE_NAME,
    SAVE_SUFFIX,
    TRACKS,
    OtConfigParser,
)

A_PREFIX = "project-1/site-2/otcamera19/"


@dataclass
class Given:
    base_folder: Path
    content: dict


def create_given(base_folder: Path, prefix: str | None = A_PREFIX) -> Given:
    content = {
        PROJECT: {"name": "My Project", "start_date": 1577836800},
        video.VIDEOS: [],
        ANALYSIS: {
            DO_EVENTS: True,
            DO_COUNTING: True,
            TRACKS: [],
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
    if prefix is not None:
        content[S3_KEY_PREFIX] = prefix
    return Given(base_folder=base_folder, content=content)


def create_project() -> Project:
    return Project(name="My Project", start_date=datetime(2020, 1, 1), metadata=None)


def create_target(given: Given) -> OtConfigParser:
    format_fixer = Mock()
    format_fixer.fix.side_effect = lambda content: content
    video_parser = Mock()
    video_parser.parse_list.return_value = ()
    video_parser.convert.return_value = {video.VIDEOS: []}
    flow_parser = Mock()
    flow_parser.parse_content.return_value = ((), ())
    flow_parser.convert.return_value = {section.SECTIONS: [], flow.FLOWS: []}
    return OtConfigParser(
        format_fixer=format_fixer,
        video_parser=video_parser,
        flow_parser=flow_parser,
    )


class TestParseKeyPrefix:
    def test_reads_the_declared_prefix(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)

        config = create_target(given).parse_from_dict(given.content, tmp_path)

        assert config.s3_key_prefix == S3KeyPrefix(A_PREFIX)

    def test_an_otconfig_without_the_key_declares_no_prefix(
        self, tmp_path: Path
    ) -> None:
        given = create_given(tmp_path, prefix=None)

        config = create_target(given).parse_from_dict(given.content, tmp_path)

        assert config.s3_key_prefix is None

    def test_a_saved_project_reopens_under_the_same_prefix(
        self, tmp_path: Path
    ) -> None:
        """The save and the load have to be exact inverses: slice 7 reopens a
        project from the file this writes.
        """
        given = create_given(tmp_path)
        target = create_target(given)
        written = target.convert(
            project=create_project(),
            video_files=[],
            track_files=[],
            sections=[],
            flows=[],
            file=tmp_path / "config.otconfig",
            remark=None,
            s3_key_prefix=S3KeyPrefix(A_PREFIX),
        )

        assert target.parse_from_dict(written, tmp_path).s3_key_prefix == S3KeyPrefix(
            A_PREFIX
        )

    def test_a_project_with_no_prefix_writes_no_key(self, tmp_path: Path) -> None:
        """A local-mode file must stay exactly as it is today. A key written as
        null would also be read back as `None`, but it would appear in every
        otconfig OTCloud has ever seen.
        """
        given = create_given(tmp_path)

        written = create_target(given).convert(
            project=create_project(),
            video_files=[],
            track_files=[],
            sections=[],
            flows=[],
            file=tmp_path / "config.otconfig",
            remark=None,
            s3_key_prefix=None,
        )

        assert S3_KEY_PREFIX not in written

    def test_refuses_a_key_that_names_nothing(self, tmp_path: Path) -> None:
        given = create_given(tmp_path, prefix="")

        with pytest.raises(InvalidS3KeyPrefix):
            create_target(given).parse_from_dict(given.content, tmp_path)

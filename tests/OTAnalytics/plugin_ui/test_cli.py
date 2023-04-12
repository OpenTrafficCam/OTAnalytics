import sys
from pathlib import Path
from shutil import copy2, rmtree
from unittest.mock import Mock, patch

import pytest

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.plugin_ui.cli import (
    EVENTLIST_FILE_TYPE,
    TRACK_FILE_TYPE,
    CliArgumentParser,
    CliArguments,
    CliParseError,
    InvalidSectionFileType,
    OTAnalyticsCli,
    SectionsFileDoesNotExist,
)
from tests.conftest import YieldFixture


@pytest.fixture
def temp_tracks_directory(
    test_data_tmp_dir: Path, ottrk_path: Path
) -> YieldFixture[Path]:
    tracks = test_data_tmp_dir / "tracks"
    tracks.mkdir()
    copy2(src=ottrk_path, dst=tracks / f"track_1.{TRACK_FILE_TYPE}")
    copy2(src=ottrk_path, dst=tracks / f"track_2.{TRACK_FILE_TYPE}")

    sub_directory = tracks / "sub_directory"
    sub_directory.mkdir()
    copy2(src=ottrk_path, dst=sub_directory / f"track_3.{TRACK_FILE_TYPE}")
    copy2(src=ottrk_path, dst=sub_directory / f"track_4.{TRACK_FILE_TYPE}")
    yield tracks
    rmtree(tracks)


@pytest.fixture
def temp_ottrk(test_data_tmp_dir: Path, ottrk_path: Path) -> YieldFixture[Path]:
    file_name = ottrk_path.name
    temp_ottrk = test_data_tmp_dir / file_name
    copy2(src=ottrk_path, dst=temp_ottrk)
    yield temp_ottrk
    temp_ottrk.unlink()


class TestCliArgumentParser:
    def test_parse_with_valid_cli_args(self) -> None:
        track_file_1 = f"track_file_1.{TRACK_FILE_TYPE}"
        track_file_2 = f"track_file_2.{TRACK_FILE_TYPE}"
        sections_file = "section_file.otflow"

        cli_args: list[str] = [
            "path",
            "--cli",
            "--ottrks",
            track_file_1,
            track_file_2,
            "--otflow",
            sections_file,
        ]
        with patch.object(sys, "argv", cli_args):
            parser = CliArgumentParser()
            args = parser.parse()
            assert args == CliArguments(
                True, [track_file_1, track_file_2], sections_file
            )


class TestOTAnalyticsCli:
    def test_init(self) -> None:
        mock_otanalytics_app = Mock(spec=OTAnalyticsApplication)
        cli_args = CliArguments(
            True, [f"track_file.{TRACK_FILE_TYPE}"], "sections_file.otflow"
        )
        cli = OTAnalyticsCli(mock_otanalytics_app, cli_args)
        assert cli.cli_args == cli_args
        assert cli._application == mock_otanalytics_app

    def test_init_empty_tracks_cli_arg(self) -> None:
        mock_otanalytics_app = Mock(spec=OTAnalyticsApplication)
        cli_args = CliArguments(
            True, track_files=[], sections_file="section_file.otflow"
        )
        with pytest.raises(CliParseError, match=r"No ottrk files passed.*"):
            OTAnalyticsCli(mock_otanalytics_app, cli_args)

    def test_init_no_section_cli_arg(self) -> None:
        mock_otanalytics_app = Mock(spec=OTAnalyticsApplication)
        cli_args = CliArguments(
            True, track_files=[f"ottrk_file.{TRACK_FILE_TYPE}"], sections_file=""
        )
        with pytest.raises(CliParseError, match=r"No otflow file passed.*"):
            OTAnalyticsCli(mock_otanalytics_app, cli_args)

    def test_validate_cli_args_no_tracks(self) -> None:
        cli_args = CliArguments(True, [], "section.otflow")
        with pytest.raises(CliParseError, match=r"No ottrk files passed.*"):
            OTAnalyticsCli._validate_cli_args(cli_args)

    def test_validate_cli_args_no_section(self) -> None:
        cli_args = CliArguments(True, [f"track.{TRACK_FILE_TYPE}"], "")
        with pytest.raises(CliParseError, match=r"No otflow file passed.*"):
            OTAnalyticsCli._validate_cli_args(cli_args)

    def test_parse_ottrk_files_with_subdirs(self, temp_tracks_directory: Path) -> None:
        tracks = OTAnalyticsCli._parse_ottrk_files([str(temp_tracks_directory)])
        assert temp_tracks_directory / f"track_1.{TRACK_FILE_TYPE}" in tracks
        assert temp_tracks_directory / f"track_2.{TRACK_FILE_TYPE}" in tracks
        assert (
            temp_tracks_directory / f"sub_directory/track_3.{TRACK_FILE_TYPE}" in tracks
        )
        assert (
            temp_tracks_directory / f"sub_directory/track_4.{TRACK_FILE_TYPE}" in tracks
        )

    def test_parse_ottrk_files_no_existing_files(self) -> None:
        track_1 = f"path/to/foo.{TRACK_FILE_TYPE}"
        track_2 = f"path/to/bar.{TRACK_FILE_TYPE}"

        parsed_tracks = OTAnalyticsCli._parse_ottrk_files([track_1, track_2])
        assert not parsed_tracks

    def test_parse_ottrk_files_single_file(self, temp_ottrk: Path) -> None:
        parsed_tracks = OTAnalyticsCli._parse_ottrk_files([str(temp_ottrk)])
        assert temp_ottrk in parsed_tracks

    def test_parse_ottrk_files_multiple_files(
        self, temp_ottrk: Path, temp_tracks_directory: Path
    ) -> None:
        parsed_tracks = OTAnalyticsCli._parse_ottrk_files(
            [str(temp_ottrk), str(temp_tracks_directory)]
        )
        assert temp_ottrk in parsed_tracks
        assert temp_tracks_directory / f"track_1.{TRACK_FILE_TYPE}" in parsed_tracks
        assert temp_tracks_directory / f"track_2.{TRACK_FILE_TYPE}" in parsed_tracks
        assert (
            temp_tracks_directory / f"sub_directory/track_3.{TRACK_FILE_TYPE}"
            in parsed_tracks
        )
        assert (
            temp_tracks_directory / f"sub_directory/track_4.{TRACK_FILE_TYPE}"
            in parsed_tracks
        )

    def test_parse_sections_file(self, otsection_file: Path) -> None:
        section_file = OTAnalyticsCli._parse_sections_file(str(otsection_file))
        assert section_file == otsection_file

    def test_parse_sections_file_does_not_exist(self) -> None:
        with pytest.raises(SectionsFileDoesNotExist, match=r"Sections file.*"):
            OTAnalyticsCli._parse_sections_file("foo/bar.otflow")

    def test_parse_sections_file_wrong_filetype(self, test_data_tmp_dir: Path) -> None:
        section_with_wrong_filetype = test_data_tmp_dir / "section.otmeow"
        section_with_wrong_filetype.touch()

        with pytest.raises(InvalidSectionFileType):
            OTAnalyticsCli._parse_sections_file(str(section_with_wrong_filetype))

    def test_determine_eventlist_save_path(self) -> None:
        track_file = Path(f"path/to/track.{TRACK_FILE_TYPE}")
        result = OTAnalyticsCli._determine_eventlist_save_path(track_file)
        assert result == Path(f"path/to/track.{EVENTLIST_FILE_TYPE}")

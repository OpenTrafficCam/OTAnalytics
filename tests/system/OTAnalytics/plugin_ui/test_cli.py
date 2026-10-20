import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from OTAnalytics.application.config import (
    CONTEXT_FILE_TYPE_COUNTS,
    CONTEXT_FILE_TYPE_EVENTS,
    CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS,
    CONTEXT_FILE_TYPE_TRACK_STATISTICS,
    CONTEXT_FILE_TYPE_TRACKS,
)
from OTAnalytics.application.parser.cli_parser import CliMode
from OTAnalytics.plugin_parser.json_parser import parse_json, write_json
from tests.conftest import YieldFixture


@dataclass
class Given:
    base_dir: Path
    filename_stem: str
    video_file: Path
    ottrk_file: Path
    otconfig_file: Path
    interval_in_minutes: int
    cli_args: list[str]


class TestMultipleDotsInFilenameResultsInIncompleteExportFilenames:
    FILENAME_STEM = "foo bär.2025_08_28-1500.00000_2025-08-28_15-00-00.bär.føo"
    COUNT_INTERVAL = 15

    @pytest.mark.parametrize("cli_mode", [CliMode.BULK, CliMode.STREAM])
    def test_multiple_dots_in_filename_creates_expected_output_files(
        self,
        cli_mode: CliMode,
        multiple_dots_test_data_dir: Path,
        cyclist_video: Path,
        ottrk_path: Path,
        otconfig_file: Path,
    ) -> None:
        """#Requirement https://openproject.platomo.de/wp/9548

        @bug by randy-seng
        """
        given = self.create_given(
            base_dir=multiple_dots_test_data_dir,
            otconfig_file=otconfig_file,
            video_file=cyclist_video,
            ottrk_file=ottrk_path,
            cli_mode=cli_mode,
        )

        actual = subprocess.run(
            given.cli_args,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

        assert actual.returncode == 0

        # Expected Feather, videos metadata, and tracks metadata files
        assert Path(given.base_dir / f"{given.filename_stem}.feather").exists()
        assert Path(
            given.base_dir / f"{given.filename_stem}.tracks_metadata.json"
        ).exists()
        assert Path(
            given.base_dir / f"{given.filename_stem}.videos_metadata.json"
        ).exists()

        # Expected event files
        assert Path(
            given.base_dir / f"{given.filename_stem}.{CONTEXT_FILE_TYPE_EVENTS}.csv"
        ).exists()
        assert Path(
            given.base_dir / f"{given.filename_stem}.{CONTEXT_FILE_TYPE_EVENTS}.xlsx"
        ).exists()
        assert Path(
            given.base_dir
            / f"{given.filename_stem}.{CONTEXT_FILE_TYPE_EVENTS}.otevents"
        ).exists()

        # Expected count file
        assert Path(
            given.base_dir / f"{given.filename_stem}.{CONTEXT_FILE_TYPE_COUNTS}"
            f"_{given.interval_in_minutes}min.csv"
        ).exists()

        # Expected track CSV file
        assert Path(
            given.base_dir / f"{given.filename_stem}.{CONTEXT_FILE_TYPE_TRACKS}.csv"
        ).exists()

        # Expected track statistics CSV files
        assert Path(
            given.base_dir
            / f"{given.filename_stem}.{CONTEXT_FILE_TYPE_TRACK_STATISTICS}.csv"
        ).exists()

        # Expected Road User Assignments CSV file
        assert Path(
            given.base_dir
            / f"{given.filename_stem}.{CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS}.csv"
        ).exists()

        # Expected Track Statistics CSV file
        assert Path(
            given.base_dir
            / f"{given.filename_stem}.{CONTEXT_FILE_TYPE_TRACK_STATISTICS}.csv"
        ).exists()

    def create_given(
        self,
        base_dir: Path,
        otconfig_file: Path,
        video_file: Path,
        ottrk_file: Path,
        cli_mode: CliMode,
    ) -> Given:
        new_video_file = copy_file_with_new_filename(
            base_dir, video_file, self.FILENAME_STEM, ".mp4"
        )
        new_ottrk_file = copy_file_with_new_filename(
            base_dir, ottrk_file, self.FILENAME_STEM, ".ottrk"
        )
        new_otconfig_file = copy_file_with_new_filename(
            base_dir, otconfig_file, self.FILENAME_STEM, ".otconfig"
        )
        new_otconfig_file = patch_files_in_otconfig_file(
            new_otconfig_file, self.FILENAME_STEM, [self.COUNT_INTERVAL]
        )
        cli_args = self.create_cli_arguments(cli_mode, new_otconfig_file)

        return Given(
            base_dir=base_dir,
            filename_stem=self.FILENAME_STEM,
            video_file=new_video_file,
            ottrk_file=new_ottrk_file,
            otconfig_file=new_otconfig_file,
            interval_in_minutes=self.COUNT_INTERVAL,
            cli_args=cli_args,
        )

    def create_cli_arguments(self, mode: CliMode, otconfig_file: Path) -> list[str]:
        return [
            sys.executable,
            "-m",
            "OTAnalytics",
            "--cli",
            "--config",
            str(otconfig_file),
            "--track-export",
            "--track-statistics-export",
            "--cli-mode",
            mode.value,
        ]


@pytest.fixture
def multiple_dots_test_data_dir(test_data_tmp_dir: Path) -> YieldFixture[Path]:
    directory = test_data_tmp_dir / "multiple_dots"
    try:
        directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        shutil.rmtree(directory, ignore_errors=True)
        directory.mkdir(parents=True, exist_ok=False)

    yield directory
    shutil.rmtree(directory, ignore_errors=True)


def copy_file_with_new_filename(
    copy_dir: Path, source_file: Path, new_filename_stem: str, new_filetype: str
) -> Path:
    dest = copy_dir / f"{new_filename_stem}{new_filetype}"
    shutil.copy(source_file, dest)
    return dest


def patch_files_in_otconfig_file(
    otconfig_file: Path, filename_stem: str, count_intervals: list[int]
) -> Path:
    otconfig_data = parse_json(otconfig_file)
    otconfig_data["videos"] = [
        {
            "path": f"{filename_stem}.mp4",
        }
    ]
    otconfig_data["analysis"]["tracks"] = [
        f"{filename_stem}.ottrk",
    ]
    otconfig_data["analysis"]["export"]["save_name"] = ""
    otconfig_data["analysis"]["export"]["save_suffix"] = ""
    otconfig_data["analysis"]["export"]["event_formats"] = ["csv", "otevents", "xlsx"]
    otconfig_data["analysis"]["export"]["count_intervals"] = count_intervals

    write_json(otconfig_data, otconfig_file)
    return otconfig_file


def create_expected_output_file(
    base_dir: Path, filename_stem: str, context_file_type: str, filetype: str
) -> Path:
    return base_dir / f"{filename_stem}.{context_file_type}{filetype}"

from pathlib import Path

import pytest
from more_itertools import chunked
from tqdm import tqdm

from OTAnalytics.application.parser.cli_parser import CliMode
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.plugin_cli.cli_application import OtAnalyticsCliApplicationStarter
from OTAnalytics.plugin_parser.otvision_parser import OtFlowParser
from tests.utils.assertions import assert_two_files_equal_sorted
from tests.utils.builders.run_configuration import create_run_config


def to_cli_path(test_data_dir: Path, input_file: str) -> str:
    return str(Path(test_data_dir / input_file).absolute())


@pytest.fixture(scope="module")
def track_file_15min(test_data_dir: Path) -> list[str]:
    return [to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24_08-00-00.ottrk")]


@pytest.fixture(scope="module")
def track_files_2hours(test_data_dir: Path) -> list[str]:
    return [
        to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24_08-00-00.ottrk"),
        to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24_08-15-00.ottrk"),
        to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24_08-30-00.ottrk"),
        to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24_08-45-00.ottrk"),
        to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24_09-00-00.ottrk"),
        to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24_09-15-00.ottrk"),
        to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24_09-30-00.ottrk"),
        to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24_09-45-00.ottrk"),
    ]


@pytest.fixture(scope="module")
def all_track_files_test_dataset() -> list[Path]:
    data_folder = Path("../../platomo/OpenTrafficCam-testdata/tests/data")
    return list(data_folder.glob("*.ottrk"))


@pytest.fixture(scope="module")
def otflow_file(test_data_dir: Path) -> str:
    return to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24.otflow")


@pytest.fixture(scope="module")
def cli_chunk_size() -> int:
    return 5


@pytest.fixture
def otflow_parser() -> FlowParser:
    return OtFlowParser()


class TestRegressionCompleteApplication:

    @pytest.mark.skip
    @pytest.mark.parametrize(
        "cli_mode",
        [CliMode.STREAM, CliMode.BULK],
    )
    def test_15_min_recreate_test_data(
        self,
        otflow_file: str,
        all_track_files_test_dataset: list[Path],
        otflow_parser: FlowParser,
        cli_mode: CliMode,
        cli_chunk_size: int,
    ) -> None:
        for test_file in tqdm(all_track_files_test_dataset, desc="test data file"):
            test_data = test_file
            test_interval = "15min"
            save_dir = test_data.parent
            self._run_otanalytics(
                count_interval=15,
                otflow_file=otflow_file,
                test_data=[str(test_data)],
                save_dir=save_dir,
                test_interval=test_interval,
                otflow_parser=otflow_parser,
                event_formats=("csv", "otevents"),
                cli_mode=cli_mode,
                cli_chunk_size=cli_chunk_size,
            )

    @pytest.mark.skip
    def test_2_h_single_recreate_test_data(
        self,
        otflow_file: str,
        all_track_files_test_dataset: list[Path],
        otflow_parser: FlowParser,
        cli_chunk_size: int,
    ) -> None:
        batches = list(chunked(sorted(all_track_files_test_dataset), n=8))
        for test_file in tqdm(batches, desc="test data file"):
            test_data = test_file
            test_interval = "2h"
            save_dir = test_data[0].parent
            self._run_otanalytics(
                count_interval=15,
                otflow_file=otflow_file,
                test_data=[str(file) for file in test_data],
                save_dir=save_dir,
                test_interval=test_interval,
                otflow_parser=otflow_parser,
                event_formats=("csv", "otevents"),
                cli_mode=CliMode.BULK,
                cli_chunk_size=cli_chunk_size,
            )

    @pytest.mark.skip
    def test_2_h_recreate_test_data(
        self,
        otflow_file: str,
        all_track_files_test_dataset: list[Path],
        otflow_parser: FlowParser,
        cli_chunk_size: int,
    ) -> None:
        batches = list(chunked(sorted(all_track_files_test_dataset), n=8))
        for test_file in tqdm(batches, desc="test data file"):
            test_data = test_file
            test_interval = "2h"
            save_dir = test_data[0].parent
            self._run_otanalytics(
                count_interval=120,
                otflow_file=otflow_file,
                test_data=[str(file) for file in test_data],
                save_dir=save_dir,
                test_interval=test_interval,
                otflow_parser=otflow_parser,
                event_formats=("csv", "otevents"),
                cli_mode=CliMode.BULK,
                cli_chunk_size=cli_chunk_size,
            )

    @pytest.mark.skip
    def test_whole_day_recreate_test_data(
        self,
        otflow_file: str,
        all_track_files_test_dataset: list[Path],
        otflow_parser: FlowParser,
        cli_chunk_size: int,
    ) -> None:
        test_data = all_track_files_test_dataset
        test_interval = "24h"
        save_dir = test_data[0].parent
        self._run_otanalytics(
            count_interval=15,
            otflow_file=otflow_file,
            test_data=[str(file) for file in test_data],
            save_dir=save_dir,
            test_interval=test_interval,
            otflow_parser=otflow_parser,
            event_formats=("csv", "otevents"),
            cli_mode=CliMode.BULK,
            cli_chunk_size=cli_chunk_size,
        )

    @pytest.mark.parametrize(
        "cli_mode",
        [CliMode.STREAM, CliMode.BULK],
    )
    def test_15_min(
        self,
        otflow_file: str,
        test_data_dir: Path,
        test_data_tmp_dir: Path,
        track_file_15min: list[str],
        otflow_parser: FlowParser,
        cli_mode: CliMode,
        cli_chunk_size: int,
    ) -> None:
        test_data = track_file_15min
        test_interval = "15min"
        self._execute_test(
            otflow_file,
            test_data,
            test_data_dir,
            test_data_tmp_dir,
            test_interval,
            otflow_parser,
            count_interval=15,
            cli_mode=cli_mode,
            cli_chunk_size=cli_chunk_size,
        )

    @pytest.mark.parametrize(
        "cli_mode",
        [CliMode.STREAM, CliMode.BULK],
    )
    def test_2_h_single(
        self,
        otflow_file: str,
        test_data_dir: Path,
        test_data_tmp_dir: Path,
        track_files_2hours: list[str],
        otflow_parser: FlowParser,
        cli_mode: CliMode,
        cli_chunk_size: int,
    ) -> None:
        for track_file in track_files_2hours:
            test_data = [track_file]
            test_interval = "15min"
            self._execute_test(
                otflow_file,
                test_data,
                test_data_dir,
                test_data_tmp_dir,
                test_interval,
                otflow_parser,
                count_interval=15,
                cli_mode=cli_mode,
                cli_chunk_size=cli_chunk_size,
            )

    @pytest.mark.parametrize(
        "cli_mode",
        [CliMode.STREAM, CliMode.BULK],
    )
    def test_2_h(
        self,
        otflow_file: str,
        test_data_dir: Path,
        test_data_tmp_dir: Path,
        track_files_2hours: list[str],
        otflow_parser: FlowParser,
        cli_mode: CliMode,
        cli_chunk_size: int,
    ) -> None:
        test_data = track_files_2hours
        test_interval = "2h"
        self._execute_test(
            otflow_file,
            test_data,
            test_data_dir,
            test_data_tmp_dir,
            test_interval,
            otflow_parser,
            count_interval=120,
            cli_mode=cli_mode,
            cli_chunk_size=cli_chunk_size,
        )

    def _execute_test(
        self,
        otflow_file: str,
        test_data: list[str],
        test_data_dir: Path,
        test_data_tmp_dir: Path,
        test_interval: str,
        otflow_parser: FlowParser,
        count_interval: int,
        cli_mode: CliMode,
        cli_chunk_size: int,
    ) -> None:
        save_name = self._run_otanalytics(
            count_interval,
            otflow_file,
            otflow_parser,
            test_data,
            test_data_tmp_dir,
            test_interval,
            cli_mode,
            cli_chunk_size,
        )

        actual_events_file = Path(test_data_tmp_dir / save_name).with_suffix(
            ".events.csv"
        )
        expected_events_file = Path(test_data_dir / save_name).with_suffix(
            ".events.csv"
        )
        assert_two_files_equal_sorted(actual_events_file, expected_events_file)

        actual_counts_file = (
            Path(test_data_tmp_dir / save_name)
            .with_suffix(f".counts_{count_interval}min.csv")
            .absolute()
        )
        expected_counts_file = (
            Path(test_data_dir / save_name)
            .with_suffix(f".counts_{count_interval}min.csv")
            .absolute()
        )
        assert_two_files_equal_sorted(actual_counts_file, expected_counts_file)

    def _run_otanalytics(
        self,
        count_interval: int,
        otflow_file: str,
        otflow_parser: FlowParser,
        test_data: list[str],
        save_dir: Path,
        test_interval: str,
        cli_mode: CliMode,
        cli_chunk_size: int,
        event_formats: tuple[str, ...] = ("csv",),
    ) -> str:
        save_name = f"{Path(test_data[0]).stem}_{test_interval}"
        run_config = create_run_config(
            track_files=[str(_file) for _file in test_data],
            otflow_file=str(otflow_file),
            save_dir=str(save_dir),
            save_name=save_name,
            event_formats=list(event_formats),
            count_intervals=[count_interval],
            flow_parser=otflow_parser,
            cli_mode=cli_mode,
            cli_chunk_size=cli_chunk_size,
        )
        OtAnalyticsCliApplicationStarter(run_config).start()
        return save_name

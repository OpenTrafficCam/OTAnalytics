from pathlib import Path

import pytest

from OTAnalytics.application.datastore import FlowParser
from OTAnalytics.plugin_parser.otvision_parser import OtFlowParser
from OTAnalytics.plugin_ui.main_application import ApplicationStarter
from tests.conftest import create_run_config


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
def otflow_file(test_data_dir: Path) -> str:
    return to_cli_path(test_data_dir, "OTCamera19_FR20_2023-05-24.otflow")


@pytest.fixture
def otflow_parser() -> FlowParser:
    return OtFlowParser()


class TestRegressionCompleteApplication:
    def test_15_min(
        self,
        otflow_file: str,
        test_data_dir: Path,
        test_data_tmp_dir: Path,
        track_file_15min: list[str],
        otflow_parser: FlowParser,
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
        )

    def test_2_h_single(
        self,
        otflow_file: str,
        test_data_dir: Path,
        test_data_tmp_dir: Path,
        track_files_2hours: list[str],
        otflow_parser: FlowParser,
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
            )

    def test_2_h(
        self,
        otflow_file: str,
        test_data_dir: Path,
        test_data_tmp_dir: Path,
        track_files_2hours: list[str],
        otflow_parser: FlowParser,
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
    ) -> None:
        save_name = f"{Path(test_data[0]).stem}_{test_interval}"

        run_config = create_run_config(
            track_files=[str(_file) for _file in test_data],
            otflow_file=str(otflow_file),
            save_dir=str(test_data_tmp_dir),
            save_name=save_name,
            event_formats=["csv"],
            count_intervals=[count_interval],
            flow_parser=otflow_parser,
        )
        ApplicationStarter().start_cli(run_config)

        actual_events_file = Path(test_data_tmp_dir / save_name).with_suffix(
            ".events.csv"
        )
        expected_events_file = Path(test_data_dir / save_name).with_suffix(
            ".events.csv"
        )
        with open(actual_events_file) as actual:
            actual_lines = sorted(actual.readlines())
            with open(expected_events_file) as expected:
                expected_lines = sorted(expected.readlines())
                assert actual_lines == expected_lines

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
        with open(actual_counts_file, mode="r") as actual:
            actual_lines = sorted(actual.readlines())
            with open(expected_counts_file, mode="r") as expected:
                expected_lines = sorted(expected.readlines())
                assert actual_lines == expected_lines

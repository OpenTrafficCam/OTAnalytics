from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.config import (
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
    DEFAULT_EVENTLIST_FILE_TYPE,
    DEFAULT_NUM_PROCESSES,
)
from OTAnalytics.application.logger import DEFAULT_LOG_FILE
from OTAnalytics.application.parser.cli_parser import CliArguments, CliMode
from OTAnalytics.application.parser.config_parser import OtConfig
from OTAnalytics.application.run_configuration import RunConfiguration


@pytest.fixture
def cli_args_otconfig() -> CliArguments:
    cli_track_files = [
        "path/to/first_track_cli.ottrk",
        "path/to/second_track_cli.ottrk",
    ]
    return CliArguments(
        start_cli=True,
        cli_mode=CliMode.BULK,
        cli_chunk_size=5,
        config_file="my_config.otconfig",
        debug=True,
        track_files=cli_track_files,
        otflow_file=None,
        save_name="cli_save_name",
        save_suffix="cli_save_suffix",
        event_formats=["csv"],
        count_intervals=[6],
        track_export=False,
        track_statistics_export=False,
        num_processes=8,
        log_file="path/to/cli_log",
        logfile_overwrite=True,
    )


@pytest.fixture
def cli_args() -> Mock:
    args = Mock()
    args.otflow_file = "path/to/my_otflow.otflow"
    return args


@pytest.fixture
def otconfig() -> Mock:
    return Mock()


def flow_parser() -> Mock:
    parser = Mock()
    parser.parse.return_value = ([], [])
    return parser


def fixed_datetime() -> datetime:
    return datetime(2025, 1, 1, 12, 34, 56)


def build_config(cli_args: CliArguments, otconfig: OtConfig | None) -> RunConfiguration:
    return RunConfiguration(flow_parser(), cli_args, otconfig, fixed_datetime)


class TestRunConfiguration:
    def test_start_cli(
        self, cli_args_otconfig: CliArguments, otconfig: OtConfig
    ) -> None:
        run_config = build_config(cli_args_otconfig, otconfig)
        assert run_config.start_cli == cli_args_otconfig.start_cli

    def test_debug(self, cli_args_otconfig: CliArguments, otconfig: OtConfig) -> None:
        run_config = build_config(cli_args_otconfig, otconfig)
        assert run_config.debug == cli_args_otconfig.debug

    def test_config_file(self, cli_args: Mock, otconfig: Mock) -> None:
        config_file = "path/to/config.otconfig"
        cli_args.config_file = config_file
        run_config = build_config(cli_args, otconfig)
        assert run_config.config_file == Path(config_file)
        run_config = build_config(cli_args, None)
        assert run_config.config_file == Path(config_file)

    @pytest.mark.parametrize(
        "cli_tracks,cfg_tracks,expected",
        [
            (
                ["path/to/first_cli.ottrk", "path/to/second_cli.ottrk"],
                [
                    "path/to/first_cfg.ottrk",
                    "path/to/second_cfg.ottrk",
                ],
                {Path("path/to/first_cli.ottrk"), Path("path/to/second_cli.ottrk")},
            ),
            (
                ["path/to/first_cli.ottrk", "path/to/second_cli.ottrk"],
                [],
                {Path("path/to/first_cli.ottrk"), Path("path/to/second_cli.ottrk")},
            ),
            (
                [],
                [
                    "path/to/first_cfg.ottrk",
                    "path/to/second_cfg.ottrk",
                ],
                {
                    Path("path/to/first_cfg.ottrk"),
                    Path("path/to/second_cfg.ottrk"),
                },
            ),
        ],
    )
    def test_track_files(
        self, cli_tracks: list[str], cfg_tracks: list[str], expected: set[Path]
    ) -> None:
        cli_args = Mock()
        cli_args.track_files = cli_tracks

        otconfig = Mock()
        analysis = Mock()
        analysis.track_files = set(map(Path, cfg_tracks))
        otconfig.analysis = analysis

        run_config = build_config(cli_args, otconfig)
        assert run_config.track_files == expected

    def test_track_files_default(self) -> None:
        cli_args = Mock()
        cli_args.track_files = None
        cli_args.otflow_file = None

        run_config = build_config(cli_args, None)
        assert run_config.track_files == set()

    def test_otflow(self) -> None:
        otflow_file = "path/to/my.otflow"
        cli_args = Mock()

        cli_args.otflow_file = otflow_file
        assert build_config(cli_args, None).otflow == Path(otflow_file)

        cli_args.otflow_file = None
        assert not build_config(cli_args, None).otflow

    @pytest.mark.parametrize(
        (
            "cli_save_name, cli_save_suffix, cfg_save_name, cfg_save_suffix,"
            "otflow_file, otconfig_file,has_otconfig,expected"
        ),
        [
            (
                "cli_save_name",
                "cli_suffix",
                "cfg_suffix",
                "cfg_save_name",
                "path/to/my_flows.otflow",
                "path/to/my_config.otconfig",
                True,
                "cli_save_name_cli_suffix",
            ),
            (
                "cli_save_name",
                "cli_suffix",
                "cfg_suffix",
                "path/to/cfg_save_name",
                "path/to/my_flows.otflow",
                "path/to/my_config.otconfig",
                False,
                "cli_save_name_cli_suffix",
            ),
            (
                "cli_save_name",
                "",
                "cfg_suffix",
                "cfg_save_name",
                "path/to/my_flows.otflow",
                "path/to/my_config.otconfig",
                False,
                "cli_save_name",
            ),
            (
                "",
                "cli_suffix",
                "cfg_suffix",
                "cfg_save_name",
                "path/to/my_flows.otflow",
                None,
                False,
                "my_flows_cli_suffix",
            ),
            (
                "",
                "",
                "cfg_suffix",
                "cfg_save_name",
                "path/to/my_flows.otflow",
                None,
                False,
                "my_flows",
            ),
            (
                "",
                "cli_suffix",
                "cfg_save_name",
                "cfg_suffix",
                "path/to/my_flows.otflow",
                "path/to/my_config.otconfig",
                True,
                "cfg_save_name_cli_suffix",
            ),
            (
                "",
                "cli_suffix",
                "",
                "cfg_suffix",
                "path/to/my_flows.otflow",
                "path/to/my_config.otconfig",
                True,
                "my_config_cli_suffix",
            ),
            (
                "",
                "",
                "",
                "cfg_suffix",
                "path/to/my_flows.otflow",
                "path/to/my_config.otconfig",
                True,
                "my_config_cfg_suffix",
            ),
            (
                "",
                "",
                "",
                "",
                "path/to/my_flows.otflow",
                "path/to/my_config.otconfig",
                True,
                "my_config",
            ),
        ],
    )
    def test_save_name(
        self,
        cli_save_name: str,
        cli_save_suffix: str,
        cfg_save_name: str,
        cfg_save_suffix: str,
        otflow_file: str | None,
        otconfig_file: str | None,
        has_otconfig: bool,
        expected: str,
    ) -> None:
        cli_args = Mock()
        cli_args.save_name = cli_save_name
        cli_args.save_suffix = cli_save_suffix
        cli_args.otflow_file = otflow_file
        cli_args.config_file = otconfig_file

        export = Mock()
        export.save_name = cfg_save_name
        export.save_suffix = cfg_save_suffix
        analysis = Mock()
        analysis.export_config = export
        otconfig = Mock()
        otconfig.analysis = analysis
        if has_otconfig:
            assert build_config(cli_args, otconfig).save_name == expected
        else:
            assert build_config(cli_args, None).save_name == expected

    def test_save_suffix(self, cli_args: Mock, otconfig: Mock) -> None:
        cli_args.save_suffix = "cli_suffix"
        analysis = Mock()
        export_config = Mock()
        cfg_save_suffix = "cfg_suffix"
        export_config.save_suffix = cfg_save_suffix
        analysis.export_config = export_config
        otconfig.analysis = analysis

        assert build_config(cli_args, otconfig).save_suffix == "_cli_suffix"
        cli_args.save_suffix = None
        assert build_config(cli_args, None).save_suffix == ""
        assert build_config(cli_args, otconfig).save_suffix == "_cfg_suffix"

    def test_event_formats(self, cli_args: Mock, otconfig: Mock) -> None:
        cli_event_formats = "csv"
        cli_args.event_formats = [cli_event_formats]
        cli_args.otflow_file = None
        cli_args.config_file = None

        analysis = Mock()
        export_config = Mock()
        cfg_event_formats = {"csv", "otevents"}
        export_config.event_formats = cfg_event_formats
        analysis.export_config = export_config
        otconfig.analysis = analysis

        assert build_config(cli_args, otconfig).event_formats == {cli_event_formats}
        cli_args.event_formats = None
        assert build_config(cli_args, otconfig).event_formats == cfg_event_formats
        export_config.event_formats = None
        assert build_config(cli_args, None).event_formats == {
            DEFAULT_EVENTLIST_FILE_TYPE
        }

    def test_count_intervals(self, cli_args: Mock, otconfig: Mock) -> None:
        cli_count_intervals = [1, 5]
        cli_args.count_intervals = cli_count_intervals

        analysis = Mock()
        export_config = Mock()
        cfg_count_intervals = {2, 3}
        export_config.count_intervals = cfg_count_intervals
        analysis.export_config = export_config
        otconfig.analysis = analysis

        assert build_config(cli_args, otconfig).count_intervals == set(
            cli_count_intervals
        )
        cli_args.count_intervals = None
        assert build_config(cli_args, otconfig).count_intervals == cfg_count_intervals
        assert build_config(cli_args, None).count_intervals == {
            DEFAULT_COUNTING_INTERVAL_IN_MINUTES
        }

    def test_num_processes(self, cli_args: Mock, otconfig: Mock) -> None:
        cli_num_processes = 1
        cli_args.num_processes = cli_num_processes

        analysis = Mock()
        cfg_num_processes = 4
        analysis.num_processes = cfg_num_processes
        otconfig.analysis = analysis
        assert build_config(cli_args, otconfig).num_processes == cli_num_processes
        cli_args.num_processes = None
        assert build_config(cli_args, otconfig).num_processes == cfg_num_processes
        assert build_config(cli_args, None).num_processes == DEFAULT_NUM_PROCESSES

    @pytest.mark.parametrize(
        "cli_argument, config_entry, expected_file",
        [
            (
                "path/to/cli_log_file.log",
                "path/to/cfg_log_file.log",
                "path/to/cli_log_file.log",
            ),
            (
                None,
                "path/to/cfg_log_file.log",
                "path/to/cfg_log_file.log",
            ),
            (
                "path/to/cli_log_folder",
                "path/to/cfg_log_folder",
                "path/to/cli_log_folder/otanalytics-2025-01-01_12-34-56.log",
            ),
            (
                None,
                "path/to/cfg_log_folder",
                "path/to/cfg_log_folder/otanalytics-2025-01-01_12-34-56.log",
            ),
            (None, None, DEFAULT_LOG_FILE),
        ],
    )
    def test_log_file(
        self,
        cli_argument: str | None,
        config_entry: str | None,
        expected_file: str,
        cli_args: Mock,
        test_data_tmp_dir: Path,
    ) -> None:
        """
        https://openproject.platomo.de/wp/7631
        """
        self._set_cli_logfile(cli_args, cli_argument, test_data_tmp_dir)
        otconfig = self._create_otconfig(config_entry, test_data_tmp_dir)

        actual = build_config(cli_args, otconfig).log_file

        expected = test_data_tmp_dir / expected_file
        assert actual == expected

    def _set_cli_logfile(
        self, cli_args: Mock, cli_argument: str | None, test_data_tmp_dir: Path
    ) -> None:
        cli_log_file = test_data_tmp_dir / cli_argument if cli_argument else None
        cli_args.log_file = cli_log_file
        cli_args.config_file = "abspath/to/my_config.otconfig"
        self.create_log_folder(cli_log_file)

    def _create_otconfig(
        self, config_entry: str | None, test_data_tmp_dir: Path
    ) -> Mock | None:
        if config_entry is None:
            return None
        cfg_log_file = test_data_tmp_dir / config_entry
        self.create_log_folder(cfg_log_file)
        otconfig = Mock()
        analysis = Mock()
        analysis.logfile = cfg_log_file
        otconfig.analysis = analysis
        return otconfig

    def create_log_folder(self, log_path: Path | None) -> None:
        if log_path is None:
            return
        if log_path.suffix == ".log":
            log_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            log_path.mkdir(parents=True, exist_ok=True)

    def test_log_file_overwrite(self, cli_args: Mock, otconfig: Mock) -> None:
        cli_args.logfile_overwrite = False
        assert build_config(cli_args, otconfig).logfile_overwrite is False

    def test_do_events(self, cli_args: Mock, otconfig: Mock) -> None:
        analysis = Mock()
        analysis.do_events = False
        otconfig.analysis = analysis
        assert build_config(cli_args, otconfig).do_events is False
        assert build_config(cli_args, None).do_events is True

    def test_do_counting(self, cli_args: Mock, otconfig: Mock) -> None:
        analysis = Mock()
        analysis.do_counting = False
        otconfig.analysis = analysis
        assert build_config(cli_args, otconfig).do_counting is False
        assert build_config(cli_args, None).do_counting is True

    def test_project(self, cli_args: Mock, otconfig: Mock) -> None:
        project = Mock()
        otconfig.project = project
        assert build_config(cli_args, otconfig).project == project
        assert build_config(cli_args, None).project is None

    def test_videos(self, cli_args: Mock, otconfig: Mock) -> None:
        videos = Mock()
        otconfig.videos = videos
        assert build_config(cli_args, otconfig).videos == videos
        assert not build_config(cli_args, None).videos

    def test_sections(self, cli_args: Mock, otconfig: Mock) -> None:
        sections = Mock()
        otconfig.sections = sections
        assert build_config(cli_args, otconfig).sections == sections
        assert not build_config(cli_args, None).sections

    def test_flows(self, cli_args: Mock, otconfig: Mock) -> None:
        flows = Mock()
        otconfig.flows = flows
        assert build_config(cli_args, otconfig).flows == flows
        assert not build_config(cli_args, None).flows

    @pytest.mark.parametrize(
        "save_dir,otflow_file,config_file,expected",
        [
            (
                "path/to/cli_save_dir",
                "path/to/otflow/flows.otflow",
                "path/to/otconfig/config.otconfig",
                "path/to/cli_save_dir",
            ),
            (None, "path/to/otflow/flows.otflow", None, "path/to/otflow"),
            (
                None,
                "path/to/otflow/flows.otflow",
                "path/to/otconfig/config.otconfig",
                "path/to/otconfig",
            ),
            (
                "~/path/to/cli_save_dir",
                "path/to/otflow/flows.otflow",
                "path/to/otconfig/config.otconfig",
                str(Path("~").expanduser() / "path/to/cli_save_dir"),
            ),
            (
                None,
                "~/path/to/otflow/flows.otflow",
                None,
                str(Path("~").expanduser() / "path/to/otflow"),
            ),
            (
                None,
                "path/to/otflow/flows.otflow",
                "~/path/to/otconfig/config.otconfig",
                str(Path("~").expanduser() / "path/to/otconfig"),
            ),
        ],
    )
    def test_save_dir(
        self,
        save_dir: str | None,
        otflow_file: str | None,
        config_file: str | None,
        expected: str,
        cli_args: Mock,
        otconfig: Mock,
    ) -> None:
        cli_args.save_dir = save_dir
        cli_args.otflow_file = otflow_file
        cli_args.config_file = config_file
        assert build_config(cli_args, None).save_dir == Path(expected)

    def test_include_classes(self, cli_args: Mock, otconfig: Mock) -> None:
        include_classes = frozenset(["car", "truck"])
        cli_args.include_classes = include_classes
        assert build_config(cli_args, otconfig).include_classes == include_classes
        cli_args.include_classes = None
        assert build_config(cli_args, otconfig).include_classes == frozenset()

    def test_exclude_classes(self, cli_args: Mock, otconfig: Mock) -> None:
        exclude_classes = frozenset(["car", "truck"])
        cli_args.exclude_classes = exclude_classes
        assert build_config(cli_args, otconfig).exclude_classes == exclude_classes
        cli_args.exclude_classes = None
        assert build_config(cli_args, otconfig).exclude_classes == frozenset()

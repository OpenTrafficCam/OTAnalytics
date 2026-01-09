from OTAnalytics.application.parser.cli_parser import CliArguments, CliMode
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.plugin_parser.otvision_parser import OtFlowParser

NUM_PROCESSES = 1


def create_run_config(
    track_files: list[str] | None = None,
    otflow_file: str | None = None,
    save_dir: str | None = None,
    event_formats: list[str] | None = None,
    flow_parser: FlowParser = OtFlowParser(),
    start_cli: bool = True,
    start_webui: bool = False,
    file_picker_directory: str | None = None,
    cli_mode: CliMode = CliMode.BULK,
    cli_chunk_size: int = 5,
    debug: bool = False,
    logfile_overwrite: bool = True,
    track_export: bool = False,
    track_statistics_export: bool = False,
    num_processes: int = NUM_PROCESSES,
    count_intervals: list[int] | None = None,
    config_file: str | None = None,
    save_name: str | None = None,
    save_suffix: str | None = None,
    log_file: str | None = None,
    include_classes: list[str] | None = None,
    exclude_classes: list[str] | None = None,
) -> RunConfiguration:
    cli_args = CliArguments(
        start_cli=start_cli,
        start_webui=start_webui,
        file_picker_directory=file_picker_directory,
        cli_mode=cli_mode,
        cli_chunk_size=cli_chunk_size,
        debug=debug,
        logfile_overwrite=logfile_overwrite,
        track_export=track_export,
        track_statistics_export=track_statistics_export,
        track_files=track_files,
        otflow_file=otflow_file,
        save_dir=save_dir,
        save_name=save_name,
        count_intervals=count_intervals,
        event_formats=event_formats,
        config_file=config_file,
        save_suffix=save_suffix,
        log_file=log_file,
        include_classes=include_classes,
        exclude_classes=exclude_classes,
    )
    return RunConfiguration(flow_parser, cli_args)

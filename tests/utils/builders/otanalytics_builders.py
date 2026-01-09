from functools import cached_property
from multiprocessing import Process
from pathlib import Path
from typing import Protocol

from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider
from OTAnalytics.application.datastore import VideoParser
from OTAnalytics.application.parser.cli_parser import (
    CliArguments,
    CliMode,
    CliValueProvider,
)
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.state import VideosMetadata
from OTAnalytics.plugin_parser.otconfig_parser import OtConfigParser
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    PilImageFactory,
    TrackImageFactory,
)
from OTAnalytics.plugin_ui.base_application import (
    create_format_fixer,
    create_otflow_parser,
    create_video_parser,
    create_videos_metadata,
)
from OTAnalytics.plugin_ui.nicegui_application import (
    OtAnalyticsNiceGuiApplicationStarter,
)
from tests.utils.builders.run_configuration import create_run_config


class Runnable(Protocol):
    def run(self) -> None: ...


class MultiprocessingWorker(Process):
    """A worker that runs a given task in a separate process using the multiprocessing
    library.

    Args:
        runner (Runnable): The task to be run by this worker.
    """

    def __init__(self, runner: Runnable) -> None:
        super(Process, self).__init__()
        self._runner = runner

    def start(self) -> None:
        """Starts the worker process and runs the task."""

        Process.start(self)

    def stop(self) -> None:
        """Stops the worker process and terminates the task."""

        self.terminate()
        self.join()

    def run(self) -> None:
        """Runs the task in the worker process."""
        self._runner.run()


def file_picker_directory() -> str:
    return str(Path().cwd())


class NiceguiWorker(Process):
    """A worker that runs a given task in a separate process using the multiprocessing
    library.

    Args:
        runner (Runnable): The task to be run by this worker.
    """

    def __init__(self, run_config: RunConfiguration | None = None) -> None:
        super(Process, self).__init__()
        self._run_config = (
            run_config
            if run_config
            else create_run_config(
                start_cli=False,
                start_webui=True,
                file_picker_directory=file_picker_directory(),
            )
        )

    def start(self) -> None:
        """Starts the worker process and runs the task."""
        Process.start(self)

    def stop(self) -> None:
        """Stops the worker process and terminates the task."""
        self.terminate()
        self.join(10)

    def run(self) -> None:
        """Runs the task in the worker process."""
        OtAnalyticsNiceGuiApplicationStarter(self._run_config).start()


class NiceguiOtanalyticsBuilder(OtAnalyticsNiceGuiApplicationStarter):

    def build(self) -> MultiprocessingWorker:
        self.register_observers()
        return MultiprocessingWorker(self.webserver)

    def __init__(self) -> None:
        super().__init__(self._run_config)

    @cached_property
    def _run_config(self) -> RunConfiguration:
        cli_args = CliArguments(
            start_cli=False,
            cli_mode=CliMode.BULK,
            cli_chunk_size=1,
            debug=False,
            logfile_overwrite=True,
            track_export=False,
            track_statistics_export=False,
        )
        cli_value_provider: OtConfigDefaultValueProvider = CliValueProvider(cli_args)
        format_fixer = create_format_fixer(cli_value_provider)
        config_parser = OtConfigParser(
            format_fixer=format_fixer,
            video_parser=self.video_parser,
            flow_parser=self.flow_parser,
        )

        if config_file := cli_args.config_file:
            config = config_parser.parse(Path(config_file))
            return RunConfiguration(self.flow_parser, cli_args, config)
        return RunConfiguration(self.flow_parser, cli_args, None)

    @cached_property
    def video_parser(self) -> VideoParser:
        return create_video_parser(self.videos_metadata, self.track_image_factory)

    @cached_property
    def flow_parser(self) -> FlowParser:
        return create_otflow_parser()

    @cached_property
    def videos_metadata(self) -> VideosMetadata:
        return create_videos_metadata()

    @cached_property
    def track_image_factory(self) -> TrackImageFactory:
        return PilImageFactory()

import logging
from functools import cached_property
from pathlib import Path

from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider
from OTAnalytics.application.datastore import VideoParser
from OTAnalytics.application.logger import logger, setup_logger
from OTAnalytics.application.parser.cli_parser import (
    CliParseError,
    CliParser,
    CliValueProvider,
)
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.startup_config import (
    StartupConfigError,
    validate_transfer_mode,
)
from OTAnalytics.application.state import VideosMetadata
from OTAnalytics.domain.transfer_mode import TransferMode
from OTAnalytics.helpers.time_profiling import log_processing_time
from OTAnalytics.plugin_cli.cli_application import OtAnalyticsCliApplicationStarter
from OTAnalytics.plugin_parser.argparse_cli_parser import ArgparseCliParser
from OTAnalytics.plugin_parser.otconfig_parser import OtConfigParser
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    PilImageFactory,
    TrackImageFactory,
)
from OTAnalytics.plugin_s3.config.env_vars import S3Env, transfer_mode_from_env
from OTAnalytics.plugin_s3.config.parsing import parse_s3_config
from OTAnalytics.plugin_s3.config.s3 import S3Config
from OTAnalytics.plugin_ui.base_application import (
    create_format_fixer,
    create_otflow_parser,
    create_video_parser,
    create_videos_metadata,
)
from OTAnalytics.plugin_ui.ctk_application import OtAnalyticsCtkApplicationStarter
from OTAnalytics.plugin_ui.nicegui_application import (
    OtAnalyticsNiceGuiApplicationStarter,
)


class ApplicationStarter:
    @log_processing_time(description="overall")
    def start(self) -> None:
        self._setup_logger(
            self.run_config.log_file,
            self.run_config.logfile_overwrite,
            self.run_config.debug,
        )
        if not self._startup_config_is_valid():
            return
        if self.run_config.start_cli:
            try:
                OtAnalyticsCliApplicationStarter(self.run_config).start()
                # add command line tag for activating -> add to PipelineBenchmark,
                # add github actions for benchmark
                # regression test lokal runner neben benchmark ->
                # OTC -> test data -> 6-1145, flow in 00 -> in test resource ordner

            except CliParseError as e:
                logger().exception(e, exc_info=True)
        elif self.run_config.start_webui:
            OtAnalyticsNiceGuiApplicationStarter(self.run_config).start()
        else:
            OtAnalyticsCtkApplicationStarter(self.run_config).start()

    @cached_property
    def run_config(self) -> RunConfiguration:
        cli_args_parser = self._build_cli_argument_parser()
        cli_args = cli_args_parser.parse()
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

    def _startup_config_is_valid(self) -> bool:
        """Report a misconfigured startup config as a message, not a traceback.

        The front-end check runs before the S3 settings are read. Otherwise a
        CTk user in S3 mode with incomplete credentials would be told which
        settings are missing, when the real problem is that CTk cannot use S3.
        """
        try:
            validate_transfer_mode(
                self.transfer_mode, start_webui=self.run_config.start_webui
            )
            self.s3_config  # reads the S3 environment, if S3 mode is configured
        except StartupConfigError as cause:
            logger().error(str(cause))
            return False
        return True

    @cached_property
    def transfer_mode(self) -> TransferMode:
        return transfer_mode_from_env()

    @cached_property
    def s3_config(self) -> S3Config | None:
        """The S3 settings, or None when not running in S3 mode."""
        if self.transfer_mode != TransferMode.S3:
            return None
        return parse_s3_config(S3Env())

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

    def _build_cli_argument_parser(self) -> CliParser:
        return ArgparseCliParser()

    def _setup_logger(self, log_file: Path, overwrite: bool, debug: bool) -> None:
        if debug:
            setup_logger(
                log_file=log_file, overwrite=overwrite, log_level=logging.DEBUG
            )
        else:
            setup_logger(log_file=log_file, overwrite=overwrite, log_level=logging.INFO)

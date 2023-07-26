from pathlib import Path

from OTAnalytics.application.datastore import ConfigParser, Datastore


class MissingDate(Exception):
    pass


class SaveConfiguration:
    def __init__(self, datastore: Datastore, config_parser: ConfigParser) -> None:
        self._datastore = datastore
        self._config_parser = config_parser

    def __call__(self, file: Path) -> None:
        self._config_parser.serialize(
            project=self._datastore.project,
            video_files=self._datastore.get_all_videos(),
            sections=self._datastore.get_all_sections(),
            flows=self._datastore.get_all_flows(),
            file=file,
        )

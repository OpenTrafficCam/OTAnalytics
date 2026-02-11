from pathlib import Path
from unittest.mock import Mock

from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.use_cases.track_export import (
    ExportTracks,
    MultiExportTracks,
    TrackExportSpecification,
    TrackFileFormat,
)


class TestMultiExportTracks:

    def test_calls_all_exporter(self) -> None:
        specification = TrackExportSpecification(
            save_path=Path("/path/to/export"),
            export_format=[TrackFileFormat.CSV, TrackFileFormat.OTTRK],
            export_mode=OVERWRITE,
        )
        exporter_1 = Mock(spec=ExportTracks)
        exporter_2 = Mock(spec=ExportTracks)

        multi_exporter = MultiExportTracks(
            {TrackFileFormat.CSV: exporter_1, TrackFileFormat.OTTRK: exporter_2}
        )

        multi_exporter.export(specification)

        exporter_1.export.assert_called_once_with(specification)
        exporter_2.export.assert_called_once_with(specification)

    def test_calls_all_configured_exporters(self) -> None:
        specification = TrackExportSpecification(
            save_path=Path("/path/to/export"),
            export_format=[TrackFileFormat.OTTRK],
            export_mode=OVERWRITE,
        )
        exporter_1 = Mock(spec=ExportTracks)
        exporter_2 = Mock(spec=ExportTracks)

        multi_exporter = MultiExportTracks(
            {TrackFileFormat.CSV: exporter_1, TrackFileFormat.OTTRK: exporter_2}
        )

        multi_exporter.export(specification)

        exporter_1.export.assert_not_called()
        exporter_2.export.assert_called_once_with(specification)

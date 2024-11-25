from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

import pandas
import pytest
from pandas import DataFrame

from OTAnalytics.application.analysis.traffic_counting import (
    LEVEL_CLASSIFICATION,
    LEVEL_END_TIME,
    LEVEL_FLOW,
    LEVEL_FROM_SECTION,
    LEVEL_START_TIME,
    LEVEL_TO_SECTION,
    Count,
    Exporter,
    FillEmptyCount,
    SingleTag,
    Tag,
    create_flow_tag,
    create_mode_tag,
    create_timeslot_tag,
)
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
    ExportSpecificationDto,
    FlowNameDto,
)
from OTAnalytics.application.export_formats.export_mode import (
    FLUSH,
    INITIAL_MERGE,
    MERGE,
    OVERWRITE,
    ExportMode,
)
from OTAnalytics.plugin_parser.export import (
    END_DATE,
    END_TIME,
    START_DATE,
    START_TIME,
    CsvExport,
    FillZerosExporter,
    TagExploder,
)


class TestCsvExport:

    def test_empty_data(self, test_data_tmp_dir: Path) -> None:
        output_file = test_data_tmp_dir / "counts.csv"
        counts = Mock(spec=Count)
        counts.to_dict.return_value = {}
        export = CsvExport(output_file=str(output_file))
        export.export(counts, OVERWRITE)

        assert not output_file.exists()

    @pytest.mark.parametrize("export_mode", [FLUSH, OVERWRITE])
    def test_export(self, test_data_tmp_dir: Path, export_mode: ExportMode) -> None:
        output_file = test_data_tmp_dir / "counts.csv"
        counts = self._mock_counts_with_single_tag()
        expected = self._expected_counts()
        export = CsvExport(output_file=str(output_file))
        export.export(counts, export_mode)

        actual: DataFrame = pandas.read_csv(output_file)
        assert actual.to_dict() == expected

    @pytest.mark.parametrize("export_mode", [INITIAL_MERGE, MERGE])
    def test_increment_no_export(
        self, test_data_tmp_dir: Path, export_mode: ExportMode
    ) -> None:
        output_file = test_data_tmp_dir / "no_counts.csv"
        counts = self._mock_counts_with_single_tag()

        export = CsvExport(output_file=str(output_file))
        export.export(counts, export_mode)

        assert not output_file.exists()
        assert len(export._counts) == 1 and list(export._counts.values())[0] == 1

        export.export(counts, export_mode)
        assert not output_file.exists()
        assert len(export._counts) == 1 and list(export._counts.values())[0] == 2

    def _expected_counts(self) -> dict:
        expected = {
            LEVEL_START_TIME: {0: "2023-01-02 08:00:00"},
            START_DATE: {0: "2023-01-02"},
            START_TIME: {0: "08:00:00"},
            LEVEL_END_TIME: {0: "2023-01-02 08:15:00"},
            END_DATE: {0: "2023-01-02"},
            END_TIME: {0: "08:15:00"},
            LEVEL_CLASSIFICATION: {0: "car"},
            LEVEL_FLOW: {0: "West --> Ost"},
            LEVEL_FROM_SECTION: {0: "West"},
            LEVEL_TO_SECTION: {0: "Ost"},
            "count": {0: 1},
        }

        return expected

    def _mock_counts_with_single_tag(self) -> Count:
        counts = Mock(spec=Count)
        tag = (
            SingleTag(LEVEL_START_TIME, "2023-01-02 08:00:00")
            .combine(SingleTag(LEVEL_END_TIME, "2023-01-02 08:15:00"))
            .combine(SingleTag(LEVEL_CLASSIFICATION, "car"))
            .combine(SingleTag(LEVEL_FLOW, "West --> Ost"))
            .combine(SingleTag(LEVEL_FROM_SECTION, "West"))
            .combine(SingleTag(LEVEL_TO_SECTION, "Ost"))
        )
        counts.to_dict.return_value = {tag: 1}
        return counts


def execute_explode(
    start: datetime,
    end: datetime,
    interval_in_minutes: int,
    flow_names: list[FlowNameDto],
    modes: list[str],
    output_file: str,
    output_format: str,
    expected_tags: list[Tag],
) -> None:
    counting_specification = CountingSpecificationDto(
        start=start,
        end=end,
        interval_in_minutes=interval_in_minutes,
        modes=modes,
        output_format=output_format,
        output_file=output_file,
        export_mode=OVERWRITE,
    )
    specification = ExportSpecificationDto(
        counting_specification=counting_specification,
        flow_name_info=flow_names,
    )
    exploder = TagExploder(specification)
    tags = exploder.explode()
    assert tags == expected_tags


class TestTagExploder:
    def test_export_single(self) -> None:
        start = datetime(2023, 1, 1, 0, 0, 10)
        end = datetime(2023, 1, 1, 0, 9, 56)
        interval_in_minutes = 10
        modes = ["first-mode"]
        output_format = "csv"
        output_file = "output-file.csv"
        flow_name_dto = FlowNameDto(
            "from first -> to second", "from first", "to second"
        )

        flow_names = [flow_name_dto]
        expected_tags: list[Tag] = [
            create_flow_tag(flow_name_dto.name)
            .combine(create_mode_tag("first-mode"))
            .combine(
                create_timeslot_tag(start.replace(second=0), timedelta(minutes=10))
            )
        ]
        execute_explode(
            start,
            end,
            interval_in_minutes,
            flow_names,
            modes,
            output_file,
            output_format,
            expected_tags,
        )

    def test_export_multiple(self) -> None:
        start = datetime(2023, 1, 1, 0, 0, 0)
        end = datetime(2023, 1, 1, 0, 10, 0)
        interval_in_minutes = 5
        interval = timedelta(minutes=interval_in_minutes)
        first_mode = "first-mode"
        second_mode = "second-mode"
        modes = [first_mode, second_mode]
        output_format = "csv"
        output_file = "output-file.csv"
        first_flow = FlowNameDto("first-flow", "section a", "section b")
        second_flow = FlowNameDto("second-flow", "section c", "section d")
        flow_names = [first_flow, second_flow]
        expected_tags: list[Tag] = [
            create_flow_tag(first_flow.name)
            .combine(create_mode_tag(first_mode))
            .combine(create_timeslot_tag(start, interval)),
            create_flow_tag(first_flow.name)
            .combine(create_mode_tag(first_mode))
            .combine(create_timeslot_tag(start + interval, interval)),
            create_flow_tag(first_flow.name)
            .combine(create_mode_tag(second_mode))
            .combine(create_timeslot_tag(start, interval)),
            create_flow_tag(first_flow.name)
            .combine(create_mode_tag(second_mode))
            .combine(create_timeslot_tag(start + interval, interval)),
            create_flow_tag(second_flow.name)
            .combine(create_mode_tag(first_mode))
            .combine(create_timeslot_tag(start, interval)),
            create_flow_tag(second_flow.name)
            .combine(create_mode_tag(first_mode))
            .combine(create_timeslot_tag(start + interval, interval)),
            create_flow_tag(second_flow.name)
            .combine(create_mode_tag(second_mode))
            .combine(create_timeslot_tag(start, interval)),
            create_flow_tag(second_flow.name)
            .combine(create_mode_tag(second_mode))
            .combine(create_timeslot_tag(start + interval, interval)),
        ]
        execute_explode(
            start,
            end,
            interval_in_minutes,
            flow_names,
            modes,
            output_file,
            output_format,
            expected_tags,
        )


class TestFillZerosExporter:
    def test_export(self) -> None:
        other = Mock(spec=Exporter)
        tag_exploder = Mock(spec=TagExploder)
        tags: list[Tag] = []
        counts = Mock(spec=Count)
        tag_exploder.explode.return_value = tags
        exporter = FillZerosExporter(other, tag_exploder)

        exporter.export(counts, OVERWRITE)

        other.export.assert_called_once_with(FillEmptyCount(counts, tags), OVERWRITE)

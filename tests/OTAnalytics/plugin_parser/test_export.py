from datetime import datetime, timedelta
from unittest.mock import Mock

from OTAnalytics.application.analysis.traffic_counting import (
    Count,
    Exporter,
    FillEmptyCount,
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
from OTAnalytics.plugin_parser.export import FillZerosExporter, TagExploder


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

        exporter.export(counts)

        other.export.assert_called_with(FillEmptyCount(counts, tags))

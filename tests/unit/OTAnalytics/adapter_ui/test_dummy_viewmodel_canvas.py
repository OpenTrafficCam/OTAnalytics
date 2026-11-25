"""What the view model draws on the canvas: section names and flow counts."""

from unittest.mock import Mock

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.application.state import CurrentOrthophoto
from OTAnalytics.domain.event import EventType
from OTAnalytics.domain.flow import Flow, FlowId
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import LineSection, SectionId


def create_section(id: str, name: str) -> LineSection:
    return LineSection(
        id=SectionId(id),
        name=name,
        relative_offset_coordinates={
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
        },
        plugin_data={},
        coordinates=[Coordinate(0, 0), Coordinate(10, 0)],
    )


NORTH = create_section("north", "North")
SOUTH = create_section("south", "South")
FLOW = Flow(id=FlowId("flow"), name="N-S", start=NORTH.id, end=SOUTH.id)
OTHER_FLOW = Flow(id=FlowId("other"), name="S-N", start=SOUTH.id, end=NORTH.id)


def create_target(flows: list[Flow], counts: dict[FlowId, int]) -> tuple:
    application = Mock()
    sections = {NORTH.id: NORTH, SOUTH.id: SOUTH}
    all_flows = {flow.id: flow for flow in flows}
    application.get_all_sections.return_value = [NORTH, SOUTH]
    application.get_section_for.side_effect = sections.get
    application.get_flow_for.side_effect = all_flows.get
    application.flow_state.selected_flows.get.return_value = list(all_flows)
    application.number_of_tracks_assigned_to_each_flow.return_value = counts
    target = DummyViewModel(
        application=application,
        ui_factory=Mock(),
        flow_parser=Mock(),
        name_generator=Mock(),
        event_list_export_formats={},
        show_svz=False,
        add_new_section=Mock(),
        update_section_coordinates=Mock(),
        provide_track_files=Mock(),
        provide_video_files=Mock(),
        current_orthophoto=CurrentOrthophoto(),
    )
    canvas = Mock(spec=AbstractCanvas)
    target.set_canvas(canvas)
    target._get_sections_to_highlight = Mock(  # type: ignore[method-assign]
        return_value=[]
    )
    return target, canvas, application


class TestCanvasItems:
    def test_sections_are_drawn_with_their_name(self) -> None:
        target, canvas, _ = create_target([], {})

        target.refresh_items_on_canvas()

        texts = [call.kwargs["text"] for call in canvas.draw_section.call_args_list]
        assert texts == ["North", "South"]

    def test_arrow_shows_assigned_tracks_of_flow(self) -> None:
        target, canvas, _ = create_target([FLOW], {FLOW.id: 12})

        target.refresh_items_on_canvas()

        assert canvas.draw_arrow.call_args.kwargs["count"] == 12

    def test_arrow_without_count_has_none(self) -> None:
        target, canvas, _ = create_target([FLOW], {})

        target.refresh_items_on_canvas()

        assert canvas.draw_arrow.call_args.kwargs["count"] is None

    def test_counts_are_read_once_for_all_arrows(self) -> None:
        target, canvas, application = create_target([FLOW, OTHER_FLOW], {})

        target.refresh_items_on_canvas()

        assert canvas.draw_arrow.call_count == 2
        application.number_of_tracks_assigned_to_each_flow.assert_called_once()

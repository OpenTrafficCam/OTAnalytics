import pytest

from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.section_geometry import (  # noqa
    close_area,
    closest_knob_index,
    delete_knob,
    has_enough_knobs,
    insert_knob,
    minimum_knob_count,
    open_area,
    ring_half_at,
    shift_knob_backward,
    shift_knob_forward,
    shift_target_index,
)

LINE = [(0, 0), (10, 0), (20, 0)]
SQUARE = [(0, 0), (10, 0), (10, 10), (0, 10)]


class TestMinimumKnobCount:
    def test_line_section_needs_two_knobs(self) -> None:
        assert minimum_knob_count(is_area_section=False) == 2

    def test_area_section_needs_three_knobs(self) -> None:
        assert minimum_knob_count(is_area_section=True) == 3

    @pytest.mark.parametrize(
        "coordinates, is_area_section, expected",
        [
            ([], False, False),
            ([(0, 0)], False, False),
            ([(0, 0), (1, 1)], False, True),
            ([(0, 0), (1, 1)], True, False),
            ([(0, 0), (1, 1), (2, 0)], True, True),
        ],
    )
    def test_has_enough_knobs(
        self,
        coordinates: list[tuple[int, int]],
        is_area_section: bool,
        expected: bool,
    ) -> None:
        assert has_enough_knobs(coordinates, is_area_section) is expected


class TestCloseArea:
    def test_closes_area(self) -> None:
        coordinates = [(0, 0), (10, 0), (10, 10)]

        assert close_area(coordinates, is_area_section=True) == [
            (0, 0),
            (10, 0),
            (10, 10),
            (0, 0),
        ]

    def test_keeps_line_untouched(self) -> None:
        coordinates = [(0, 0), (10, 0)]

        assert close_area(coordinates, is_area_section=False) == coordinates

    def test_does_not_close_already_closed_area(self) -> None:
        coordinates = [(0, 0), (10, 0), (10, 10), (0, 0)]

        assert close_area(coordinates, is_area_section=True) == coordinates


class TestOpenArea:
    def test_drops_closing_coordinate_of_area(self) -> None:
        assert open_area(SQUARE + [(0, 0)], is_area_section=True) == SQUARE

    def test_keeps_open_area(self) -> None:
        assert open_area(SQUARE, is_area_section=True) == SQUARE

    def test_keeps_line(self) -> None:
        assert open_area([(0, 0), (0, 0)], is_area_section=False) == [(0, 0), (0, 0)]


class TestClosestKnobIndex:
    def test_returns_closest_knob_in_radius(self) -> None:
        assert closest_knob_index(LINE, (12, 3), radius=5) == 1

    def test_returns_none_if_no_knob_in_radius(self) -> None:
        assert closest_knob_index(LINE, (5, 8), radius=5) is None

    def test_returns_none_for_empty_coordinates(self) -> None:
        assert closest_knob_index([], (5, 8), radius=5) is None

    def test_prefers_closer_knob(self) -> None:
        assert closest_knob_index([(0, 0), (4, 0)], (3, 0), radius=5) == 1


class TestInsertKnob:
    def test_inserts_between_closest_knobs_of_line(self) -> None:
        coordinates, index = insert_knob(LINE, (14, 2), is_area_section=False)

        assert coordinates == [(0, 0), (10, 0), (14, 2), (20, 0)]
        assert index == 2

    def test_prepends_before_start_of_line(self) -> None:
        coordinates, index = insert_knob(LINE, (-5, 1), is_area_section=False)

        assert coordinates == [(-5, 1), (0, 0), (10, 0), (20, 0)]
        assert index == 0

    def test_appends_after_end_of_line(self) -> None:
        coordinates, index = insert_knob(LINE, (25, 1), is_area_section=False)

        assert coordinates == [(0, 0), (10, 0), (20, 0), (25, 1)]
        assert index == 3

    def test_inserts_into_closing_segment_of_area(self) -> None:
        coordinates, index = insert_knob(SQUARE, (-1, 5), is_area_section=True)

        assert coordinates == SQUARE + [(-1, 5)]
        assert index == 4

    def test_inserts_between_knobs_of_area(self) -> None:
        coordinates, index = insert_knob(SQUARE, (11, 5), is_area_section=True)

        assert coordinates == [(0, 0), (10, 0), (11, 5), (10, 10), (0, 10)]
        assert index == 2

    def test_appends_to_single_knob(self) -> None:
        coordinates, index = insert_knob([(0, 0)], (5, 5), is_area_section=False)

        assert coordinates == [(0, 0), (5, 5)]
        assert index == 1

    def test_does_not_modify_input(self) -> None:
        original = list(LINE)

        insert_knob(original, (14, 2), is_area_section=False)

        assert original == LINE


class TestShiftKnob:
    def test_shift_forward(self) -> None:
        coordinates, index = shift_knob_forward(LINE, 0, is_area_section=False)

        assert coordinates == [(10, 0), (0, 0), (20, 0)]
        assert index == 1

    def test_shift_forward_at_end_of_line_is_ignored(self) -> None:
        coordinates, index = shift_knob_forward(LINE, 2, is_area_section=False)

        assert coordinates == LINE
        assert index == 2

    def test_shift_forward_at_end_of_area_wraps_around(self) -> None:
        coordinates, index = shift_knob_forward(SQUARE, 3, is_area_section=True)

        assert coordinates == [(0, 10), (10, 0), (10, 10), (0, 0)]
        assert index == 0

    def test_shift_backward(self) -> None:
        coordinates, index = shift_knob_backward(LINE, 2, is_area_section=False)

        assert coordinates == [(0, 0), (20, 0), (10, 0)]
        assert index == 1

    def test_shift_backward_at_start_of_line_is_ignored(self) -> None:
        coordinates, index = shift_knob_backward(LINE, 0, is_area_section=False)

        assert coordinates == LINE
        assert index == 0

    def test_shift_backward_at_start_of_area_wraps_around(self) -> None:
        coordinates, index = shift_knob_backward(SQUARE, 0, is_area_section=True)

        assert coordinates == [(0, 10), (10, 0), (10, 10), (0, 0)]
        assert index == 3


class TestDeleteKnob:
    def test_deletes_knob(self) -> None:
        assert delete_knob(LINE, 1, is_area_section=False) == [(0, 0), (20, 0)]

    def test_keeps_minimum_of_line(self) -> None:
        coordinates = [(0, 0), (10, 0)]

        assert delete_knob(coordinates, 1, is_area_section=False) == coordinates

    def test_keeps_minimum_of_area(self) -> None:
        coordinates = [(0, 0), (10, 0), (10, 10)]

        assert delete_knob(coordinates, 1, is_area_section=True) == coordinates

    def test_deletes_knob_of_area(self) -> None:
        assert delete_knob(SQUARE, 0, is_area_section=True) == SQUARE[1:]


class TestShiftRing:
    @pytest.mark.parametrize(
        "index, forward, is_area, expected",
        [
            (1, True, False, 2),
            (1, False, False, 0),
            (0, False, False, None),
            (2, True, False, None),
            (0, False, True, 2),
            (2, True, True, 0),
            (5, True, False, None),
        ],
    )
    def test_shift_target_index(
        self, index: int, forward: bool, is_area: bool, expected: int | None
    ) -> None:
        assert shift_target_index(3, index, forward, is_area) == expected

    @pytest.mark.parametrize(
        "point, expected",
        [
            ((130, 100), True),
            ((70, 100), False),
            ((100, 100), None),
            ((200, 100), None),
        ],
    )
    def test_ring_half_at(self, point: tuple[int, int], expected: bool | None) -> None:
        assert ring_half_at((100, 100), point, 14, 40) is expected

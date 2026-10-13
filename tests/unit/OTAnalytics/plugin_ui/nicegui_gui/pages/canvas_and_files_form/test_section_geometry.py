import pytest

from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.section_geometry import (  # noqa
    close_area,
    has_enough_knobs,
    minimum_knob_count,
)


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

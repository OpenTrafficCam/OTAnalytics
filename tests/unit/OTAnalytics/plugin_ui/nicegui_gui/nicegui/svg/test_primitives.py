import pytest

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.knob import Knob
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polygon import Polygon
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import (
    dot,
    fmt,
    screen_px,
)

STYLE_ATTRIBUTES = ["fill=", "stroke=", "stroke-width", "pointer-events", "cursor"]


@pytest.mark.parametrize(
    "value, expected", [(12.0, "12"), (12.25, "12.2"), (-3.04, "-3"), (7, "7")]
)
def test_fmt(value: float, expected: str) -> None:
    assert fmt(value) == expected


def test_dot_is_zero_length_path() -> None:
    assert dot(10, 20, "pt", "s-0") == '<path id="s-0" class="pt" d="M10 20h0"/>'
    assert dot(1.5, 2, "pt-ring") == '<path class="pt-ring" d="M1.5 2h0"/>'


def test_screen_px_wraps_content_in_scaled_group() -> None:
    assert screen_px(5, 6, "X", "ota-chip") == (
        '<g transform="translate(5 6)"><g class="ota-scaled ota-chip">X</g></g>'
    )
    assert screen_px(5, 6, "X") == (
        '<g transform="translate(5 6)"><g class="ota-scaled">X</g></g>'
    )


def test_polyline() -> None:
    assert Polyline([(10, 20), (30, 40)]).to_svg("line") == (
        '<polyline class="line" points="10,20 30,40"/>'
    )
    assert Polyline([]).to_svg("line") == '<polyline class="line" points=""/>'


def test_polygon() -> None:
    assert Polygon([(0, 0), (10, 0), (10, 10)]).to_svg("casing") == (
        '<polygon class="casing" points="0,0 10,0 10,10"/>'
    )


def test_circle_is_point_dot() -> None:
    circle = Circle(id="new_point-0", x=3, y=4)

    assert circle.to_svg() == dot(3, 4, "pt", "new_point-0")
    assert circle.to_tuple() == (3, 4)


def test_line_is_rubber_band() -> None:
    assert Line(id="rubber", x1=0, y1=1, x2=5, y2=6).to_svg() == (
        '<line class="ota-rubber" x1="0" y1="1" x2="5" y2="6"/>'
    )


def test_knob() -> None:
    svg = Knob(index=2, x=7, y=8).to_svg()

    assert svg.startswith('<g class="ota-knob">')
    assert dot(7, 8, "halo") in svg
    assert dot(7, 8, "ring") in svg
    assert dot(7, 8, "core") in svg
    assert dot(7, 8, "hit", "edit-knob-2") in svg
    assert svg.count("id=") == 1


def test_active_knob() -> None:
    svg = Knob(index=2, x=7, y=8, active=True).to_svg()

    assert svg.startswith('<g class="ota-knob active">')


def test_moving_knob() -> None:
    svg = Knob(index=2, x=7, y=8, active=True, moving=True).to_svg()

    assert svg.startswith('<g class="ota-knob active moving">')


@pytest.mark.parametrize(
    "svg",
    [
        Polyline([(0, 0), (1, 1)]).to_svg("line"),
        Polygon([(0, 0), (1, 1), (1, 0)]).to_svg("line"),
        Circle(id="c", x=0, y=0).to_svg(),
        Line(id="l", x1=0, y1=0, x2=1, y2=1).to_svg(),
        Knob(index=0, x=0, y=0, active=True).to_svg(),
    ],
)
def test_no_inline_styles(svg: str) -> None:
    for attribute in STYLE_ATTRIBUTES:
        assert attribute not in svg

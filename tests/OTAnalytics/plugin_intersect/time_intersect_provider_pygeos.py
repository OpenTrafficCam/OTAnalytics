from typing import Any

import matplotlib.pyplot as plt
from pygeos import GeometryType
from pygeos import get_coordinates as pygeos_coords
from pygeos import get_type_id as pygeos_type
from pygeos import intersection, is_empty, linestrings

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Detection, Track
from tests.OTAnalytics.plugin_intersect.validate import time

OFFSET_X = 0.5
OFFSET_Y = 0.5
EVENTS = list[tuple[float, float]]


def detection_to_coords(d: Detection) -> tuple[float, float]:
    return (d.x + OFFSET_X * d.w, d.y + OFFSET_Y * d.h)


def track_to_pygeos(track: Track) -> Any:
    return linestrings([[detection_to_coords(d) for d in track.detections]])


def detection_project_x_time(d: Detection) -> tuple[float, float]:
    return (d.frame, d.x + OFFSET_X * d.w)


def track_to_pygeos_project_x(track: Track) -> Any:
    return linestrings([[detection_project_x_time(d) for d in track.detections]])


def detection_project_y_time(d: Detection) -> tuple[float, float]:
    return (d.frame, d.y + OFFSET_Y * d.h)


def track_to_pygeos_project_y(track: Track) -> Any:
    return linestrings([[detection_project_y_time(d) for d in track.detections]])


def point_project_x_time(p: Any) -> Any:
    return linestrings([[(0, p.x), (1000000, p.x)]])


def point_project_y_time(p: Any) -> Any:
    return linestrings([[(0, p.y), (1000000, p.y)]])


def section_to_pygeos(section: Section) -> Any:
    return linestrings([[(c.x, c.y) for c in section.get_coordinates()]])


def intersection_to_points(intersection: Any) -> Any:
    points: list[Any] = []
    if is_empty(points):
        if pygeos_type(points) == GeometryType.POINT:
            points = [intersection]

        if pygeos_type(points) == GeometryType.MULTIPOINT:
            return points

    return points


@time
def test(datastore: Datastore) -> None:
    tracks = datastore.get_all_tracks()
    track_geom_map = {track.id: track_to_pygeos(track) for track in tracks}
    track_x_projection = {
        track.id: track_to_pygeos_project_x(track) for track in tracks
    }
    track_y_projection = {
        track.id: track_to_pygeos_project_y(track) for track in tracks
    }

    sections = datastore.get_all_sections()
    section_geom_map = {section.id: section_to_pygeos(section) for section in sections}

    compute(
        tracks,
        track_geom_map,
        track_x_projection,
        track_y_projection,
        sections,
        section_geom_map,
    )


@time
def compute(
    tracks: Any,
    track_geom_map: Any,
    track_x_projection: Any,
    track_y_projection: Any,
    sections: Any,
    section_geom_map: Any,
) -> Any:
    for section in sections:
        sec_geom = section_geom_map[section.id]

        for track in tracks:
            track_geom = track_geom_map[track.id]

            points = intersection_to_points(intersection(track_geom, sec_geom))

            times = []
            for point in points:
                x_points = [
                    (round(p.x, 5), p.y)
                    for p in intersection_to_points(
                        intersection(
                            point_project_x_time(point), track_x_projection[track.id]
                        )
                    )
                ]
                y_points = [
                    (round(p.x, 5), p.y)
                    for p in intersection_to_points(
                        intersection(
                            point_project_y_time(point), track_y_projection[track.id]
                        )
                    )
                ]

                time = [
                    (x, y, t_x)
                    for t_x, x in x_points
                    for t_y, y in y_points
                    if abs(t_x - t_y) < 0.00001
                ]

                times += time

            if len(times) > 0:
                print("min", min(times, key=lambda t: t[2]))


if __name__ == "__main__":
    # data = load_data(skip_tracks=False, size="medium")
    # test(data)

    line = linestrings(
        [
            [
                (0, 0),
                (2, 1),
                (4, 1),
                (5, 6),
                (7, 7),
                (10, 7),
                (11, 5),
                (16, 8),
                (10, 11),
            ]
        ]
    )
    sec = linestrings([[(11, 11), (15, 4)]])
    coords_l = pygeos_coords(line)
    # plt.plot(*)
    plt.plot(*pygeos_coords(sec))
    plt.show()
    plt.clf()

    x_proj = linestrings(
        [
            [
                (0, 0),
                (1, 2),
                (2, 4),
                (3, 5),
                (4, 7),
                (5, 10),
                (6, 11),
                (7, 16),
                (8, 10),
            ]
        ]
    )

    x1 = linestrings([[(0, 13.553191489361701), (8, 13.553191489361701)]])
    x2 = linestrings([[(0, 11.4), (8, 11.4)]])

    plt.plot(*x_proj)
    plt.plot(*x1)
    plt.plot(*x2)
    # plt.show()
    plt.clf()

    y_proj = linestrings(
        [
            [
                (0, 0),
                (1, 1),
                (2, 1),
                (3, 6),
                (4, 7),
                (5, 7),
                (6, 5),
                (7, 8),
                (8, 11),
            ]
        ]
    )

    y1 = linestrings([[(0, 6.531914893617022), (8, 6.531914893617022)]])
    y2 = linestrings([[(0, 10.3), (8, 10.3)]])

    plt.plot(*y_proj)
    plt.plot(*y1)
    plt.plot(*y2)
    # plt.show()
    plt.clf()

    print("xy X sec:", intersection(line, sec))

    print("xt X x1:", intersection(x_proj, x1))
    print("yt X y1:", intersection(y_proj, y1))

    print("xt X x2:", intersection(x_proj, x2))
    print("yt X y2:", intersection(y_proj, y2))

from typing import Any

import matplotlib.pyplot as plt
import shapely
from pygeos import linestrings
from shapely import LineString as ShapelyLineString

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Detection, Track
from tests.OTAnalytics.plugin_intersect.validate import time

OFFSET_X = 0.5
OFFSET_Y = 0.5
EVENTS = list[tuple[float, float]]


def detection_to_coords(d: Detection) -> tuple[float, float]:
    return (d.x + OFFSET_X * d.w, d.y + OFFSET_Y * d.h)


def track_to_shapely(track: Track) -> ShapelyLineString:
    return ShapelyLineString([detection_to_coords(d) for d in track.detections])


def detection_project_x_time(d: Detection) -> tuple[float, float]:
    return (d.frame, d.x + OFFSET_X * d.w)


def track_to_shapely_project_x(track: Track) -> ShapelyLineString:
    return ShapelyLineString([detection_project_x_time(d) for d in track.detections])


def detection_project_y_time(d: Detection) -> tuple[float, float]:
    return (d.frame, d.y + OFFSET_Y * d.h)


def track_to_shapely_project_y(track: Track) -> ShapelyLineString:
    return ShapelyLineString([detection_project_y_time(d) for d in track.detections])


def point_project_x_time(p: shapely.Point) -> ShapelyLineString:
    return ShapelyLineString([(0, p.x), (1000000, p.x)])


def point_project_y_time(p: shapely.Point) -> ShapelyLineString:
    return ShapelyLineString([(0, p.y), (1000000, p.y)])


def segment_to_time_shapely(
    frm: tuple[float, float], to: tuple[float, float]
) -> shapely.Polygon:
    return ShapelyLineString([frm, to])


def section_to_shapely(section: Section) -> ShapelyLineString:
    return ShapelyLineString([(c.x, c.y) for c in section.get_coordinates()])


def section_to_shapely_plane(section: Section) -> shapely.MultiPolygon:
    return shapely.MultiPolygon(
        polygons=[
            (
                (f.x, f.y, 0),
                (t.x, t.y, 0),
                (t.x, t.y, 100000),
                (f.x, f.y, 100000),
                (f.x, f.y, 0),
            )
            for f in section.get_coordinates()[:-1]
            for t in section.get_coordinates()[1:]
        ]
    )


def coords_to_pygeos(coord_list: list[tuple[float, float]]) -> Any:
    return linestrings([coord_list])


def section_to_pygeos(section: Section) -> Any:
    return linestrings([[(c.x, c.y) for c in section.get_coordinates()]])


def intersection_to_points(intersection: Any) -> Any:
    points = []
    if not intersection.is_empty:
        if isinstance(intersection, shapely.Point):
            points = [intersection]
        elif isinstance(intersection, shapely.MultiPoint):
            points = list(intersection.geoms)

    return points


@time
def test(datastore: Datastore) -> None:
    tracks = datastore.get_all_tracks()
    track_geom_map = {track.id: track_to_shapely(track) for track in tracks}
    track_x_projection = {
        track.id: track_to_shapely_project_x(track) for track in tracks
    }
    track_y_projection = {
        track.id: track_to_shapely_project_y(track) for track in tracks
    }

    sections = datastore.get_all_sections()
    section_geom_map = {section.id: section_to_shapely(section) for section in sections}

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

            points = intersection_to_points(track_geom.intersection(sec_geom))

            times = []
            for point in points:
                x_points = [
                    (round(p.x, 5), p.y)
                    for p in intersection_to_points(
                        point_project_x_time(point).intersection(
                            track_x_projection[track.id]
                        )
                    )
                ]
                y_points = [
                    (round(p.x, 5), p.y)
                    for p in intersection_to_points(
                        point_project_y_time(point).intersection(
                            track_y_projection[track.id]
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

    line = shapely.LineString(
        coordinates=[
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
    )
    sec = shapely.LineString(coordinates=[(11, 11), (15, 4)])

    print(line.xy)
    print(sec.xy)
    print(*line.xy)
    print(*sec.xy)
    plt.plot(*line.xy)
    plt.plot(*sec.xy)
    plt.show()
    plt.clf()

    x_proj = shapely.LineString(
        coordinates=[
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
    )

    x1 = shapely.LineString(
        coordinates=[(0, 13.553191489361701), (8, 13.553191489361701)]
    )
    x2 = shapely.LineString(coordinates=[(0, 11.4), (8, 11.4)])

    plt.plot(*x_proj.xy)
    plt.plot(*x1.xy)
    plt.plot(*x2.xy)
    # plt.show()
    plt.clf()

    y_proj = shapely.LineString(
        coordinates=[
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
    )

    y1 = shapely.LineString(
        coordinates=[(0, 6.531914893617022), (8, 6.531914893617022)]
    )
    y2 = shapely.LineString(coordinates=[(0, 10.3), (8, 10.3)])

    plt.plot(*y_proj.xy)
    plt.plot(*y1.xy)
    plt.plot(*y2.xy)
    # plt.show()
    plt.clf()

    print("xy X sec:", line.intersection(sec))

    print("xt X x1:", x_proj.intersection(x1))
    print("yt X y1:", y_proj.intersection(y1))

    print("xt X x2:", x_proj.intersection(x2))
    print("yt X y2:", y_proj.intersection(y2))

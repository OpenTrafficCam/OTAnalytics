import bz2
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import polars as pl
import pytest

from OTAnalytics.application.use_cases.geo_track_export import (
    GeoTrackExportSpecification,
)
from OTAnalytics.domain import track
from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_datastore.polars_track_store import PolarsTrackDataset
from OTAnalytics.plugin_datastore.python_track_store import PythonTrackDataset
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    PolarsTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_parser.json_parser import parse_json_bz2
from OTAnalytics.plugin_track_export.geo.geo_track_writer import (
    DomainGeoTrackWriter,
    GeoTrackExport,
    GeoTrackWriter,
    PolarsGeoTrackWriter,
)
from tests.utils.builders.track_builder import TrackBuilder

GEO_X = 455123.123456789
GEO_Y = 5701234.56789012


def build_track(
    track_id: str,
    geo: list[tuple[float, float] | None],
    start_second: int = 0,
    track_class: str = "car",
) -> Track:
    builder = TrackBuilder(
        track_id=track_id, track_class=track_class, detection_class=track_class
    )
    for offset, coordinate in enumerate(geo):
        builder.add_second(start_second + offset)
        builder.geo_x, builder.geo_y = coordinate if coordinate else (None, None)
        builder.append_detection()
    return builder.build_track()


def polars_dataset(tracks: list[Track]) -> TrackDataset:
    """Polars dataset incl. geo columns (`from_list` does not carry them)."""
    dataset = PolarsTrackDataset.from_list(
        tracks, PolarsTrackGeometryDataset.from_track_dataset
    )
    detections = [d for t in tracks for d in t.detections]
    data = dataset.get_data().with_columns(
        pl.Series(track.GEO_X, [d.geo_x for d in detections], dtype=pl.Float64),
        pl.Series(track.GEO_Y, [d.geo_y for d in detections], dtype=pl.Float64),
    )
    return PolarsTrackDataset.from_dataframe(
        data, PolarsTrackGeometryDataset.from_track_dataset
    )


def python_dataset(tracks: list[Track]) -> TrackDataset:
    return PythonTrackDataset.from_list(
        tracks, ShapelyTrackGeometryDataset.from_track_dataset
    )


def read(path: Path) -> dict:
    return parse_json_bz2(path)


@pytest.fixture
def spec(tmp_path: Path) -> GeoTrackExportSpecification:
    return GeoTrackExportSpecification(tmp_path, "chunk")


WRITERS = [
    pytest.param(PolarsGeoTrackWriter(), polars_dataset, id="polars"),
    pytest.param(DomainGeoTrackWriter(), python_dataset, id="domain"),
]


@pytest.mark.parametrize("writer, provide", WRITERS)
class TestGeoTrackWriters:
    def test_export_writes_only_display_fields(
        self,
        writer: GeoTrackWriter,
        provide: Callable[[list[Track]], TrackDataset],
        spec: GeoTrackExportSpecification,
    ) -> None:
        path = writer.write(provide([build_track("1", [(1.0, 2.0)])]), spec)

        assert path is not None
        content = read(path)
        assert content["metadata"] == {"format": "otanalytics.geo_tracks", "version": 1}
        (detection,) = content["data"]["detections"]
        assert set(detection) == {"track-id", "class", "geo_x", "geo_y", "occurrence"}
        assert detection["track-id"] == "1"
        assert detection["class"] == "car"

    def test_geo_values_keep_full_precision(
        self,
        writer: GeoTrackWriter,
        provide: Callable[[list[Track]], TrackDataset],
        spec: GeoTrackExportSpecification,
    ) -> None:
        path = writer.write(provide([build_track("1", [(GEO_X, GEO_Y)])]), spec)

        assert path is not None
        (detection,) = read(path)["data"]["detections"]
        assert detection["geo_x"] == GEO_X
        assert detection["geo_y"] == GEO_Y

    def test_detection_without_geo_is_dropped(
        self,
        writer: GeoTrackWriter,
        provide: Callable[[list[Track]], TrackDataset],
        spec: GeoTrackExportSpecification,
    ) -> None:
        given = build_track("1", [(1.0, 2.0), None, (3.0, 4.0)])

        path = writer.write(provide([given]), spec)

        assert path is not None
        detections = read(path)["data"]["detections"]
        assert [d["geo_x"] for d in detections] == [1.0, 3.0]

    def test_detection_with_nan_geo_is_dropped(
        self,
        writer: GeoTrackWriter,
        provide: Callable[[list[Track]], TrackDataset],
        spec: GeoTrackExportSpecification,
    ) -> None:
        nan = float("nan")
        given = build_track("1", [(1.0, 2.0), (nan, 2.5), (2.5, nan), (3.0, 4.0)])

        path = writer.write(provide([given]), spec)

        assert path is not None
        with bz2.open(path, "rt", encoding="UTF-8") as file:
            raw = file.read()
        assert "NaN" not in raw
        detections = read(path)["data"]["detections"]
        assert [d["geo_x"] for d in detections] == [1.0, 3.0]

    def test_no_geo_detections_returns_none_and_writes_nothing(
        self,
        writer: GeoTrackWriter,
        provide: Callable[[list[Track]], TrackDataset],
        spec: GeoTrackExportSpecification,
    ) -> None:
        assert writer.write(provide([build_track("1", [None, None])]), spec) is None
        assert list(spec.export_directory.iterdir()) == []

    def test_filename_uses_earliest_detection_in_utc(
        self,
        writer: GeoTrackWriter,
        provide: Callable[[list[Track]], TrackDataset],
        spec: GeoTrackExportSpecification,
    ) -> None:
        given = build_track("1", [(1.0, 2.0), (3.0, 4.0)], start_second=5)

        path = writer.write(provide([given]), spec)

        assert path is not None
        first = given.first_detection.occurrence.astimezone(timezone.utc)
        expected = first.strftime("%Y-%m-%d_%H-%M-%S")
        assert path.name == f"chunk_{expected}.geo_tracks.json.bz2"
        first_detection, _ = read(path)["data"]["detections"]
        assert first_detection["occurrence"] == first.timestamp()


def test_polars_and_domain_writer_produce_same_content(
    tmp_path: Path,
) -> None:
    tracks = [
        build_track("1", [(GEO_X, GEO_Y), None, (3.5, 4.5)], 0, "car"),
        build_track("2", [(5.5, 6.5), (7.5, 8.5)], 1, "truck"),
    ]
    polars_spec = GeoTrackExportSpecification(tmp_path / "polars", "chunk")
    domain_spec = GeoTrackExportSpecification(tmp_path / "domain", "chunk")

    polars_path = PolarsGeoTrackWriter().write(polars_dataset(tracks), polars_spec)
    domain_path = DomainGeoTrackWriter().write(python_dataset(tracks), domain_spec)

    assert polars_path is not None and domain_path is not None
    assert polars_path.name == domain_path.name
    polars_content = read(polars_path)
    domain_content = read(domain_path)
    key = lambda d: (d["occurrence"], d["track-id"])  # noqa: E731
    polars_content["data"]["detections"].sort(key=key)
    domain_content["data"]["detections"].sort(key=key)
    assert polars_content == domain_content


@pytest.mark.skipif(
    sys.platform == "win32", reason="Windows has no POSIX file permissions"
)
def test_written_file_gets_default_permissions(tmp_path: Path) -> None:
    spec = GeoTrackExportSpecification(tmp_path, "chunk")
    tracks = [build_track("1", [(1.0, 2.0)])]
    old_umask = os.umask(0o022)
    try:
        path = PolarsGeoTrackWriter().write(polars_dataset(tracks), spec)
    finally:
        os.umask(old_umask)

    assert path is not None
    assert path.stat().st_mode & 0o777 == 0o644


def test_failed_write_keeps_old_file_and_leaves_no_temp_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = GeoTrackExportSpecification(tmp_path, "chunk")
    tracks = [build_track("1", [(1.0, 2.0)])]
    path = PolarsGeoTrackWriter().write(polars_dataset(tracks), spec)
    assert path is not None
    old_content = path.read_bytes()

    def fail(*args: object, **kwargs: object) -> None:
        raise OSError("boom")

    monkeypatch.setattr("os.replace", fail)

    with pytest.raises(OSError):
        DomainGeoTrackWriter().write(python_dataset(tracks), spec)

    assert path.read_bytes() == old_content
    assert list(tmp_path.iterdir()) == [path]


class TestGeoTrackExport:
    def test_uses_first_supporting_writer(
        self, spec: GeoTrackExportSpecification
    ) -> None:
        dataset = Mock()
        repository = Mock()
        repository.get_all.return_value = dataset
        unsupported = Mock()
        unsupported.supports.return_value = False
        supported = Mock()
        supported.supports.return_value = True

        result = GeoTrackExport(repository, [unsupported, supported]).export(spec)

        assert result is supported.write.return_value
        supported.write.assert_called_once_with(dataset, spec)
        unsupported.write.assert_not_called()

    def test_raises_without_supporting_writer(
        self, spec: GeoTrackExportSpecification
    ) -> None:
        writer = Mock()
        writer.supports.return_value = False
        with pytest.raises(TypeError):
            GeoTrackExport(Mock(), [writer]).export(spec)


def test_naive_occurrence_is_utc() -> None:
    from OTAnalytics.plugin_track_export.geo.geo_track_writer import _to_unix_seconds

    assert _to_unix_seconds(datetime(2023, 1, 1)) == 1672531200.0

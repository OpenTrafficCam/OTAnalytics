import bz2
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol, Sequence, cast

import polars as pl

from OTAnalytics.application.use_cases.geo_track_export import (
    ExportGeoTracks,
    GeoTrackExportSpecification,
)
from OTAnalytics.domain import track
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.plugin_datastore.polars_track_store import (
    PolarsDataFrameProvider,
    drop_row_id,
)

FORMAT_NAME = "otanalytics.geo_tracks"
FORMAT_VERSION = 1
FILE_SUFFIX = ".geo_tracks.json.bz2"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
TRACK_ID_KEY = "track-id"
CLASS_KEY = "class"
GEO_X_KEY = "geo_x"
GEO_Y_KEY = "geo_y"
OCCURRENCE_KEY = "occurrence"


class GeoTrackWriter(Protocol):
    """Writes the geo tracks of one kind of track dataset."""

    def supports(self, dataset: object) -> bool: ...

    def write(
        self, dataset: object, specification: GeoTrackExportSpecification
    ) -> Path | None: ...


def _to_unix_seconds(occurrence: datetime) -> float:
    if occurrence.tzinfo is None:
        occurrence = occurrence.replace(tzinfo=timezone.utc)
    return occurrence.timestamp()


def _write_detections(
    detections: list[dict[str, Any]], specification: GeoTrackExportSpecification
) -> Path | None:
    """Write detections to the file named after the earliest detection (UTC)."""
    if not detections:
        return None
    earliest = min(detection[OCCURRENCE_KEY] for detection in detections)
    timestamp = datetime.fromtimestamp(earliest, tz=timezone.utc).strftime(
        TIMESTAMP_FORMAT
    )
    path = specification.export_directory / (
        f"{specification.export_filename_stem}_{timestamp}{FILE_SUFFIX}"
    )
    content = {
        "metadata": {"format": FORMAT_NAME, "version": FORMAT_VERSION},
        "data": {"detections": detections},
    }
    specification.export_directory.mkdir(parents=True, exist_ok=True)
    with bz2.open(path, "wt", encoding="UTF-8") as file:
        json.dump(content, file)
    return path


class PolarsGeoTrackWriter:
    """Selects the needed columns of a polars dataset without a per-detection loop."""

    def supports(self, dataset: object) -> bool:
        return isinstance(dataset, PolarsDataFrameProvider)

    def write(
        self, dataset: object, specification: GeoTrackExportSpecification
    ) -> Path | None:
        df = drop_row_id(cast(PolarsDataFrameProvider, dataset).get_data())
        if track.GEO_X not in df.columns or track.GEO_Y not in df.columns:
            return None
        class_column = (
            track.TRACK_CLASSIFICATION
            if track.TRACK_CLASSIFICATION in df.columns
            else track.CLASSIFICATION
        )
        occurrence = pl.col(track.OCCURRENCE)
        if cast(pl.Datetime, df.schema[track.OCCURRENCE]).time_zone is None:
            occurrence = occurrence.dt.replace_time_zone("UTC")
        selected = (
            df.drop_nulls([track.GEO_X, track.GEO_Y])
            .select(
                pl.col(track.TRACK_ID).cast(pl.Utf8).alias(TRACK_ID_KEY),
                pl.col(class_column).alias(CLASS_KEY),
                pl.col(track.GEO_X).alias(GEO_X_KEY),
                pl.col(track.GEO_Y).alias(GEO_Y_KEY),
                (occurrence.dt.cast_time_unit("us").dt.epoch("us") / 1_000_000).alias(
                    OCCURRENCE_KEY
                ),
            )
            .sort(OCCURRENCE_KEY, maintain_order=True)
        )
        return _write_detections(selected.to_dicts(), specification)


class DomainGeoTrackWriter:
    """Fallback iterating over tracks and detections of any `TrackDataset`."""

    def supports(self, dataset: object) -> bool:
        return isinstance(dataset, TrackDataset)

    def write(
        self, dataset: object, specification: GeoTrackExportSpecification
    ) -> Path | None:
        detections: list[dict[str, Any]] = [
            {
                TRACK_ID_KEY: _track.id.id,
                CLASS_KEY: _track.classification,
                GEO_X_KEY: detection.geo_x,
                GEO_Y_KEY: detection.geo_y,
                OCCURRENCE_KEY: _to_unix_seconds(detection.occurrence),
            }
            for _track in cast(TrackDataset, dataset).as_list()
            for detection in _track.detections
            if detection.geo_x is not None and detection.geo_y is not None
        ]
        detections.sort(key=lambda detection: detection[OCCURRENCE_KEY])
        return _write_detections(detections, specification)


class GeoTrackExport(ExportGeoTracks):
    """Exports the geo tracks of the repository with the first supporting writer."""

    def __init__(
        self, track_repository: TrackRepository, writers: Sequence[GeoTrackWriter]
    ) -> None:
        self._track_repository = track_repository
        self._writers = writers

    def export(self, specification: GeoTrackExportSpecification) -> Path | None:
        dataset = self._track_repository.get_all()
        for writer in self._writers:
            if writer.supports(dataset):
                return writer.write(dataset, specification)
        raise TypeError(
            f"No geo track writer found for dataset of type {type(dataset).__name__}."
        )

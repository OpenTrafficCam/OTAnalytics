from typing import Any

import pytest

from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset.track_dataset import (
    IncompatibleGeoreferenceMetadataError,
    TrackDataset,
)
from OTAnalytics.plugin_datastore.python_track_store import PythonTrackIdSet
from tests.utils.assertions import assert_equal_track_properties
from tests.utils.builders.track_dataset_provider import (
    IMPLEMENTATIONS,
    TrackDatasetProvider,
)

SAMPLE_METADATA = GeoreferenceMetadata(
    geo_min_x=0.0,
    geo_min_y=0.0,
    geo_max_x=100.0,
    geo_max_y=100.0,
    birds_eye_view_width=10,
    birds_eye_view_height=10,
    padding=0,
    crs="EPSG:25833",
)


class _MinimalTrackDataset(TrackDataset):
    """Concrete subclass that overrides only the methods touched by this test."""

    track_ids = None  # type: ignore[assignment]
    first_occurrence = None  # type: ignore[assignment]
    last_occurrence = None  # type: ignore[assignment]
    classifications = frozenset()  # type: ignore[assignment]
    empty = True  # type: ignore[assignment]

    def __len__(self) -> int:
        return 0

    def add_all(self, other: Any) -> Any:  # type: ignore[override]
        raise NotImplementedError

    def get_for(self, id: Any) -> Any:  # type: ignore[override]
        return None

    def remove(self, track_id: Any) -> Any:  # type: ignore[override]
        return self

    def remove_multiple(self, track_ids: Any) -> Any:  # type: ignore[override]
        return self

    def clear(self) -> Any:  # type: ignore[override]
        return self

    def split_finished(self) -> Any:  # type: ignore[override]
        return self, self

    def as_list(self) -> Any:  # type: ignore[override]
        return []

    def intersecting_tracks(
        self, sections: Any, offset: Any
    ) -> Any:  # type: ignore[override]
        return None

    def intersection_points(
        self, sections: Any, offset: Any
    ) -> Any:  # type: ignore[override]
        return None

    def contained_by_sections(
        self, sections: Any, offset: Any
    ) -> Any:  # type: ignore[override]
        return {}

    def split(self, chunks: Any) -> Any:  # type: ignore[override]
        return [self]

    def filter_by_min_detection_length(
        self, length: Any
    ) -> Any:  # type: ignore[override]
        return self

    def calculate_geometries_for(self, offsets: Any) -> None:  # type: ignore[override]
        return None

    def get_first_segments(self) -> Any:  # type: ignore[override]
        return None

    def get_last_segments(self) -> Any:  # type: ignore[override]
        return None

    def cut_with_section(
        self, section: Any, offset: Any
    ) -> Any:  # type: ignore[override]
        return self, None

    def get_max_confidences_for(self, track_ids: Any) -> Any:  # type: ignore[override]
        return {}

    def revert_cuts_for(self, original_track_ids: Any) -> Any:  # type: ignore[override]
        return self, None, None

    def remove_by_original_ids(
        self, original_ids: Any
    ) -> Any:  # type: ignore[override]
        return self, None


class TestTrackDatasetGeoreferenceDefaults:
    def test_georeference_metadata_default_is_none(self) -> None:
        dataset = _MinimalTrackDataset()
        assert dataset.georeference_metadata is None

    def test_with_georeference_metadata_raises_not_implemented(self) -> None:
        dataset = _MinimalTrackDataset()
        with pytest.raises(NotImplementedError) as info:
            dataset.with_georeference_metadata(SAMPLE_METADATA)
        assert "_MinimalTrackDataset" in str(info.value)


class TestIncompatibleGeoreferenceMetadataError:
    def test_can_be_raised_and_carries_message(self) -> None:
        with pytest.raises(IncompatibleGeoreferenceMetadataError) as info:
            raise IncompatibleGeoreferenceMetadataError("boom")
        assert str(info.value) == "boom"


class TestTrackDataset:
    def test_revert_cuts_for(
        self,
        first_track_part_1: Track,
        first_track_part_2: Track,
        uncut_track: Track,
        bicycle_track: Track,
        expected_first_track: Track,
    ) -> None:
        targets = create_track_datasets(
            [bicycle_track, first_track_part_2, first_track_part_1, uncut_track]
        )
        for target in targets:
            assert len(target) == 4
            actual_dataset, reverted_ids, removed_ids = target.revert_cuts_for(
                PythonTrackIdSet(
                    [first_track_part_1.original_id, uncut_track.original_id]
                )
            )
            assert reverted_ids == PythonTrackIdSet([first_track_part_1.original_id])
            assert removed_ids == PythonTrackIdSet(
                [first_track_part_1.id, first_track_part_2.id]
            )
            assert len(actual_dataset) == 3
            actual_first_track = actual_dataset.get_for(first_track_part_1.original_id)
            actual_uncut_track = actual_dataset.get_for(uncut_track.original_id)
            actual_bicycle_track = actual_dataset.get_for(bicycle_track.id)
            assert actual_first_track is not None
            assert actual_uncut_track is not None
            assert actual_bicycle_track is not None
            assert_equal_track_properties(actual_first_track, expected_first_track)
            assert_equal_track_properties(actual_uncut_track, uncut_track)
            assert_equal_track_properties(actual_bicycle_track, bicycle_track)

    def test_remove_by_original_ids(
        self, first_track_part_1: Track, first_track_part_2: Track, uncut_track: Track
    ) -> None:
        targets = create_track_datasets(
            [first_track_part_1, first_track_part_2, uncut_track]
        )
        for target in targets:
            assert len(target) == 3
            actual_dataset, removed_ids = target.remove_by_original_ids(
                PythonTrackIdSet([first_track_part_1.original_id])
            )
            assert actual_dataset.track_ids == PythonTrackIdSet([uncut_track.id])
            assert removed_ids == PythonTrackIdSet(
                [first_track_part_1.id, first_track_part_2.id]
            )
            assert len(actual_dataset) == 1


def create_track_datasets(tracks: list[Track]) -> list[TrackDataset]:
    provider = TrackDatasetProvider()
    return [
        provider.provide(implementation, tracks) for implementation in IMPLEMENTATIONS
    ]

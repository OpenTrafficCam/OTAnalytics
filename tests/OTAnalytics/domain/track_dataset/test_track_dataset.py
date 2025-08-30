from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_datastore.python_track_store import PythonTrackIdSet
from tests.utils.assertions import assert_equal_track_properties
from tests.utils.builders.track_dataset_provider import (
    IMPLEMENTATIONS,
    TrackDatasetProvider,
)


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
            actual = target.revert_cuts_for(
                PythonTrackIdSet(
                    [first_track_part_1.original_id, uncut_track.original_id]
                )
            )
            assert len(actual) == 3
            actual_first_track = actual.get_for(first_track_part_1.original_id)
            actual_uncut_track = actual.get_for(uncut_track.original_id)
            actual_bicycle_track = actual.get_for(bicycle_track.id)
            assert actual_first_track is not None
            assert actual_uncut_track is not None
            assert actual_bicycle_track is not None
            assert_equal_track_properties(actual_first_track, expected_first_track)
            assert_equal_track_properties(actual_uncut_track, uncut_track)
            assert_equal_track_properties(actual_bicycle_track, bicycle_track)


def create_track_datasets(tracks: list[Track]) -> list[TrackDataset]:
    provider = TrackDatasetProvider()
    return [
        provider.provide(implementation, tracks) for implementation in IMPLEMENTATIONS
    ]

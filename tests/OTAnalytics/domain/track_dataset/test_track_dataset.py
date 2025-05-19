from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
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
            actual_dataset, reverted_ids, removed_ids = target.revert_cuts_for(
                frozenset([first_track_part_1.original_id, uncut_track.original_id])
            )
            assert reverted_ids == frozenset([first_track_part_1.original_id])
            assert removed_ids == frozenset(
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
                frozenset([first_track_part_1.original_id])
            )
            assert actual_dataset.track_ids == frozenset([uncut_track.id])
            assert removed_ids == frozenset(
                [first_track_part_1.id, first_track_part_2.id]
            )
            assert len(actual_dataset) == 1


def create_track_datasets(tracks: list[Track]) -> list[TrackDataset]:
    provider = TrackDatasetProvider()
    return [
        provider.provide(implementation, tracks) for implementation in IMPLEMENTATIONS
    ]

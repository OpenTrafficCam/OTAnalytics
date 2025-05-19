from typing import Callable, cast
from unittest.mock import Mock, call

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.plugin_intersect_parallelization.sequential import SequentialIntersect


class TestSequentialIntersect:
    def test_execute(self) -> None:
        event_1 = Mock(spec=Event)
        event_2 = Mock(spec=Event)
        side_effect = [[event_1], [event_2]]

        mock_intersect = Mock(spec=Callable, side_effect=side_effect)
        first_track_dataset = Mock()
        second_track_dataset = Mock()
        sections: list[Section] = [Mock()]

        tasks: list[tuple[TrackDataset, list[Section]]] = [
            (first_track_dataset, sections),
            (second_track_dataset, sections),
        ]
        sequential_intersect = SequentialIntersect()

        result = sequential_intersect.execute(cast(Callable, mock_intersect), tasks)
        assert result == [event_1, event_2]
        assert mock_intersect.call_args_list == [
            call(first_track_dataset, sections),
            call(second_track_dataset, sections),
        ]

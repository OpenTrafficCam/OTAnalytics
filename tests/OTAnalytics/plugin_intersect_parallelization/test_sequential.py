from unittest.mock import Mock, call

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section
from OTAnalytics.plugin_intersect_parallelization.sequential import SequentialIntersect


class TestSequentialIntersect:
    def test_execute(self) -> None:
        event_1 = Mock(spec=Event)
        event_2 = Mock(spec=Event)
        side_effect = [[event_1], [event_2]]

        mock_intersect = Mock(spec=callable, side_effect=side_effect)
        first_track = Mock()
        second_track = Mock()
        sections = [Mock(spec=Section)]
        offset = Mock()

        tasks = [
            ([first_track], sections, offset),
            ([second_track], sections, offset),
        ]
        sequential_intersect = SequentialIntersect()

        result = sequential_intersect.execute(mock_intersect, tasks)
        assert result == [event_1, event_2]
        assert mock_intersect.call_args_list == [
            call([first_track], sections, offset),
            call([second_track], sections, offset),
        ]

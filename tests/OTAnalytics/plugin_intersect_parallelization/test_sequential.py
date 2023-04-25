from unittest.mock import Mock

from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import Track
from OTAnalytics.plugin_intersect_parallelization.sequential import SequentialIntersect


class TestSequentialIntersect:
    def test_execute(self) -> None:
        event_1 = Mock(spec=Event)
        event_2 = Mock(spec=Event)
        side_effect = [[event_1], [event_2]]

        mock_intersect = Mock(spec=callable, side_effect=side_effect)
        tracks = [Mock(spec=Track), Mock(spec=Track)]

        sections = [Mock(spec=Section)]
        sequential_intersect = SequentialIntersect()

        result = sequential_intersect.execute(mock_intersect, tracks, sections)
        assert result == [event_1, event_2]
        mock_intersect.assert_any_call(tracks[0], sections)
        mock_intersect.assert_any_call(tracks[1], sections)
        assert mock_intersect.call_count == 2

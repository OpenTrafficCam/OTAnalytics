from datetime import datetime
from typing import Callable, Optional
from unittest.mock import Mock, call, patch

import pytest

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import (
    ObservableOptionalProperty,
    ObservableProperty,
    Plotter,
    SectionState,
    TrackImageUpdater,
    TrackObserver,
    TracksMetadata,
    TrackState,
    TrackViewState,
)
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import (
    Detection,
    Track,
    TrackId,
    TrackImage,
    TrackRepository,
)


class TestTrackState:
    def test_notify_observer(self) -> None:
        first_track = TrackId(1)
        changed_track = TrackId(2)
        observer = Mock(spec=TrackObserver)
        state = TrackState()
        state.register(observer)

        state.select(first_track)
        state.select(changed_track)
        state.select(changed_track)

        assert observer.notify_track.call_args_list == [
            call(first_track),
            call(changed_track),
        ]

    def test_update_selected_track_on_notify_tracks(self) -> None:
        first_track = TrackId(1)
        second_track = TrackId(2)
        state = TrackState()

        state.notify_tracks([first_track, second_track])

        assert state.selected_track == first_track

    def test_update_selected_track_on_notify_tracks_with_empty_list(self) -> None:
        first_track = TrackId(1)
        state = TrackState()

        state.notify_tracks([first_track])
        state.notify_tracks([])

        assert state.selected_track is None


class TestObservableProperty:
    def test_notify_observer(self) -> None:
        first_filter_element = FilterElement(DateRange(None, None), set())
        changed_filter_element = FilterElement(
            DateRange(datetime(2000, 1, 1), datetime(2000, 1, 3)), {"car", "truck"}
        )
        observer = Mock(spec=Callable[[FilterElement], None])
        state = ObservableProperty[FilterElement](first_filter_element)
        state.register(observer)

        state.set(changed_filter_element)
        state.set(changed_filter_element)

        assert observer.call_args_list == [
            call(changed_filter_element),
        ]

    def test_update_filter_element_on_on_notify_filter_element(self) -> None:
        filter_element = FilterElement(
            DateRange(datetime(2000, 1, 1), datetime(2000, 1, 3)), {"car", "truck"}
        )
        state = TrackViewState()

        state.filter_element.set(filter_element)

        assert state.filter_element.get() == filter_element

    def test_get_default(self) -> None:
        default_value = SectionId("default")

        state = ObservableProperty[SectionId](default=default_value)

        assert state.get() == default_value

    def test_get_value(self) -> None:
        default_value = SectionId("default")
        value = SectionId("value")

        state = ObservableProperty[SectionId](default=default_value)
        state.set(value)

        assert state.get() == value


class TestOptionalObservableProperty:
    def test_notify_observer(self) -> None:
        first_section = SectionId("north")
        changed_section = SectionId("south")
        observer = Mock(spec=Callable[[Optional[SectionId]], None])
        state = ObservableOptionalProperty[SectionId]()
        state.register(observer)

        state.set(first_section)
        state.set(changed_section)
        state.set(changed_section)

        assert observer.call_args_list == [
            call(first_section),
            call(changed_section),
        ]

    def test_update_selected_section_on_notify_sections(self) -> None:
        first = SectionId("north")
        second = SectionId("south")
        state = SectionState()

        state.notify_sections([first, second])

        assert state.selected_sections.get() == [first]

    def test_update_selected_section_on_notify_sections_with_empty_list(self) -> None:
        first = SectionId("north")
        state = SectionState()

        state.notify_sections([first])
        state.notify_sections([])

        assert state.selected_sections.get() == []


class TestTrackImageUpdater:
    def test_update_image(self) -> None:
        plotter = Mock(spec=Plotter)
        background_image = Mock(spec=TrackImage)
        plotter.plot.return_value = background_image
        track_id = TrackId(1)
        track = Mock(spec=Track)
        datastore = Mock(spec=Datastore)
        track_view_state = TrackViewState()
        track_view_state.show_tracks.set(True)
        track.id = track_id
        updater = TrackImageUpdater(datastore, track_view_state, plotter)
        tracks: list[TrackId] = [track_id]

        updater.notify_tracks(tracks)

        assert track_view_state.background_image.get() == background_image

        plotter.plot.assert_called_once()


class TestTracksMetadata:
    @pytest.fixture
    def first_detection(self) -> Mock:
        first_detection = Mock(spec=Detection).return_value
        first_detection.occurrence = datetime(2000, 1, 1, 7, 0, 0, 0)
        first_detection.classification = "car"
        return first_detection

    @pytest.fixture
    def second_detection(self) -> Mock:
        second_detection = Mock(spec=Detection).return_value
        second_detection.occurrence = datetime(2000, 2, 1, 0, 0, 0, 0)
        second_detection.classification = "truck"
        return second_detection

    @pytest.fixture
    def third_detection(self) -> Mock:
        third_detection = Mock(spec=Detection).return_value
        third_detection.occurrence = datetime(2000, 2, 5, 0, 0, 0, 0)
        third_detection.classification = "car"
        return third_detection

    @pytest.fixture
    def track(
        self, first_detection: Mock, second_detection: Mock, third_detection: Mock
    ) -> Mock:
        track = Mock(spec=Track).return_value
        track.id = TrackId(1)
        track.classification = "car"
        track.detections = [first_detection, second_detection, third_detection]
        return track

    @patch("OTAnalytics.application.state.TracksMetadata._get_all_track_detections")
    def test_update_detection_occurrences(
        self,
        mock_get_all_track_detections: Mock,
        first_detection: Mock,
        second_detection: Mock,
        third_detection: Mock,
    ) -> None:
        mock_track_repository = Mock(spec=TrackRepository)

        mock_get_all_track_detections.return_value = [
            first_detection,
            third_detection,
            second_detection,
        ]
        tracks_metadata = TracksMetadata(mock_track_repository)

        assert tracks_metadata.first_detection_occurrence is None
        assert tracks_metadata.last_detection_occurrence is None

        tracks_metadata._update_detection_occurrences()
        assert tracks_metadata.first_detection_occurrence == first_detection.occurrence
        assert tracks_metadata.last_detection_occurrence == third_detection.occurrence

        mock_get_all_track_detections.assert_called_once()

    def test_get_all_track_detections(
        self, first_detection: Mock, second_detection: Mock
    ) -> None:
        track = Mock(spec=Track).return_value
        track.detections = [first_detection, second_detection]
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_all.return_value = [track]

        tracks_metadata = TracksMetadata(track_repository)
        detections = tracks_metadata._get_all_track_detections()

        assert detections == [first_detection, second_detection]
        track_repository.get_all.assert_called_once()

    def test_update_classifications(self, track: Mock) -> None:
        mock_track_repository = Mock(spec=TrackRepository)
        mock_track_repository.get_for.return_value = track

        tracks_metadata = TracksMetadata(mock_track_repository)

        assert tracks_metadata.classifications == set()

        tracks_metadata._update_classifications([track.id])

        assert tracks_metadata.classifications == {"car"}
        mock_track_repository.get_for.assert_any_call(track.id)
        assert mock_track_repository.get_for.call_count == 1

        track.detections[0].classification = "bicycle"
        tracks_metadata._update_classifications([track.id])

        assert tracks_metadata.classifications == {"car"}
        mock_track_repository.get_for.assert_any_call(track.id)
        assert mock_track_repository.get_for.call_count == 2

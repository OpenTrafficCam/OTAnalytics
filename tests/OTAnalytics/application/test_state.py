from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional
from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.config import DEFAULT_TRACK_OFFSET
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import (
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    ConfigurationFile,
    FlowState,
    ObservableOptionalProperty,
    ObservableProperty,
    Plotter,
    SectionState,
    TrackImageUpdater,
    TracksMetadata,
    TrackState,
    TrackViewState,
    VideosMetadata,
)
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.flow import FlowId
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import (
    Section,
    SectionId,
    SectionRepositoryEvent,
    SectionType,
)
from OTAnalytics.domain.track import Detection, Track, TrackId, TrackImage
from OTAnalytics.domain.track_repository import (
    TrackObserver,
    TrackRepository,
    TrackRepositoryEvent,
)
from OTAnalytics.domain.video import VideoMetadata

FIRST_START_DATE = datetime(
    year=2019,
    month=12,
    day=31,
    hour=23,
    minute=0,
    tzinfo=timezone.utc,
)
SECOND_START_DATE = FIRST_START_DATE + timedelta(seconds=3)

CAR = "car"
TRUCK = "truck"
BICYCLE = "bicycle"
CARGO_BIKE = "cargo_bike"
PEDESTRIAN = "pedestrian"
ALL_CLASSES = [CAR, TRUCK, BICYCLE, CARGO_BIKE, PEDESTRIAN]


class TestTrackState:
    def test_notify_observer(self) -> None:
        first_track = TrackId("1")
        changed_track = TrackId("2")
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
        first_track = TrackId("1")
        second_track = TrackId("2")
        state = TrackState()

        state.notify_tracks(
            TrackRepositoryEvent.create_added([first_track, second_track])
        )

        assert state.selected_track in [first_track, second_track]

    def test_update_selected_track_on_notify_tracks_with_empty_list(self) -> None:
        first_track = TrackId("1")
        state = TrackState()

        state.notify_tracks(TrackRepositoryEvent.create_added([first_track]))
        state.notify_tracks(TrackRepositoryEvent(frozenset(), frozenset()))

        assert state.selected_track is None

    def test_reset(self) -> None:
        first_track = TrackId("1")
        target = TrackState()
        target.notify_tracks(TrackRepositoryEvent.create_added([first_track]))

        target.reset()

        assert target.selected_track is None


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

        state.unregister(observer)

        state.set(changed_filter_element)

        assert observer.call_count == 1
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
    @pytest.fixture
    def section_north(self) -> Section:
        section = Mock()
        section.id = SectionId("north")
        section.get_type.return_value = SectionType.LINE
        return section

    @pytest.fixture
    def section_south(self) -> Section:
        section = Mock()
        section.id = SectionId("south")
        section.get_type.return_value = SectionType.LINE
        return section

    @pytest.fixture
    def section_cutting(self) -> Section:
        section = Mock()
        section.id = SectionId("#cut")
        section.get_type.return_value = SectionType.CUTTING
        return section

    def test_notify_observer(
        self, section_north: Section, section_south: Section
    ) -> None:
        observer = Mock(spec=Callable[[Optional[SectionId]], None])
        state = ObservableOptionalProperty[SectionId]()
        state.register(observer)

        state.set(section_north.id)
        state.set(section_south.id)
        state.set(section_south.id)

        state.unregister(observer)
        state.set(section_north.id)
        state.set(section_south.id)

        assert observer.call_count == 2
        assert observer.call_args_list == [
            call(section_north.id),
            call(section_south.id),
        ]

    def test_update_selected_section_on_notify_sections(
        self, section_north: Section, section_south: Section
    ) -> None:
        get_sections_by_id = Mock()
        get_sections_by_id.return_value = [section_north, section_south]
        state = SectionState(get_sections_by_id)

        state.notify_sections(
            SectionRepositoryEvent.create_added([section_north.id, section_south.id])
        )

        assert state.selected_sections.get() == [section_north.id]

    def test_update_with_cutting_section(self, section_cutting: Section) -> None:
        get_sections_by_id = Mock()
        get_sections_by_id.return_value = [section_cutting]
        state = SectionState(get_sections_by_id)

        state.notify_sections(SectionRepositoryEvent.create_added([section_cutting.id]))

        assert state.selected_sections.get() == []


class TestTrackImageUpdater:
    def test_update_image(self) -> None:
        plotter = Mock(spec=Plotter)
        section_state = SectionState(Mock())
        background_image = Mock(spec=TrackImage)
        plotter.plot.return_value = background_image
        track_id = TrackId("1")
        track = Mock(spec=Track)
        datastore = Mock(spec=Datastore)
        track_view_state = TrackViewState()
        track_view_state.track_offset.set(RelativeOffsetCoordinate(0.5, 0.7))
        track.id = track_id
        flow_state = FlowState()
        updater = TrackImageUpdater(
            datastore, track_view_state, section_state, flow_state, plotter
        )
        tracks: list[TrackId] = [track_id]

        updater.notify_tracks(TrackRepositoryEvent.create_added(tracks))

        assert track_view_state.background_image.get() == background_image

        plotter.plot.assert_called_once()


@pytest.fixture
def first_full_metadata() -> VideoMetadata:
    return VideoMetadata(
        path="video_path_1.mp4",
        recorded_start_date=FIRST_START_DATE,
        expected_duration=timedelta(seconds=3),
        recorded_fps=20.0,
        actual_fps=20.0,
        number_of_frames=60,
    )


@pytest.fixture
def second_full_metadata() -> VideoMetadata:
    return VideoMetadata(
        path="video_path_2.mp4",
        recorded_start_date=SECOND_START_DATE,
        expected_duration=timedelta(seconds=3),
        recorded_fps=20.0,
        actual_fps=20.0,
        number_of_frames=60,
    )


@pytest.fixture
def first_partial_metadata() -> VideoMetadata:
    return VideoMetadata(
        path="video_path_1.mp4",
        recorded_start_date=FIRST_START_DATE,
        expected_duration=None,
        recorded_fps=20.0,
        actual_fps=None,
        number_of_frames=60,
    )


class TestVideosMetadata:
    def test_nothing_updated(self) -> None:
        videos_metadata = VideosMetadata()

        assert videos_metadata.first_video_start is None
        assert videos_metadata.last_video_end is None

    def test_update_single_full_item(self, first_full_metadata: VideoMetadata) -> None:
        videos_metadata = VideosMetadata()

        videos_metadata.update(first_full_metadata)

        assert (
            videos_metadata.first_video_start == first_full_metadata.recorded_start_date
        )
        assert videos_metadata.last_video_end == FIRST_START_DATE + timedelta(seconds=3)

    def test_update_multiple_full_items(
        self,
        first_full_metadata: VideoMetadata,
        second_full_metadata: VideoMetadata,
    ) -> None:
        videos_metadata = VideosMetadata()

        videos_metadata.update(first_full_metadata)
        videos_metadata.update(second_full_metadata)

        assert (
            videos_metadata.first_video_start == first_full_metadata.recorded_start_date
        )
        assert videos_metadata.last_video_end == SECOND_START_DATE + timedelta(
            seconds=3
        )

    def test_update_single_partial_item(
        self, first_partial_metadata: VideoMetadata
    ) -> None:
        videos_metadata = VideosMetadata()

        videos_metadata.update(first_partial_metadata)

        assert (
            videos_metadata.first_video_start
            == first_partial_metadata.recorded_start_date
        )
        expected_video_length = FIRST_START_DATE + timedelta(seconds=3)
        assert videos_metadata.last_video_end == expected_video_length

    def test_ensure_order(
        self, first_full_metadata: VideoMetadata, second_full_metadata: VideoMetadata
    ) -> None:
        videos_metadata = VideosMetadata()

        videos_metadata.update(second_full_metadata)
        videos_metadata.update(first_full_metadata)

        assert (
            videos_metadata.first_video_start == first_full_metadata.recorded_start_date
        )
        assert videos_metadata.last_video_end == SECOND_START_DATE + timedelta(
            seconds=3
        )

    def test_add_metadata_with_same_start_date_fails(
        self, first_full_metadata: VideoMetadata, first_partial_metadata: VideoMetadata
    ) -> None:
        videos_metadata = VideosMetadata()

        videos_metadata.update(first_full_metadata)
        with pytest.raises(ValueError):
            videos_metadata.update(first_partial_metadata)

    def test_get_metadata_for_date(
        self,
        first_full_metadata: VideoMetadata,
        second_full_metadata: VideoMetadata,
    ) -> None:
        metadata = VideosMetadata()

        metadata.update(first_full_metadata)
        metadata.update(second_full_metadata)

        exact_result = metadata.get_metadata_for(first_full_metadata.start)
        floored_result = metadata.get_metadata_for(
            first_full_metadata.start + timedelta(seconds=1)
        )
        floored_second_result = metadata.get_metadata_for(
            second_full_metadata.start + timedelta(seconds=1)
        )

        assert exact_result == first_full_metadata
        assert floored_result == first_full_metadata
        assert floored_second_result == second_full_metadata

    def test_get_metadata_for_too_late_date(
        self,
        first_full_metadata: VideoMetadata,
    ) -> None:
        metadata = VideosMetadata()

        metadata.update(first_full_metadata)

        result = metadata.get_metadata_for(
            first_full_metadata.start + timedelta(seconds=4)
        )

        assert result is None

    def test_get_by_video_name(
        self, first_full_metadata: VideoMetadata, second_full_metadata: VideoMetadata
    ) -> None:
        target = VideosMetadata()
        target.update(first_full_metadata)
        target.update(second_full_metadata)
        actual = target.get_by_video_name(second_full_metadata.path)
        assert actual == second_full_metadata

    def test_get_by_video_name_empty(self, first_full_metadata: VideoMetadata) -> None:
        target = VideosMetadata()
        actual = target.get_by_video_name(first_full_metadata.path)
        assert actual is None

    def test_reset(
        self, first_full_metadata: VideoMetadata, second_full_metadata: VideoMetadata
    ) -> None:
        target = VideosMetadata()
        target.update(first_full_metadata)
        target.update(second_full_metadata)

        target.reset()

        assert target.get_metadata_for(first_full_metadata.start) is None
        assert target.get_by_video_name(second_full_metadata.path) is None
        assert target.first_video_start is None
        assert target.last_video_end is None


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
        track.id = TrackId("1")
        track.classification = "car"
        track.detections = [first_detection, second_detection, third_detection]
        return track

    def test_update_detection_occurrences(self) -> None:
        first_occurrence = datetime(2000, 1, 1, 12)
        last_occurrence = datetime(2000, 1, 1, 15)
        track_repository = Mock(spec=TrackRepository)
        track_repository.first_occurrence = first_occurrence
        track_repository.last_occurrence = last_occurrence

        tracks_metadata = TracksMetadata(track_repository)

        assert tracks_metadata.first_detection_occurrence is None
        assert tracks_metadata.last_detection_occurrence is None

        tracks_metadata._update_detection_occurrences()
        assert tracks_metadata.first_detection_occurrence == first_occurrence
        assert tracks_metadata.last_detection_occurrence == last_occurrence

    def test_update_classifications(self) -> None:
        classifications = frozenset(["truck", "car", "pedestrian"])
        mock_track_repository = Mock(spec=TrackRepository)
        mock_track_repository.classifications = classifications

        tracks_metadata = TracksMetadata(mock_track_repository)
        assert tracks_metadata.classifications == set()

        tracks_metadata._update_classifications()
        assert tracks_metadata.classifications == classifications

    def test_update_detection_classes(self) -> None:
        tracks_metadata = TracksMetadata(Mock())
        classes = frozenset(["class 1", "class 2"])
        tracks_metadata.update_detection_classes(classes)
        assert classes == tracks_metadata.detection_classifications

    @pytest.mark.parametrize(
        "detection_classes,include_classes,exclude_classes,expected",
        [
            ([CAR, BICYCLE], [CAR], [BICYCLE], [CAR]),
            ([BICYCLE], [CAR], [], [CAR]),
            ([CAR, BICYCLE], [], [BICYCLE], [CAR]),
            ([CAR, BICYCLE], [], [], [CAR, BICYCLE]),
            ([], [], [], []),
        ],
    )
    def test_filtered_detection_classifications(
        self,
        detection_classes: list[str],
        include_classes: list[str],
        exclude_classes: list[str],
        expected: list[str],
    ) -> None:
        tracks_metadata = TracksMetadata(
            Mock(), frozenset(include_classes), frozenset(exclude_classes)
        )
        tracks_metadata.update_detection_classes(frozenset(detection_classes))
        assert tracks_metadata.filtered_detection_classifications == frozenset(expected)

    def test_reset(
        self, first_full_metadata: VideoMetadata, second_full_metadata: VideoMetadata
    ) -> None:
        target = TracksMetadata(Mock())
        classes = frozenset(["class 1", "class 2"])
        target.update_detection_classes(classes)

        target.reset()

        assert target.first_detection_occurrence is None
        assert target.last_detection_occurrence is None
        assert target.classifications == frozenset([])
        assert target.filtered_detection_classifications == frozenset([])
        assert target.detection_classifications == frozenset([])


class TestTrackViewState:
    def test_reset(self) -> None:
        image = Mock()
        filter_element = Mock()
        track_offset = Mock()
        video = Mock()
        track_view_state = TrackViewState()
        track_view_state.selected_videos.set([video])
        track_view_state.background_image.set(image)
        track_view_state.view_width.set(20)
        track_view_state.view_height.set(25)
        track_view_state.filter_element.set(filter_element)
        track_view_state.track_offset.set(track_offset)

        assert track_view_state.selected_videos.get() == [video]
        assert track_view_state.background_image.get() == image
        assert track_view_state.view_width.get() == 20
        assert track_view_state.view_height.get() == 25
        assert track_view_state.filter_element.get() == filter_element
        assert track_view_state.track_offset.get() == track_offset

        track_view_state.reset()
        assert track_view_state.selected_videos.get() == []
        assert track_view_state.background_image.get() is None
        assert track_view_state.view_width.get() == DEFAULT_WIDTH
        assert track_view_state.view_height.get() == DEFAULT_HEIGHT
        current_filter_element = track_view_state.filter_element.get()
        assert current_filter_element.date_range == DateRange(None, None)
        assert current_filter_element.classifications is None
        assert track_view_state.track_offset.get() == DEFAULT_TRACK_OFFSET


class TestConfigurationFile:
    @pytest.fixture
    def otflow_file(self) -> Path:
        return Path("path/to/my.otflow")

    @pytest.fixture
    def otconfig_file(self) -> Path:
        return Path("path/to/my.otconfig")

    def test_is_otflow(self, otflow_file: Path, otconfig_file: Path) -> None:
        assert ConfigurationFile(otflow_file, Mock()).is_otflow
        assert not ConfigurationFile(otconfig_file, Mock()).is_otflow

    def test_is_otconfig(self, otconfig_file: Path, otflow_file: Path) -> None:
        assert ConfigurationFile(otconfig_file, Mock()).is_otconfig
        assert not ConfigurationFile(otflow_file, Mock()).is_otconfig

    def test_file_type(self, otflow_file: Path) -> None:
        assert ConfigurationFile(otflow_file, Mock()).file_type == "otflow"

    def test_file_type_has_no_type(self) -> None:
        no_file_type = Path("path/to/no_file_type")
        assert ConfigurationFile(no_file_type, Mock()).file_type == ""


class TestSectionState:
    def test_reset(self, get_sections_by_id: Mock) -> None:
        section_id = SectionId("1")
        target = SectionState(get_sections_by_id)
        target.notify_sections(SectionRepositoryEvent.create_added([section_id]))

        target.reset()

        assert target.selected_sections.get() == []

    @pytest.fixture
    def get_sections_by_id(self) -> Mock:
        mock = Mock()
        mock.side_effect = lambda section_ids: [
            self.create_mock_section(section_id) for section_id in section_ids
        ]
        return mock

    def create_mock_section(self, section_id: SectionId) -> Section:
        mock = Mock(spec=Section)
        mock.id = section_id
        return mock


class TestFlowState:
    def test_reset(self) -> None:
        flow_id = FlowId("1")
        target = FlowState()
        target.notify_flows([flow_id])

        target.reset()

        assert target.selected_flows.get() == []

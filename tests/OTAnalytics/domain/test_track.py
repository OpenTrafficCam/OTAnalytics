from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, call

import pytest

import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.domain.event import VIDEO_NAME
from OTAnalytics.domain.track import (
    BuildTrackWithLessThanNDetectionsError,
    CalculateTrackClassificationByMaxConfidence,
    Detection,
    Track,
    TrackFileRepository,
    TrackId,
    TrackListObserver,
    TrackObserver,
    TrackRemoveError,
    TrackRepository,
    TrackSubject,
)
from tests.conftest import TrackBuilder


@pytest.fixture
def valid_detection_dict() -> dict:
    return {
        ottrk_format.CLASS: "car",
        ottrk_format.CONFIDENCE: 0.5,
        ottrk_format.X: 0.0,
        ottrk_format.Y: 0.0,
        ottrk_format.W: 0.0,
        ottrk_format.H: 0.0,
        ottrk_format.FRAME: 1,
        ottrk_format.OCCURRENCE: datetime(2022, 1, 1, 1, 0, 0),
        ottrk_format.INPUT_FILE_PATH: Path("path/to/file.otdet"),
        ottrk_format.INTERPOLATED_DETECTION: False,
        "track-id": TrackId("1"),
        "video_name": "file.mp4",
    }


@pytest.fixture
def valid_detection(valid_detection_dict: dict) -> Detection:
    return Detection(
        classification=valid_detection_dict[ottrk_format.CLASS],
        confidence=valid_detection_dict[ottrk_format.CONFIDENCE],
        x=valid_detection_dict[ottrk_format.X],
        y=valid_detection_dict[ottrk_format.Y],
        w=valid_detection_dict[ottrk_format.W],
        h=valid_detection_dict[ottrk_format.H],
        frame=valid_detection_dict[ottrk_format.FRAME],
        occurrence=valid_detection_dict[ottrk_format.OCCURRENCE],
        interpolated_detection=valid_detection_dict[
            ottrk_format.INTERPOLATED_DETECTION
        ],
        track_id=valid_detection_dict[ottrk_format.TRACK_ID],
        video_name=valid_detection_dict[VIDEO_NAME],
    )


class TestTrackSubject:
    def test_notify_observer(self) -> None:
        changed_track = TrackId("1")
        observer = Mock(spec=TrackObserver)
        subject = TrackSubject()
        subject.register(observer)

        subject.notify(changed_track)

        observer.notify_track.assert_called_with(changed_track)


class TestDetection:
    @pytest.mark.parametrize(
        "confidence,x,y,w,h,frame,track_id",
        [
            (-1, 1, 1, 1, 1, 1, 1),
            (2, 1, 1, 1, 1, 1, 1),
            (0, -0.0001, 1, 1, 1, 1, 1),
            (0, -1, -0.0001, 1, 1, 1, 1),
            (0, 2, 1, 1, -0.0001, 1, 1),
            (0, 2, 1, 1, 1, 0, 1),
        ],
    )
    def test_value_error_raised_with_invalid_arg(
        self,
        confidence: float,
        x: float,
        y: float,
        w: float,
        h: float,
        frame: int,
        track_id: int,
    ) -> None:
        with pytest.raises(ValueError):
            Detection(
                classification="car",
                confidence=confidence,
                x=x,
                y=y,
                w=w,
                h=h,
                frame=frame,
                occurrence=datetime(2022, 1, 1, 1, 0, 0),
                interpolated_detection=False,
                track_id=TrackId(str(track_id)),
                video_name="file.mp4",
            )

    def test_instantiation_with_valid_args(
        self, valid_detection: Detection, valid_detection_dict: dict
    ) -> None:
        det = valid_detection
        assert det.classification == valid_detection_dict[ottrk_format.CLASS]
        assert det.confidence == valid_detection_dict[ottrk_format.CONFIDENCE]
        assert det.x == valid_detection_dict[ottrk_format.X]
        assert det.y == valid_detection_dict[ottrk_format.Y]
        assert det.w == valid_detection_dict[ottrk_format.W]
        assert det.h == valid_detection_dict[ottrk_format.H]
        assert det.frame == valid_detection_dict[ottrk_format.FRAME]
        assert det.occurrence == valid_detection_dict[ottrk_format.OCCURRENCE]
        assert det.video_name == valid_detection_dict[VIDEO_NAME]
        assert (
            det.interpolated_detection
            == valid_detection_dict[ottrk_format.INTERPOLATED_DETECTION]
        )
        assert det.track_id == valid_detection_dict["track-id"]


class TestTrack:
    def test_raise_error_on_empty_detections(self) -> None:
        with pytest.raises(BuildTrackWithLessThanNDetectionsError):
            Track(id=TrackId("1"), classification="car", detections=[])

    def test_error_on_single_detection(self, valid_detection: Detection) -> None:
        with pytest.raises(BuildTrackWithLessThanNDetectionsError):
            Track(id=TrackId("5"), classification="car", detections=[valid_detection])

    def test_instantiation_with_valid_args(self, valid_detection: Detection) -> None:
        track = Track(
            id=TrackId("5"),
            classification="car",
            detections=[
                valid_detection,
                valid_detection,
                valid_detection,
                valid_detection,
                valid_detection,
            ],
        )
        assert track.id == TrackId("5")
        assert track.classification == "car"
        assert track.detections == [
            valid_detection,
            valid_detection,
            valid_detection,
            valid_detection,
            valid_detection,
        ]

    def test_start_and_end_time(self) -> None:
        start_time = datetime(2022, 1, 1, 13)
        end_time = datetime(2022, 1, 1, 14)

        start_detection = Mock(spec=Detection)
        start_detection.occurrence = start_time
        second_detection = Mock(spec=Detection)
        second_detection.occurrence = datetime(2022, 1, 1, 13, 15)
        third_detection = Mock(spec=Detection)
        third_detection.occurrence = datetime(2022, 1, 1, 13, 30)
        fourth_detection = Mock(spec=Detection)
        fourth_detection.occurrence = datetime(2022, 1, 1, 13, 45)

        end_detection = Mock(spec=Detection)
        end_detection.occurrence = end_time
        track = Track(
            TrackId("1"),
            "car",
            [
                start_detection,
                second_detection,
                third_detection,
                fourth_detection,
                end_detection,
            ],
        )

        assert track.start == start_time
        assert track.end == end_time

    def test_first_and_last_detection(self, valid_detection: Detection) -> None:
        first = Mock(spec=Detection)
        first.occurrence = datetime.min
        last = Mock(spec=Detection)
        last.occurrence = datetime.max
        detections: list[Detection] = [
            first,
            valid_detection,
            valid_detection,
            valid_detection,
            last,
        ]
        track = Track(TrackId("1"), "car", detections)
        assert track.first_detection == first
        assert track.last_detection == last


class TestCalculateTrackClassificationByMaxConfidence:
    def test_calculate(self) -> None:
        builder = TrackBuilder(
            confidence=0.8,
            w=10,
            h=10,
        )
        builder.append_detection()

        builder.add_confidence(0.8)
        builder.add_frame(2)
        builder.append_detection()

        builder.add_detection_class("truck")
        builder.add_confidence(0.8)
        builder.add_frame(3)
        builder.append_detection()

        builder.add_detection_class("truck")
        builder.add_confidence(0.4)
        builder.add_frame(2)
        builder.append_detection()

        detections = builder.build_detections()
        track_classification_calculator = CalculateTrackClassificationByMaxConfidence()
        result = track_classification_calculator.calculate(detections)

        assert result == "car"
        assert detections[2].classification == "truck"


class TestTrackRepository:
    @pytest.fixture
    def track_1(self) -> Mock:
        track = Mock(spec=Track)
        track.id = TrackId("1")
        return track

    @pytest.fixture
    def track_2(self) -> Mock:
        track = Mock(spec=Track)
        track.id = TrackId("2")
        return track

    def test_add(self, track_1: Mock) -> None:
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository()
        repository.register_tracks_observer(observer)

        repository.add(track_1)

        assert track_1 in repository.get_all()
        observer.notify_tracks.assert_called_with([track_1.id])

    def test_add_nothing(self) -> None:
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository()
        repository.register_tracks_observer(observer)

        repository.add_all([])

        assert 0 == len(repository.get_all())
        observer.notify_tracks.assert_not_called()

    def test_add_all(self, track_1: Mock, track_2: Mock) -> None:
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository()
        repository.register_tracks_observer(observer)

        repository.add_all([track_1, track_2])

        assert track_1 in repository.get_all()
        assert track_2 in repository.get_all()
        observer.notify_tracks.assert_called_with([track_1.id, track_2.id])

    def test_get_by_id(self, track_1: Mock, track_2: Mock) -> None:
        repository = TrackRepository()
        repository.add_all([track_1, track_2])

        returned = repository.get_for(track_1.id)

        assert returned == track_1

    def test_clear(self, track_1: Mock, track_2: Mock) -> None:
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository()
        repository.register_tracks_observer(observer)

        repository.add_all([track_1, track_2])
        repository.clear()

        assert not list(repository.get_all())
        assert observer.notify_tracks.call_args_list == [
            call([track_1.id, track_2.id]),
            call([]),
        ]

    def test_get_all_ids(self, track_1: Mock, track_2: Mock) -> None:
        repository = TrackRepository()
        repository.add_all([track_1, track_2])
        ids = repository.get_all_ids()
        assert set(ids) == {track_1.id, track_2.id}

    def test_remove(self, track_1: Mock, track_2: Mock) -> None:
        repository = TrackRepository()
        repository.add_all([track_1, track_2])

        observer = Mock(spec=TrackListObserver)
        repository.register_tracks_observer(observer)

        repository.remove(track_1.id)
        assert repository.get_all() == [track_2]
        repository.remove(track_2.id)
        assert repository.get_all() == []
        with pytest.raises(TrackRemoveError):
            repository.remove(track_2.id)

        assert observer.notify_tracks.call_args_list == [call([]), call([])]


class TestTrackFileRepository:
    @pytest.fixture
    def mock_file(self) -> Mock:
        return Mock(spec=Path)

    @pytest.fixture
    def mock_other_file(self) -> Mock:
        return Mock(spec=Path)

    def test_add(self, mock_file: Mock, mock_other_file: Mock) -> None:
        repository = TrackFileRepository()
        assert repository._files == set()
        repository.add(mock_file)
        assert repository._files == {mock_file}
        repository.add(mock_file)
        assert repository._files == {mock_file}
        repository.add(mock_other_file)
        assert repository._files == {mock_file, mock_other_file}

    def test_add_all(self, mock_file: Mock, mock_other_file: Mock) -> None:
        repository = TrackFileRepository()
        repository.add_all([mock_file, mock_other_file])
        assert repository._files == {mock_file, mock_other_file}

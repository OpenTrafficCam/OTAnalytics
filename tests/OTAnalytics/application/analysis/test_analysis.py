from unittest.mock import Mock

from OTAnalytics.application.analysis.analysis import RunSceneEventDetection
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.track import Track


class TestRunSceneEventDetection:
    def test_init(self) -> None:
        scene_action_detector = Mock(spec=SceneActionDetector)
        run_scene_event_detection = RunSceneEventDetection(scene_action_detector)

        assert run_scene_event_detection._scene_action_detector == scene_action_detector

    def test_run(self) -> None:
        track = Mock(spec=Track)
        scene_action_detector = Mock(spec=SceneActionDetector)
        mock_event = Mock(spec=Event)
        scene_action_detector.detect.return_value = [mock_event]

        run_scene_event_detection = RunSceneEventDetection(scene_action_detector)
        events = run_scene_event_detection.run([track])

        scene_action_detector.detect.assert_called_once()
        assert events == [mock_event]

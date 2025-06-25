from OTAnalytics.application.state import (
    ActionState,
    FileState,
    FlowState,
    SectionState,
    TracksMetadata,
    TrackState,
    TrackViewState,
    VideosMetadata,
)


class ResetState:
    def __init__(
        self,
        videos_metadata: VideosMetadata,
        tracks_metadata: TracksMetadata,
        track_view_state: TrackViewState,
        track_state: TrackState,
        section_state: SectionState,
        flow_state: FlowState,
        action_state: ActionState,
        file_state: FileState,
    ) -> None:
        self._videos_metadata = videos_metadata
        self._tracks_metadata = tracks_metadata
        self._track_view_state = track_view_state
        self._track_state = track_state
        self._section_state = section_state
        self._flow_state = flow_state
        self._action_state = action_state
        self._file_state = file_state

    def reset(self) -> None:
        self._videos_metadata.reset()
        self._tracks_metadata.reset()
        self._track_view_state.reset()
        self._track_state.reset()
        self._section_state.reset()
        self._flow_state.reset()
        self._action_state.reset()
        self._file_state.reset()

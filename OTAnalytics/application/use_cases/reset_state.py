from OTAnalytics.application.state import VideosMetadata


class ResetState:
    def __init__(self, videos_metadata: VideosMetadata) -> None:
        self._videos_metadata = videos_metadata

    def reset(self) -> None:
        self._videos_metadata.reset()

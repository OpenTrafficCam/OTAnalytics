"""Progress doubles for tests that do not care about showing progress."""

from OTAnalytics.domain.progress import CompletionProgress, CompletionProgressBuilder


class SilentProgress(CompletionProgress):
    """Progress that shows nothing and is never cancelled."""

    def complete(self, item: str) -> None:
        pass

    def close(self) -> None:
        pass

    @property
    def is_cancelled(self) -> bool:
        return False


class SilentProgressBuilder(CompletionProgressBuilder):
    """Builds progress that shows nothing."""

    def build(self, description: str, unit: str, total: int) -> CompletionProgress:
        return SilentProgress()

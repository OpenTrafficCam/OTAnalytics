"""Asking the user which time range to load.

A port rather than a method on `UiFactory`: a new abstract method there would
make OTCloud's `UnimplementedUiFactory` abstract and break it on instantiation.
It lives in the application layer, not in a plugin, so that the front-end
implementing it does not have to depend on the plugin consuming it.
"""

from abc import ABC, abstractmethod

from OTAnalytics.domain.load_window import LoadWindow


class AskForLoadWindow(ABC):
    """Asks the user which time range to load."""

    @abstractmethod
    async def ask(self, title: str, source: str) -> LoadWindow | None:
        """Ask for the time range to load.

        Args:
            title (str): the dialog title.
            source (str): where the files will come from, shown so the user can
                see which site they are loading, since they cannot choose it.

        Returns:
            LoadWindow | None: the selected window, None if the user cancelled.
        """
        raise NotImplementedError

    @abstractmethod
    def report_clamped(self, window: LoadWindow) -> None:
        """Tell the user the selected range was shortened.

        Args:
            window (LoadWindow): the window that will actually be loaded.
        """
        raise NotImplementedError

    @abstractmethod
    def report_error(self, message: str) -> None:
        """Tell the user why nothing could be loaded.

        Args:
            message (str): what went wrong, in the user's terms.
        """
        raise NotImplementedError

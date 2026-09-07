from typing import Iterable, Optional, Sequence

from nicegui import context, ui

from OTAnalytics.application.progress import (
    AutoIncrementingProgressbar,
    Cancellation,
    ProgressState,
    SimpleCounter,
)
from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    ResourceManager,
)
from OTAnalytics.domain.progress import (
    CompletionProgress,
    CompletionProgressBuilder,
    Counter,
    ProgressbarBuilder,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

MARKER_PROGRESSBAR_CANCEL = "progressbar-cancel"
MARKER_MESSAGE = "progressbar-message"
MARKER_CURRENT_ITEM = "progressbar-current-item"


class NiceguiProgressbar(CompletionProgress):
    """A determinate progressbar rendered in the browser.

    Shows how many of the expected items are done, which item was completed last,
    and offers a cancel button setting a `Cancellation` the caller can act on.
    """

    def __init__(
        self,
        resource_manager: ResourceManager,
        description: str,
        unit: str,
        total: int,
        counter: Optional[Counter] = None,
        cancellation: Optional[Cancellation] = None,
    ) -> None:
        self._resource_manager = resource_manager
        self._counter = counter if counter is not None else SimpleCounter()
        self._cancellation = cancellation if cancellation else Cancellation()
        self._state = ProgressState(
            description=description,
            unit=unit,
            total=total,
            counter=self._counter,
            on_change=self._refresh,
        )
        self._dialog: Optional[ui.dialog] = None
        self._message: Optional[ui.label] = None
        self._bar: Optional[ui.linear_progress] = None
        self._item: Optional[ui.label] = None

    @property
    def state(self) -> ProgressState:
        """The progress being shown."""
        return self._state

    @property
    def counter(self) -> Counter:
        """The counter advancing the progress."""
        return self._counter

    @property
    def cancellation(self) -> Cancellation:
        """The signal set when the user presses cancel."""
        return self._cancellation

    @property
    def is_cancelled(self) -> bool:
        """Whether the user pressed cancel."""
        return self._cancellation.is_cancelled

    @property
    def is_open(self) -> bool:
        """Whether the dialog is currently shown."""
        return self._dialog is not None and self._dialog.value

    def open(self) -> None:
        """Build and show the progressbar dialog.

        Does nothing without a browser to show it in, which is the case while
        input files given on the command line are preloaded at startup, and
        nothing when there is no progress left to show, because only progress
        closes the dialog again.
        """
        if context.client.is_auto_index_client or self._state.finished:
            return
        with ui.dialog().props("persistent") as dialog, ui.card().classes("w-96"):
            self._dialog = dialog
            self._message = ui.label(self._state.message)
            self._message.props(f"{TEST_ID}={MARKER_MESSAGE}")
            self._bar = ui.linear_progress(value=self._state.fraction).props(
                "instant-feedback"
            )
            self._item = ui.label(self._state.current_item)
            self._item.props(f"{TEST_ID}={MARKER_CURRENT_ITEM}")
            cancel = ui.button(
                self._resource_manager.get(GeneralKeys.LABEL_CANCEL),
                on_click=self._on_cancel,
            )
            cancel.mark(MARKER_PROGRESSBAR_CANCEL)
            cancel.props(f"{TEST_ID}={MARKER_PROGRESSBAR_CANCEL}")
        dialog.open()

    def complete(self, item: str) -> None:
        """Report one item as completed.

        Completions may arrive in any order, which is what concurrent work does.

        Args:
            item (str): the name of the completed item.
        """
        self._state.complete(item)

    def notify(self) -> None:
        """Report progress made through the counter."""
        self._state.notify()

    def close(self) -> None:
        """Hide the progressbar dialog."""
        if self._dialog:
            self._dialog.close()

    def _on_cancel(self) -> None:
        self._cancellation.cancel()
        self.close()

    def _refresh(self) -> None:
        if self._message:
            self._message.set_text(self._state.message)
        if self._bar:
            self._bar.set_value(self._state.fraction)
        if self._item:
            self._item.set_text(self._state.current_item)
        if self._state.finished:
            self.close()


class NiceguiProgressbarBuilder(ProgressbarBuilder, CompletionProgressBuilder):
    """Builds progressbars rendering in the browser.

    The most recently built progressbar is kept accessible, so a caller driving
    concurrent work can report completions and observe its cancellation signal.
    """

    def __init__(self, resource_manager: ResourceManager) -> None:
        self._resource_manager = resource_manager
        self._progressbar: Optional[NiceguiProgressbar] = None

    @property
    def progressbar(self) -> NiceguiProgressbar:
        """The most recently built progressbar.

        Raises:
            ValueError: if no progressbar has been built yet.
        """
        if self._progressbar is None:
            raise ValueError("No progressbar has been built yet")
        return self._progressbar

    def start(self, description: str, unit: str, total: int) -> NiceguiProgressbar:
        """Show a progressbar until the caller closes it again.

        Args:
            description (str): what the operation being tracked is doing.
            unit (str): the unit of the counted items.
            total (int): the number of items expected to complete.

        Returns:
            NiceguiProgressbar: the opened progressbar.
        """
        return self.build(description, unit, total)

    def build(self, description: str, unit: str, total: int) -> NiceguiProgressbar:
        """Build and show a progressbar advanced by reporting completions.

        Args:
            description (str): the description.
            unit (str): the unit of the counted items.
            total (int): the number of items expected to complete.

        Returns:
            NiceguiProgressbar: the opened progressbar.
        """
        if self._progressbar:
            self._progressbar.close()
        progressbar = NiceguiProgressbar(
            self._resource_manager, description, unit, total
        )
        self._progressbar = progressbar
        progressbar.open()
        return progressbar

    def __call__(self, sequence: Sequence, description: str, unit: str) -> Iterable:
        progressbar = self.build(description, unit, len(sequence))
        return AutoIncrementingProgressbar(
            sequence, progressbar.counter, progressbar.notify, step_percentage=1
        )

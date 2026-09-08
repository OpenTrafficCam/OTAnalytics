"""The dialog that asks which time range to load from S3."""

from datetime import datetime

from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    LoadWindowKeys,
    ResourceManager,
)
from OTAnalytics.domain.load_window import LoadWindow
from OTAnalytics.plugin_s3.s3_file_providers import AskForLoadWindow
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import DateTimeForm
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

MARKER_START_DATE = "load-window-start-date"
MARKER_START_TIME = "load-window-start-time"
MARKER_END_DATE = "load-window-end-date"
MARKER_END_TIME = "load-window-end-time"
MARKER_LOAD = "load-window-load"
MARKER_CANCEL = "load-window-cancel"


class LoadWindowDialog(AskForLoadWindow):
    """Asks the user for the time range to load.

    Only the time range is asked for: the bucket and key prefix are fixed at
    startup, so one instance is pinned to one camera or site and the user
    chooses only *when*, never *where*.

    Args:
        resource_manager (ResourceManager): provides the labels.
    """

    def __init__(self, resource_manager: ResourceManager) -> None:
        self._resource_manager = resource_manager

    async def ask(self, title: str) -> LoadWindow | None:
        """Ask for the time range to load.

        Args:
            title (str): the dialog title.

        Returns:
            LoadWindow | None: the selected window, None if the user cancelled.
        """
        start = DateTimeForm(
            label_date_text=self._label(LoadWindowKeys.LABEL_START_DATE),
            label_time_text=self._label(LoadWindowKeys.LABEL_START_TIME),
            marker_date=MARKER_START_DATE,
            marker_time=MARKER_START_TIME,
        )
        end = DateTimeForm(
            label_date_text=self._label(LoadWindowKeys.LABEL_END_DATE),
            label_time_text=self._label(LoadWindowKeys.LABEL_END_TIME),
            marker_date=MARKER_END_DATE,
            marker_time=MARKER_END_TIME,
        )
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label(title).classes("text-lg")
            start.build()
            end.build()
            ui.label(self._label(LoadWindowKeys.LABEL_UTC_HINT)).classes("text-xs")
            with ui.row():
                load = ui.button(
                    self._label(LoadWindowKeys.LABEL_LOAD),
                    on_click=lambda: self._submit(dialog, start.value, end.value),
                )
                load.mark(MARKER_LOAD)
                load.props(f"{TEST_ID}={MARKER_LOAD}")
                cancel = ui.button(
                    self._label(GeneralKeys.LABEL_CANCEL),
                    on_click=lambda: dialog.submit(None),
                )
                cancel.mark(MARKER_CANCEL)
                cancel.props(f"{TEST_ID}={MARKER_CANCEL}")
        dialog.open()
        selected = await dialog
        dialog.delete()
        return selected

    def report_clamped(self, window: LoadWindow) -> None:
        """Tell the user the selected range was shortened.

        Args:
            window (LoadWindow): the window that will actually be loaded.
        """
        message = self._label(LoadWindowKeys.MESSAGE_CLAMPED)
        ui.notify(f"{message} {window.end:%Y-%m-%d %H:%M:%S} UTC.", type="warning")

    def report_error(self, message: str) -> None:
        """Tell the user why nothing could be loaded.

        Args:
            message (str): what went wrong, in the user's terms.
        """
        ui.notify(message, type="negative", multi_line=True)

    def _submit(
        self, dialog: ui.dialog, start: datetime | None, end: datetime | None
    ) -> None:
        """Validate the selection and close the dialog if it is loadable.

        The dialog stays open on an impossible selection, so the user can fix it
        rather than losing what they typed.

        Args:
            dialog (ui.dialog): the dialog to submit.
            start (datetime | None): the selected start.
            end (datetime | None): the selected end.
        """
        if start is None or end is None:
            ui.notify(self._label(LoadWindowKeys.MESSAGE_INCOMPLETE), type="warning")
            return
        if end < start:
            ui.notify(
                self._label(LoadWindowKeys.MESSAGE_END_BEFORE_START), type="warning"
            )
            return
        dialog.submit(LoadWindow(start=start, end=end))

    def _label(self, key: LoadWindowKeys | GeneralKeys) -> str:
        return self._resource_manager.get(key)

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable, List, Literal

from nicegui import ui
from nicegui.elements.table import Table

from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

HEADER_SLOT = "header"
BODY_SLOT = "body"

COLUMN_ID = "id"


class MissingInstanceError(Exception):
    pass


@dataclass(frozen=True)
class TableObserver:
    """Represents an observer to be registered in NiceGUI's ui.table.

    Attributes:
        event_name (str): the event that should be listened to.
        callback (Callable[[Any], Any]): the function to be called when event is fired.
    """

    event_name: str
    callback: Callable[[Any], None]


class CustomTable:
    @property
    def size(self) -> int:
        """The current table size defined by the numbers of rows.

        Returns:
            int: the current table size.
        """
        return len(self._table.rows)

    @property
    def _table(self) -> Table:
        if self.__table is None:
            raise MissingInstanceError("Table has not been instantiated yet")
        return self.__table

    @property
    def _instantiated(self) -> bool:
        return self.__table is not None

    def __init__(
        self,
        columns: List[dict],
        rows: List[dict],
        title: str = "",
        header_slot: str = "",
        body_slot: str = "",
        observers: list[TableObserver] | None = None,
        pagination: dict | None = None,
        marker: str | None = None,
        on_select_method: Callable[[Any], None] | None = None,
        selection: Literal["single", "multiple"] | None = None,
        on_row_click_method: Callable[[Any], None] | None = None,
        auto_select_on_row_click: bool = False,
    ) -> None:
        self._columns = columns
        self._rows = rows
        self.__table: Table | None = None
        self._title = title
        self._header_slot = header_slot
        self._body_slot = body_slot
        self._pagination = pagination
        self._marker = marker
        self._on_select_method = on_select_method
        self._on_row_click_method = on_row_click_method
        self._selection = selection
        self._observers = []
        self._auto_select_on_row_click = auto_select_on_row_click
        if observers:
            self._observers = observers

    def build(self) -> None:
        """Build the NiceGUI table."""
        with ui.table(
            columns=self._columns,
            rows=self._rows,
            title=self._title,
            pagination=self._pagination,
            on_select=self._on_select_method,
            selection=self._selection,
        ) as table:
            self.__table = table
            self.__table.style("width: 100%")
            # Register row click handling
            if self._auto_select_on_row_click:
                table.on("rowClick", self._internal_on_row_click)
            if self._on_row_click_method is not None:
                table.on("rowClick", self._on_row_click_method)
            self._add_header_slot()
            self._add_body_slot()
            self._register_callback()
            if self._marker:
                table.mark(self._marker)
                table.props(f"{TEST_ID}={self._marker}")

    def _add_header_slot(self) -> None:
        if self._header_slot:
            self._table.add_slot(HEADER_SLOT, self._header_slot)

    def _add_body_slot(self) -> None:
        if self._body_slot:
            self._table.add_slot(BODY_SLOT, self._body_slot)
            self._table.add_slot(HEADER_SLOT, self._header_slot)

    def _register_callback(self) -> None:
        """Register callbacks to events emitted by this table, such as buttons,
        when defined in body_slot.

        Callbacks can only be successfully registered if `event_name` is defined in
        `body_slot`.
        """
        for table_callback in self._observers:
            self._table.on(table_callback.event_name, table_callback.callback)

    def update(self, rows: List[dict]) -> None:
        """Update the contents of this table.

        Args:
            rows (list[dict]): the new contents of the table to be replaced with.
        """
        self._rows.clear()
        self._rows.extend(rows)
        if self._instantiated:
            self._table.update()

    def select(self, item_ids: list[str]) -> None:
        if self._instantiated:
            self._table.selected = self._rows_to_select(item_ids)

    def _rows_to_select(self, item_ids: list[str]) -> list[dict]:
        return [row for row in self._rows if row[COLUMN_ID] in item_ids]

    # --- Internal helpers ---
    def _internal_on_row_click(self, e: Any) -> None:
        """Default behavior for row clicks: select clicked row and notify.

        Tries to extract the clicked row dict from various possible event shapes
        and updates the table selection accordingly. If an ``on_select_method``
        was provided, it is invoked with a minimal event-like object exposing a
        ``selection`` attribute compatible with existing handlers.
        """
        try:
            row: dict | None = None
            if hasattr(e, "args"):
                args = getattr(e, "args")
                if isinstance(args, dict):
                    row = args.get("row")  # type: ignore[assignment]
                elif isinstance(args, (list, tuple)) and len(args) >= 2:
                    row = args[1]  # (evt, row, ...)
            elif isinstance(e, dict):
                row = e.get("row")  # type: ignore[assignment]
            if isinstance(row, dict):
                row_id = row.get(COLUMN_ID)
                if row_id:
                    self.select([row_id])
                    if self._on_select_method is not None:
                        self._on_select_method(SimpleNamespace(selection=[row]))
        except Exception:
            # Be resilient to varying event payloads
            pass

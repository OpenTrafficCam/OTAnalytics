from dataclasses import dataclass
from typing import Any, Callable, List

from nicegui import ui
from nicegui.elements.table import Table

HEADER_SLOT = "header"
BODY_SLOT = "body"


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
    ) -> None:
        self._columns = columns
        self._rows = rows
        self.__table: Table | None = None
        self._title = title
        self._header_slot = header_slot
        self._body_slot = body_slot
        self._pagination = pagination
        self._marker = marker
        self._observers = []
        if observers:
            self._observers = observers

    def build(self) -> None:
        """Build the NiceGUI table."""
        with ui.table(
            columns=self._columns,
            rows=self._rows,
            title=self._title,
            pagination=self._pagination,
        ) as table:
            self.__table = table
            self._add_header_slot()
            self._add_body_slot()
            self._register_callback()
            if self._marker:
                table.mark(self._marker)

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
        self._table.update()

from abc import ABC, abstractmethod
from datetime import date, datetime, time, timezone
from typing import Callable, Generic, Optional, TypeVar

from nicegui import ui
from nicegui.element import Element
from nicegui.elements.checkbox import Checkbox
from nicegui.elements.input import Input
from nicegui.elements.mixins.validation_element import ValidationElement
from nicegui.elements.number import Number
from nicegui.elements.select import Select
from nicegui.events import ValueChangeEventArguments

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import (
    MissingInstanceError,
)

YEAR_MONTH_DAY_FORMAT = "%Y-%m-%d"
DAY_MONTH_YEAR_FORMAT = "%d.%m.%Y"

HOUR_MINUTE_FORMAT = "%H:%M"
HOUR_MINUTE_SECOND_FORMAT = f"{HOUR_MINUTE_FORMAT}:%S"

T = TypeVar("T")


class LazyInitializedElement(ABC, Generic[T]):
    """Abstract base class for managing an optional instance of type `T`.

    This class provides a property `element` that retrieves the stored instance
    of type `T`, if it has been instantiated. Raises a `MissingInstanceError` if
    accessed before instantiation.

    Attributes:
        _instance (T | None): The stored instance of type `T`, initialized to None.
    """

    @property
    def element(self) -> T:
        """Retrieve the instance of type `T`.

        Returns:
            T: The instance of type `T`.

        Raises:
            MissingInstanceError: If the instance has not been instantiated yet.
        """
        if self._instance:
            return self._instance
        raise MissingInstanceError(
            f"{self.__class__.__name__} has not been instantiated yet"
        )

    def __init__(self) -> None:
        self._instance: T | None = None


S = TypeVar("S", bound=ValidationElement)
V = TypeVar("V")


class FormField(LazyInitializedElement[S], Generic[S, V]):
    """Abstract base class for form fields in a UI framework.

    This class provides a structure for creating various form fields with
    specific properties and marker attributes. It mandates the implementation
    of property and method definitions for handling props and marker attributes,
    as well as a method for constructing the field.
    """

    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def props(self) -> list[str] | None:
        """
        Represents additional properties that can be applied to the form field.

        Returns:
            list[str] | None: additional properties to be applied.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def marker(self) -> str | None:
        """
        The marker to tag the UI element.

        This helps to identify the form field in the UI.

        Returns:
            str | None: the marker.
        """
        raise NotImplementedError

    @abstractmethod
    def build(self) -> None:
        """Builds the UI form element."""
        raise NotImplementedError

    def _apply(self, element: Element) -> None:
        self._apply_props(element)
        self._apply_marker(element)

    def _apply_props(self, element: Element) -> None:
        if self.props:
            for prop in self.props:
                element.props(prop)

    def _apply_marker(self, element: Element) -> None:
        if self.marker:
            element.mark(self.marker)

    def validate(self) -> bool:
        """Handles the validation logic for an element.

        Returns:
            bool: True if the element passes validation, False otherwise.
        """
        return self.element.validate()

    def set_value(self, value: V) -> None:
        """Sets the value for the element.

        Also refreshes the UI element.

        Args:
            value (V): The value to set for the element.
        """
        self.element.set_value(value)
        self.update()

    def update(self) -> None:
        """
        Updates the state of the number element.

        This method calls the update method of the element associated with
        the instance, ensuring the element's state is refreshed with any
        new changes.

        """
        self.element.update()


class FormFieldText(FormField[Input, str]):
    """A class that represents a form field for text input, inheriting from
    LazyInitializedElement with NiceGUI's Input as the element type.

    Args:
        label_text (str): Label text for the form field.
        initial_value (str): Initial value to be set for the element, default is an
            empty string.
        validation(Callable[..., str | None] | dict[str, Callable[..., bool]] | None):
            Validation functions to be applied on the element's data. Defaults to None.
        autogrow (bool): Specifies if the element should automatically grow to
            accommodate content, default is True.
        disabled (bool): Specifies if the input element should be disabled.
        readonly (bool): Specifies if the input element should be read-only.
    """

    @property
    def value(self) -> str:
        """Provides the current input of the form field

        Returns:
            str: The current input of the form field.
        """
        return self.element.value

    @property
    def props(self) -> list[str] | None:
        props = []
        if self._autogrow:
            props.append("autogrow")
        if self._disabled:
            props.append("disable")
        if self._readonly:
            props.append("readonly")
        if props:
            return props
        return None

    @property
    def marker(self) -> str | None:
        return self._marker

    def __init__(
        self,
        label_text: str,
        initial_value: str = "",
        validation: (
            Callable[..., str | None] | dict[str, Callable[..., bool]] | None
        ) = None,
        on_value_change: Callable[[ValueChangeEventArguments], None] | None = None,
        autogrow: bool = True,
        disabled: bool = False,
        readonly: bool = False,
        marker: str | None = None,
    ):
        LazyInitializedElement.__init__(self)
        self._label_text = label_text
        self._initial_value = initial_value
        self._validation = validation
        self._on_value_change = on_value_change
        self._autogrow = autogrow
        self._disabled = disabled
        self._readonly = readonly
        self._marker = marker

    def build(self) -> None:
        """Builds the UI form element."""
        self._instance = ui.input(
            self._label_text,
            value=self._initial_value,
            validation=self._validation,
        ).classes("w-full")
        if self._on_value_change:
            self._instance.on_value_change(self._on_value_change)
        self._apply(self.element)
        if self._disabled:
            self.element.disable()


class FormFieldFloat(FormField[Number, float]):
    """A class representing a floating point form field with validation and updating
    capabilities.

    Args:
        label_text (float): The label for the input field.
        initial_value (float): The initial value of the input.
        min_value (float): The minimum allowable value for the input. Defaults to None.
        max_value (float): The maximum allowable value for the input. Defaults to None.
        precision (int) : The number of decimal places to display. Defaults to 2.
        validation(Callable[..., str | None] | dict[str, Callable[..., bool]] | None):
            Validation functions to be applied on the element's data. Defaults to None.
        props (list[str] | None): props to be set for the number element.
        marker (str | None): marker to be set for the number element.
    """

    @property
    def value(self) -> float:
        """Provides the current input of the form field

        Returns:
            float: The current input of the form field.
        """

        return float(self.element.value)

    @property
    def props(self) -> list[str] | None:
        return self._props

    @property
    def marker(self) -> str | None:
        return self._marker

    def __init__(
        self,
        label_text: str,
        initial_value: float,
        min_value: float | None = None,
        max_value: float | None = None,
        precision: int = 2,
        step: float = 0.01,
        validation: (
            Callable[..., str | None] | dict[str, Callable[..., bool]] | None
        ) = None,
        props: list[str] | None = None,
        marker: str | None = None,
    ):
        super().__init__()
        self._label_text = label_text
        self._initial_value = initial_value
        self._min = min_value
        self._max = max_value
        self._precision = precision
        self._step = step
        self._validation = validation
        self._props = props
        self._marker = marker

    def build(self) -> None:
        """Builds the UI form element."""
        self._instance = ui.number(
            label=self._label_text,
            value=self._initial_value,
            min=self._min,
            max=self._max,
            precision=self._precision,
            validation=self._validation,
            step=self._step,
        ).classes("w-full")
        self._apply(self.element)


class FormFieldOptionalFloat(FormField[Number, float | None]):
    """A class representing a floating point form field with validation and updating
    capabilities. It supports optional values.

    Args:
        label_text (float): The label for the input field.
        initial_value (float): The initial value of the input. Defaults to None.
        min_value (float): The minimum allowable value for the input. Defaults to None.
        max_value (float): The maximum allowable value for the input. Defaults to None.
        precision (int) : The number of decimal places to display. Defaults to 2.
        validation(Callable[..., str | None] | dict[str, Callable[..., bool]] | None):
            Validation functions to be applied on the element's data. Defaults to None.
        props (list[str] | None): props to be set for the number element.
        marker (str | None): marker to be set for the number element.
    """

    @property
    def value(self) -> float | None:
        """Provides the current input of the form field

        Returns:
            float: The current input of the form field.
        """

        return float(self.element.value) if self.element.value else None

    @property
    def props(self) -> list[str] | None:
        return self._props

    @property
    def marker(self) -> str | None:
        return self._marker

    def __init__(
        self,
        label_text: str,
        initial_value: float | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        precision: int = 2,
        step: float = 0.01,
        validation: (
            Callable[..., str | None] | dict[str, Callable[..., bool]] | None
        ) = None,
        props: list[str] | None = None,
        marker: str | None = None,
    ):
        super().__init__()
        self._label_text = label_text
        self._initial_value = initial_value
        self._min = min_value
        self._max = max_value
        self._precision = precision
        self._step = step
        self._validation = validation
        self._props = props
        self._marker = marker

    def build(self) -> None:
        """Builds the UI form element."""
        self._instance = ui.number(
            label=self._label_text,
            value=self._initial_value,
            min=self._min,
            max=self._max,
            precision=self._precision,
            validation=self._validation,
            step=self._step,
        ).classes("w-full")
        self._apply(self.element)


class FormFieldInteger(FormField[Number, int]):
    """A class representing a integer form field with validation and updating
    capabilities.

    Args:
        label_text (int): The label for the input field.
        initial_value (int): The initial value of the input.
        min_value (int): The minimum allowable value for the input. Defaults to None.
        max_value (int): The maximum allowable value for the input. Defaults to None.
        validation(Callable[..., str | None] | dict[str, Callable[..., bool]] | None):
            Validation functions to be applied on the element's data. Defaults to None.
        props (list[str] | None): props to be set for the number element.
        marker (str | None): marker to be set for the number element.

    """

    @property
    def value(self) -> int:
        """Provides the current input of the form field

        Returns:
            int: The current input of the form field.
        """
        return int(self.element.value)

    @property
    def props(self) -> list[str] | None:
        return self._props

    @property
    def marker(self) -> str | None:
        return self._marker

    def __init__(
        self,
        label_text: str,
        initial_value: int,
        min_value: int | None = None,
        max_value: int | None = None,
        step: int = 1,
        validation: (
            Callable[..., str | None] | dict[str, Callable[..., bool]] | None
        ) = None,
        on_value_change: Callable[[ValueChangeEventArguments], None] | None = None,
        props: list[str] | None = None,
        marker: str | None = None,
    ) -> None:
        super().__init__()
        self._label_text = label_text
        self._initial_value = initial_value
        self._min = min_value
        self._max = max_value
        self._precision = 0
        self._step = step
        self._validation = validation
        self._on_value_change = on_value_change
        self._props = props
        self._marker = marker

    def build(self) -> None:
        """Builds the UI form element."""
        self._instance = ui.number(
            label=self._label_text,
            value=self._initial_value,
            min=self._min,
            max=self._max,
            precision=self._precision,
            validation=self._validation,
            step=self._step,
        ).classes("w-full")
        if self._on_value_change:
            self._instance.on_value_change(self._on_value_change)
        self._apply(self.element)

    @property
    def initial_value(self) -> int | None:
        return self._initial_value


class FormFieldDate(FormField[Input, Optional[date]]):

    @property
    def initial_value_text(self) -> str:
        return self.__format(self._initial_value)

    @property
    def value(self) -> Optional[date]:
        if self.element and self.element.value:
            if isinstance(self.element.value, date):
                return self.element.value
            return parse_datetime(
                self.element.value,
                formats=[YEAR_MONTH_DAY_FORMAT, DAY_MONTH_YEAR_FORMAT],
            ).date()
        return None

    @property
    def props(self) -> list[str] | None:
        return self._props

    @property
    def marker(self) -> str | None:
        return self._marker

    def __init__(
        self,
        label_text: str,
        initial_value: date | None = None,
        min_value: date | None = None,
        max_value: date | None = None,
        validation: (
            Callable[..., str | None] | dict[str, Callable[..., bool]] | None
        ) = None,
        on_value_change: Callable[[ValueChangeEventArguments], None] | None = None,
        props: list[str] | None = None,
        marker: str | None = None,
    ):
        super().__init__()
        self._label_text = label_text
        self._initial_value = initial_value
        self._min = min_value
        self._max = max_value
        self._validation = validation
        self._on_value_change = on_value_change
        self._props = props
        self._marker = marker

    def build(self) -> None:
        """Builds the UI form element."""
        self._instance = ui.input(
            self._label_text, value=self.initial_value_text
        ).style("max-width: 40%")
        with self._instance:
            with ui.menu().props("no-parent-event") as menu:
                with ui.date(value=self.initial_value_text).bind_value(self._instance):
                    with ui.row().classes("justify-end"):
                        ui.button("Close", on_click=menu.close).props("flat")
            with self._instance.add_slot("append"):
                ui.icon("edit_calendar").on("click", menu.open).classes(
                    "cursor-pointer"
                )

        if self._on_value_change:
            self._instance.on_value_change(self._on_value_change)
        self._apply(self.element)

    @staticmethod
    def __format(value: date | None) -> str:
        if value:
            return value.strftime(DAY_MONTH_YEAR_FORMAT)
        return ""


def parse_datetime(value: str, formats: list[str]) -> datetime:
    for format in formats:
        try:
            return datetime.strptime(value, format).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Could not parse datetime from {value}")


class FormFieldTime(FormField[Input, Optional[time]]):

    @property
    def initial_value_text(self) -> str:
        return self.__format(self._initial_value)

    @property
    def value(self) -> Optional[time]:
        if self.element and self.element.value:
            if isinstance(self.element.value, time):
                return self.element.value
            return parse_datetime(
                self.element.value,
                formats=[HOUR_MINUTE_SECOND_FORMAT, HOUR_MINUTE_FORMAT],
            ).time()
        return None

    @property
    def props(self) -> list[str] | None:
        return self._props

    @property
    def marker(self) -> str | None:
        return self._marker

    def __init__(
        self,
        label_text: str,
        initial_value: time | None = None,
        min_value: time | None = None,
        max_value: time | None = None,
        validation: (
            Callable[..., str | None] | dict[str, Callable[..., bool]] | None
        ) = None,
        on_value_change: Callable[[ValueChangeEventArguments], None] | None = None,
        props: list[str] | None = None,
        marker: str | None = None,
    ):
        super().__init__()
        self._label_text = label_text
        self._initial_value = initial_value
        self._min = min_value
        self._max = max_value
        self._validation = validation
        self._on_value_change = on_value_change
        self._props = props
        self._marker = marker

    def build(self) -> None:
        self._instance = ui.input(
            self._label_text, value=self.initial_value_text
        ).style("max-width: 40%")
        with self._instance:
            with ui.menu().props("no-parent-event") as menu:
                with ui.time(self.initial_value_text, mask="HH:mm:ss").bind_value(
                    self._instance
                ):
                    with ui.row().classes("justify-end"):
                        ui.button("Close", on_click=menu.close).props("flat")
            with self._instance.add_slot("append"):
                ui.icon("access_time").on("click", menu.open).classes("cursor-pointer")
        if self._on_value_change:
            self._instance.on_value_change(self._on_value_change)
        self._apply(self.element)

    @staticmethod
    def __format(value: time | None) -> str:
        if value:
            return value.strftime("%H:%M:%S")
        return ""


class DateTimeForm:
    """A class representing a integer form field with validation and updating
    capabilities.

    Args:
        label_text (int): The label for the input field.
        initial_value (int): The initial value of the input.
        min_value (int): The minimum allowable value for the input. Defaults to None.
        max_value (int): The maximum allowable value for the input. Defaults to None.
        validation(Callable[..., str | None] | dict[str, Callable[..., bool]] | None):
            Validation functions to be applied on the element's data. Defaults to None.
        props (list[str] | None): props to be set for the number element.
        marker (str | None): marker to be set for the number element.

    """

    @property
    def value(self) -> datetime | None:
        """Provides the current input of the form field

        Returns:
            int: The current input of the form field.
        """
        start_date = self._start_date.value
        start_time = self._start_time.value
        if start_date and start_time:
            return datetime.combine(start_date, start_time, tzinfo=timezone.utc)
        return None

    def set_value(self, value: datetime | None) -> None:
        if value:
            self._start_date.set_value(value.date())
            self._start_time.set_value(value.time())
        else:
            self._start_date.set_value(None)
            self._start_time.set_value(None)

    def __init__(
        self,
        label_date_text: str,
        label_time_text: str,
        initial_value: datetime | None = None,
        min_value: datetime | None = None,
        max_value: datetime | None = None,
        validation: (
            Callable[..., str | None] | dict[str, Callable[..., bool]] | None
        ) = None,
        on_value_change: Callable[[datetime | None], None] | None = None,
        props: list[str] | None = None,
        marker_date: str | None = None,
        marker_time: str | None = None,
    ) -> None:
        super().__init__()
        self._validation = validation
        self._on_value_change = on_value_change
        self._props = props
        self._start_date = FormFieldDate(
            label_text=label_date_text,
            initial_value=initial_value.date() if initial_value else None,
            min_value=min_value.date() if min_value else None,
            max_value=max_value.date() if max_value else None,
            on_value_change=self.__internal_update,
            marker=marker_date,
        )
        self._start_time = FormFieldTime(
            label_text=label_time_text,
            initial_value=initial_value.time() if initial_value else None,
            min_value=min_value.time() if min_value else None,
            max_value=max_value.time() if max_value else None,
            on_value_change=self.__internal_update,
            marker=marker_time,
        )

    def __internal_update(self, _: ValueChangeEventArguments) -> None:
        if self._on_value_change:
            self._on_value_change(self.value)

    def build(self) -> None:
        """Builds the UI form element."""
        with ui.grid().classes("w-full"):
            with ui.row():
                self._start_date.build()
                self._start_time.build()


class FormFieldCheckbox(LazyInitializedElement[Checkbox]):
    """A class representing a checkbox form field with updating capabilities.

    Args:
        label_text (str): The text to be displayed as the label.
        initial_value (bool): The initial value of the checkbox. Defaults False.
        props (str): Additional properties to be applied to the checkbox.
        marker (str): A marker to identify the checkbox in the UI.

    """

    @property
    def value(self) -> bool:
        """Provides the current checkbox value of the form field.

        Returns:
            bool: the current checkbox value.
        """
        return self.element.value

    def __init__(
        self,
        label_text: str,
        initial_value: bool = False,
        on_value_change: Callable[[ValueChangeEventArguments], None] | None = None,
        props: list[str] | None = None,
        marker: str | None = None,
    ):
        super().__init__()
        self._label_text = label_text
        self._initial_value = initial_value
        self._on_value_change = on_value_change
        self._props = props
        self._marker = marker

    def __internal_update(self, event: ValueChangeEventArguments) -> None:
        if self._on_value_change:
            self._on_value_change(event)

    def build(self) -> None:
        """Builds the UI form element."""
        self._instance = ui.checkbox(text=self._label_text, value=self._initial_value)
        if self._marker:
            self._instance.mark(self._marker)
        if self._on_value_change:
            self._instance.on_value_change(self._on_value_change)

    def set_value(self, value: bool) -> None:
        """Sets the value for the checkbox element.

        Also refreshes the UI element.

        Args:
            value (bool): The value to set for the element.
        """
        self.element.set_value(value)
        self.update()

    def update(self) -> None:
        """
        Updates the state of the checkbox element.

        This method calls the update method of the element associated with
        the instance, ensuring the element's state is refreshed with any
        new changes.

        """
        self.element.update()


class FormFieldSelect(FormField[Select, str]):
    """A class representing a select form field with updating capabilities.

    Args:
        label_text (str): The label for the select field.
        options (list[str]): The values to be selected from.
        initial_value (str): The initial value of the select field.
        props (list[str] | None): props to be set for the select element.
        marker (str | None): marker to be set for the select element.

    """

    @property
    def value(self) -> str:
        """Provides the current input of the form field

        Returns:
            int: The current input of the form field.
        """
        return self.element.value

    @property
    def props(self) -> list[str] | None:
        return self._props

    @property
    def marker(self) -> str | None:
        return self._marker

    def __init__(
        self,
        label_text: str,
        options: list[str],
        initial_value: str | None = None,
        on_value_change: Callable[[ValueChangeEventArguments], None] | None = None,
        props: list[str] | None = None,
        marker: str | None = None,
    ) -> None:
        super().__init__()
        self._label_text = label_text
        self._options = options
        self._initial_value = initial_value
        self._on_value_change = on_value_change
        self._props = props
        self._marker = marker

    def build(self) -> None:
        """Builds the UI form element."""
        self._instance = ui.select(
            label=self._label_text,
            options=self._options,
            value=self._initial_value if self._initial_value else self._options[0],
        ).classes("w-full")
        if self._on_value_change:
            self._instance.on_value_change(self._on_value_change)
        self._apply(self.element)

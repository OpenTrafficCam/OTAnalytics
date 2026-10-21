from collections.abc import Callable
from datetime import datetime
from typing import Any

from nicegui import ui
from nicegui.elements.button import Button
from nicegui.events import ValueChangeEventArguments

from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.default_values import DATETIME_FORMAT
from OTAnalytics.adapter_ui.dto import DateRangeDto
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.logger import logger
from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    ResourceManager,
    VisualizationFiltersKeys,
)
from OTAnalytics.domain.date import DateRange
from OTAnalytics.plugin_ui.customtkinter_gui.frame_filter import (
    InvalidDatetimeFormatError,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.constants import TestIdAttributes
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    DateTimeForm,
    FormFieldCheckbox,
    FormFieldInteger,
)

MARKER_FILTER_BY_DATE_CHECKBOX = "marker-filter-by-date-checkbox"
MARKER_FILTER_BY_DATE_BUTTON = "marker-filter-by-date-button"
MARKER_FILTER_BY_DATE_APPLY_BUTTON = "marker-filter-by-date-apply"
MARKER_FILTER_START_DATE_INPUT = "marker-filter-start-date"
MARKER_FILTER_START_TIME_INPUT = "marker-filter-start-time"
MARKER_FILTER_END_DATE_INPUT = "marker-filter-end-date"
MARKER_FILTER_END_TIME_INPUT = "marker-filter-end-time"
MARKER_FILTER_RANGE_LABEL = "marker-filter-range-label"

# Additional navigation markers for Playwright tests
MARKER_PREV_DATE_BUTTON = "marker-prev-date"
MARKER_NEXT_DATE_BUTTON = "marker-next-date"
MARKER_PREV_SECONDS_BUTTON = "marker-prev-seconds"
MARKER_NEXT_SECONDS_BUTTON = "marker-next-seconds"
MARKER_PREV_FRAMES_BUTTON = "marker-prev-frames"
MARKER_NEXT_FRAMES_BUTTON = "marker-next-frames"
MARKER_PREV_EVENT_BUTTON = "marker-prev-event"
MARKER_NEXT_EVENT_BUTTON = "marker-next-event"


class FilterDateRangeForm:
    def __init__(
        self,
        resource_manager: ResourceManager,
        viewmodel: ViewModel,
    ):
        self._resource_manager = resource_manager
        self._viewmodel = viewmodel
        self._start_date = DateTimeForm(
            self._resource_manager.get(VisualizationFiltersKeys.LABEL_START_DATE),
            self._resource_manager.get(VisualizationFiltersKeys.LABEL_START_TIME),
            marker_date=MARKER_FILTER_START_DATE_INPUT,
            marker_time=MARKER_FILTER_START_TIME_INPUT,
            date_validation=self._validate_date,
            time_validation=self._validate_time,
        )
        self._end_date = DateTimeForm(
            self._resource_manager.get(VisualizationFiltersKeys.LABEL_END_DATE),
            self._resource_manager.get(VisualizationFiltersKeys.LABEL_END_TIME),
            marker_date=MARKER_FILTER_END_DATE_INPUT,
            marker_time=MARKER_FILTER_END_TIME_INPUT,
            date_validation=self._validate_date,
            time_validation=self._validate_time,
        )

    def open(self) -> None:
        """Open the dialog, preset with the current date filter.

        Without a current filter, the start and end are preset with the first
        and last detection occurrence.
        """
        first_occurrence = self._viewmodel.get_first_detection_occurrence()
        last_occurrence = self._viewmodel.get_last_detection_occurrence()
        current_date_range = self._viewmodel.get_filter_tracks_by_date_setting()

        with ui.dialog() as self._dialog, ui.card():
            ui.label(
                self._label(VisualizationFiltersKeys.LABEL_FILTER_BY_DATE_TITLE)
            ).classes("text-lg")
            ui.label(self._label(VisualizationFiltersKeys.LABEL_CHOOSE_DATE_RANGE))
            with ui.row():
                ui.label(self._label(VisualizationFiltersKeys.LABEL_DATE_RANGE_FROM))
                self._start_date.build()
            with ui.row():
                ui.label(self._label(VisualizationFiltersKeys.LABEL_DATE_RANGE_TO))
                self._end_date.build()
            self._start_date.set_value(
                current_date_range.start_date or first_occurrence
            )
            self._end_date.set_value(current_date_range.end_date or last_occurrence)
            # Mark only what the user types.
            self._start_date.clear_validation()
            self._end_date.clear_validation()
            ui.label(
                self._occurrence_text(
                    VisualizationFiltersKeys.LABEL_FIRST_DETECTION_OCCURRENCE,
                    first_occurrence,
                )
            )
            ui.label(
                self._occurrence_text(
                    VisualizationFiltersKeys.LABEL_LAST_DETECTION_OCCURRENCE,
                    last_occurrence,
                )
            )
            with ui.row():
                apply_button = ui.button(
                    self._label(GeneralKeys.LABEL_APPLY),
                    on_click=self._on_apply_button_clicked,
                )
                # marker for Playwright: Apply button inside the filter-by-date dialog
                apply_button.mark(MARKER_FILTER_BY_DATE_APPLY_BUTTON)
                apply_button.props(
                    f"{TestIdAttributes.DATA_TESTID}={MARKER_FILTER_BY_DATE_APPLY_BUTTON}"  # noqa
                )
                ui.button(
                    self._label(GeneralKeys.LABEL_RESET),
                    on_click=self._on_reset_button_clicked,
                )
        self._dialog.open()

    def _validate_date(self, value: Any) -> str | None:
        """Validate the date while the user types.

        Returns:
            str | None: the error message, None if the date is valid or empty.
        """
        text = str(value) if value else ""
        if not text or self._viewmodel.validate_date(text):
            return None
        return self._label(VisualizationFiltersKeys.MESSAGE_INVALID_DATE_FORMAT)

    def _validate_time(self, value: Any) -> str | None:
        """Validate the hour, minute and, if given, second while the user types.

        Returns:
            str | None: the message for the first invalid part, None if the time
                is valid or empty.
        """
        text = str(value) if value else ""
        if not text:
            return None
        parts = text.split(":")
        checks = [
            (
                self._viewmodel.validate_hour,
                VisualizationFiltersKeys.MESSAGE_INVALID_HOUR,
            ),
            (
                self._viewmodel.validate_minute,
                VisualizationFiltersKeys.MESSAGE_INVALID_MINUTE,
            ),
            (
                self._viewmodel.validate_second,
                VisualizationFiltersKeys.MESSAGE_INVALID_SECOND,
            ),
        ]
        # Seconds are optional, as FormFieldTime accepts HH:MM as well.
        required = max(len(parts), 2)
        for index, (is_valid, message_key) in enumerate(checks[:required]):
            part = parts[index] if index < len(parts) else ""
            if not is_valid(part):
                return self._label(message_key)
        return None

    def _label(self, key: VisualizationFiltersKeys | GeneralKeys) -> str:
        return self._resource_manager.get(key)

    def _occurrence_text(
        self, key: VisualizationFiltersKeys, occurrence: datetime | None
    ) -> str:
        occurrence_text = occurrence.strftime(DATETIME_FORMAT) if occurrence else ""
        return f"{self._label(key)}: {occurrence_text}"

    def _on_apply_button_clicked(self) -> None:
        keys = VisualizationFiltersKeys
        try:
            date_range = DateRange(
                self._read(self._start_date, keys.LABEL_DATE_RANGE_FROM),
                self._read(self._end_date, keys.LABEL_DATE_RANGE_TO),
            )
            self._viewmodel.apply_filter_tracks_by_date(date_range)
            logger().info("Filter tracks by date applied")
            self._dialog.close()
        except InvalidDatetimeFormatError as e:
            logger().info(e)
            ui.notify(str(e), type="negative")

    def _read(
        self, date_time: DateTimeForm, name_key: VisualizationFiltersKeys
    ) -> datetime | None:
        """Read the entered date and time.

        An empty field means no bound. A partially filled or unparsable field is
        rejected, as in the customtkinter GUI.

        Raises:
            InvalidDatetimeFormatError: if the input is not a valid date and time.
        """
        if date_time.is_empty:
            return None
        try:
            value = date_time.value
        except ValueError:
            value = None
        if value is None:
            raise InvalidDatetimeFormatError(
                f"{self._label(name_key)} "
                f"{self._label(VisualizationFiltersKeys.MESSAGE_INVALID_DATETIME)}"
            )
        return value

    def _on_reset_button_clicked(self) -> None:
        self._viewmodel.reset_filter_tracks_by_date()
        self._dialog.close()


class FilterClassificationForm:
    """Dialog to select the classes whose tracks are shown.

    The checkboxes show the current class filter selection. Without a selection,
    every class counts as selected, as in the customtkinter GUI.
    """

    def __init__(self, resource_manager: ResourceManager, viewmodel: ViewModel) -> None:
        self._resource_manager = resource_manager
        self._viewmodel = viewmodel
        self._classes: list[str] = []
        self._selected_classes: set[str] = set()

    def open(self) -> None:
        self._classes = self._viewmodel.get_classes()
        self._selected_classes = set(self._current_selection())
        with ui.dialog() as self._dialog, ui.card():
            for classification in self._classes:
                self._build_checkbox(classification)
            with ui.row():
                self._build_buttons()
        self._dialog.open()

    def _current_selection(self) -> list[str]:
        selection = self._viewmodel.get_class_filter_selection()
        return self._classes if selection is None else selection

    def _build_checkbox(self, classification: str) -> None:
        FormFieldCheckbox(
            label_text=classification,
            initial_value=classification in self._selected_classes,
            on_value_change=self._create_class_toggle(classification),
        ).build()

    def _create_class_toggle(
        self, classification: str
    ) -> Callable[[ValueChangeEventArguments], None]:
        def toggle(event: ValueChangeEventArguments) -> None:
            self._select_class(classification, event.value)

        return toggle

    def _build_buttons(self) -> None:
        ui.button(
            self._resource_manager.get(GeneralKeys.LABEL_APPLY),
            on_click=self._on_apply_button_clicked,
        )
        ui.button(
            self._resource_manager.get(GeneralKeys.LABEL_RESET),
            on_click=self._on_reset_button_clicked,
        )

    def _select_class(self, classification: str, selected: bool) -> None:
        if selected:
            self._selected_classes.add(classification)
        else:
            self._selected_classes.discard(classification)

    def _on_apply_button_clicked(self) -> None:
        self._viewmodel.apply_filter_tracks_by_class(self._selected_classes)
        logger().info("Filter tracks by classification applied")
        self._dialog.close()

    def _on_reset_button_clicked(self) -> None:
        self._viewmodel.reset_filter_tracks_by_class()
        self._dialog.close()


class VisualizationFiltersForm(AbstractFrameFilter, ButtonForm):

    def __init__(
        self,
        resource_manager: ResourceManager,
        view_model: ViewModel,
    ) -> None:
        self._resource_manager = resource_manager
        self._viewmodel = view_model
        self._filter_by_date: ui.checkbox
        self._filter_by_class: ui.checkbox
        self._button_previous_second: ui.button | None = None
        self._button_previous_frame: ui.button | None = None
        self._button_previous_event: ui.button | None = None
        self._button_next_second: ui.button | None = None
        self._button_next_frame: ui.button | None = None
        self._button_next_event: ui.button | None = None
        # Created by `build()`, which runs when a browser first asks for the
        # page -- long after `_introduce_to_viewmodel` below makes this form
        # reachable from the view model. Until then the form exists and has no
        # widgets, and saying so here is what keeps that window harmless.
        self._filter_by_date_button: ui.button | None = None
        self._filter_by_date_button_left: ui.button | None = None
        self._filter_by_date_button_right: ui.button | None = None
        self._filter_by_class_button: ui.button | None = None
        self._label_filter_by_date: ui.label | None = None
        self._introduce_to_viewmodel()
        self._frames_to_skip = 0
        self._seconds_to_skip = 0

        self._filter_by_date_checkbox = FormFieldCheckbox(
            label_text="",
            initial_value=False,
            marker=MARKER_FILTER_BY_DATE_CHECKBOX,
            on_value_change=lambda e: self.change_button_date(e.value),
        )
        self._filter_by_date_popup = FilterDateRangeForm(
            self._resource_manager, self._viewmodel
        )
        self._filter_by_class_popup = FilterClassificationForm(
            self._resource_manager, self._viewmodel
        )
        self._input_seconds = FormFieldInteger(
            label_text=self._resource_manager.get(
                VisualizationFiltersKeys.LABEL_SECONDS
            ),
            initial_value=self._viewmodel.get_skip_seconds(),
            on_value_change=self.on_input_change,
        )
        self._input_frames = FormFieldInteger(
            label_text=self._resource_manager.get(
                VisualizationFiltersKeys.LABEL_FRAMES
            ),
            initial_value=self._viewmodel.get_skip_frames(),
            on_value_change=self.on_input_change,
        )

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_filter_frame(self)
        self._viewmodel.set_video_control_frame(self)

    def build(self) -> None:
        with ui.grid(columns=3):
            with ui.column():
                with ui.row():
                    self._filter_by_date_checkbox.build()
                    self._filter_by_date_button = ui.button(
                        self._resource_manager.get(
                            VisualizationFiltersKeys.BUTTON_FILTER_BY_DATE
                        ),
                        on_click=self.open_range_dialog,
                    )
                    # Attach a stable test marker for Playwright selection
                    self._filter_by_date_button.mark(MARKER_FILTER_BY_DATE_BUTTON)
                    self._filter_by_date_button.props(
                        f"{TestIdAttributes.DATA_TESTID}={MARKER_FILTER_BY_DATE_BUTTON}"
                    )
                    self._filter_by_date_button.disable()

                self._button_previous_second = ui.button(
                    "<", on_click=self._viewmodel.previous_second
                )
                self._button_previous_second.mark(MARKER_PREV_SECONDS_BUTTON)
                self._button_previous_second.props(
                    f"{TestIdAttributes.DATA_TESTID}={MARKER_PREV_SECONDS_BUTTON}"
                )
                self._button_previous_frame = ui.button(
                    "<", on_click=self._viewmodel.previous_frame
                )
                self._button_previous_frame.mark(MARKER_PREV_FRAMES_BUTTON)
                self._button_previous_frame.props(
                    f"{TestIdAttributes.DATA_TESTID}={MARKER_PREV_FRAMES_BUTTON}"
                )
                self._button_previous_event = ui.button(
                    "<", on_click=self._viewmodel.previous_event
                )
                self._button_previous_event.mark(MARKER_PREV_EVENT_BUTTON)
                self._button_previous_event.props(
                    f"{TestIdAttributes.DATA_TESTID}={MARKER_PREV_EVENT_BUTTON}"
                )
            with ui.column():
                with ui.row():
                    self._filter_by_date_button_left = ui.button(
                        "<", on_click=self._viewmodel.switch_to_prev_date_range
                    )
                    self._filter_by_date_button_left.mark(MARKER_PREV_DATE_BUTTON)
                    self._filter_by_date_button_left.props(
                        f"{TestIdAttributes.DATA_TESTID}={MARKER_PREV_DATE_BUTTON}"
                    )
                    self._label_filter_by_date = ui.label()
                    # Expose the current applied date range for Playwright assertions
                    self._label_filter_by_date.mark(MARKER_FILTER_RANGE_LABEL)
                    self._label_filter_by_date.props(
                        f"{TestIdAttributes.DATA_TESTID}={MARKER_FILTER_RANGE_LABEL}"
                    )
                    self._filter_by_date_button_right = ui.button(
                        ">", on_click=self._viewmodel.switch_to_next_date_range
                    )
                    self._filter_by_date_button_right.mark(MARKER_NEXT_DATE_BUTTON)
                    self._filter_by_date_button_right.props(
                        f"{TestIdAttributes.DATA_TESTID}={MARKER_NEXT_DATE_BUTTON}"
                    )
                    self._filter_by_date_button_left.disable()
                    self._filter_by_date_button_right.disable()
                self._input_seconds.build()
                self._input_frames.build()
                ui.label(
                    self._resource_manager.get(VisualizationFiltersKeys.LABEL_EVENT)
                )
            with ui.column():
                with ui.row():
                    self._filter_by_class_checkbox = ui.checkbox(
                        on_change=lambda e: self.change_button_class(e.value)
                    )
                    self._filter_by_class_button = ui.button(
                        self._resource_manager.get(
                            VisualizationFiltersKeys.BUTTON_FILTER_BY_CLASSIFICATION
                        ),
                        on_click=self.open_classification_dialog,
                    )
                    self._filter_by_class_button.disable()
                self._button_next_second = ui.button(
                    ">", on_click=self._viewmodel.next_second
                )
                self._button_next_second.mark(MARKER_NEXT_SECONDS_BUTTON)
                self._button_next_second.props(
                    f"{TestIdAttributes.DATA_TESTID}={MARKER_NEXT_SECONDS_BUTTON}"
                )
                self._button_next_frame = ui.button(
                    ">", on_click=self._viewmodel.next_frame
                )
                self._button_next_frame.mark(MARKER_NEXT_FRAMES_BUTTON)
                self._button_next_frame.props(
                    f"{TestIdAttributes.DATA_TESTID}={MARKER_NEXT_FRAMES_BUTTON}"
                )
                self._button_next_event = ui.button(
                    ">", on_click=self._viewmodel.next_event
                )
                self._button_next_event.mark(MARKER_NEXT_EVENT_BUTTON)
                self._button_next_event.props(
                    f"{TestIdAttributes.DATA_TESTID}={MARKER_NEXT_EVENT_BUTTON}"
                )
        self.set_enabled_general_buttons(False)

    def change_button_date(self, checkbox_status: bool) -> None:
        if checkbox_status:
            self._viewmodel.enable_filter_track_by_date()
        else:
            self._viewmodel.disable_filter_track_by_date()

    def change_button_class(self, checkbox_status: bool) -> None:
        if checkbox_status:
            self._viewmodel.enable_filter_track_by_class()
        else:
            self._viewmodel.disable_filter_track_by_class()

    def on_input_change(self, _: ValueChangeEventArguments) -> None:
        self._viewmodel.update_skip_time(
            self._input_seconds.value, self._input_frames.value
        )

    def open_classification_dialog(self) -> None:
        self._filter_by_class_popup.open()

    def open_range_dialog(self) -> None:
        self._filter_by_date_popup.open()

    def _date_buttons(self) -> list[ui.button]:
        """Every date button, or none at all while the form is unbuilt."""
        return [
            button
            for button in (
                self._filter_by_date_button,
                self._filter_by_date_button_left,
                self._filter_by_date_button_right,
            )
            if button is not None
        ]

    def set_active_color_on_filter_by_date_button(self) -> None:
        if self._filter_by_date_button is None:
            return
        self._filter_by_date_button.props("color=orange")
        # Expose active state for Playwright assertions
        self._filter_by_date_button.props("data-filter-by-date-active=true")

    def set_inactive_color_on_filter_by_date_button(self) -> None:
        if self._filter_by_date_button is None:
            return
        self._filter_by_date_button.props("color=primary")
        # Expose inactive state for Playwright assertions
        self._filter_by_date_button.props("data-filter-by-date-active=false")

    def set_active_color_on_filter_by_class_button(self) -> None:
        if self._filter_by_class_button is None:
            return
        self._filter_by_class_button.props("color=orange")

    def enable_filter_by_class_button(self) -> None:
        if self._filter_by_class_button is None:
            return
        self._filter_by_class_button.enable()

    def enable_filter_by_date_button(self) -> None:
        for button in self._date_buttons():
            button.enable()

    def set_inactive_color_on_filter_by_class_button(self) -> None:
        if self._filter_by_class_button is None:
            return
        self._filter_by_class_button.props("color=primary")

    def disable_filter_by_date_button(self) -> None:
        self.set_inactive_color_on_filter_by_date_button()
        for button in self._date_buttons():
            button.disable()

    def disable_filter_by_class_button(self) -> None:
        if self._filter_by_class_button is None:
            return
        self._filter_by_class_button.disable()

    def update_date_range(self, date_range: DateRangeDto) -> None:
        if self._label_filter_by_date is None:
            # The range still reaches the view model's state, so the label shows
            # it as soon as `build()` reads that state. Nothing is lost here.
            return
        start_date = date_range["start_date"]
        end_date = date_range["end_date"]

        if start_date == "" and end_date == "":
            self._label_filter_by_date.text = ""
        else:
            self._label_filter_by_date.text = f"{start_date} - {end_date}"

    def reset(self) -> None:
        pass

    def get_general_buttons(self) -> list[Button]:
        buttons = []
        if self._button_previous_second:
            buttons.append(self._button_previous_second)
        if self._button_previous_frame:
            buttons.append(self._button_previous_frame)
        if self._button_previous_event:
            buttons.append(self._button_previous_event)
        if self._button_next_second:
            buttons.append(self._button_next_second)
        if self._button_next_frame:
            buttons.append(self._button_next_frame)
        if self._button_next_event:
            buttons.append(self._button_next_event)
        return buttons

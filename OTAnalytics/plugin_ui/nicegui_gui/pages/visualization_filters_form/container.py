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
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    DateTimeForm,
    FormFieldCheckbox,
    FormFieldInteger,
)

MARKER_FILTER_BY_DATE_CHECKBOX = "marker-filter-by-date-checkbox"


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
        )
        self._end_date = DateTimeForm(
            self._resource_manager.get(VisualizationFiltersKeys.LABEL_END_DATE),
            self._resource_manager.get(VisualizationFiltersKeys.LABEL_END_TIME),
        )

    def open(self) -> None:
        first_occurrence_info_text = self._resource_manager.get(
            VisualizationFiltersKeys.LABEL_FIRST_DETECTION_OCCURRENCE
        )
        last_occurrence_info_text = self._resource_manager.get(
            VisualizationFiltersKeys.LABEL_LAST_DETECTION_OCCURRENCE
        )

        # Get first and last occurrence values
        first_occurrence = self._viewmodel.get_first_detection_occurrence()
        last_occurrence = self._viewmodel.get_last_detection_occurrence()

        # Update info text
        if first_occurrence:
            first_occurrence_info_text += first_occurrence.strftime(DATETIME_FORMAT)

        if last_occurrence:
            last_occurrence_info_text += last_occurrence.strftime(DATETIME_FORMAT)

        with ui.dialog() as self._dialog, ui.card():
            with ui.row():
                ui.label(
                    self._resource_manager.get(
                        VisualizationFiltersKeys.LABEL_DATE_RANGE_FROM
                    )
                )
                self._start_date.build()
            with ui.row():
                ui.label(
                    self._resource_manager.get(
                        VisualizationFiltersKeys.LABEL_DATE_RANGE_TO
                    )
                )
                self._end_date.build()

            # Set values after building the UI elements
            if first_occurrence:
                # Preset start date with first occurrence
                self._start_date.set_value(first_occurrence)

            if last_occurrence:
                # Preset end date with last occurrence
                self._end_date.set_value(last_occurrence)
            ui.label(first_occurrence_info_text)
            ui.label(last_occurrence_info_text)
            with ui.row():
                ui.button(
                    self._resource_manager.get(GeneralKeys.LABEL_APPLY),
                    on_click=self._on_apply_button_clicked,
                )
                ui.button(
                    self._resource_manager.get(GeneralKeys.LABEL_RESET),
                    on_click=self._on_reset_button_clicked,
                )
        self._dialog.open()

    def _on_apply_button_clicked(self) -> None:
        try:
            date_range = DateRange(self._start_date.value, self._end_date.value)
            self._viewmodel.apply_filter_tracks_by_date(date_range)
            logger().info("Filter tracks by date applied")
            self._dialog.close()
        except InvalidDatetimeFormatError as e:
            logger().info(e)

    def _on_reset_button_clicked(self) -> None:
        self._viewmodel.reset_filter_tracks_by_date()
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
        self._filter_by_class_list: list = []
        self._button_previous_second: ui.button | None = None
        self._button_previous_frame: ui.button | None = None
        self._button_previous_event: ui.button | None = None
        self._button_next_second: ui.button | None = None
        self._button_next_frame: ui.button | None = None
        self._button_next_event: ui.button | None = None
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
                    self._filter_by_date_button.disable()

                self._button_previous_second = ui.button(
                    "<", on_click=self._viewmodel.previous_second
                )
                self._button_previous_frame = ui.button(
                    "<", on_click=self._viewmodel.previous_frame
                )
                self._button_previous_event = ui.button(
                    "<", on_click=self._viewmodel.previous_event
                )
            with ui.column():
                with ui.row():
                    self._filter_by_date_button_left = ui.button(
                        "<", on_click=self._viewmodel.switch_to_prev_date_range
                    )
                    self._label_filter_by_date = ui.label()
                    self._filter_by_date_button_right = ui.button(
                        ">", on_click=self._viewmodel.switch_to_next_date_range
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
                self._button_next_frame = ui.button(
                    ">", on_click=self._viewmodel.next_frame
                )
                self._button_next_event = ui.button(
                    ">", on_click=self._viewmodel.next_event
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
        self._filter_by_class_list = self._viewmodel.get_classes()
        with ui.dialog() as dialog, ui.card():
            for classification_class in self._filter_by_class_list:
                FormFieldCheckbox(
                    label_text=classification_class,
                    initial_value=classification_class in self._selected_classes(),
                    on_value_change=lambda e: self.remove_or_add_class(
                        classification_class
                    ),
                )
            ui.button("Apply", on_click=lambda e: self.apply_new_classification(dialog))
        dialog.open()

    def _selected_classes(self) -> list[str]:
        selected_classes = self._viewmodel.get_class_filter_selection()
        return selected_classes if selected_classes else self._viewmodel.get_classes()

    def apply_new_classification(self, dialog: ui.dialog) -> None:
        self._viewmodel.apply_filter_tracks_by_class(self._filter_by_class_list)
        self._filter_by_class_list = []
        dialog.close()

    def remove_or_add_class(self, class_name: str) -> None:
        if class_name in self._filter_by_class_list:
            self._filter_by_class_list.remove(class_name)
        else:
            self._filter_by_class_list.append(class_name)

    def open_range_dialog(self) -> None:
        self._filter_by_date_popup.open()

    def set_active_color_on_filter_by_date_button(self) -> None:
        self._filter_by_date_button.props("color=orange")

    def set_inactive_color_on_filter_by_date_button(self) -> None:
        self._filter_by_date_button.props("color=primary")

    def set_active_color_on_filter_by_class_button(self) -> None:
        self._filter_by_class_button.props("color=orange")

    def enable_filter_by_class_button(self) -> None:
        self._filter_by_class_button.enable()

    def enable_filter_by_date_button(self) -> None:
        self._filter_by_date_button.enable()
        self._filter_by_date_button_left.enable()
        self._filter_by_date_button_right.enable()

    def set_inactive_color_on_filter_by_class_button(self) -> None:
        self._filter_by_class_button.props("color=primary")

    def disable_filter_by_date_button(self) -> None:
        self.set_inactive_color_on_filter_by_date_button()
        self._filter_by_date_button.disable()
        self._filter_by_date_button_left.disable()
        self._filter_by_date_button_right.disable()

    def disable_filter_by_class_button(self) -> None:
        self._filter_by_class_button.disable()

    def update_date_range(self, date_range: DateRangeDto) -> None:
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

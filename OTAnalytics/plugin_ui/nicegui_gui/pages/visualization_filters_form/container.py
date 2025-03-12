from nicegui import ui

from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.default_values import DATETIME_FORMAT
from OTAnalytics.adapter_ui.dto import DateRangeDto
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.logger import logger
from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
    VisualizationFiltersKeys,
)
from OTAnalytics.domain.date import DateRange
from OTAnalytics.plugin_ui.customtkinter_gui.frame_filter import (
    InvalidDatetimeFormatError,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import DateTimeForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)


class VisualizationFiltersForm(AbstractFrameFilter):

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
        self._introduce_to_viewmodel()
        self._frames_to_skip = 0
        self._seconds_to_skip = 0

        self._start_date = DateTimeForm(
            self._resource_manager.get(ProjectKeys.LABEL_START_DATE),
            self._resource_manager.get(ProjectKeys.LABEL_START_TIME),
        )
        self._second_start_date = DateTimeForm(
            self._resource_manager.get(ProjectKeys.LABEL_START_DATE),
            self._resource_manager.get(ProjectKeys.LABEL_START_TIME),
        )

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_filter_frame(self)

    def build(self) -> None:
        with ui.grid(columns=3):
            with ui.column():
                with ui.row():
                    ui.checkbox(on_change=lambda e: self.change_button_date(e.value))
                    self._filter_by_date_button = ui.button(
                        self._resource_manager.get(
                            VisualizationFiltersKeys.BUTTON_FILTER_BY_DATE
                        ),
                        on_click=self.open_range_dialog,
                    )
                    self._filter_by_date_button.disable()

                ui.button("<", on_click=self._viewmodel.previous_second)
                ui.button("<", on_click=self._viewmodel.previous_frame)
                ui.button("<", on_click=self._viewmodel.previous_event)
            with ui.column():
                with ui.row():
                    self.filter_by_date_button_left = ui.button(
                        "<", on_click=self._viewmodel.switch_to_prev_date_range
                    )
                    self.label_filter_by_date = ui.label()
                    self.filter_by_date_button_right = ui.button(
                        ">", on_click=self._viewmodel.switch_to_next_date_range
                    )
                    self.filter_by_date_button_left.disable()
                    self.filter_by_date_button_right.disable()
                self.input_seconds = ui.number(
                    value=self._viewmodel.get_skip_seconds(),
                    on_change=self.on_input_change,
                )
                self.input_frames = ui.number(
                    value=self._viewmodel.get_skip_frames(),
                    on_change=self.on_input_change,
                )
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
                ui.button(">", on_click=self._viewmodel.next_second)
                ui.button(">", on_click=self._viewmodel.next_frame)
                ui.button(">", on_click=self._viewmodel.next_event)

    def change_button_date(self, checkbox_status: bool) -> None:
        self._filter_by_date_button.set_enabled(checkbox_status)
        self.filter_by_date_button_left.set_enabled(checkbox_status)
        self.filter_by_date_button_right.set_enabled(checkbox_status)

    def change_button_class(self, checkbox_status: bool) -> None:
        self._filter_by_class_button.set_enabled(checkbox_status)

    def on_input_change(self) -> None:
        self._viewmodel.update_skip_time(
            self.input_seconds.value, self.input_frames.value
        )

    def open_classification_dialog(self) -> None:
        self._filter_by_class_list = self._viewmodel.get_classes()
        with ui.dialog() as dialog, ui.card():
            for classification_class in self._viewmodel.get_classes():
                ui.checkbox(
                    classification_class,
                    on_change=lambda e: self.remove_or_add_class(classification_class),
                )
            ui.button("Apply", on_click=lambda e: self.apply_new_classification(dialog))
        dialog.open()

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
        first_occurrence_info_text = self._resource_manager.get(
            VisualizationFiltersKeys.LABEL_FIRST_DETECTION_OCCURRENCE
        )
        last_occurrence_info_text = self._resource_manager.get(
            VisualizationFiltersKeys.LABEL_LAST_DETECTION_OCCURRENCE
        )
        if first_occurrence := self._viewmodel.get_first_detection_occurrence():
            first_occurrence_info_text += first_occurrence.strftime(DATETIME_FORMAT)

        if last_occurrence := self._viewmodel.get_last_detection_occurrence():
            last_occurrence_info_text += last_occurrence.strftime(DATETIME_FORMAT)
        with ui.dialog() as dialog, ui.card():

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
                self._second_start_date.build()
            ui.label(first_occurrence_info_text)
            ui.label(last_occurrence_info_text)
            with ui.row():
                ui.button("Apply", on_click=self._on_apply_button_clicked)
                ui.button("Reset", on_click=dialog.close)
        dialog.open()

    def set_active_color_on_filter_by_date_button(self) -> None:
        self._filter_by_date_button.props("color=orange")

    def set_inactive_color_on_filter_by_date_button(self) -> None:
        self._filter_by_date_button.props("color=green")

    def set_active_color_on_filter_by_class_button(self) -> None:
        self._filter_by_class_button.props("color=orange")

    def enable_filter_by_class_button(self) -> None:
        self._filter_by_class_button.enable()

    def enable_filter_by_date_button(self) -> None:
        self._filter_by_date_button.enable()

    def set_inactive_color_on_filter_by_class_button(self) -> None:
        self._filter_by_class_button.props("color=green")

    def disable_filter_by_date_button(self) -> None:
        pass

    def disable_filter_by_class_button(self) -> None:
        pass

    def update_date_range(self, date_range: DateRangeDto) -> None:
        start_date = date_range["start_date"]
        end_date = date_range["end_date"]

        if start_date == "" and end_date == "":
            self.label_filter_by_date.text = ""
        else:
            self.label_filter_by_date.text = f"{start_date} - {end_date}"

    def _on_apply_button_clicked(self) -> None:
        try:
            date_range = DateRange(
                self._start_date.value, self._second_start_date.value
            )
            self._viewmodel.apply_filter_tracks_by_date(date_range)
            logger().info("Filter tracks by date applied")
        except InvalidDatetimeFormatError as e:
            logger().info(e)

    def reset(self) -> None:
        pass

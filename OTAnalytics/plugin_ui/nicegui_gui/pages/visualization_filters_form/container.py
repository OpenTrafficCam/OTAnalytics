from nicegui import ui

from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.dto import DateRangeDto
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.logger import logger
from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
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
                    self._filter_by_date_checkbox = ui.checkbox(
                        on_change=lambda e: self.change_button_date(e.value)
                    )
                    self._filter_by_date_button = ui.button(
                        "Funktioniert", on_click=self.open_range_dialog
                    )
                    self._filter_by_date_button.disable()

                self.seconds_left = ui.button(
                    "<", on_click=self._viewmodel.previous_second
                )
                self.frames_left = ui.button(
                    "<", on_click=self._viewmodel.previous_frame
                )
                self.event_left = ui.button(
                    "<", on_click=self._viewmodel.previous_event
                )
            with ui.column():
                with ui.row():
                    self.button_left = ui.button(
                        "<", on_click=self._viewmodel.switch_to_prev_date_range
                    )
                    self.button_right = ui.button(
                        ">", on_click=self._viewmodel.switch_to_next_date_range
                    )
                self.input_seconds = ui.number(
                    value=self._viewmodel.get_skip_seconds(),
                    on_change=self.on_input_change,
                )
                self.input_frames = ui.number(
                    value=self._viewmodel.get_skip_frames(),
                    on_change=self.on_input_change,
                )
                self.event_label = ui.label("Event")
            with ui.column():
                with ui.row():
                    self._filter_by_class_checkbox = ui.checkbox(
                        on_change=lambda e: self.change_button_class(e.value)
                    )
                    self._filter_by_class_button = ui.button(
                        "Funktioniert", on_click=self.open_classification_dialog
                    )
                    self._filter_by_class_button.disable()
                self.seconds_right = ui.button(
                    ">", on_click=self._viewmodel.next_second
                )
                self.frames_right = ui.button(">", on_click=self._viewmodel.next_frame)
                self.event_right = ui.button(">", on_click=self._viewmodel.next_event)

    def change_button_date(self, checkbox_status: bool) -> None:
        if checkbox_status:
            self._filter_by_date_button.set_enabled(True)
        else:
            self._filter_by_date_button.set_enabled(False)

    def change_button_class(self, checkbox_status: bool) -> None:
        if checkbox_status:
            self._filter_by_class_button.set_enabled(True)
        else:
            self._filter_by_class_button.set_enabled(False)

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
        with ui.dialog() as dialog, ui.card():
            ui.label("Hello world!")
            self._start_date.build()
            self._second_start_date.build()
            ui.button("Apply", on_click=self._on_apply_button_clicked)
            ui.button("Reset", on_click=dialog.close)
        dialog.open()

    def set_active_color_on_filter_by_date_button(self) -> None:
        pass

    def set_inactive_color_on_filter_by_date_button(self) -> None:
        pass

    def set_active_color_on_filter_by_class_button(self) -> None:
        self._filter_by_class.style()

    def enable_filter_by_class_button(self) -> None:
        self._filter_by_class_button.enable()

    def enable_filter_by_date_button(self) -> None:
        self._filter_by_date_button.enable()

    def set_inactive_color_on_filter_by_class_button(self) -> None:
        self._filter_by_class.style()

    def disable_filter_by_date_button(self) -> None:
        pass

    def disable_filter_by_class_button(self) -> None:
        self._filter_by_class.disable()

    def update_date_range(self, date_range: DateRangeDto) -> None:
        pass

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

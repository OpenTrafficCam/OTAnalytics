import tkinter
from tkinter import E, StringVar, W
from typing import Any, Optional

from customtkinter import CTkEntry, CTkLabel, CTkOptionMenu

from OTAnalytics.adapter_ui.flow_dto import FlowDto
from OTAnalytics.adapter_ui.text_resources import ColumnResources
from OTAnalytics.application.application import CancelAddFlow
from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.generate_flows import FlowNameGenerator
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_template import (
    FrameContent,
    ToplevelTemplate,
)

FLOW_ID = "Id"
FLOW_NAME = "Name"
START_SECTION = "Start section"
END_SECTION = "End section"
DISTANCE = "Distance"


class TooFewSectionsForFlowException(Exception):
    pass


class SectionSeveralTimesInFlowException(Exception):
    pass


class NotExistingSectionException(Exception):
    pass


class InvalidFlowNameException(Exception):
    pass


class FrameConfigureFlow(FrameContent):
    def __init__(
        self,
        section_ids: ColumnResources,
        name_generator: FlowNameGenerator,
        input_values: FlowDto | None = None,
        show_distance: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._section_ids = section_ids
        self._name_generator = name_generator
        self._current_name = StringVar()
        self._input_values: dict = self.__create_input_values(input_values)
        self._show_distance = show_distance
        self._last_autofilled_name: str = self._input_values.get(FLOW_NAME, "")
        self.__set_initial_values()
        self._get_widgets()
        self._place_widgets()

    def set_focus(self) -> None:
        self.after(0, lambda: self.entry_distance.focus_set())

    def _get_widgets(self) -> None:
        self.label_section_start = CTkLabel(master=self, text="First section:")
        self.dropdown_section_start = CTkOptionMenu(
            master=self,
            width=180,
            values=self._section_ids.names,
            command=self._autofill_name,
        )
        self.dropdown_section_start.set(self._get_start_section_name())
        self.label_section_end = CTkLabel(master=self, text="Second section:")
        self.dropdown_section_end = CTkOptionMenu(
            master=self,
            width=180,
            values=self._section_ids.names,
            command=self._autofill_name,
        )
        self.dropdown_section_end.set(self._get_end_section_name())
        self.label_name = CTkLabel(master=self, text="Name:")
        self.entry_name = CTkEntry(
            master=self,
            width=180,
            textvariable=self._current_name,
        )
        self.label_distance = CTkLabel(master=self, text="Distance [m]:")
        self.entry_distance = CTkEntry(
            master=self,
            width=180,
            validate="key",
            validatecommand=(self.register(self._is_float_above_zero), "%P"),
        )
        if current_distance := self._input_values[DISTANCE]:
            self.entry_distance.insert(index=0, string=current_distance)

    def _place_widgets(self) -> None:
        self.label_section_start.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="E")
        self.dropdown_section_start.grid(
            row=0, column=1, padx=PADX, pady=PADY, sticky="W"
        )
        self.label_section_end.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=E)
        self.dropdown_section_end.grid(row=1, column=1, padx=PADX, pady=PADY, sticky=W)
        self.label_name.grid(row=2, column=0, padx=PADX, pady=PADY, sticky=tkinter.E)
        self.entry_name.grid(row=2, column=1, padx=PADX, pady=PADY, sticky=tkinter.W)
        if self._show_distance:
            self.label_distance.grid(row=3, column=0, padx=PADX, pady=PADY, sticky=E)
            self.entry_distance.grid(row=3, column=1, padx=PADX, pady=PADY, sticky=W)

    def __set_initial_values(self) -> None:
        self._current_name.set(self._input_values.get(FLOW_NAME, ""))

    def __create_input_values(self, input_values: Optional[FlowDto]) -> dict:
        if input_values is not None:
            return {
                FLOW_ID: input_values.flow_id,
                FLOW_NAME: input_values.name,
                START_SECTION: input_values.start_section,
                END_SECTION: input_values.end_section,
                DISTANCE: input_values.distance,
            }
        return {
            FLOW_ID: "",
            FLOW_NAME: "",
            START_SECTION: "",
            END_SECTION: "",
            DISTANCE: None,
        }

    def _autofill_name(self, event: Any) -> None:
        if self._last_autofilled_name == self.entry_name.get():
            self.entry_name.delete(0, tkinter.END)
            start_section = self.dropdown_section_start.get()
            end_section = self.dropdown_section_end.get()
            auto_name = self._name_generator.generate_from_string(
                start_section, end_section
            )
            self.entry_name.insert(0, auto_name)
            self._last_autofilled_name = auto_name

    def _get_end_section_name(self) -> str:
        _id = self._input_values[END_SECTION]
        return self._section_ids.get_name_for(_id)

    def _get_start_section_name(self) -> str:
        _id = self._input_values[START_SECTION]
        return self._section_ids.get_name_for(_id)

    def _get_end_section_id(self) -> str:
        name = self.dropdown_section_end.get()
        return self._section_ids.get_id_for(name)

    def _get_start_section_id(self) -> str:
        name = self.dropdown_section_start.get()
        return self._section_ids.get_id_for(name)

    def _is_float_above_zero(self, entry_value: Any) -> bool:
        try:
            float_value = self.__parse_distance(entry_value)
        except Exception:
            return False
        return float_value >= 0 if float_value else True

    def __parse_distance(self, entry_value: Any) -> Optional[float]:
        return float(entry_value) if entry_value else None

    def _check_sections(self) -> None:
        section_start = self._get_start_section_id()
        section_end = self._get_end_section_id()
        sections = [section_start, section_end]
        if "" in [section_start, section_end]:
            raise TooFewSectionsForFlowException(
                "Please choose both a start and an end section!"
            )
        else:
            for section in sections:
                if not self._section_ids.has(section):
                    raise NotExistingSectionException(
                        f"{section} is not an existing section"
                    )

    def _check_flow_name(self) -> None:
        if self._current_name.get() == "":
            raise InvalidFlowNameException("Please choose a flow name!")

    def get_input_values(self) -> FlowDto:
        self._check_sections()
        self._check_flow_name()
        return FlowDto(
            flow_id=self._input_values[FLOW_ID],
            name=self._current_name.get(),
            start_section=self._get_start_section_id(),
            end_section=self._get_end_section_id(),
            distance=self.__parse_distance(self.entry_distance.get()),
        )


class ToplevelFlows(ToplevelTemplate):
    def __init__(
        self,
        section_ids: ColumnResources,
        name_generator: FlowNameGenerator,
        input_values: FlowDto | None = None,
        show_distance: bool = True,
        **kwargs: Any,
    ) -> None:
        self._input_values = input_values
        self._section_ids = section_ids
        self._name_generator = name_generator
        self._show_distance = show_distance
        super().__init__(**kwargs)

    def _create_frame_content(self, master: Any) -> FrameContent:
        return FrameConfigureFlow(
            master=master,
            section_ids=self._section_ids,
            name_generator=self._name_generator,
            input_values=self._input_values,
            show_distance=self._show_distance,
        )

    def _on_ok(self, event: Any = None) -> None:
        self._input_values = self._frame_content.get_input_values()
        self._close()

    def get_data(self) -> FlowDto:
        self.wait_window()
        if self._canceled:
            raise CancelAddFlow()
        if self._input_values is None:
            raise ValueError("input values is None, but should be a dict")
        logger().debug(self._input_values)
        return self._input_values

"""Form to edit the static analysis configuration of the current project."""

from pathlib import Path

from nicegui import ui
from nicegui.events import ValueChangeEventArguments

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    StaticAnalysisConfigKeys,
)
from OTAnalytics.application.use_cases.static_analysis_config import (
    GetCountingEventOfCurrentAnalysisConfig,
    GetCountIntervalsOfCurrentAnalysisConfig,
    GetDoCountingOfCurrentAnalysisConfig,
    GetDoEventsOfCurrentAnalysisConfig,
    GetEventFormatsOfCurrentAnalysisConfig,
    GetLogfileOfCurrentAnalysisConfig,
    GetNumProcessesOfCurrentAnalysisConfig,
    GetSaveNameOfCurrentAnalysisConfig,
    GetSaveSuffixOfCurrentAnalysisConfig,
    SetCountingEventInCurrentAnalysisConfig,
    SetCountIntervalsInCurrentAnalysisConfig,
    SetDoCountingInCurrentAnalysisConfig,
    SetDoEventsInCurrentAnalysisConfig,
    SetEventFormatsInCurrentAnalysisConfig,
    SetLogfileInCurrentAnalysisConfig,
    SetNumProcessesInCurrentAnalysisConfig,
    SetSaveNameInCurrentAnalysisConfig,
    SetSaveSuffixInCurrentAnalysisConfig,
)
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    EXTENSION_CSV,
    EXTENSION_EXCEL,
    EXTENSION_OTEVENTS,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    FormFieldCheckbox,
    FormFieldInteger,
    FormFieldMultiSelect,
    FormFieldSelect,
    FormFieldText,
)

MARKER_DO_EVENTS = "marker-do-events"
MARKER_DO_COUNTING = "marker-do-counting"
MARKER_SAVE_NAME = "marker-save-name"
MARKER_SAVE_SUFFIX = "marker-save-suffix"
MARKER_EVENT_FORMATS = "marker-event-formats"
MARKER_COUNT_INTERVALS = "marker-count-intervals"
MARKER_COUNTING_EVENT = "marker-counting-event"
MARKER_NUM_PROCESSES = "marker-num-processes"
MARKER_LOGFILE = "marker-logfile"

EVENT_FORMAT_OPTIONS = [EXTENSION_OTEVENTS, EXTENSION_CSV, EXTENSION_EXCEL]
COUNT_INTERVAL_SEPARATOR = ","
MINIMUM_NUM_PROCESSES = 1


def parse_count_intervals(text: str) -> set[int]:
    """Parse count intervals from a separated list of whole numbers.

    Args:
        text (str): the count intervals in minutes, separated by commas.

    Returns:
        set[int]: the parsed count intervals in minutes.

    Raises:
        ValueError: if an entry is not a positive whole number.
    """
    intervals = set()
    for entry in text.split(COUNT_INTERVAL_SEPARATOR):
        stripped = entry.strip()
        if not stripped:
            continue
        interval = int(stripped)
        if interval <= 0:
            raise ValueError(f"Count interval must be positive but is {interval}")
        intervals.add(interval)
    return intervals


def format_count_intervals(count_intervals: set[int]) -> str:
    """Format count intervals as a separated list of whole numbers.

    Args:
        count_intervals (set[int]): the count intervals in minutes.

    Returns:
        str: the count intervals in minutes, separated by commas.
    """
    return f"{COUNT_INTERVAL_SEPARATOR} ".join(
        str(interval) for interval in sorted(count_intervals)
    )


class StaticAnalysisConfigForm:
    """Form to display and edit the static analysis configuration.

    Each field writes its value to the application state as soon as it changes.

    Args:
        resource_manager (ResourceManager): the resource manager for localization.
        get_do_events (GetDoEventsOfCurrentAnalysisConfig): provides whether events
            are to be detected.
        set_do_events (SetDoEventsInCurrentAnalysisConfig): sets whether events are
            to be detected.
        get_do_counting (GetDoCountingOfCurrentAnalysisConfig): provides whether
            counts are to be created.
        set_do_counting (SetDoCountingInCurrentAnalysisConfig): sets whether counts
            are to be created.
        get_save_name (GetSaveNameOfCurrentAnalysisConfig): provides the save name.
        set_save_name (SetSaveNameInCurrentAnalysisConfig): sets the save name.
        get_save_suffix (GetSaveSuffixOfCurrentAnalysisConfig): provides the save
            suffix.
        set_save_suffix (SetSaveSuffixInCurrentAnalysisConfig): sets the save suffix.
        get_event_formats (GetEventFormatsOfCurrentAnalysisConfig): provides the
            event formats.
        set_event_formats (SetEventFormatsInCurrentAnalysisConfig): sets the event
            formats.
        get_count_intervals (GetCountIntervalsOfCurrentAnalysisConfig): provides the
            count intervals in minutes.
        set_count_intervals (SetCountIntervalsInCurrentAnalysisConfig): sets the
            count intervals in minutes.
        get_counting_event (GetCountingEventOfCurrentAnalysisConfig): provides the
            counting event.
        set_counting_event (SetCountingEventInCurrentAnalysisConfig): sets the
            counting event.
        get_num_processes (GetNumProcessesOfCurrentAnalysisConfig): provides the
            number of processes.
        set_num_processes (SetNumProcessesInCurrentAnalysisConfig): sets the number
            of processes.
        get_logfile (GetLogfileOfCurrentAnalysisConfig): provides the logfile.
        set_logfile (SetLogfileInCurrentAnalysisConfig): sets the logfile.
    """

    def __init__(
        self,
        resource_manager: ResourceManager,
        get_do_events: GetDoEventsOfCurrentAnalysisConfig,
        set_do_events: SetDoEventsInCurrentAnalysisConfig,
        get_do_counting: GetDoCountingOfCurrentAnalysisConfig,
        set_do_counting: SetDoCountingInCurrentAnalysisConfig,
        get_save_name: GetSaveNameOfCurrentAnalysisConfig,
        set_save_name: SetSaveNameInCurrentAnalysisConfig,
        get_save_suffix: GetSaveSuffixOfCurrentAnalysisConfig,
        set_save_suffix: SetSaveSuffixInCurrentAnalysisConfig,
        get_event_formats: GetEventFormatsOfCurrentAnalysisConfig,
        set_event_formats: SetEventFormatsInCurrentAnalysisConfig,
        get_count_intervals: GetCountIntervalsOfCurrentAnalysisConfig,
        set_count_intervals: SetCountIntervalsInCurrentAnalysisConfig,
        get_counting_event: GetCountingEventOfCurrentAnalysisConfig,
        set_counting_event: SetCountingEventInCurrentAnalysisConfig,
        get_num_processes: GetNumProcessesOfCurrentAnalysisConfig,
        set_num_processes: SetNumProcessesInCurrentAnalysisConfig,
        get_logfile: GetLogfileOfCurrentAnalysisConfig,
        set_logfile: SetLogfileInCurrentAnalysisConfig,
    ) -> None:
        self._resource_manager = resource_manager
        self._get_do_events = get_do_events
        self._set_do_events = set_do_events
        self._get_do_counting = get_do_counting
        self._set_do_counting = set_do_counting
        self._get_save_name = get_save_name
        self._set_save_name = set_save_name
        self._get_save_suffix = get_save_suffix
        self._set_save_suffix = set_save_suffix
        self._get_event_formats = get_event_formats
        self._set_event_formats = set_event_formats
        self._get_count_intervals = get_count_intervals
        self._set_count_intervals = set_count_intervals
        self._get_counting_event = get_counting_event
        self._set_counting_event = set_counting_event
        self._get_num_processes = get_num_processes
        self._set_num_processes = set_num_processes
        self._get_logfile = get_logfile
        self._set_logfile = set_logfile
        self._do_events: FormFieldCheckbox
        self._do_counting: FormFieldCheckbox
        self._save_name: FormFieldText
        self._save_suffix: FormFieldText
        self._event_formats: FormFieldMultiSelect
        self._count_intervals: FormFieldText
        self._counting_event: FormFieldSelect
        self._num_processes: FormFieldInteger
        self._logfile: FormFieldText
        self._create_fields()

    def _create_fields(self) -> None:
        """Creates the form fields prefilled with the current configuration."""
        self._do_events = FormFieldCheckbox(
            label_text=self._label(StaticAnalysisConfigKeys.LABEL_DO_EVENTS),
            initial_value=self._get_do_events.get(),
            on_value_change=self._update_do_events,
            marker=MARKER_DO_EVENTS,
        )
        self._do_counting = FormFieldCheckbox(
            label_text=self._label(StaticAnalysisConfigKeys.LABEL_DO_COUNTING),
            initial_value=self._get_do_counting.get(),
            on_value_change=self._update_do_counting,
            marker=MARKER_DO_COUNTING,
        )
        self._save_name = FormFieldText(
            label_text=self._label(StaticAnalysisConfigKeys.LABEL_SAVE_NAME),
            initial_value=self._get_save_name.get(),
            on_value_change=self._update_save_name,
            marker=MARKER_SAVE_NAME,
        )
        self._save_suffix = FormFieldText(
            label_text=self._label(StaticAnalysisConfigKeys.LABEL_SAVE_SUFFIX),
            initial_value=self._get_save_suffix.get(),
            on_value_change=self._update_save_suffix,
            marker=MARKER_SAVE_SUFFIX,
        )
        self._event_formats = FormFieldMultiSelect(
            label_text=self._label(StaticAnalysisConfigKeys.LABEL_EVENT_FORMATS),
            options=EVENT_FORMAT_OPTIONS,
            initial_value=sorted(self._get_event_formats.get()),
            on_value_change=self._update_event_formats,
            marker=MARKER_EVENT_FORMATS,
        )
        self._count_intervals = FormFieldText(
            label_text=self._label(StaticAnalysisConfigKeys.LABEL_COUNT_INTERVALS),
            initial_value=format_count_intervals(self._get_count_intervals.get()),
            validation={
                self._label(
                    StaticAnalysisConfigKeys.VALIDATION_COUNT_INTERVALS
                ): self._are_valid_count_intervals
            },
            on_value_change=self._update_count_intervals,
            marker=MARKER_COUNT_INTERVALS,
        )
        self._counting_event = FormFieldSelect(
            label_text=self._label(StaticAnalysisConfigKeys.LABEL_COUNTING_EVENT),
            options=[event.value for event in CountingEvent],
            initial_value=self._get_counting_event.get().value,
            on_value_change=self._update_counting_event,
            marker=MARKER_COUNTING_EVENT,
        )
        self._num_processes = FormFieldInteger(
            label_text=self._label(StaticAnalysisConfigKeys.LABEL_NUM_PROCESSES),
            initial_value=self._get_num_processes.get(),
            min_value=MINIMUM_NUM_PROCESSES,
            on_value_change=self._update_num_processes,
            marker=MARKER_NUM_PROCESSES,
        )
        self._logfile = FormFieldText(
            label_text=self._label(StaticAnalysisConfigKeys.LABEL_LOGFILE),
            initial_value=str(self._get_logfile.get()),
            on_value_change=self._update_logfile,
            marker=MARKER_LOGFILE,
        )

    def build(self) -> None:
        """Builds the UI form elements.

        The fields are recreated so that a page build always shows the
        configuration currently held by the application.
        """
        self._create_fields()
        ui.label(
            self._label(
                StaticAnalysisConfigKeys.LABEL_STATIC_ANALYSIS_CONFIG_FORM_HEADER
            )
        ).classes("text-lg font-bold")
        with ui.column().classes("w-full"):
            self._do_events.build()
            self._do_counting.build()
            self._save_name.build()
            self._save_suffix.build()
            self._event_formats.build()
            self._count_intervals.build()
            self._counting_event.build()
            self._num_processes.build()
            self._logfile.build()

    def _label(self, key: StaticAnalysisConfigKeys) -> str:
        return self._resource_manager.get(key)

    def _update_do_events(self, event: ValueChangeEventArguments) -> None:
        self._set_do_events.set(bool(event.value))

    def _update_do_counting(self, event: ValueChangeEventArguments) -> None:
        self._set_do_counting.set(bool(event.value))

    def _update_save_name(self, event: ValueChangeEventArguments) -> None:
        self._set_save_name.set(str(event.value))

    def _update_save_suffix(self, event: ValueChangeEventArguments) -> None:
        self._set_save_suffix.set(str(event.value))

    def _update_event_formats(self, event: ValueChangeEventArguments) -> None:
        self._set_event_formats.set(set(event.value))

    def _update_count_intervals(self, event: ValueChangeEventArguments) -> None:
        if not self._are_valid_count_intervals(event.value):
            return
        self._set_count_intervals.set(parse_count_intervals(event.value))

    def _update_counting_event(self, event: ValueChangeEventArguments) -> None:
        self._set_counting_event.set(CountingEvent.parse(event.value))

    def _update_num_processes(self, event: ValueChangeEventArguments) -> None:
        if event.value is None:
            return
        self._set_num_processes.set(int(event.value))

    def _update_logfile(self, event: ValueChangeEventArguments) -> None:
        self._set_logfile.set(Path(str(event.value)))

    @staticmethod
    def _are_valid_count_intervals(value: str) -> bool:
        try:
            return bool(parse_count_intervals(value))
        except ValueError:
            return False

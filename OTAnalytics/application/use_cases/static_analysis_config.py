"""Use cases to read and change single values of the static analysis config."""

from pathlib import Path

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.state import (
    CurrentExportConfigState,
    CurrentStaticAnalysisConfigState,
)
from OTAnalytics.domain.observer import OBSERVER, Subject


class StaticAnalysisConfigChanged:
    """Notify observers that a value of the static analysis config was changed.

    Only changes made by the user are published. Loading a project replaces the
    whole configuration without passing this notifier, so a load does not look
    like an unsaved change.
    """

    def __init__(self) -> None:
        self._subject = Subject[None]()

    def register(self, observer: OBSERVER[None]) -> None:
        """Listen to changes of the static analysis config.

        Args:
            observer (OBSERVER[None]): the observer to be registered.
        """
        self._subject.register(observer)

    def notify(self) -> None:
        """Notify all observers about a changed static analysis config."""
        self._subject.notify(None)


class GetDoEventsOfCurrentAnalysisConfig:
    """Provide whether event detection is enabled.

    Args:
        state (CurrentStaticAnalysisConfigState): the state holding the analysis
            settings.
    """

    def __init__(self, state: CurrentStaticAnalysisConfigState) -> None:
        self._state = state

    def get(self) -> bool:
        """Get whether event detection is enabled.

        Returns:
            bool: True if events are to be detected.
        """
        return self._state.do_events


class SetDoEventsInCurrentAnalysisConfig:
    """Enable or disable event detection.

    Args:
        state (CurrentStaticAnalysisConfigState): the state holding the analysis
            settings.
        config_changed (StaticAnalysisConfigChanged): notifies observers about
            the change.
    """

    def __init__(
        self,
        state: CurrentStaticAnalysisConfigState,
        config_changed: StaticAnalysisConfigChanged,
    ) -> None:
        self._state = state
        self._config_changed = config_changed

    def set(self, do_events: bool) -> None:
        """Set whether events are to be detected.

        Args:
            do_events (bool): True if events are to be detected.
        """
        self._state.do_events = do_events
        self._config_changed.notify()


class GetDoCountingOfCurrentAnalysisConfig:
    """Provide whether counting is enabled.

    Args:
        state (CurrentStaticAnalysisConfigState): the state holding the analysis
            settings.
    """

    def __init__(self, state: CurrentStaticAnalysisConfigState) -> None:
        self._state = state

    def get(self) -> bool:
        """Get whether counting is enabled.

        Returns:
            bool: True if counts are to be created.
        """
        return self._state.do_counting


class SetDoCountingInCurrentAnalysisConfig:
    """Enable or disable counting.

    Args:
        state (CurrentStaticAnalysisConfigState): the state holding the analysis
            settings.
        config_changed (StaticAnalysisConfigChanged): notifies observers about
            the change.
    """

    def __init__(
        self,
        state: CurrentStaticAnalysisConfigState,
        config_changed: StaticAnalysisConfigChanged,
    ) -> None:
        self._state = state
        self._config_changed = config_changed

    def set(self, do_counting: bool) -> None:
        """Set whether counts are to be created.

        Args:
            do_counting (bool): True if counts are to be created.
        """
        self._state.do_counting = do_counting
        self._config_changed.notify()


class GetNumProcessesOfCurrentAnalysisConfig:
    """Provide the number of processes to be used for the analysis.

    Args:
        state (CurrentStaticAnalysisConfigState): the state holding the analysis
            settings.
    """

    def __init__(self, state: CurrentStaticAnalysisConfigState) -> None:
        self._state = state

    def get(self) -> int:
        """Get the number of processes to be used for the analysis.

        Returns:
            int: the number of processes.
        """
        return self._state.num_processes


class SetNumProcessesInCurrentAnalysisConfig:
    """Change the number of processes to be used for the analysis.

    Args:
        state (CurrentStaticAnalysisConfigState): the state holding the analysis
            settings.
        config_changed (StaticAnalysisConfigChanged): notifies observers about
            the change.
    """

    def __init__(
        self,
        state: CurrentStaticAnalysisConfigState,
        config_changed: StaticAnalysisConfigChanged,
    ) -> None:
        self._state = state
        self._config_changed = config_changed

    def set(self, num_processes: int) -> None:
        """Set the number of processes to be used for the analysis.

        Args:
            num_processes (int): the number of processes.
        """
        self._state.num_processes = num_processes
        self._config_changed.notify()


class GetLogfileOfCurrentAnalysisConfig:
    """Provide the logfile the analysis log is written to.

    Args:
        state (CurrentStaticAnalysisConfigState): the state holding the analysis
            settings.
    """

    def __init__(self, state: CurrentStaticAnalysisConfigState) -> None:
        self._state = state

    def get(self) -> Path:
        """Get the logfile the analysis log is written to.

        Returns:
            Path: the logfile.
        """
        return self._state.logfile


class SetLogfileInCurrentAnalysisConfig:
    """Change the logfile the analysis log is written to.

    Args:
        state (CurrentStaticAnalysisConfigState): the state holding the analysis
            settings.
        config_changed (StaticAnalysisConfigChanged): notifies observers about
            the change.
    """

    def __init__(
        self,
        state: CurrentStaticAnalysisConfigState,
        config_changed: StaticAnalysisConfigChanged,
    ) -> None:
        self._state = state
        self._config_changed = config_changed

    def set(self, logfile: Path) -> None:
        """Set the logfile the analysis log is written to.

        Args:
            logfile (Path): the logfile.
        """
        self._state.logfile = logfile
        self._config_changed.notify()


class GetSaveNameOfCurrentAnalysisConfig:
    """Provide the name used to save analysis results.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
    """

    def __init__(self, state: CurrentExportConfigState) -> None:
        self._state = state

    def get(self) -> str:
        """Get the name used to save analysis results.

        Returns:
            str: the save name.
        """
        return self._state.save_name


class SetSaveNameInCurrentAnalysisConfig:
    """Change the name used to save analysis results.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
        config_changed (StaticAnalysisConfigChanged): notifies observers about
            the change.
    """

    def __init__(
        self,
        state: CurrentExportConfigState,
        config_changed: StaticAnalysisConfigChanged,
    ) -> None:
        self._state = state
        self._config_changed = config_changed

    def set(self, save_name: str) -> None:
        """Set the name used to save analysis results.

        Args:
            save_name (str): the save name.
        """
        self._state.save_name = save_name
        self._config_changed.notify()


class GetSaveSuffixOfCurrentAnalysisConfig:
    """Provide the suffix appended to the name used to save analysis results.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
    """

    def __init__(self, state: CurrentExportConfigState) -> None:
        self._state = state

    def get(self) -> str:
        """Get the suffix appended to the save name.

        Returns:
            str: the save suffix.
        """
        return self._state.save_suffix


class SetSaveSuffixInCurrentAnalysisConfig:
    """Change the suffix appended to the name used to save analysis results.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
        config_changed (StaticAnalysisConfigChanged): notifies observers about
            the change.
    """

    def __init__(
        self,
        state: CurrentExportConfigState,
        config_changed: StaticAnalysisConfigChanged,
    ) -> None:
        self._state = state
        self._config_changed = config_changed

    def set(self, save_suffix: str) -> None:
        """Set the suffix appended to the save name.

        Args:
            save_suffix (str): the save suffix.
        """
        self._state.save_suffix = save_suffix
        self._config_changed.notify()


class GetEventFormatsOfCurrentAnalysisConfig:
    """Provide the formats the event list is exported to.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
    """

    def __init__(self, state: CurrentExportConfigState) -> None:
        self._state = state

    def get(self) -> set[str]:
        """Get the formats the event list is exported to.

        Returns:
            set[str]: the event formats.
        """
        return self._state.event_formats


class SetEventFormatsInCurrentAnalysisConfig:
    """Change the formats the event list is exported to.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
        config_changed (StaticAnalysisConfigChanged): notifies observers about
            the change.
    """

    def __init__(
        self,
        state: CurrentExportConfigState,
        config_changed: StaticAnalysisConfigChanged,
    ) -> None:
        self._state = state
        self._config_changed = config_changed

    def set(self, event_formats: set[str]) -> None:
        """Set the formats the event list is exported to.

        Args:
            event_formats (set[str]): the event formats.
        """
        self._state.event_formats = event_formats
        self._config_changed.notify()


class GetCountIntervalsOfCurrentAnalysisConfig:
    """Provide the count intervals in minutes.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
    """

    def __init__(self, state: CurrentExportConfigState) -> None:
        self._state = state

    def get(self) -> set[int]:
        """Get the count intervals in minutes.

        Returns:
            set[int]: the count intervals in minutes.
        """
        return self._state.count_intervals


class SetCountIntervalsInCurrentAnalysisConfig:
    """Change the count intervals in minutes.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
        config_changed (StaticAnalysisConfigChanged): notifies observers about
            the change.
    """

    def __init__(
        self,
        state: CurrentExportConfigState,
        config_changed: StaticAnalysisConfigChanged,
    ) -> None:
        self._state = state
        self._config_changed = config_changed

    def set(self, count_intervals: set[int]) -> None:
        """Set the count intervals in minutes.

        Args:
            count_intervals (set[int]): the count intervals in minutes.
        """
        self._state.count_intervals = count_intervals
        self._config_changed.notify()


class GetCountingEventOfCurrentAnalysisConfig:
    """Provide the event a road user is counted at.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
    """

    def __init__(self, state: CurrentExportConfigState) -> None:
        self._state = state

    def get(self) -> CountingEvent:
        """Get the event a road user is counted at.

        Returns:
            CountingEvent: the counting event.
        """
        return self._state.counting_event


class SetCountingEventInCurrentAnalysisConfig:
    """Change the event a road user is counted at.

    Args:
        state (CurrentExportConfigState): the state holding the export settings.
        config_changed (StaticAnalysisConfigChanged): notifies observers about
            the change.
    """

    def __init__(
        self,
        state: CurrentExportConfigState,
        config_changed: StaticAnalysisConfigChanged,
    ) -> None:
        self._state = state
        self._config_changed = config_changed

    def set(self, counting_event: CountingEvent) -> None:
        """Set the event a road user is counted at.

        Args:
            counting_event (CountingEvent): the counting event.
        """
        self._state.counting_event = counting_event
        self._config_changed.notify()

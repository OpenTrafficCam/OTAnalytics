from pathlib import Path
from typing import Iterable

import pandas as pd

from OTAnalytics.application.config import DEFAULT_EVENTLIST_FILE_TYPE
from OTAnalytics.application.datastore import EventListParser
from OTAnalytics.application.export_formats import event_list
from OTAnalytics.application.logger import logger
from OTAnalytics.application.use_cases.export_events import (
    EventListExporter,
    ExporterNotFoundError,
)
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section
from OTAnalytics.plugin_parser.otvision_parser import OtEventListParser

EXTENSION_CSV = "csv"
EXTENSION_EXCEL = "xlsx"
EXTENSION_OTEVENTS = DEFAULT_EVENTLIST_FILE_TYPE

OTC_EXCEL_FORMAT_NAME = "Excel (OpenTrafficCam)"
OTC_CSV_FORMAT_NAME = "CSV (OpenTrafficCam)"
OTC_OTEVENTS_FORMAT_NAME = "OTEvents (OpenTrafficCam)"


class EventListDataFrameBuilder:
    def __init__(self, events: Iterable[Event], sections: Iterable[Section]):
        self._events = events
        self._sections = sections
        self._df = self._convert_to_dataframe(events)

    def _convert_to_dataframe(self, events: Iterable[Event]) -> pd.DataFrame:
        return pd.DataFrame([event.to_dict() for event in events])

    def build(self) -> pd.DataFrame:
        self._convert_occurrence_to_seconds_since_epoch()
        self._split_columns_with_lists()
        self._add_section_names()
        self._add_detailed_date_time_columns()
        return self._df

    def _add_detailed_date_time_columns(self) -> None:
        occurrence_column = pd.to_datetime(self._df[event_list.OCCURRENCE])
        self._df[event_list.OCCURRENCE_DATE] = occurrence_column.dt.strftime(
            event_list.DATE_FORMAT
        )
        self._df[event_list.OCCURRENCE_TIME] = occurrence_column.dt.strftime(
            event_list.TIME_FORMAT
        )

    def _convert_occurrence_to_seconds_since_epoch(self) -> None:
        # TODO: Use OTAnalytics´ builtin timestamp methods
        epoch = pd.Timestamp("1970-01-01")
        occurrence = pd.to_datetime(self._df[event_list.OCCURRENCE])
        self._df[f"{event_list.OCCURRENCE}_sec"] = (
            occurrence - epoch
        ).dt.total_seconds()

    def _split_columns_with_lists(self) -> None:
        self._df[[event_list.EVENT_COORDINATE_X, event_list.EVENT_COORDINATE_Y]] = (
            pd.DataFrame(
                self._df[event_list.EVENT_COORDINATE].tolist(), index=self._df.index
            )
        )
        self._df[[event_list.DIRECTION_VECTOR_X, event_list.DIRECTION_VECTOR_Y]] = (
            pd.DataFrame(
                self._df[event_list.DIRECTION_VECTOR].tolist(), index=self._df.index
            )
        )
        self._df = self._df.drop(
            columns=[event_list.EVENT_COORDINATE, event_list.DIRECTION_VECTOR]
        )

    def _add_section_names(self) -> None:
        sections_list_of_dicts = [section.to_dict() for section in self._sections]
        sections_dict = {
            section["id"]: section["name"] for section in sections_list_of_dicts
        }
        self._df["section_name"] = self._df[event_list.SECTION_ID].map(
            lambda x: sections_dict.get(x)
        )


class SectionsDataFrameBuilder:
    def __init__(self, sections: Iterable[Section]):
        self._sections = sections
        self._df = self._convert_to_dataframe(sections)

    def _convert_to_dataframe(self, sections: Iterable[Section]) -> pd.DataFrame:
        sections_list_of_dicts = [section.to_dict() for section in self._sections]
        return pd.json_normalize(sections_list_of_dicts, sep="_")

    def build(self) -> pd.DataFrame:
        return self._df


class EventListExcelExporter(EventListExporter):
    def export(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        df_events = EventListDataFrameBuilder(events=events, sections=sections).build()
        df_sections = SectionsDataFrameBuilder(sections=sections).build()
        self._write_to_excel(file, df_events, df_sections)

    def _write_to_excel(
        self, file: Path, df_events: pd.DataFrame, df_sections: pd.DataFrame
    ) -> None:
        writer = pd.ExcelWriter(file, engine="openpyxl")
        df_events.to_excel(writer, index=False, sheet_name="Events")
        df_sections.to_excel(writer, index=False, sheet_name="Sections")
        writer.close()

    def get_extension(self) -> str:
        return f".{EXTENSION_EXCEL}"

    def get_name(self) -> str:
        return OTC_EXCEL_FORMAT_NAME


class EventListCSVExporter(EventListExporter):
    def export(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        df_events = EventListDataFrameBuilder(events=events, sections=sections).build()
        self._write_to_excel(file, df_events)

    def _write_to_excel(self, file: Path, df_events: pd.DataFrame) -> None:
        df_events.to_csv(file, index=False)

    def get_extension(self) -> str:
        return f".{EXTENSION_CSV}"

    def get_name(self) -> str:
        return OTC_CSV_FORMAT_NAME


class EventListOteventsExporter(EventListExporter):
    def __init__(self, event_list_parser: EventListParser) -> None:
        self._event_list_parser = event_list_parser

    def export(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        self._event_list_parser.serialize(events, sections, file)

    def get_extension(self) -> str:
        return f".{EXTENSION_OTEVENTS}"

    def get_name(self) -> str:
        return OTC_OTEVENTS_FORMAT_NAME


class EventListDictPrinter(EventListExporter):
    def export(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        logger().info("Events:")
        logger().info([event.to_dict() for event in events])
        logger().info(
            "__________________________________________________________________"
        )
        logger().info("Sections:")
        logger().info([section.to_dict() for section in sections])

    def get_extension(self) -> str:
        return ""

    def get_name(self) -> str:
        return "print dicts to console"


class EventListDataFramePrinter(EventListExporter):
    def export(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        df_events = EventListDataFrameBuilder(events=events, sections=sections).build()
        df_sections = SectionsDataFrameBuilder(sections=sections).build()
        logger().info("Events:")
        logger().info(df_events)
        logger().info(
            "__________________________________________________________________"
        )
        logger().info("Sections:")
        logger().info(df_sections)

    def get_extension(self) -> str:
        return ""

    def get_name(self) -> str:
        return "print Dataframe to console"


AVAILABLE_EVENTLIST_EXPORTERS: dict[str, EventListExporter] = {
    OTC_CSV_FORMAT_NAME: EventListCSVExporter(),
    OTC_EXCEL_FORMAT_NAME: EventListExcelExporter(),
    OTC_OTEVENTS_FORMAT_NAME: EventListOteventsExporter(OtEventListParser()),
}


def provide_available_eventlist_exporter(event_format: str) -> EventListExporter:
    _format = event_format.lower()
    if _format == EXTENSION_CSV or _format == f".{EXTENSION_CSV}":
        return AVAILABLE_EVENTLIST_EXPORTERS[OTC_CSV_FORMAT_NAME]
    elif _format == EXTENSION_EXCEL or _format == f".{EXTENSION_EXCEL}":
        return AVAILABLE_EVENTLIST_EXPORTERS[OTC_EXCEL_FORMAT_NAME]
    elif _format == EXTENSION_OTEVENTS or _format == f".{EXTENSION_OTEVENTS}":
        return AVAILABLE_EVENTLIST_EXPORTERS[OTC_OTEVENTS_FORMAT_NAME]
    else:
        raise ExporterNotFoundError(
            f"{event_format} is a not supported eventlist format. "
            f"Supported formats are: [{EXTENSION_CSV}, "
            f"{EXTENSION_EXCEL}, {EXTENSION_OTEVENTS}]"
        )

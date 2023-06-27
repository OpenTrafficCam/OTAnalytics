from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd

from OTAnalytics.application.datastore import EventListExporter
from OTAnalytics.domain.event import (
    DIRECTION_VECTOR,
    EVENT_COORDINATE,
    OCCURRENCE,
    SECTION_ID,
    Event,
)
from OTAnalytics.domain.section import Section

OTC_EXCEL_FORMAT_NAME = "Excel (OpenTrafficCam)"
OTC_CSV_FORMAT_NAME = "CSV (OpenTrafficCam)"


class EventListDataFrameBuilder:
    def __init__(self, events: Iterable[Event], sections: Iterable[Section]):
        self._events = events
        self._sections = sections
        self._df = self._convert_to_dataframe(events)

    def _convert_to_dataframe(self, events: Iterable[Event]) -> pd.DataFrame:
        return pd.DataFrame([event.to_dict() for event in events])

    def build(self) -> pd.DataFrame:
        self._convert_occurence_to_seconds_since_epoch()
        self._split_columns_with_lists()
        self._add_section_names()
        return self._df

    def _convert_occurence_to_seconds_since_epoch(self) -> None:
        epoch = pd.Timestamp("1970-01-01")
        occurence = pd.to_datetime(self._df[OCCURRENCE])
        self._df[f"{OCCURRENCE}_sec"] = (occurence - epoch).dt.total_seconds()

    def _split_columns_with_lists(self) -> None:
        self._df[["coordinate_px_x", "coordinate_px_y"]] = pd.DataFrame(
            self._df[EVENT_COORDINATE].tolist(), index=self._df.index
        )
        self._df[["vector_px_x", "vector_px_y"]] = pd.DataFrame(
            self._df[DIRECTION_VECTOR].tolist(), index=self._df.index
        )
        self._df = self._df.drop(columns=[EVENT_COORDINATE, DIRECTION_VECTOR])

    def _add_section_names(self) -> None:
        sections_list_of_dicts = [section.to_dict() for section in self._sections]
        sections_dict = {
            section["id"]: section["name"] for section in sections_list_of_dicts
        }
        self._df["section_name"] = self._df[SECTION_ID].map(
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
        return "xlsx"

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
        return "csv"

    def get_name(self) -> str:
        return OTC_CSV_FORMAT_NAME


class EventListDictPrinter(EventListExporter):
    def export(
        self, events: Iterable[Event], sections: Iterable[Section], file: Path
    ) -> None:
        print("Events:")
        print([event.to_dict() for event in events])
        print("__________________________________________________________________")
        print("Sections:")
        print([section.to_dict() for section in sections])

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
        print("Events:")
        print(df_events)
        print("__________________________________________________________________")
        print("Sections:")
        print(df_sections)

    def get_extension(self) -> str:
        return ""

    def get_name(self) -> str:
        return "print Dataframe to console"


class ExporterNotFoundError(Exception):
    pass


@dataclass
class EventListExporterStrategies:
    AVAILABLE_EXPORTERS: list[EventListExporter] = field(
        default_factory=lambda: [
            EventListExcelExporter(),
            EventListCSVExporter(),
            # EventListPrinter(),
            # EventListDataFramePrinter(),
        ]
    )

    def get_exporter_by_name(self, name: str) -> EventListExporter:
        for exporter in self.AVAILABLE_EXPORTERS:
            if exporter.get_name() == name:
                return exporter
        raise ExporterNotFoundError(f"Exporter {name} not found in available exporters")

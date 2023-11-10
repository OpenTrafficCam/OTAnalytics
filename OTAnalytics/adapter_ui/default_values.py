from OTAnalytics.domain.section import RelativeOffsetCoordinate

RELATIVE_SECTION_OFFSET: RelativeOffsetCoordinate = RelativeOffsetCoordinate(0.5, 0.5)
DATE_FORMAT: str = r"%Y-%m-%d"
DATETIME_FORMAT: str = r"%Y-%m-%d %H:%M:%S"
DATE_FORMAT_PLACEHOLDER = "yyyy-mm-dd"

DATE_FORMAT_GERMAN: str = r"%d.%m.%Y"
DATETIME_FORMAT_GERMAN: str = r"%d.%m.%Y %H:%M:%S"
DATE_FORMAT_PLACEHOLDER_GERMAN = "dd.mm.yyyy"

SUPPORTED_FORMATS: list[str] = [DATE_FORMAT, DATE_FORMAT_GERMAN]

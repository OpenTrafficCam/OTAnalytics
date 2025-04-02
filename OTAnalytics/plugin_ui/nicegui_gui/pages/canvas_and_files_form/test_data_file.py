from OTAnalytics.domain.geometry import RelativeOffsetCoordinate, Coordinate
from OTAnalytics.domain.section import LineSection, SectionId
from OTAnalytics.domain.types import EventType

TestData = [
    LineSection(
        id=SectionId(id='1'),
        name='Süd',
        relative_offset_coordinates={
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(x=0.5, y=0.5)
        },
        plugin_data={},
        coordinates=[
            Coordinate(x=43, y=184),
            Coordinate(x=137, y=200),
            Coordinate(x=352, y=145),
            Coordinate(x=362, y=89),
        ],
    ),
    LineSection(
        id=SectionId(id='2'),
        name='West',
        relative_offset_coordinates={
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(x=0.5, y=0.5)
        },
        plugin_data={'distances': {'Süd': '022', 'Ost': '0', 'Nord': '0'}},
        coordinates=[
            Coordinate(x=388, y=83),
            Coordinate(x=428, y=139),
            Coordinate(x=577, y=159),
            Coordinate(x=694, y=125),
        ],
    ),
    LineSection(
        id=SectionId(id='3'),
        name='Nord',
        relative_offset_coordinates={
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(x=0.5, y=0.5)
        },
        plugin_data={'distances': {'West': '0'}},
        coordinates=[
            Coordinate(x=788, y=175),
            Coordinate(x=621, y=213),
            Coordinate(x=287, y=394),
            Coordinate(x=230, y=578),
        ],
    ),
    LineSection(
        id=SectionId(id='4'),
        name='Ost',
        relative_offset_coordinates={
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(x=0.7, y=0.2)
        },
        plugin_data={},
        coordinates=[
            Coordinate(x=15, y=204),
            Coordinate(x=130, y=222),
            Coordinate(x=270, y=369),
            Coordinate(x=215, y=573),
        ],
    ),
]

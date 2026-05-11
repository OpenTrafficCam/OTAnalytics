from datetime import datetime

from OTAnalytics.application.project import (
    COORDINATE_X,
    COORDINATE_Y,
    COUNTING_DAY,
    COUNTING_LOCATION_NUMBER,
    DIRECTION,
    DIRECTION_DESCRIPTION,
    HAS_BICYCLE_LANE,
    IS_BICYCLE_COUNTING,
    METADATA,
    NAME,
    REMARK,
    START_DATE,
    TK_NUMBER,
    WEATHER,
    CountingDayType,
    DirectionOfStationing,
    Project,
    SvzMetadata,
    WeatherType,
)


class TestSvzMetadata:
    def test_to_dict(self) -> None:
        tk_number = "1"
        counting_location_number = "2"
        direction = "1"
        direction_description = "direction_description"
        has_bicycle_lane = True
        is_bicycle_counting = True
        counting_day = "2"
        weather = "2"
        remark = "something"
        coordinate_x = "1.2"
        coordinate_y = "3.4"
        metadata = SvzMetadata(
            tk_number=tk_number,
            counting_location_number=counting_location_number,
            direction=DirectionOfStationing.parse(direction),
            direction_description=direction_description,
            has_bicycle_lane=has_bicycle_lane,
            is_bicycle_counting=is_bicycle_counting,
            counting_day=CountingDayType.parse(counting_day),
            weather=WeatherType.parse(weather),
            remark=remark,
            coordinate_x=coordinate_x,
            coordinate_y=coordinate_y,
        )

        actual = metadata.to_dict()

        expected = {
            TK_NUMBER: tk_number,
            COUNTING_LOCATION_NUMBER: counting_location_number,
            DIRECTION: direction,
            DIRECTION_DESCRIPTION: direction_description,
            HAS_BICYCLE_LANE: has_bicycle_lane,
            IS_BICYCLE_COUNTING: is_bicycle_counting,
            COUNTING_DAY: counting_day,
            WEATHER: weather,
            REMARK: remark,
            COORDINATE_X: coordinate_x,
            COORDINATE_Y: coordinate_y,
        }

        assert actual == expected


class TestProject:
    def test_to_dict(self) -> None:
        name = "some"
        timestamp = 12345678.0
        tk_number = "1"
        counting_location_number = "2"
        direction = "1"
        direction_description = "direction_description"
        has_bicycle_lane = True
        is_bicycle_counting = True
        counting_day = "2"
        weather = "2"
        remark = "something"
        coordinate_x = "1.2"
        coordinate_y = "3.4"
        metadata = SvzMetadata(
            tk_number=tk_number,
            counting_location_number=counting_location_number,
            direction=DirectionOfStationing.parse(direction),
            direction_description=direction_description,
            has_bicycle_lane=has_bicycle_lane,
            is_bicycle_counting=is_bicycle_counting,
            counting_day=CountingDayType.parse(counting_day),
            weather=WeatherType.parse(weather),
            remark=remark,
            coordinate_x=coordinate_x,
            coordinate_y=coordinate_y,
        )
        start_date = datetime.fromtimestamp(timestamp)
        project = Project(name=name, start_date=start_date, metadata=metadata)

        result = project.to_dict()

        expected_metadata = metadata.to_dict()
        expected_result = {
            NAME: name,
            START_DATE: timestamp,
            METADATA: expected_metadata,
        }
        assert result == expected_result

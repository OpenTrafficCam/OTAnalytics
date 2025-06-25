from abc import ABC
from typing import Self

from nicegui import ui
from nicegui.events import ValueChangeEventArguments

from OTAnalytics.adapter_ui.abstract_frame_project import AbstractFrameSvzMetadata
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.project import (
    COORDINATE_X,
    COORDINATE_Y,
    COUNTING_DAY,
    COUNTING_LOCATION_NUMBER,
    DIRECTION,
    DIRECTION_DESCRIPTION,
    HAS_BICYCLE_LANE,
    IS_BICYCLE_COUNTING,
    REMARK,
    TK_NUMBER,
    WEATHER,
)
from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    SvzMetadataKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    FormFieldCheckbox,
    FormFieldSelect,
    FormFieldText,
)

MARKER_TK_NUMBER = "marker-tk-number"
MARKER_COUNTING_LOCATION_NUMBER = "marker-counting-location-number"
MARKER_DIRECTION_SELECT = "marker-direction-select"
MARKER_DIRECTION_DESCRIPTION = "marker-direction-description"
MARKER_HAS_BICYCLE_LANE = "marker-has-bicycle-lane"
MARKER_IS_BICYCLE_COUNTING = "marker-is-bicycle-counting"
MARKER_COUNTING_DAY_SELECT = "marker-counting-day-select"
MARKER_WEATHER_TYPE_SELECT = "marker-weather-type_select"
MARKER_REMARK = "marker-remark"
MARKER_COORDINATE_X = "marker-coordinate-x"
MARKER_COORDINATE_Y = "marker-coordinate-y"


class SvzMetadataForm(AbstractFrameSvzMetadata, ABC):

    def __init__(self, viewmodel: ViewModel, resource_manager: ResourceManager) -> None:
        self._viewmodel = viewmodel
        self._resource_manager = resource_manager
        self._directions = self._viewmodel.get_directions_of_stationing()
        self._counting_day_types = self._viewmodel.get_counting_day_types()
        self._weather_types = self._viewmodel.get_weather_types()
        self.introduce_to_viewmodel()

        self._tk_number: FormFieldText = FormFieldText(
            label_text=self._resource_manager.get(SvzMetadataKeys.LABEL_TK_NUMBER),
            on_value_change=self._update_metadata,
            marker=MARKER_TK_NUMBER,
        )
        self._counting_location_number = FormFieldText(
            label_text=self._resource_manager.get(
                SvzMetadataKeys.LABEL_COUNTING_LOCATION_NUMBER
            ),
            on_value_change=self._update_metadata,
            marker=MARKER_COUNTING_LOCATION_NUMBER,
        )
        self._direction_select = FormFieldSelect(
            label_text=self._resource_manager.get(
                SvzMetadataKeys.LABEL_COUNTING_SELECTION
            ),
            options=self._directions.names,
            on_value_change=self._update_metadata,
            marker=MARKER_DIRECTION_SELECT,
        )
        self._direction_description = FormFieldText(
            label_text=self._resource_manager.get(
                SvzMetadataKeys.LABEL_DIRECTION_DESCRIPTION
            ),
            on_value_change=self._update_metadata,
            marker=MARKER_DIRECTION_DESCRIPTION,
        )
        self._has_bicycle_lane = FormFieldCheckbox(
            label_text=self._resource_manager.get(
                SvzMetadataKeys.LABEL_HAS_BICYCLE_LANE
            ),
            on_value_change=self._update_metadata,
            marker=MARKER_HAS_BICYCLE_LANE,
        )
        self._is_bicycle_counting = FormFieldCheckbox(
            label_text=self._resource_manager.get(
                SvzMetadataKeys.LABEL_IS_BICYCLE_COUNTING
            ),
            on_value_change=self._update_metadata,
            marker=MARKER_IS_BICYCLE_COUNTING,
        )
        self._counting_day_select = FormFieldSelect(
            label_text=self._resource_manager.get(
                SvzMetadataKeys.LABEL_COUNTING_DAY_SELECT
            ),
            options=self._counting_day_types.names,
            on_value_change=self._update_metadata,
            marker=MARKER_COUNTING_DAY_SELECT,
        )
        self._weather_type_select = FormFieldSelect(
            label_text=self._resource_manager.get(SvzMetadataKeys.LABEL_WEATHER),
            options=self._weather_types.names,
            on_value_change=self._update_metadata,
            marker=MARKER_WEATHER_TYPE_SELECT,
        )
        self._remark = FormFieldText(
            label_text=self._resource_manager.get(SvzMetadataKeys.LABEL_REMARK),
            on_value_change=self._update_metadata,
            marker=MARKER_REMARK,
        )
        self._coordinate_x = FormFieldText(
            label_text=self._resource_manager.get(SvzMetadataKeys.LABEL_X_COORDINATE),
            on_value_change=self._update_metadata,
            marker=MARKER_COORDINATE_X,
        )
        self._coordinate_y = FormFieldText(
            label_text=self._resource_manager.get(SvzMetadataKeys.LABEL_Y_COORDINATE),
            on_value_change=self._update_metadata,
            marker=MARKER_COORDINATE_Y,
        )

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_svz_metadata_frame(self)

    def update(self, metadata: dict) -> None:
        if metadata:
            if TK_NUMBER in metadata and self._tk_number and self._tk_number._instance:
                self._tk_number.set_value(metadata[TK_NUMBER])
            if (
                COUNTING_LOCATION_NUMBER in metadata
                and self._counting_location_number
                and self._counting_location_number._instance
            ):
                self._counting_location_number.set_value(
                    metadata[COUNTING_LOCATION_NUMBER]
                )
            if (
                DIRECTION in metadata
                and self._direction_select
                and self._direction_select._instance
            ):
                self._direction_select.set_value(metadata[DIRECTION])
            if (
                DIRECTION_DESCRIPTION in metadata
                and self._direction_description
                and self._direction_description._instance
            ):
                self._direction_description.set_value(metadata[DIRECTION_DESCRIPTION])
            if (
                HAS_BICYCLE_LANE in metadata
                and self._has_bicycle_lane
                and self._has_bicycle_lane._instance
            ):
                self._has_bicycle_lane.set_value(metadata[HAS_BICYCLE_LANE])
            if (
                IS_BICYCLE_COUNTING in metadata
                and self._is_bicycle_counting
                and self._is_bicycle_counting._instance
            ):
                self._is_bicycle_counting.set_value(metadata[IS_BICYCLE_COUNTING])
            if (
                COUNTING_DAY in metadata
                and self._counting_day_select
                and self._counting_day_select._instance
            ):
                self._counting_day_select.set_value(metadata[COUNTING_DAY])
            if (
                WEATHER in metadata
                and self._weather_type_select
                and self._weather_type_select._instance
            ):
                self._weather_type_select.set_value(metadata[WEATHER])
            if REMARK in metadata and self._remark and self._remark._instance:
                self._remark.set_value(metadata[REMARK])
            if (
                COORDINATE_X in metadata
                and self._coordinate_x
                and self._coordinate_x._instance
            ):
                self._coordinate_x.set_value(metadata[COORDINATE_X])
            if (
                COORDINATE_Y in metadata
                and self._coordinate_y
                and self._coordinate_y._instance
            ):
                self._coordinate_y.set_value(metadata[COORDINATE_Y])

    def build(self) -> Self:
        self._tk_number.build()
        self._counting_location_number.build()
        self._direction_select.build()
        self._direction_description.build()
        self._has_bicycle_lane.build()
        self._is_bicycle_counting.build()
        self._counting_day_select.build()
        self._weather_type_select.build()
        self._remark.build()
        ui.label(self._resource_manager.get(SvzMetadataKeys.LABEL_COORDINATES))
        self._coordinate_x.build()
        self._coordinate_y.build()

        return self

    def _build_metadata(self) -> dict:
        return {
            TK_NUMBER: self._tk_number.value if self._tk_number else None,
            COUNTING_LOCATION_NUMBER: (
                self._counting_location_number.value
                if self._counting_location_number
                else None
            ),
            DIRECTION: (
                self._directions.get_id_for(self._direction_select.value)
                if self._direction_select
                else None
            ),
            DIRECTION_DESCRIPTION: (
                self._direction_description.value
                if self._direction_description
                else None
            ),
            HAS_BICYCLE_LANE: (
                self._has_bicycle_lane.value if self._has_bicycle_lane else None
            ),
            IS_BICYCLE_COUNTING: (
                self._is_bicycle_counting.value if self._is_bicycle_counting else None
            ),
            COUNTING_DAY: (
                self._counting_day_types.get_id_for(self._counting_day_select.value)
                if self._counting_day_select
                else None
            ),
            WEATHER: (
                self._weather_types.get_id_for(self._weather_type_select.value)
                if self._weather_type_select
                else None
            ),
            REMARK: self._remark.value if self._remark else None,
            COORDINATE_X: self._coordinate_x.value if self._coordinate_x else None,
            COORDINATE_Y: self._coordinate_y.value if self._coordinate_y else None,
        }

    def _update_metadata(self, event: ValueChangeEventArguments) -> None:
        self._viewmodel.update_svz_metadata(self._build_metadata())

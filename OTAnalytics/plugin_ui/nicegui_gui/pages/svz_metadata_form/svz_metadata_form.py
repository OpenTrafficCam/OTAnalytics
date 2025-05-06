from abc import ABC
from typing import Self

from nicegui import ui

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


class SVZMetadataForm(AbstractFrameSvzMetadata, ABC):

    def __init__(self, viewmodel: ViewModel, resource_manager: ResourceManager) -> None:
        self._viewmodel = viewmodel
        self._resource_manager = resource_manager
        self._directions = self._viewmodel.get_directions_of_stationing()
        self._counting_day_types = self._viewmodel.get_counting_day_types()
        self._weather_types = self._viewmodel.get_weather_types()
        self.introduce_to_viewmodel()

        self._tk_number: ui.input | None = None
        self._counting_location_number: ui.input | None = None
        self._direction_select: ui.select | None = None
        self._direction_description: ui.input | None = None
        self._has_bicycle_lane: ui.checkbox | None = None
        self._is_bicycle_counting: ui.checkbox | None = None
        self._counting_day_select: ui.select | None = None
        self._weather_type_select: ui.select | None = None
        self._remark: ui.input | None = None
        self._coordinate_x: ui.input | None = None
        self._coordinate_y: ui.input | None = None

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_svz_metadata_frame(self)

    def update(self, metadata: dict) -> None:
        if metadata:
            if TK_NUMBER in metadata and self._tk_number:
                self._tk_number.value = metadata[TK_NUMBER]
            if COUNTING_LOCATION_NUMBER in metadata and self._counting_location_number:
                self._counting_location_number.value = metadata[
                    COUNTING_LOCATION_NUMBER
                ]
            if DIRECTION in metadata and self._direction_select:
                self._direction_select.value = metadata[DIRECTION]
            if DIRECTION_DESCRIPTION in metadata and self._direction_description:
                self._direction_description.value = metadata[DIRECTION_DESCRIPTION]
            if HAS_BICYCLE_LANE in metadata and self._has_bicycle_lane:
                self._has_bicycle_lane.value = metadata[HAS_BICYCLE_LANE]
            if IS_BICYCLE_COUNTING in metadata and self._is_bicycle_counting:
                self._is_bicycle_counting.value = metadata[IS_BICYCLE_COUNTING]
            if COUNTING_DAY in metadata and self._counting_day_select:
                self._counting_day_select.value = metadata[COUNTING_DAY]
            if WEATHER in metadata and self._weather_type_select:
                self._weather_type_select.value = metadata[WEATHER]
            if REMARK in metadata and self._remark:
                self._remark.value = metadata[REMARK]
            if COORDINATE_X in metadata and self._coordinate_x:
                self._coordinate_x.value = metadata[COORDINATE_X]
            if COORDINATE_Y in metadata and self._coordinate_y:
                self._coordinate_y.value = metadata[COORDINATE_Y]

    def build(self) -> Self:
        self._tk_number = ui.input(
            label=self._resource_manager.get(SvzMetadataKeys.LABEL_TK_NUMBER),
            on_change=self._update_metadata,
        )
        self._counting_location_number = ui.input(
            label=self._resource_manager.get(
                SvzMetadataKeys.LABEL_COUNTING_LOCATION_NUMBER
            ),
            on_change=self._update_metadata,
        )
        self._direction_select = ui.select(self._directions.names)
        self._direction_description = ui.input(
            label=self._resource_manager.get(
                SvzMetadataKeys.LABEL_DIRECTION_DESCRIPTION
            ),
            on_change=self._update_metadata,
        )
        self._has_bicycle_lane = ui.checkbox(
            self._resource_manager.get(SvzMetadataKeys.LABEL_HAS_BICYCLE_LANE),
            on_change=self._update_metadata,
        )
        self._is_bicycle_counting = ui.checkbox(
            self._resource_manager.get(SvzMetadataKeys.LABEL_IS_BICYCLE_COUNTING),
            on_change=self._update_metadata,
        )
        self._counting_day_select = ui.select(self._counting_day_types.names)
        self._weather_type_select = ui.select(self._weather_types.names)
        self._remark = ui.input(
            label=self._resource_manager.get(SvzMetadataKeys.LABEL_REMARK),
            on_change=self._update_metadata,
        )
        ui.label("Geeokoordinate")
        self._coordinate_x = ui.input(
            label=self._resource_manager.get(SvzMetadataKeys.LABEL_X_COORDINATE),
            on_change=self._update_metadata,
        )
        self._coordinate_y = ui.input(
            label=self._resource_manager.get(SvzMetadataKeys.LABEL_Y_COORDINATE),
            on_change=self._update_metadata,
        )

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

    def _update_metadata(self) -> None:
        self._viewmodel.update_svz_metadata(self._build_metadata())

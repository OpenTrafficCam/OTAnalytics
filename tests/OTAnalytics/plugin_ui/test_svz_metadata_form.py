from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

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
from OTAnalytics.plugin_ui.nicegui_gui.pages.svz_metadata_form.svz_metadata_form import (  # noqa
    MARKER_COORDINATE_X,
    MARKER_COORDINATE_Y,
    MARKER_COUNTING_LOCATION_NUMBER,
    MARKER_DIRECTION_DESCRIPTION,
    MARKER_HAS_BICYCLE_LANE,
    MARKER_IS_BICYCLE_COUNTING,
    MARKER_REMARK,
    MARKER_TK_NUMBER,
    SvzMetadataForm,
)

# Constants for testing
TK_NUMBER_VALUE = "TK123"
COUNTING_LOCATION_NUMBER_VALUE = "CL456"
DIRECTION_VALUE = "North"
DIRECTION_DESCRIPTION_VALUE = "Northbound"
REMARK_VALUE = "Test remark"
COORDINATE_X_VALUE = "123.45"
COORDINATE_Y_VALUE = "678.90"
TEST_NAME_INPUT = "NewTK456"
ENDPOINT_NAME = "/test-svz-metadata"


class MockDirections:
    def __init__(self) -> None:
        self.names = ["North", "South", "East", "West"]

    def get_id_for(self, name: str) -> str | None:
        return f"dir-{name}" if name else None

    def get_name_for(self, id_: Any) -> int:
        return id_[4:] if id_ and id_.startswith("dir-") else id_


class MockCountingDayTypes:
    def __init__(self) -> None:
        self.names = ["Weekday", "Weekend", "Holiday"]

    def get_id_for(self, name: str) -> str | None:
        return f"day-{name}" if name else None

    def get_name_for(self, id_: Any) -> int:
        return id_[4:] if id_ and id_.startswith("day-") else id_


class MockWeatherTypes:
    def __init__(self) -> None:
        self.names = ["Sunny", "Rainy", "Cloudy", "Snowy"]

    def get_id_for(self, name: str) -> str | None:
        return f"weather-{name}" if name else None

    def get_name_for(self, id_: Any) -> int:
        return id_[8:] if id_ and id_.startswith("weather-") else id_


@pytest.fixture
def viewmodel() -> Mock:

    # Create the main viewmodel mock
    viewmodel = MagicMock(spec=ViewModel)

    # Create a separate mock for the update_svz_metadata method
    update_mock = Mock()

    # Assign the mock to the viewmodel
    viewmodel.update_svz_metadata = update_mock

    # Set up other return values
    viewmodel.get_directions_of_stationing.return_value = MockDirections()
    viewmodel.get_counting_day_types.return_value = MockCountingDayTypes()
    viewmodel.get_weather_types.return_value = MockWeatherTypes()

    return viewmodel


@pytest.fixture
def svz_metadata_form(
    viewmodel: ViewModel, resource_manager: ResourceManager
) -> SvzMetadataForm:
    return SvzMetadataForm(viewmodel, resource_manager)


class TestSvzMetadataForm:

    @pytest.mark.asyncio
    async def test_form_build_up(
        self,
        user: User,
        svz_metadata_form: SvzMetadataForm,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that the form builds correctly and displays all fields."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            svz_metadata_form.build()

        await user.open(ENDPOINT_NAME)

        # Check that all form elements are visible
        await user.should_see(marker=MARKER_TK_NUMBER)
        await user.should_see(marker=MARKER_COUNTING_LOCATION_NUMBER)
        await user.should_see(marker=MARKER_DIRECTION_DESCRIPTION)
        await user.should_see(marker=MARKER_HAS_BICYCLE_LANE)
        await user.should_see(marker=MARKER_IS_BICYCLE_COUNTING)
        await user.should_see(marker=MARKER_REMARK)
        await user.should_see(resource_manager.get(SvzMetadataKeys.LABEL_COORDINATES))
        await user.should_see(marker=MARKER_COORDINATE_X)
        await user.should_see(marker=MARKER_COORDINATE_Y)

    @pytest.mark.asyncio
    async def test_input_field_updates_viewmodel(
        self, user: User, svz_metadata_form: SvzMetadataForm, viewmodel: Mock
    ) -> None:
        """Test that entering text in an input field updates the viewmodel."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            svz_metadata_form.build()

        await user.open(ENDPOINT_NAME)

        # Enter text in the TK Number field
        user.find(marker=MARKER_TK_NUMBER).type(TK_NUMBER_VALUE)

        # Verify that the viewmodel was updated
        viewmodel.update_svz_metadata.assert_called_once()
        metadata = viewmodel.update_svz_metadata.call_args[0][0]
        assert metadata[TK_NUMBER] == TK_NUMBER_VALUE

    @pytest.mark.asyncio
    async def test_checkbox_updates_viewmodel(
        self, user: User, svz_metadata_form: SvzMetadataForm, viewmodel: Mock
    ) -> None:
        """Test that checking a checkbox updates the viewmodel."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            svz_metadata_form.build()

        await user.open(ENDPOINT_NAME)

        # Check the Has Bicycle Lane checkbox
        user.find(marker=MARKER_HAS_BICYCLE_LANE).click()

        # Verify that the viewmodel was updated
        viewmodel.update_svz_metadata.assert_called()
        metadata = viewmodel.update_svz_metadata.call_args[0][0]
        assert metadata[HAS_BICYCLE_LANE] is True

    @pytest.mark.asyncio
    async def test_update_from_metadata(
        self, user: User, svz_metadata_form: SvzMetadataForm, viewmodel: Mock
    ) -> None:
        """Test that the form updates correctly when metadata is provided."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            svz_metadata_form.build()

        await user.open(ENDPOINT_NAME)

        # Create test metadata
        metadata = {
            TK_NUMBER: TK_NUMBER_VALUE,
            COUNTING_LOCATION_NUMBER: COUNTING_LOCATION_NUMBER_VALUE,
            DIRECTION: f"dir-{DIRECTION_VALUE}",
            DIRECTION_DESCRIPTION: DIRECTION_DESCRIPTION_VALUE,
            HAS_BICYCLE_LANE: True,
            IS_BICYCLE_COUNTING: False,
            COUNTING_DAY: "day-Weekday",
            WEATHER: "weather-Sunny",
            REMARK: REMARK_VALUE,
            COORDINATE_X: COORDINATE_X_VALUE,
            COORDINATE_Y: COORDINATE_Y_VALUE,
        }

        # Update the form with metadata
        svz_metadata_form.update(metadata)

        # Verify that the form fields are updated - with null checks
        if svz_metadata_form._tk_number:
            assert svz_metadata_form._tk_number.value == TK_NUMBER_VALUE
        if svz_metadata_form._counting_location_number:
            assert (
                svz_metadata_form._counting_location_number.value
                == COUNTING_LOCATION_NUMBER_VALUE
            )
        if svz_metadata_form._direction_description:
            assert (
                svz_metadata_form._direction_description.value
                == DIRECTION_DESCRIPTION_VALUE
            )
        if svz_metadata_form._has_bicycle_lane:
            assert svz_metadata_form._has_bicycle_lane.value is True
        if svz_metadata_form._is_bicycle_counting:
            assert svz_metadata_form._is_bicycle_counting.value is False
        if svz_metadata_form._remark:
            assert svz_metadata_form._remark.value == REMARK_VALUE
        if svz_metadata_form._coordinate_x:
            assert svz_metadata_form._coordinate_x.value == COORDINATE_X_VALUE
        if svz_metadata_form._coordinate_y:
            assert svz_metadata_form._coordinate_y.value == COORDINATE_Y_VALUE

        # Now change a field and verify the viewmodel is updated
        user.find(marker=MARKER_TK_NUMBER).clear()
        user.find(marker=MARKER_TK_NUMBER).type(TEST_NAME_INPUT)

        # Verify that the viewmodel was updated with the new value
        viewmodel.update_svz_metadata.assert_called()
        updated_metadata = viewmodel.update_svz_metadata.call_args[0][0]
        assert updated_metadata[TK_NUMBER] == TEST_NAME_INPUT
        # Other values should remain the same
        assert (
            updated_metadata[COUNTING_LOCATION_NUMBER] == COUNTING_LOCATION_NUMBER_VALUE
        )

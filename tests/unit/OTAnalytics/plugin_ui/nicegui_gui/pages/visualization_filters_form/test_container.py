"""Tests the form before its page has been built.

The form introduces itself to the view model in `__init__`
(`_introduce_to_viewmodel`), so the view model can call it from the moment it
exists. `build()` runs much later, when a browser asks for the page. Anything
the application does in between -- preloading a `--config` file while the
webserver is still being constructed, for one -- reaches a form whose widgets
do not exist yet.

#Requirement https://openproject.platomo.de/wp/10325
"""

from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from OTAnalytics.adapter_ui.dto import DateRangeDto
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters_form.container import (  # noqa
    VisualizationFiltersForm,
)

A_RANGE: DateRangeDto = {"start_date": "2023-05-24", "end_date": "2023-05-25"}
NO_RANGE: DateRangeDto = {"start_date": "", "end_date": ""}


@dataclass
class Given:
    resource_manager: Mock
    view_model: Mock


def create_given() -> Given:
    resource_manager = Mock()
    resource_manager.get.return_value = "label"
    view_model = Mock()
    view_model.get_skip_seconds.return_value = 1
    view_model.get_skip_frames.return_value = 1
    return Given(resource_manager=resource_manager, view_model=view_model)


def create_target(given: Given) -> VisualizationFiltersForm:
    """The form as the application first has it: constructed, not yet built."""
    return VisualizationFiltersForm(given.resource_manager, given.view_model)


class TestBeforeThePageIsBuilt:
    def test_introduces_itself_to_the_view_model(self) -> None:
        """
        #Requirement https://openproject.platomo.de/wp/10325
        """
        given = create_given()

        target = create_target(given)

        given.view_model.set_filter_frame.assert_called_once_with(target)

    @pytest.mark.parametrize(
        "call",
        [
            lambda form: form.update_date_range(A_RANGE),
            lambda form: form.update_date_range(NO_RANGE),
            lambda form: form.enable_filter_by_date_button(),
            lambda form: form.disable_filter_by_date_button(),
            lambda form: form.enable_filter_by_class_button(),
            lambda form: form.disable_filter_by_class_button(),
            lambda form: form.set_active_color_on_filter_by_date_button(),
            lambda form: form.set_inactive_color_on_filter_by_date_button(),
            lambda form: form.set_active_color_on_filter_by_class_button(),
            lambda form: form.set_inactive_color_on_filter_by_class_button(),
        ],
    )
    def test_the_view_model_can_call_it_without_raising(self, call) -> None:  # type: ignore[no-untyped-def] # noqa: E501
        """Each of these reaches a widget that only `build()` creates. Before
        this fix, `update_date_range` raised `AttributeError` and took the whole
        startup with it.

        #Requirement https://openproject.platomo.de/wp/10325

        @bug by randy-seng
        """
        target = create_target(create_given())

        call(target)

    def test_offers_no_general_buttons_yet(self) -> None:
        """
        #Requirement https://openproject.platomo.de/wp/10325
        """
        target = create_target(create_given())

        assert target.get_general_buttons() == []

"""Tests the form before its page has been built.

#Requirement https://openproject.platomo.de/wp/10325
"""

from dataclasses import dataclass
from unittest.mock import Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.dto import DateRangeDto
from OTAnalytics.application.resources.resource_manager import GeneralKeys
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters_form.container import (  # noqa
    VisualizationFiltersForm,
)

APPLY = "Apply from resources"
RESET = "Reset from resources"
LABELS = {GeneralKeys.LABEL_APPLY: APPLY, GeneralKeys.LABEL_RESET: RESET}

A_RANGE: DateRangeDto = {"start_date": "2023-05-24", "end_date": "2023-05-25"}
NO_RANGE: DateRangeDto = {"start_date": "", "end_date": ""}


@dataclass
class Given:
    resource_manager: Mock
    view_model: Mock


def create_given() -> Given:
    resource_manager = Mock()
    resource_manager.get.side_effect = lambda key: LABELS.get(key, "label")
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


BICYCLE = "bicycle"
CAR = "car"
TRUCK = "truck"
ALL_CLASSES = [BICYCLE, CAR, TRUCK]


async def open_classification_dialog(
    user: User, given: Given, selection: list[str] | None
) -> None:
    given.view_model.get_classes.return_value = ALL_CLASSES
    given.view_model.get_class_filter_selection.return_value = selection
    target = create_target(given)

    @ui.page("/test")
    def page() -> None:
        target.open_classification_dialog()

    await user.open("/test")
    await user.should_see(APPLY)


def checked_classes(user: User) -> list[str]:
    return sorted(
        checkbox.text
        for checkbox in user.find(kind=ui.checkbox).elements
        if checkbox.value
    )


class TestClassificationDialog:
    async def test_toggling_a_checkbox_changes_only_its_own_class(
        self, user: User
    ) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=None)

        user.find(kind=ui.checkbox, content=BICYCLE).click()
        assert checked_classes(user) == [CAR, TRUCK]
        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_class.assert_called_once_with(
            [CAR, TRUCK]
        )

    async def test_checking_an_unselected_class_adds_only_that_class(
        self, user: User
    ) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=[CAR])

        user.find(kind=ui.checkbox, content=TRUCK).click()
        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_class.assert_called_once_with(
            [CAR, TRUCK]
        )

    async def test_applying_unchanged_partial_selection_keeps_it(
        self, user: User
    ) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=[CAR, TRUCK])

        assert checked_classes(user) == [CAR, TRUCK]
        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_class.assert_called_once_with(
            [CAR, TRUCK]
        )

    async def test_without_selection_all_classes_are_selected(self, user: User) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=None)

        assert checked_classes(user) == ALL_CLASSES
        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_class.assert_called_once_with(
            ALL_CLASSES
        )

    async def test_empty_selection_selects_no_class(self, user: User) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=[])

        assert checked_classes(user) == []
        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_class.assert_called_once_with([])

    async def test_apply_closes_the_dialog(self, user: User) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=None)

        user.find(APPLY).click()

        dialog = user.find(kind=ui.dialog).elements.pop()
        assert dialog.value is False

    async def test_shows_reset_label_from_resources(self, user: User) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=None)

        await user.should_see(RESET)

    async def test_reset_resets_the_class_filter_and_closes_the_dialog(
        self, user: User
    ) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=[CAR])

        user.find(RESET).click()

        given.view_model.reset_filter_tracks_by_class.assert_called_once_with()
        given.view_model.apply_filter_tracks_by_class.assert_not_called()
        dialog = user.find(kind=ui.dialog).elements.pop()
        assert dialog.value is False

"""Tests the form before its page has been built.

#Requirement https://openproject.platomo.de/wp/10325
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.default_values import SUPPORTED_FORMATS
from OTAnalytics.adapter_ui.dto import DateRangeDto
from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    VisualizationFiltersKeys,
)
from OTAnalytics.domain.date import (
    DateRange,
    validate_date,
    validate_hour,
    validate_minute,
    validate_second,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.theme.global_theme import (
    VALID_FIELD_CLASS,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters_form.container import (  # noqa
    MARKER_FILTER_END_DATE_INPUT,
    MARKER_FILTER_END_TIME_INPUT,
    MARKER_FILTER_START_DATE_INPUT,
    MARKER_FILTER_START_TIME_INPUT,
    VisualizationFiltersForm,
)

APPLY = "Apply from resources"
RESET = "Reset from resources"
TITLE = "Filter tracks by date"
CHOOSE = "Choose date range"
FROM = "From"
TO = "To"
FIRST = "First detection occurrence"
LAST = "Last detection occurrence"
INVALID = "datetime is not valid."
INVALID_DATE = "Date must be of format: 'yyyy-mm-dd'"
INVALID_HOUR = "Hour must be a digit in range [0,23]"
INVALID_MINUTE = "Minute must be a digit in range [0,59]"
INVALID_SECOND = "Second must be a digit in range [0,59]"
START_NOT_BEFORE_END = "Start must be before end."
LABELS = {
    GeneralKeys.LABEL_APPLY: APPLY,
    GeneralKeys.LABEL_RESET: RESET,
    VisualizationFiltersKeys.LABEL_FILTER_BY_DATE_TITLE: TITLE,
    VisualizationFiltersKeys.LABEL_CHOOSE_DATE_RANGE: CHOOSE,
    VisualizationFiltersKeys.LABEL_DATE_RANGE_FROM: FROM,
    VisualizationFiltersKeys.LABEL_DATE_RANGE_TO: TO,
    VisualizationFiltersKeys.LABEL_FIRST_DETECTION_OCCURRENCE: FIRST,
    VisualizationFiltersKeys.LABEL_LAST_DETECTION_OCCURRENCE: LAST,
    VisualizationFiltersKeys.MESSAGE_INVALID_DATETIME: INVALID,
    VisualizationFiltersKeys.MESSAGE_INVALID_DATE_FORMAT: INVALID_DATE,
    VisualizationFiltersKeys.MESSAGE_INVALID_HOUR: INVALID_HOUR,
    VisualizationFiltersKeys.MESSAGE_INVALID_MINUTE: INVALID_MINUTE,
    VisualizationFiltersKeys.MESSAGE_INVALID_SECOND: INVALID_SECOND,
    VisualizationFiltersKeys.MESSAGE_START_NOT_BEFORE_END: START_NOT_BEFORE_END,
}

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
    view_model.validate_date.side_effect = lambda value: any(
        validate_date(value, date_format) for date_format in SUPPORTED_FORMATS
    )
    view_model.validate_hour.side_effect = lambda value: (
        value.isdigit() and (validate_hour(int(value)))
    )
    view_model.validate_minute.side_effect = lambda value: (
        value.isdigit() and (validate_minute(int(value)))
    )
    view_model.validate_second.side_effect = lambda value: (
        value.isdigit() and (validate_second(int(value)))
    )
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
            {CAR, TRUCK}
        )

    async def test_checking_an_unselected_class_adds_only_that_class(
        self, user: User
    ) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=[CAR])

        user.find(kind=ui.checkbox, content=TRUCK).click()
        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_class.assert_called_once_with(
            {CAR, TRUCK}
        )

    async def test_applying_unchanged_partial_selection_keeps_it(
        self, user: User
    ) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=[CAR, TRUCK])

        assert checked_classes(user) == [CAR, TRUCK]
        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_class.assert_called_once_with(
            {CAR, TRUCK}
        )

    async def test_without_selection_all_classes_are_selected(self, user: User) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=None)

        assert checked_classes(user) == ALL_CLASSES
        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_class.assert_called_once_with(
            set(ALL_CLASSES)
        )

    async def test_empty_selection_selects_no_class(self, user: User) -> None:
        given = create_given()
        await open_classification_dialog(user, given, selection=[])

        assert checked_classes(user) == []
        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_class.assert_called_once_with(set())

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


FIRST_OCCURRENCE = datetime(2023, 5, 24, 8, 0, 0, tzinfo=timezone.utc)
LAST_OCCURRENCE = datetime(2023, 5, 24, 9, 30, 15, tzinfo=timezone.utc)
FILTER_START = datetime(2023, 5, 24, 8, 15, 0, tzinfo=timezone.utc)
FILTER_END = datetime(2023, 5, 24, 8, 45, 30, tzinfo=timezone.utc)


async def open_date_dialog(
    user: User,
    given: Given,
    current: DateRange = DateRange(None, None),
    first: datetime | None = FIRST_OCCURRENCE,
    last: datetime | None = LAST_OCCURRENCE,
) -> None:
    given.view_model.get_first_detection_occurrence.return_value = first
    given.view_model.get_last_detection_occurrence.return_value = last
    given.view_model.get_filter_tracks_by_date_setting.return_value = current
    target = create_target(given)

    @ui.page("/test")
    def page() -> None:
        target.open_range_dialog()

    await user.open("/test")
    await user.should_see(APPLY)


def find_input(user: User, marker: str) -> ui.input:
    return user.find(kind=ui.input, marker=marker).elements.pop()


def input_value(user: User, marker: str) -> object:
    return find_input(user, marker).value


def set_input(user: User, marker: str, value: str) -> None:
    find_input(user, marker).value = value


def date_dialog_is_open(user: User) -> bool:
    return user.find(kind=ui.dialog).elements.pop().value


class TestDateRangeDialog:
    """The dialog matches FilterTracksByDatePopup of the customtkinter GUI."""

    async def test_shows_title_and_instruction(self, user: User) -> None:
        await open_date_dialog(user, create_given())

        await user.should_see(TITLE)
        await user.should_see(CHOOSE)
        await user.should_see(FROM)
        await user.should_see(TO)

    async def test_shows_first_and_last_detection_occurrence(self, user: User) -> None:
        await open_date_dialog(user, create_given())

        await user.should_see(f"{FIRST}: 2023-05-24 08:00:00")
        await user.should_see(f"{LAST}: 2023-05-24 09:30:15")

    async def test_shows_occurrence_labels_without_detections(self, user: User) -> None:
        await open_date_dialog(user, create_given(), first=None, last=None)

        await user.should_see(f"{FIRST}:")
        await user.should_see(f"{LAST}:")

    async def test_presets_the_current_filter(self, user: User) -> None:
        await open_date_dialog(
            user, create_given(), current=DateRange(FILTER_START, FILTER_END)
        )

        assert input_value(user, MARKER_FILTER_START_DATE_INPUT) == FILTER_START.date()
        assert input_value(user, MARKER_FILTER_START_TIME_INPUT) == FILTER_START.time()
        assert input_value(user, MARKER_FILTER_END_DATE_INPUT) == FILTER_END.date()
        assert input_value(user, MARKER_FILTER_END_TIME_INPUT) == FILTER_END.time()

    async def test_presets_detection_occurrences_without_filter(
        self, user: User
    ) -> None:
        await open_date_dialog(user, create_given())

        assert (
            input_value(user, MARKER_FILTER_START_TIME_INPUT) == FIRST_OCCURRENCE.time()
        )
        assert input_value(user, MARKER_FILTER_END_TIME_INPUT) == LAST_OCCURRENCE.time()

    async def test_apply_applies_the_entered_range_and_closes(self, user: User) -> None:
        given = create_given()
        await open_date_dialog(user, given, current=DateRange(FILTER_START, FILTER_END))

        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_date.assert_called_once_with(
            DateRange(FILTER_START, FILTER_END)
        )
        assert not date_dialog_is_open(user)

    async def test_empty_fields_apply_an_open_range(self, user: User) -> None:
        given = create_given()
        await open_date_dialog(user, given, first=None, last=None)

        user.find(APPLY).click()

        given.view_model.apply_filter_tracks_by_date.assert_called_once_with(
            DateRange(None, None)
        )

    async def test_incomplete_start_is_rejected(self, user: User) -> None:
        given = create_given()
        await open_date_dialog(user, given)

        set_input(user, MARKER_FILTER_START_TIME_INPUT, "")
        user.find(APPLY).click()

        await user.should_see(f"{FROM} {INVALID}")
        given.view_model.apply_filter_tracks_by_date.assert_not_called()
        assert date_dialog_is_open(user)

    async def test_unparsable_end_is_rejected(self, user: User) -> None:
        given = create_given()
        await open_date_dialog(user, given)

        set_input(user, MARKER_FILTER_END_DATE_INPUT, "2023-13-45")
        user.find(APPLY).click()

        await user.should_see(f"{TO} {INVALID}")
        given.view_model.apply_filter_tracks_by_date.assert_not_called()

    @pytest.mark.parametrize(
        "end_date, end_time",
        [
            ("2023-05-24", "08:00:00"),
            ("2023-05-24", "07:59:59"),
            ("2023-05-23", "09:00:00"),
        ],
    )
    async def test_start_not_before_end_is_rejected(
        self, user: User, end_date: str, end_time: str
    ) -> None:
        given = create_given()
        await open_date_dialog(user, given)

        set_input(user, MARKER_FILTER_END_DATE_INPUT, end_date)
        set_input(user, MARKER_FILTER_END_TIME_INPUT, end_time)
        user.find(APPLY).click()

        await user.should_see(START_NOT_BEFORE_END)
        given.view_model.apply_filter_tracks_by_date.assert_not_called()
        assert date_dialog_is_open(user)

    async def test_reset_resets_the_date_filter_and_closes(self, user: User) -> None:
        given = create_given()
        await open_date_dialog(user, given)

        user.find(RESET).click()

        given.view_model.reset_filter_tracks_by_date.assert_called_once_with()
        given.view_model.apply_filter_tracks_by_date.assert_not_called()
        assert not date_dialog_is_open(user)


def is_marked_valid(user: User, marker: str) -> bool:
    return VALID_FIELD_CLASS in find_input(user, marker).classes


def error_of(user: User, marker: str) -> str | None:
    return find_input(user, marker).error


class TestDateRangeDialogValidatesWhileTyping:
    """Fields are marked green or red as in DateRow of the customtkinter GUI."""

    async def test_preset_fields_are_unmarked(self, user: User) -> None:
        await open_date_dialog(user, create_given())

        for marker in [
            MARKER_FILTER_START_DATE_INPUT,
            MARKER_FILTER_START_TIME_INPUT,
            MARKER_FILTER_END_DATE_INPUT,
            MARKER_FILTER_END_TIME_INPUT,
        ]:
            assert not is_marked_valid(user, marker)
            assert error_of(user, marker) is None

    @pytest.mark.parametrize(
        "marker, value",
        [
            (MARKER_FILTER_START_DATE_INPUT, "2023-05-25"),
            (MARKER_FILTER_END_TIME_INPUT, "23:59:59"),
            (MARKER_FILTER_END_TIME_INPUT, "23:59"),
        ],
    )
    async def test_marks_valid_input_green(
        self, user: User, marker: str, value: str
    ) -> None:
        await open_date_dialog(user, create_given())

        set_input(user, marker, value)

        assert is_marked_valid(user, marker)
        assert error_of(user, marker) is None

    @pytest.mark.parametrize(
        "marker, value, message",
        [
            (MARKER_FILTER_START_DATE_INPUT, "2023-13-45", INVALID_DATE),
            (MARKER_FILTER_START_DATE_INPUT, "2023-05", INVALID_DATE),
            (MARKER_FILTER_START_TIME_INPUT, "24:00:00", INVALID_HOUR),
            (MARKER_FILTER_START_TIME_INPUT, "10:60:00", INVALID_MINUTE),
            (MARKER_FILTER_START_TIME_INPUT, "10:00:60", INVALID_SECOND),
            (MARKER_FILTER_START_TIME_INPUT, "10", INVALID_MINUTE),
            (MARKER_FILTER_START_TIME_INPUT, "10:30:", INVALID_SECOND),
        ],
    )
    async def test_marks_invalid_input_red_with_message(
        self, user: User, marker: str, value: str, message: str
    ) -> None:
        await open_date_dialog(user, create_given())

        set_input(user, marker, value)

        assert not is_marked_valid(user, marker)
        assert error_of(user, marker) == message

    async def test_correcting_input_turns_the_field_green(self, user: User) -> None:
        await open_date_dialog(user, create_given())

        set_input(user, MARKER_FILTER_START_TIME_INPUT, "24:00:00")
        set_input(user, MARKER_FILTER_START_TIME_INPUT, "23:00:00")

        assert is_marked_valid(user, MARKER_FILTER_START_TIME_INPUT)
        assert error_of(user, MARKER_FILTER_START_TIME_INPUT) is None

    async def test_emptied_field_is_unmarked(self, user: User) -> None:
        await open_date_dialog(user, create_given())

        set_input(user, MARKER_FILTER_END_DATE_INPUT, "2023-05-25")
        set_input(user, MARKER_FILTER_END_DATE_INPUT, "")

        assert not is_marked_valid(user, MARKER_FILTER_END_DATE_INPUT)
        assert error_of(user, MARKER_FILTER_END_DATE_INPUT) is None

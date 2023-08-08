import pytest

from OTAnalytics.application.exception import gather_exception_messages

VALUE_ERROR_MESSAGE: str = "I am a ValueError"
VALUE_ERROR: Exception = ValueError(VALUE_ERROR_MESSAGE)

TYPE_ERROR_MESSAGE: str = "I am a TypeError"
TYPE_ERROR: Exception = TypeError(TYPE_ERROR_MESSAGE)

KEY_ERROR_MESSAGE: str = "I am a KeyError"
KEY_ERROR: Exception = KeyError(KEY_ERROR_MESSAGE)

EXCEPTION_GROUP_MESSAGE_1: str = "I am ExceptionGroup 1"
EXCEPTION_GROUP_MESSAGE_2: str = "I am ExceptionGroup 2"
EXCEPTION_GROUP_MESSAGE_3: str = "I am ExceptionGroup 3"
EXCEPTION_GROUP_MESSAGE_4: str = "I am ExceptionGroup 4"

INITIAL_MESSAGES: list[str] = ["bla", "blubb"]

exception_group_of_one = ExceptionGroup(EXCEPTION_GROUP_MESSAGE_1, [VALUE_ERROR])
messages_group_of_one = [EXCEPTION_GROUP_MESSAGE_1, VALUE_ERROR_MESSAGE]

exception_group_of_two = ExceptionGroup(
    EXCEPTION_GROUP_MESSAGE_1, [VALUE_ERROR, TYPE_ERROR]
)
messages_group_of_two = [
    EXCEPTION_GROUP_MESSAGE_1,
    VALUE_ERROR_MESSAGE,
    TYPE_ERROR_MESSAGE,
]


exception_group_of_group_of_two = ExceptionGroup(
    EXCEPTION_GROUP_MESSAGE_1,
    [
        ExceptionGroup(EXCEPTION_GROUP_MESSAGE_2, [VALUE_ERROR, TYPE_ERROR]),
        KEY_ERROR,
    ],
)
messages_group_of_group_of_two = [
    EXCEPTION_GROUP_MESSAGE_1,
    EXCEPTION_GROUP_MESSAGE_2,
    VALUE_ERROR_MESSAGE,
    TYPE_ERROR_MESSAGE,
    KEY_ERROR_MESSAGE,
]

exception_group_of_group_of_group_of_three = ExceptionGroup(
    EXCEPTION_GROUP_MESSAGE_1,
    [
        ExceptionGroup(
            EXCEPTION_GROUP_MESSAGE_2,
            [
                VALUE_ERROR,
                ExceptionGroup(
                    EXCEPTION_GROUP_MESSAGE_3, [TYPE_ERROR, KEY_ERROR, KEY_ERROR]
                ),
            ],
        ),
        ExceptionGroup(EXCEPTION_GROUP_MESSAGE_4, [KEY_ERROR, VALUE_ERROR]),
    ],
)
messages_group_of_group_of_group_of_three = [
    EXCEPTION_GROUP_MESSAGE_1,
    EXCEPTION_GROUP_MESSAGE_2,
    VALUE_ERROR_MESSAGE,
    EXCEPTION_GROUP_MESSAGE_3,
    TYPE_ERROR_MESSAGE,
    KEY_ERROR_MESSAGE,
    KEY_ERROR_MESSAGE,
    EXCEPTION_GROUP_MESSAGE_4,
    KEY_ERROR_MESSAGE,
    VALUE_ERROR_MESSAGE,
]

exception_group_of_two = ExceptionGroup(
    EXCEPTION_GROUP_MESSAGE_1, [VALUE_ERROR, TYPE_ERROR]
)
messages_group_of_two = [
    EXCEPTION_GROUP_MESSAGE_1,
    VALUE_ERROR_MESSAGE,
    TYPE_ERROR_MESSAGE,
]


@pytest.mark.parametrize(
    "exception_group,expected_result",
    [
        (exception_group_of_one, messages_group_of_one),
        (exception_group_of_two, messages_group_of_two),
        (exception_group_of_group_of_two, messages_group_of_group_of_two),
        (
            exception_group_of_group_of_group_of_three,
            messages_group_of_group_of_group_of_three,
        ),
    ],
)
def test_pass_get_all_messages_from_exception_group(
    exception_group: BaseExceptionGroup,
    expected_result: list[str],
) -> None:
    actual_result = gather_exception_messages(exception_group)

    assert actual_result == expected_result

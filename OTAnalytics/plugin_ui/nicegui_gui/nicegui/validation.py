ERROR_MSG_REQUIRED = "Required"
ERROR_MESSAGE_NO_FILES = "Please include at least one file"
ERROR_MESSAGE_NUMBER_ONE_OR_LESS = "The number must be 1 or less"
ERROR_MSG_NUMBER_MUST_BE_POSITIVE = "The number must be positive"

VALIDATION_REQUIRED = {ERROR_MSG_REQUIRED: lambda value: value is not None}
VALIDATION_NUMBER_POSITIVE = VALIDATION_REQUIRED | {
    ERROR_MSG_NUMBER_MUST_BE_POSITIVE: lambda value: not value or value >= 0,
}
VALIDATION_NUMBER_ONE_OR_LESS = VALIDATION_REQUIRED | {
    ERROR_MESSAGE_NUMBER_ONE_OR_LESS: lambda value: not value or value <= 1,
}
VALIDATION_NUMBER_RANGE_0_1 = (
    VALIDATION_REQUIRED | VALIDATION_NUMBER_POSITIVE | VALIDATION_NUMBER_ONE_OR_LESS
)
VALIDATION_FILES = {
    ERROR_MESSAGE_NO_FILES: lambda value: value or len(value) > 0,
}

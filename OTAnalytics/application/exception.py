import re

MESSAGE_SUFFIX_PATTERN = re.compile(r" .((\d+)\s*sub-exception.*.)")


def gather_exception_messages(
    exception: BaseException | BaseExceptionGroup,
) -> list[str]:
    """Gathers all exception messages within an ExceptionGroup or a single
    BaseException.

    If a sub-exception is an ExceptionGroup itself, the list will also contain its
    message and the messages of its sub-exceptions and so on...

    Args:
        exception_group (BaseException | BaseExceptionGroup): The exception instance.

    Returns:
        list[str]: all exception messages of a single BaseException or ExceptionGroup
        and ExceptionGroups it contains.
    """
    messages = []

    if isinstance(exception, BaseExceptionGroup):
        messages.append(re.sub(MESSAGE_SUFFIX_PATTERN, "", str(exception)))
        for sub_exception in exception.exceptions:
            messages.extend(gather_exception_messages(sub_exception))
    else:
        messages.append(str(exception).replace("'", ""))

    return messages

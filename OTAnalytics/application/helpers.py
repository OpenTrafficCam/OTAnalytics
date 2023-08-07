import re


def get_all_messages_from_exception_group(
    exception_group: BaseExceptionGroup,
) -> list[str]:
    """Returns a list of messages of the ExceptionGroup itself and all of its
    sub-exceptions.

    If a sub-exception is an ExceptionGroup itself, the list will also contain its
    message and the messages of its sub-exceptions and so on...

    Args:
        exception_group (BaseExceptionGroup): The ExceptionGroup instance

    Returns:
        list[str]: List of all messages of the ExceptionGroup and all of the Exceptions
        and ExceptionGroups it contains
    """

    def _get_all_messages_from_exception_group(
        exception_group: BaseExceptionGroup,
    ) -> list[str]:
        messages = []

        PATTERN = re.compile(r" .((\d+)\s*sub-exception.*.)")
        if match := re.search(PATTERN, str(exception_group)):
            messages.append(str(exception_group).replace(match[0], ""))
        else:
            messages.append(str(exception_group))

        for sub_exception in exception_group.exceptions:
            if isinstance(sub_exception, BaseExceptionGroup):
                messages.extend(_get_all_messages_from_exception_group(sub_exception))
            else:
                message = str(sub_exception)
                message = re.sub("'", "", message)
                messages.append(message)
        return messages

    return _get_all_messages_from_exception_group(exception_group)

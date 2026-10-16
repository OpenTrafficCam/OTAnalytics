"""Tests for the defaults of the non-abstract `UiFactory` methods.

Other front-ends (e.g. OTCloud) implement `UiFactory`. New methods there are
not abstract, so these front-ends keep working; their defaults fall back to
`info_box` and keep the previous behaviour.
"""

from typing import Any
from unittest.mock import Mock

import pytest

from OTAnalytics.adapter_ui.info_box import InfoBox
from OTAnalytics.adapter_ui.message_type import MessageType
from OTAnalytics.adapter_ui.ui_factory import UiFactory

MESSAGE = "message"
POSITION = (1, 2)


def create_target(info_box: InfoBox) -> UiFactory:
    """A front-end that only implements the abstract methods of `UiFactory`."""
    abstract_methods: dict[str, Any] = {
        name: Mock() for name in UiFactory.__abstractmethods__
    }
    abstract_methods["info_box"] = Mock(return_value=info_box)
    factory_type = type("MinimalUiFactory", (UiFactory,), abstract_methods)
    return factory_type()


class TestUiFactoryDefaults:
    @pytest.mark.parametrize("message_type", list(MessageType))
    def test_show_message_falls_back_to_info_box(
        self, message_type: MessageType
    ) -> None:
        target = create_target(Mock(canceled=False))

        target.show_message(
            message=MESSAGE, initial_position=POSITION, message_type=message_type
        )

        target.info_box.assert_called_once_with(  # type: ignore[attr-defined]
            message=MESSAGE, initial_position=POSITION
        )

    @pytest.mark.parametrize("canceled, expected", [(False, True), (True, False)])
    async def test_ask_for_confirmation_falls_back_to_info_box(
        self, canceled: bool, expected: bool
    ) -> None:
        target = create_target(Mock(canceled=canceled))

        confirmed = await target.ask_for_confirmation(
            message=MESSAGE, initial_position=POSITION
        )

        assert confirmed is expected
        target.info_box.assert_called_once_with(  # type: ignore[attr-defined]
            message=MESSAGE, initial_position=POSITION
        )

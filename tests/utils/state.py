from typing import Any
from unittest.mock import Mock

from OTAnalytics.application.state import ObservableProperty


def observable(value: Any) -> Mock:
    observable_property = Mock(spec=ObservableProperty)
    observable_property.get.return_value = value
    return observable_property

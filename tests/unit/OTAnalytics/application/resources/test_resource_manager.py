import pytest

from OTAnalytics.application.resources.resource_manager import (
    ResourceKey,
    ResourceManager,
)


class TestKeys(ResourceKey):
    KEY = "key"
    KEY2 = "key2"


class TestResourceManager:
    @pytest.mark.parametrize(
        "key, expected_value",
        [(TestKeys.KEY, "value"), (TestKeys.KEY2, str(TestKeys.KEY2))],
    )
    def test_get_resource(self, key: ResourceKey, expected_value: str) -> None:
        resources: dict[ResourceKey, str] = {TestKeys.KEY: "value"}

        assert TestKeys.KEY2 not in resources
        assert ResourceManager(resources).get(key) == expected_value

import pytest

from OTAnalytics.application.resources.resource_manager import ResourceManager


@pytest.fixture
def resource_manager() -> ResourceManager:
    return ResourceManager()

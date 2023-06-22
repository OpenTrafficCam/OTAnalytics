from OTAnalytics.domain.observer import Registrable


class MockRegistrable(Registrable[int]):
    def __init__(self) -> None:
        super().__init__()


class TestRegistrable:
    def test_register(self) -> None:
        registrable = MockRegistrable()
        registrable.register(1)
        registrable.register(2)
        assert registrable._observers == [1, 2]
        registrable.register(1)
        assert registrable._observers == [1, 2]

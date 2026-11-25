from OTAnalytics.domain.remark import RemarkRepository


class TestRemarkRepository:
    def test_clear(self) -> None:
        repository = RemarkRepository()
        repository.add("remark of previous project")

        repository.clear()

        assert repository.get() == ""

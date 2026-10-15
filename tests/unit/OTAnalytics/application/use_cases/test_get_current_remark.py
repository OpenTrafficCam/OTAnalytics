from unittest.mock import Mock

from OTAnalytics.application.use_cases.get_current_remark import ClearRemark
from OTAnalytics.domain.remark import RemarkRepository


class TestClearRemark:
    def test_clear(self) -> None:
        remark_repository = Mock(spec=RemarkRepository)

        ClearRemark(remark_repository)()

        remark_repository.clear.assert_called_once()

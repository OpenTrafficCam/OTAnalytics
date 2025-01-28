from OTAnalytics.domain.remark import RemarkRepository


class AddNewRemark:
    def __init__(self, remark_repository: RemarkRepository):
        self.remark_repository = remark_repository

    def add(self, remark: str) -> None:
        self.remark_repository.add(remark)

from OTAnalytics.domain.remark import RemarkRepository


class GetCurrentRemark:
    def __init__(self, remark_repository: RemarkRepository):
        self.remark_repository = remark_repository

    def get(self) -> str:
        return self.remark_repository.get()

from dataclasses import dataclass
from datetime import datetime

NAME: str = "name"
START_DATE: str = "start_date"


@dataclass
class Project:
    name: str
    start_date: datetime

    def to_dict(self) -> dict:
        return {
            NAME: self.name,
            START_DATE: self.start_date.timestamp(),
        }

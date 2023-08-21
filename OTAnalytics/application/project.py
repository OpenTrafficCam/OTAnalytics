from dataclasses import dataclass
from datetime import datetime
from typing import Optional

NAME: str = "name"
START_DATE: str = "start_date"


class StartDateMissing(Exception):
    pass


@dataclass
class Project:
    name: str
    start_date: Optional[datetime]

    def to_dict(self) -> dict:
        if self.start_date:
            return {
                NAME: self.name,
                START_DATE: self.start_date.timestamp(),
            }
        raise StartDateMissing()

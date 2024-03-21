from dataclasses import dataclass
from datetime import datetime
from typing import Optional

NAME: str = "name"
START_DATE: str = "start_date"


@dataclass
class Project:
    name: str
    start_date: Optional[datetime]

    def to_dict(self) -> dict:
        return {
            NAME: self.name,
            START_DATE: self.start_date.timestamp() if self.start_date else None,
        }

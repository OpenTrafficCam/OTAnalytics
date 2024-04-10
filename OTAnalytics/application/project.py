from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

NAME: str = "name"
START_DATE: str = "start_date"
METADATA: str = "metadata"
TK_NUMBER: str = "tk_number"
COUNTING_LOCATION_NUMBER: str = "counting_location_number"
DIRECTION: str = "direction"
REMARK: str = "remark"
COORDINATE_X: str = "coordinate_x"
COORDINATE_Y: str = "coordinate_y"


class DirectionOfStationing(Enum):
    IN_DIRECTION = 1
    OPPOSITE_DIRECTION = 2


@dataclass
class Project:
    name: str
    start_date: Optional[datetime] = None
    metadata: Optional[dict] = field(default_factory=lambda: {})

    def to_dict(self) -> dict:
        return {
            NAME: self.name,
            START_DATE: self.start_date.timestamp() if self.start_date else None,
            METADATA: self.metadata if METADATA else None,
        }

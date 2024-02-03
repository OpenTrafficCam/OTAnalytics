from dataclasses import dataclass


@dataclass(frozen=True)
class SkipTime:
    seconds: int
    frames: int

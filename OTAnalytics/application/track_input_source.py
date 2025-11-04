from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator


class OttrkFileInputSource(ABC):
    """Interface representing an input source that emits ottrk files"""

    @abstractmethod
    def produce(self) -> Iterator[Path]:
        """Create an iterator over ottrk files.

        Returns:
            Iterator[Path]: the iterator over ottrk files.

        """
        raise NotImplementedError

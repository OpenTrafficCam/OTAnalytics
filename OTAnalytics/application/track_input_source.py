from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncIterator


class OttrkFileInputSource(ABC):
    """Interface representing an input source that emits ottrk files"""

    @abstractmethod
    def produce(self) -> AsyncIterator[Path]:
        """Create an async iterator over ottrk files.

        Returns:
            AsyncIterator[Path]: the async iterator over ottrk files.

        """
        raise NotImplementedError

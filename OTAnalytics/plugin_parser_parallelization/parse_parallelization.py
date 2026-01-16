"""Abstract base class for parser parallelization strategies."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable


class ParseParallelization(ABC):
    """Strategy for parallelizing file parsing/conversion.

    This interface defines a strategy pattern for parallelizing file conversion
    operations. Implementations can execute conversions sequentially or in parallel
    using multiprocessing.

    The strategy takes a callable that converts a single file and applies it to
    a list of files, returning the list of converted file paths.
    """

    @property
    @abstractmethod
    def num_processes(self) -> int:
        """Return the number of processes used for parallelization."""
        raise NotImplementedError

    @abstractmethod
    def set_num_processes(self, value: int) -> None:
        """Set the number of processes for parallelization.

        Args:
            value: Number of processes to use. Must be >= 1.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        convert_func: Callable[[Path], Path],
        files: list[Path],
    ) -> list[Path]:
        """Execute file conversion with parallelization strategy.

        Args:
            convert_func: Function that converts a single file and returns
                the path to the converted file.
            files: List of files to convert.

        Returns:
            List of converted file paths in the same order as input files.
        """
        raise NotImplementedError

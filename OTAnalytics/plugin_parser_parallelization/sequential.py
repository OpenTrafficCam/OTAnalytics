"""Sequential implementation of parser parallelization strategy."""

from pathlib import Path
from typing import Callable

from OTAnalytics.plugin_parser_parallelization.parse_parallelization import (
    ParseParallelization,
)


class SequentialParseParallelization(ParseParallelization):
    """Executes file conversion sequentially (default behavior).

    This implementation processes files one at a time in order.
    It serves as the default strategy when parallelization is not needed
    or when only a single process is requested.
    """

    @property
    def num_processes(self) -> int:
        """Return 1 since sequential processing uses a single process."""
        return 1

    def set_num_processes(self, value: int) -> None:
        """No-op for sequential implementation.

        Args:
            value: Ignored since sequential always uses 1 process.
        """
        pass

    def execute(
        self,
        convert_func: Callable[[Path], Path],
        files: list[Path],
    ) -> list[Path]:
        """Execute file conversion sequentially.

        Args:
            convert_func: Function that converts a single file.
            files: List of files to convert.

        Returns:
            List of converted file paths in the same order as input files.
        """
        return [convert_func(file) for file in files]

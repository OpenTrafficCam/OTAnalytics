"""Multiprocessing implementation of parser parallelization strategy."""

import multiprocessing
from pathlib import Path
from typing import Callable

from OTAnalytics.application.config import DEFAULT_NUM_PARSE_PROCESSES
from OTAnalytics.application.logger import logger
from OTAnalytics.plugin_parser_parallelization.parse_parallelization import (
    ParseParallelization,
)


class MultiprocessingParseParallelization(ParseParallelization):
    """Executes file conversion in parallel using multiprocessing.

    This implementation uses Python's multiprocessing.Pool to process files
    in parallel. It falls back to sequential processing when num_processes
    is 1 or when there's only a single file to process.
    """

    def __init__(self, num_processes: int = DEFAULT_NUM_PARSE_PROCESSES) -> None:
        """Initialize the multiprocessing strategy.

        Args:
            num_processes: Number of worker processes to use. Must be >= 1.
                Defaults to DEFAULT_NUM_PARSE_PROCESSES.

        Raises:
            ValueError: If num_processes is less than 1.
        """
        self._validate_num_processes(num_processes)
        self._num_processes = num_processes

    @property
    def num_processes(self) -> int:
        """Return the number of processes used for parallelization."""
        return self._num_processes

    def _validate_num_processes(self, value: int) -> None:
        """Validate that num_processes is at least 1.

        Args:
            value: Number of processes to validate.

        Raises:
            ValueError: If value is less than 1.
        """
        if value < 1:
            raise ValueError("Number of processes must be greater than or equal to 1.")

    def set_num_processes(self, value: int) -> None:
        """Set the number of processes for parallelization.

        Args:
            value: Number of processes to use. Must be >= 1.

        Raises:
            ValueError: If value is less than 1.
        """
        self._validate_num_processes(value)
        self._num_processes = value

    def execute(
        self,
        convert_func: Callable[[Path], Path],
        files: list[Path],
    ) -> list[Path]:
        """Execute file conversion in parallel.

        Uses multiprocessing.Pool.map() to process files in parallel when
        num_processes > 1 and there are multiple files. Otherwise, falls
        back to sequential processing.

        Args:
            convert_func: Function that converts a single file. Must be
                picklable (e.g., a module-level function, not a method).
            files: List of files to convert.

        Returns:
            List of converted file paths in the same order as input files.
        """
        if not files:
            return []

        if self._num_processes > 1 and len(files) > 1:
            logger().debug(
                f"Start parallel file conversion with {self._num_processes} processes "
                f"for {len(files)} files."
            )
            # Use 'spawn' context to avoid deadlocks in multi-threaded applications
            # (e.g., when running with --webui where NiceGUI creates threads)
            ctx = multiprocessing.get_context("spawn")
            with ctx.Pool(processes=self._num_processes) as pool:
                return pool.map(convert_func, files)
        else:
            logger().debug(f"Sequential file conversion for {len(files)} file(s).")
            return [convert_func(file) for file in files]

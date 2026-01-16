"""Tests for SequentialParseParallelization."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from OTAnalytics.plugin_parser_parallelization import SequentialParseParallelization


class TestSequentialParseParallelization:
    """Test suite for SequentialParseParallelization."""

    def test_num_processes_returns_one(self) -> None:
        """Sequential strategy always returns 1 for num_processes."""
        strategy = SequentialParseParallelization()
        assert strategy.num_processes == 1

    def test_set_num_processes_is_noop(self) -> None:
        """set_num_processes should be a no-op for sequential."""
        strategy = SequentialParseParallelization()
        strategy.set_num_processes(4)
        assert strategy.num_processes == 1

    def test_execute_with_empty_list(self) -> None:
        """execute should return empty list for empty input."""
        strategy = SequentialParseParallelization()
        convert_func = MagicMock()

        result = strategy.execute(convert_func, [])

        assert result == []
        convert_func.assert_not_called()

    def test_execute_with_single_file(self) -> None:
        """execute should process a single file correctly."""
        strategy = SequentialParseParallelization()
        input_file = Path("/test/input.ottrk")
        output_file = Path("/test/input.feather")
        convert_func = MagicMock(return_value=output_file)

        result = strategy.execute(convert_func, [input_file])

        assert result == [output_file]
        convert_func.assert_called_once_with(input_file)

    def test_execute_with_multiple_files(self) -> None:
        """execute should process multiple files in order."""
        strategy = SequentialParseParallelization()
        input_files = [
            Path("/test/file1.ottrk"),
            Path("/test/file2.ottrk"),
            Path("/test/file3.ottrk"),
        ]
        output_files = [
            Path("/test/file1.feather"),
            Path("/test/file2.feather"),
            Path("/test/file3.feather"),
        ]
        convert_func = MagicMock(side_effect=output_files)

        result = strategy.execute(convert_func, input_files)

        assert result == output_files
        assert convert_func.call_count == 3

    def test_execute_preserves_order(self) -> None:
        """execute should preserve the order of files."""
        strategy = SequentialParseParallelization()
        input_files = [Path(f"/test/file{i}.ottrk") for i in range(5)]

        def track_order(file: Path) -> Path:
            return file.with_suffix(".feather")

        result = strategy.execute(track_order, input_files)

        expected = [f.with_suffix(".feather") for f in input_files]
        assert result == expected

    def test_execute_propagates_exception(self) -> None:
        """execute should propagate exceptions from convert_func."""
        strategy = SequentialParseParallelization()
        convert_func = MagicMock(side_effect=ValueError("Conversion failed"))

        with pytest.raises(ValueError, match="Conversion failed"):
            strategy.execute(convert_func, [Path("/test/file.ottrk")])

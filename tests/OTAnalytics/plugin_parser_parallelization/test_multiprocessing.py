"""Tests for MultiprocessingParseParallelization."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from OTAnalytics.plugin_parser_parallelization import (
    MultiprocessingParseParallelization,
)


# Module-level functions for integration tests (must be picklable)
def _identity(path: Path) -> Path:
    """Return the path unchanged."""
    return path


def _change_suffix(path: Path) -> Path:
    """Change the path suffix to .feather."""
    return path.with_suffix(".feather")


class TestMultiprocessingParseParallelization:
    """Test suite for MultiprocessingParseParallelization."""

    def test_init_default_num_processes(self) -> None:
        """Default num_processes should be 1."""
        strategy = MultiprocessingParseParallelization()
        assert strategy.num_processes == 1

    def test_init_custom_num_processes(self) -> None:
        """Custom num_processes should be set correctly."""
        strategy = MultiprocessingParseParallelization(num_processes=4)
        assert strategy.num_processes == 4

    def test_init_invalid_num_processes_raises(self) -> None:
        """num_processes < 1 should raise ValueError."""
        with pytest.raises(ValueError, match="greater than or equal to 1"):
            MultiprocessingParseParallelization(num_processes=0)

        with pytest.raises(ValueError, match="greater than or equal to 1"):
            MultiprocessingParseParallelization(num_processes=-1)

    def test_set_num_processes(self) -> None:
        """set_num_processes should update the value."""
        strategy = MultiprocessingParseParallelization(num_processes=2)
        strategy.set_num_processes(8)
        assert strategy.num_processes == 8

    def test_set_num_processes_invalid_raises(self) -> None:
        """set_num_processes with invalid value should raise ValueError."""
        strategy = MultiprocessingParseParallelization(num_processes=2)
        with pytest.raises(ValueError, match="greater than or equal to 1"):
            strategy.set_num_processes(0)

    def test_execute_with_empty_list(self) -> None:
        """execute should return empty list for empty input."""
        strategy = MultiprocessingParseParallelization(num_processes=4)
        convert_func = MagicMock()

        result = strategy.execute(convert_func, [])

        assert result == []
        convert_func.assert_not_called()

    def test_execute_single_process_sequential(self) -> None:
        """With num_processes=1, should use sequential execution."""
        strategy = MultiprocessingParseParallelization(num_processes=1)
        input_files = [Path("/test/file1.ottrk"), Path("/test/file2.ottrk")]
        output_files = [Path("/test/file1.feather"), Path("/test/file2.feather")]
        convert_func = MagicMock(side_effect=output_files)

        with patch(
            "OTAnalytics.plugin_parser_parallelization.multiprocessing.multiprocessing"
        ) as mock_mp:
            result = strategy.execute(convert_func, input_files)

        # get_context should not be called with num_processes=1
        mock_mp.get_context.assert_not_called()
        assert result == output_files

    def test_execute_single_file_sequential(self) -> None:
        """With only one file, should use sequential execution."""
        strategy = MultiprocessingParseParallelization(num_processes=4)
        input_files = [Path("/test/file1.ottrk")]
        output_files = [Path("/test/file1.feather")]
        convert_func = MagicMock(side_effect=output_files)

        with patch(
            "OTAnalytics.plugin_parser_parallelization.multiprocessing.multiprocessing"
        ) as mock_mp:
            result = strategy.execute(convert_func, input_files)

        # get_context should not be called for single file
        mock_mp.get_context.assert_not_called()
        assert result == output_files

    def test_execute_multiprocessing_used(self) -> None:
        """With num_processes > 1 and multiple files, should use spawn Pool."""
        strategy = MultiprocessingParseParallelization(num_processes=4)
        input_files = [Path("/test/file1.ottrk"), Path("/test/file2.ottrk")]
        output_files = [Path("/test/file1.feather"), Path("/test/file2.feather")]

        mock_pool_instance = MagicMock()
        mock_pool_instance.map.return_value = output_files
        mock_pool_instance.__enter__ = MagicMock(return_value=mock_pool_instance)
        mock_pool_instance.__exit__ = MagicMock(return_value=False)

        mock_context = MagicMock()
        mock_context.Pool.return_value = mock_pool_instance

        with patch(
            "OTAnalytics.plugin_parser_parallelization.multiprocessing.multiprocessing"
        ) as mock_mp:
            mock_mp.get_context.return_value = mock_context
            convert_func = MagicMock()
            result = strategy.execute(convert_func, input_files)

        mock_mp.get_context.assert_called_once_with("spawn")
        mock_context.Pool.assert_called_once_with(processes=4)
        mock_pool_instance.map.assert_called_once_with(convert_func, input_files)
        assert result == output_files


class TestMultiprocessingParseParallelizationIntegration:
    """Integration tests for MultiprocessingParseParallelization.

    These tests actually use multiprocessing to verify the functionality works
    end-to-end. They use module-level functions that are picklable.
    """

    def test_actual_parallel_execution(self) -> None:
        """Test actual parallel execution with a simple function."""
        strategy = MultiprocessingParseParallelization(num_processes=2)

        input_files = [Path(f"/test/file{i}.ottrk") for i in range(4)]

        result = strategy.execute(_identity, input_files)

        assert result == input_files

    def test_parallel_execution_with_transformation(self) -> None:
        """Test parallel execution with a transformation function."""
        strategy = MultiprocessingParseParallelization(num_processes=2)

        input_files = [Path(f"/test/file{i}.ottrk") for i in range(4)]
        expected = [Path(f"/test/file{i}.feather") for i in range(4)]

        result = strategy.execute(_change_suffix, input_files)

        assert result == expected

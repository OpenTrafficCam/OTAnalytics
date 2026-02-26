from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from OTAnalytics.application.analysis.traffic_counting import CountImage
from OTAnalytics.application.state import ObservableProperty, TrackViewState
from OTAnalytics.application.use_cases.update_count_plots import (
    CountPlotSaver,
    CountPlotsUpdater,
)
from OTAnalytics.plugin_ui.visualization.counts.counts_plotter import CountPlotter


@pytest.fixture
def track_view_state() -> Mock:
    """Create a mock TrackViewState with observable properties."""
    state = Mock(spec=TrackViewState)
    state.view_width = Mock(spec=ObservableProperty)
    state.view_height = Mock(spec=ObservableProperty)
    state.count_plots = Mock(spec=ObservableProperty)
    return state


@pytest.fixture
def count_plotter() -> Mock:
    """Create a mock CountPlotter."""
    return Mock(spec=CountPlotter)


@pytest.fixture
def count_image() -> CountImage:
    """Create a sample CountImage for testing."""
    image = Mock()
    return CountImage(
        image=image,
        width=100,
        height=100,
        name="Test Count Plot",
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
    )


class TestCountPlotsUpdater:
    def test_update(self, track_view_state: Mock, count_plotter: Mock) -> None:
        """Test that update method gets width from state and updates count_plots."""
        # Setup
        width_value = 800
        height_value = 600
        plots = [Mock(spec=CountImage)]
        track_view_state.view_width.get.return_value = width_value
        track_view_state.view_height.get.return_value = height_value
        count_plotter.plot.return_value = plots

        # Create the updater
        updater = CountPlotsUpdater(track_view_state, count_plotter)

        # Execute
        updater.update()

        # Verify
        track_view_state.view_width.get.assert_called_once()
        track_view_state.view_height.get.assert_called_once()
        count_plotter.plot.assert_called_once_with(width_value, height_value)
        track_view_state.count_plots.set.assert_called_once_with(plots)

    @patch(
        "OTAnalytics.application.use_cases.update_count_plots.CountPlotsUpdater.update"
    )
    def test_call_invokes_update(
        self, mock_update: Mock, track_view_state: Mock, count_plotter: Mock
    ) -> None:
        """Test that calling the updater invokes the update method."""
        # Setup - create a spy on the update method
        updater = CountPlotsUpdater(track_view_state, count_plotter)

        # Execute
        updater()

        # Verify
        mock_update.assert_called_once()


class TestCountPlotSaver:
    @patch("OTAnalytics.application.analysis.traffic_counting.CountImage.save")
    def test_save(self, mock_save: Mock, count_image: CountImage) -> None:
        """Test that save method calls save on each plot."""
        # Setup
        path = Path("test/path")
        plots = [count_image, count_image]  # Two identical plots for testing
        saver = CountPlotSaver(path)

        # Execute
        saver.save(plots)

        # Verify
        assert mock_save.call_count == 2
        mock_save.assert_has_calls([call(path), call(path)])

    @patch("OTAnalytics.application.analysis.traffic_counting.CountImage.save")
    def test_call_invokes_save(self, mock_save: Mock, count_image: CountImage) -> None:
        """Test that calling the saver invokes the save method."""
        # Setup
        path = Path("test/path")
        plots = [count_image]
        saver = CountPlotSaver(path)

        # Execute
        saver(plots)

        # Verify
        mock_save.assert_has_calls([call(path)])

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("Normal_Name", "Normal_Name"),
            ("File: with/special*chars?", "File-with-special-chars"),
            ("File with   spaces", "File-with-spaces"),
            ("Café Ñandú", "Cafe-Nandu"),
            ("Line1\nLine2\r\nLine3", "Line1-Line2-Line3"),
            ("File///with----multi***replace", "File-with-multi-replace"),
            ("  Leading_and_trailing  ", "Leading_and_trailing"),
            ("x" * 300, "x" * 120),
        ],
        ids=[
            "normal_characters",
            "special_characters",
            "whitespace",
            "unicode_characters",
            "linebreaks",
            "multiple_replacements",
            "leading_trailing_replacements",
            "long_name_truncation",
        ],
    )
    def test_safe_filename(self, name: str, expected: str) -> None:
        """Test that safe_filename correctly sanitizes filenames."""
        # Setup - create a CountImage with the test name
        image = Mock()
        count_image = CountImage(
            image=image,
            width=100,
            height=100,
            name=name,
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
        )

        # Execute - call the method with the appropriate parameters
        result = count_image.safe_filename(max_length=120, replacement="-")

        # Verify - check that the result matches the expected output
        assert result == expected, f"expected '{expected}', got '{result}'"

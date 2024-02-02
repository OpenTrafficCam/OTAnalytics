from pathlib import Path
from unittest.mock import Mock, PropertyMock

from OTAnalytics.application.use_cases.preload_input_files import PreloadInputFiles


class TestPreloadInputFiles:
    def test_load(self) -> None:
        load_track_files = Mock()
        load_otflow = Mock()

        run_config = Mock()
        type(run_config).otflow = PropertyMock(return_value=Path("path/to/my/otflow"))
        type(run_config).track_files = PropertyMock(
            return_value=[Path("path/one.ottrk"), Path("path/two.ottrk")]
        )
        preload_input_files = PreloadInputFiles(load_track_files, load_otflow)
        preload_input_files.load(run_config)

        load_otflow.assert_called_once_with(run_config.otflow)
        load_track_files.assert_called_once_with(run_config.track_files)

    def test_load_nothing_to_load(self) -> None:
        load_track_files = Mock()
        load_otflow = Mock()

        run_config = Mock()
        type(run_config).otflow = PropertyMock(return_value=None)
        type(run_config).track_files = PropertyMock(return_value=[])
        preload_input_files = PreloadInputFiles(load_track_files, load_otflow)
        preload_input_files.load(run_config)

        load_otflow.assert_not_called()
        load_track_files.assert_not_called()

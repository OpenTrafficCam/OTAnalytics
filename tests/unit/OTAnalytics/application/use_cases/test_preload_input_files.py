from pathlib import Path
from unittest.mock import Mock, PropertyMock

from OTAnalytics.application.use_cases.preload_input_files import PreloadInputFiles


class TestPreloadInputFiles:
    def test_load_config_file(self) -> None:
        load_track_files = Mock()
        load_otconfig = Mock()
        load_otflow = Mock()
        apply_cli_cuts = Mock()

        run_config = Mock()
        type(run_config).config_file = PropertyMock(
            return_value=Path("path/to/my/otconfig")
        )
        type(run_config).track_files = PropertyMock(
            return_value=[Path("path/one.ottrk"), Path("path/two.ottrk")]
        )
        type(run_config).otflow = None
        type(run_config).sections = PropertyMock(return_value={Mock(), Mock()})

        preload_input_files = PreloadInputFiles(
            load_track_files, load_otconfig, load_otflow, apply_cli_cuts
        )
        preload_input_files.load(run_config)

        load_otflow.assert_not_called()
        load_otconfig.load.assert_called_once_with(run_config.config_file)
        load_track_files.assert_not_called()
        apply_cli_cuts.apply.assert_called_once_with(
            run_config.sections, preserve_cutting_sections=True
        )

    def test_load_flow_file(self) -> None:
        load_track_files = Mock()
        load_otconfig = Mock()
        load_otflow = Mock()
        apply_cli_cuts = Mock()

        run_config = Mock()
        type(run_config).otflow = PropertyMock(return_value=Path("path/to/my/otflow"))
        type(run_config).config_file = PropertyMock(return_value=None)
        type(run_config).track_files = PropertyMock(
            return_value=[Path("path/one.ottrk"), Path("path/two.ottrk")]
        )
        type(run_config).sections = PropertyMock(return_value={Mock(), Mock()})

        preload_input_files = PreloadInputFiles(
            load_track_files, load_otconfig, load_otflow, apply_cli_cuts
        )
        preload_input_files.load(run_config)

        load_otflow.assert_called_once_with(run_config.otflow)
        load_otconfig.assert_not_called()
        load_track_files.assert_called_once_with(run_config.track_files)
        apply_cli_cuts.apply.assert_called_once_with(
            run_config.sections, preserve_cutting_sections=True
        )

    def test_load_nothing_to_load(self) -> None:
        load_track_files = Mock()
        load_otconfig = Mock()
        load_otflow = Mock()
        apply_cli_cuts = Mock()

        run_config = Mock()
        type(run_config).otflow = PropertyMock(return_value=None)
        type(run_config).config_file = PropertyMock(return_value=None)
        type(run_config).track_files = PropertyMock(return_value=[])
        type(run_config).sections = PropertyMock(return_value=set())
        preload_input_files = PreloadInputFiles(
            load_track_files, load_otconfig, load_otflow, apply_cli_cuts
        )
        preload_input_files.load(run_config)

        load_otflow.assert_not_called()
        load_track_files.assert_not_called()
        apply_cli_cuts.apply.assert_not_called()

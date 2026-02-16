from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.project import Project
from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.config import MissingDate, SaveOtconfig
from OTAnalytics.domain.track_repository import TrackFileRepository


class TestSaveOtconfig:
    def test_correct_date(self, test_data_tmp_dir: Path) -> None:
        track_file_repository = Mock(spec=TrackFileRepository)
        datastore = Mock(spec=Datastore)
        datastore._track_file_repository = track_file_repository
        datastore.project = Project("name", start_date=datetime(2023, 1, 1))
        convert_result = Mock()
        config_parser = Mock(spec=ConfigParser)
        config_parser.convert.return_value = convert_result
        output = test_data_tmp_dir / "test.otconfig"
        file_state = Mock()
        get_current_remark = Mock()
        use_case = SaveOtconfig(
            datastore, config_parser, file_state, get_current_remark
        )

        use_case(output)

        config_parser.serialize.assert_called_once()
        file_state.last_saved_config.set.assert_called_once_with(
            ConfigurationFile(output, convert_result)
        )
        get_current_remark.get.assert_called_once()

    def test_missing_date(self, test_data_tmp_dir: Path) -> None:
        datastore = Mock(spec=Datastore)
        datastore.project = Project("name", start_date=None)
        config_parser = Mock(spec=ConfigParser)
        output = test_data_tmp_dir / "test.otconfig"
        file_state = Mock()
        get_current_remark = Mock()
        use_case = SaveOtconfig(
            datastore, config_parser, file_state, get_current_remark
        )

        with pytest.raises(MissingDate):
            use_case(output)
        file_state.last_saved_config.set.assert_not_called()
        get_current_remark.get.assert_not_called()

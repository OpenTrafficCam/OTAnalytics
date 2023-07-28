from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.datastore import ConfigParser, Datastore
from OTAnalytics.application.project import Project
from OTAnalytics.application.use_cases.config import MissingDate, SaveConfiguration


class TestSaveConfiguration:
    def test_correct_date(self, test_data_tmp_dir: Path) -> None:
        datastore = Mock(spec=Datastore)
        datastore.project = Project("name", start_date=datetime(2023, 1, 1))
        config_parser = Mock(spec=ConfigParser)
        output = test_data_tmp_dir / "test.otconfig"
        use_case = SaveConfiguration(datastore, config_parser)

        use_case(output)

        config_parser.serialize.assert_called_once()

    def test_missing_date(self, test_data_tmp_dir: Path) -> None:
        datastore = Mock(spec=Datastore)
        datastore.project = Project("name", start_date=None)
        config_parser = Mock(spec=ConfigParser)
        output = test_data_tmp_dir / "test.otconfig"
        use_case = SaveConfiguration(datastore, config_parser)

        with pytest.raises(MissingDate):
            use_case(output)

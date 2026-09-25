from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.parser.config_parser import ConfigParser
from OTAnalytics.application.project import Project
from OTAnalytics.application.state import ConfigurationFile
from OTAnalytics.application.use_cases.config import ConfigValidationError, SaveOtconfig
from OTAnalytics.domain.track_repository import TrackFileRepository

A_PREFIX = S3KeyPrefix("project-1/site-2/otcamera19/")


class TestSaveOtconfig:
    async def test_correct_date(self, test_data_tmp_dir: Path) -> None:
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
        current_key_prefix = Mock()
        current_key_prefix.get.return_value = A_PREFIX
        otconfig_upload = AsyncMock()
        use_case = SaveOtconfig(
            datastore,
            config_parser,
            file_state,
            get_current_remark,
            current_key_prefix,
            otconfig_upload,
        )

        await use_case(output)

        config_parser.serialize.assert_called_once()
        assert config_parser.serialize.call_args.kwargs["s3_key_prefix"] == A_PREFIX
        file_state.last_saved_config.set.assert_called_once_with(
            ConfigurationFile(output, convert_result)
        )
        get_current_remark.get.assert_called_once()

    async def test_writes_the_same_location_it_records_as_saved(
        self, test_data_tmp_dir: Path
    ) -> None:
        """The written file and the content remembered as "last saved" have to
        agree. If only the file carried the prefix, the comparison in
        OtconfigHasChanged would never match and every project would report
        itself as permanently unsaved.

        #Requirement https://openproject.platomo.de/wp/10322
        """
        track_file_repository = Mock(spec=TrackFileRepository)
        datastore = Mock(spec=Datastore)
        datastore._track_file_repository = track_file_repository
        datastore.project = Project("name", start_date=datetime(2023, 1, 1))
        config_parser = Mock(spec=ConfigParser)
        current_key_prefix = Mock()
        current_key_prefix.get.return_value = A_PREFIX
        use_case = SaveOtconfig(
            datastore,
            config_parser,
            Mock(),
            Mock(),
            current_key_prefix,
            AsyncMock(),
        )

        await use_case(test_data_tmp_dir / "test.otconfig")

        written = config_parser.serialize.call_args.kwargs["s3_key_prefix"]
        recorded = config_parser.convert.call_args.args[-1]
        assert written == recorded == A_PREFIX

    async def test_uploads_when_project_names_a_key_prefix(
        self, test_data_tmp_dir: Path
    ) -> None:
        track_file_repository = Mock(spec=TrackFileRepository)
        datastore = Mock(spec=Datastore)
        datastore._track_file_repository = track_file_repository
        datastore.project = Project("name", start_date=datetime(2023, 1, 1))
        config_parser = Mock(spec=ConfigParser)
        current_key_prefix = Mock()
        current_key_prefix.get.return_value = A_PREFIX
        otconfig_upload = AsyncMock()
        output = test_data_tmp_dir / "test.otconfig"
        use_case = SaveOtconfig(
            datastore,
            config_parser,
            Mock(),
            Mock(),
            current_key_prefix,
            otconfig_upload,
        )

        await use_case(output)

        otconfig_upload.upload.assert_awaited_once_with(output, A_PREFIX)

    async def test_does_not_upload_when_project_names_no_key_prefix(
        self, test_data_tmp_dir: Path
    ) -> None:
        track_file_repository = Mock(spec=TrackFileRepository)
        datastore = Mock(spec=Datastore)
        datastore._track_file_repository = track_file_repository
        datastore.project = Project("name", start_date=datetime(2023, 1, 1))
        config_parser = Mock(spec=ConfigParser)
        current_key_prefix = Mock()
        current_key_prefix.get.return_value = None
        otconfig_upload = AsyncMock()
        use_case = SaveOtconfig(
            datastore,
            config_parser,
            Mock(),
            Mock(),
            current_key_prefix,
            otconfig_upload,
        )

        await use_case(test_data_tmp_dir / "test.otconfig")

        otconfig_upload.upload.assert_not_awaited()

    async def test_missing_date(self, test_data_tmp_dir: Path) -> None:
        datastore = Mock(spec=Datastore)
        datastore.project = Project("name", start_date=None)
        config_parser = Mock(spec=ConfigParser)
        output = test_data_tmp_dir / "test.otconfig"
        file_state = Mock()
        get_current_remark = Mock()
        use_case = SaveOtconfig(
            datastore,
            config_parser,
            file_state,
            get_current_remark,
            Mock(),
            AsyncMock(),
        )

        with pytest.raises(ConfigValidationError) as exc_info:
            await use_case(output)
        assert "Start date and time are missing or incomplete" in exc_info.value.errors
        file_state.last_saved_config.set.assert_not_called()
        get_current_remark.get.assert_not_called()

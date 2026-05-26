from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from OTAnalytics.adapter_ui.cancel_export_counts import CancelExportCounts
from OTAnalytics.adapter_ui.cancel_export_file import CancelExportFile
from OTAnalytics.adapter_ui.file_export_dto import ExportFileDto
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import DialogResult
from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import NiceGuiUiFactory


@pytest.fixture
def resource_manager() -> ResourceManager:
    return ResourceManager()


@pytest.fixture
def viewmodel() -> Mock:
    vm = MagicMock(spec=ViewModel)
    vm.get_save_path_suggestion.return_value = Path("/tmp/mydata.events.csv")
    return vm


@pytest.fixture
def factory(resource_manager: ResourceManager) -> NiceGuiUiFactory:
    return NiceGuiUiFactory(resource_manager=resource_manager)


class TestConfigureExportFile:
    @pytest.mark.asyncio
    async def test_returns_dto_with_correct_stem(
        self,
        factory: NiceGuiUiFactory,
        viewmodel: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        dialog_instance = MagicMock()
        dialog_instance.result = AsyncMock(return_value=DialogResult.APPLY)()
        dialog_instance.get_directory.return_value = Path("/tmp")
        dialog_instance.get_file_stem.return_value = "mydata"
        dialog_instance.get_export_format_extension.return_value = ".csv"
        dialog_instance.get_format.return_value = "CSV"

        monkeypatch.setattr(
            "OTAnalytics.plugin_ui.nicegui_gui.ui_factory.FileChooserDialog",
            lambda **kwargs: dialog_instance,
        )

        result = await factory.configure_export_file(
            title="Export events",
            export_format_extensions={"CSV": ".csv"},
            context_file_type="events",
            viewmodel=viewmodel,
        )

        assert result == ExportFileDto(
            export_directory=Path("/tmp"),
            file_stem="mydata",
            export_format_extension=".csv",
            export_format="CSV",
        )
        assert result.as_file_path() == Path("/tmp/mydata.csv")

    @pytest.mark.asyncio
    async def test_raises_cancel_export_file_on_cancel(
        self,
        factory: NiceGuiUiFactory,
        viewmodel: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        dialog_instance = MagicMock()
        dialog_instance.result = AsyncMock(return_value=DialogResult.CANCEL)()
        monkeypatch.setattr(
            "OTAnalytics.plugin_ui.nicegui_gui.ui_factory.FileChooserDialog",
            lambda **kwargs: dialog_instance,
        )

        with pytest.raises(CancelExportFile):
            await factory.configure_export_file(
                title="Export events",
                export_format_extensions={"CSV": ".csv"},
                context_file_type="events",
                viewmodel=viewmodel,
            )


class TestConfigureExportCounts:
    @pytest.mark.asyncio
    async def test_raises_cancel_export_counts_on_cancel(
        self,
        factory: NiceGuiUiFactory,
        viewmodel: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        dialog_instance = MagicMock()
        dialog_instance.result = AsyncMock(return_value=DialogResult.CANCEL)()
        monkeypatch.setattr(
            "OTAnalytics.plugin_ui.nicegui_gui.ui_factory.ExportCountsDialog",
            lambda **kwargs: dialog_instance,
        )

        with pytest.raises(CancelExportCounts):
            await factory.configure_export_counts(
                start=None,
                end=None,
                default_format="CSV",
                modes=[],
                export_formats={"CSV": ".csv"},
                viewmodel=viewmodel,
            )

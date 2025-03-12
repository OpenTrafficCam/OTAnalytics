from nicegui import ui

from OTAnalytics.adapter_ui.abstract_frame_remark import AbstractFrameRemark
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    RemarkKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)


class RemarkForm(AbstractFrameRemark):
    def __init__(
        self,
        resource_manager: ResourceManager,
        view_model: ViewModel,
    ) -> None:
        self._resource_manager = resource_manager
        self._viewmodel = view_model

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_remark_frame(self)

    def build(self) -> None:
        self.remark_textbox = ui.textarea(
            label=self._resource_manager.get(RemarkKeys.REMARK_PLACEHOLDER)
        )

    def load_remark(self) -> None:
        self.remark_textbox.clear()
        remark = self._resource_manager.get(RemarkKeys.REMARK_NO_COMMENT)
        if self._viewmodel.get_remark():
            remark = self._viewmodel.get_remark()
        self.remark_textbox.set_value(remark)

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
        ui.label(self._resource_manager.get(RemarkKeys.LABEL_REMARK_HEADER))
        self._remark_label = ui.label()
        self.load_remark()

    def load_remark(self) -> None:
        self._remark_label.clear()
        if remark := self._viewmodel.get_remark():
            self._remark_label.set_text(remark)
        else:
            self._remark_label.set_text(
                self._resource_manager.get(RemarkKeys.REMARK_NO_COMMENT)
            )

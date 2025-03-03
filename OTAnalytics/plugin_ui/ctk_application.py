from functools import cached_property

from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.plugin_ui.gui_application import OtAnalyticsGuiApplicationStarter


class OtAnalyticsCtkApplicationStarter(OtAnalyticsGuiApplicationStarter):
    def __init__(self, run_config: RunConfiguration) -> None:
        super().__init__(run_config)
        from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_progress import (
            PullingProgressbarPopupBuilder,
        )

        self._pulling_progressbar_popup_builder = PullingProgressbarPopupBuilder()

    def start_ui(self) -> None:
        from OTAnalytics.plugin_ui.customtkinter_gui.gui import (
            ModifiedCTk,
            OTAnalyticsGui,
        )

        layer_groups, layers = self.layers
        main_window = ModifiedCTk(self.view_model)
        self._pulling_progressbar_popup_builder.add_widget(main_window)
        OTAnalyticsGui(
            main_window,
            self.view_model,
            layer_groups,
            self.preload_input_files,
            self.run_config,
        ).start()

    @cached_property
    def ui_factory(self) -> UiFactory:
        from OTAnalytics.plugin_ui.customtkinter_gui.ctk_ui_factory import CtkUiFactory

        return CtkUiFactory()

    @cached_property
    def progressbar_builder(self) -> ProgressbarBuilder:
        from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_progress import (
            PullingProgressbarBuilder,
        )

        pulling_progressbar_builder = PullingProgressbarBuilder(
            self._pulling_progressbar_popup_builder
        )
        return pulling_progressbar_builder

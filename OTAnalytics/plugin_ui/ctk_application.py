from OTAnalytics.plugin_ui.gui_application import OtAnalyticsGuiApplicationStarter


class OtAnalyticsCtkApplicationStarter(OtAnalyticsGuiApplicationStarter):
    def start_ui(self) -> None:
        from OTAnalytics.plugin_ui.customtkinter_gui.gui import (
            ModifiedCTk,
            OTAnalyticsGui,
        )

        layer_groups, layers = self.layers
        main_window = ModifiedCTk(self.view_model)
        self.pulling_progressbar_popup_builder.add_widget(main_window)
        OTAnalyticsGui(
            main_window,
            self.view_model,
            layer_groups,
            self.preload_input_files,
            self.run_config,
        ).start()

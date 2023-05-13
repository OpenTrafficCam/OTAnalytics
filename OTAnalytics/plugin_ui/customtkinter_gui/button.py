from typing import Any, Callable

from customtkinter import CTkButton

from OTAnalytics.adapter_ui.abstract_stateful_widget import AbstractStatefulWidget


class StatefulButton(CTkButton, AbstractStatefulWidget):
    def __init__(
        self, viewmodel_setter: Callable[["StatefulButton"], None], **kwargs: Any
    ) -> None:
        self._viewmodel_setter = viewmodel_setter
        super().__init__(**kwargs)
        self._introduce_to_viewmodel()

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel_setter(self)

    def activate(self) -> None:
        print(f"trying to enable {self}")
        self.configure(state="enabled")

    def deactivate(self) -> None:
        print(f"trying to disable {self}")
        self.configure(state="disabled")

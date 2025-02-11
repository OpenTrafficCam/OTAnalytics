from abc import ABC, abstractmethod

from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.theme.global_theme import global_theme


class LayoutComponents(ABC):
    @abstractmethod
    def build(self) -> None:
        raise NotImplementedError


class NiceguiPageBuilder(ABC):
    """The NiceguiPageBuilder class serves as an abstract base class for building
    pages in NiceGUI.

    Provides a template method `build` that sets up the page with the given endpoint.
    Subclasses should provide an implementation for the `_build` method to define custom
    behavior for the constructed page.

    Args:
        endpoint_name (str): the endpoint name to be set up with the page to be built.

    """

    def __init__(self, endpoint_name: str) -> None:
        self._endpoint_name = endpoint_name

    def build(self, layout_components: LayoutComponents) -> None:
        """The template method to set up and build the page with the given endpoint."""

        @ui.page(self._endpoint_name)
        def build() -> None:
            with global_theme():
                layout_components.build()
                self._build()

    @abstractmethod
    def _build(self) -> None:
        """The abstract method to be implemented by subclasses to build the page."""
        raise NotImplementedError

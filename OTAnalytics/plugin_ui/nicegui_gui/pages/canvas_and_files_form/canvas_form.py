from typing import Optional, Self

from nicegui import ui
from nicegui.elements.interactive_image import InteractiveImage
from PIL import Image

from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    CanvasKeys,
    ResourceManager,
)
from OTAnalytics.domain.track import TrackImage


class CanvasForm(AbstractFrameCanvas):

    def __init__(
        self,
        viewmodel: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._viewmodel = viewmodel
        self._resource_manager = resource_manager
        self._background_image: Optional[InteractiveImage] = None
        self._current_image: Optional[Image.Image] = None

        self.introduce_to_viewmodel()
        self.add_preview_image()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_canvas(self)

    def add_preview_image(self) -> None:
        self._current_image = self._resource_manager.get_image(CanvasKeys.IMAGE_DEFAULT)

    def build(self) -> Self:
        self._background_image = ui.interactive_image("").classes("w-64")
        self._change_image()
        return self

    def update_background(self, image: TrackImage) -> None:
        self._current_image = image.as_image()
        self._change_image()

    def _change_image(self) -> None:
        if self._current_image and self._background_image:
            self._background_image.set_source(self._current_image)
        else:
            self.clear_image()

    def clear_image(self) -> None:
        if self._background_image:
            self._background_image.set_source("")

from dataclasses import dataclass

import numpy
from PIL import Image

from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_prototypes.track_visualization.cv2_image import serialize_image


@dataclass(frozen=True, slots=True)
class PilImage(TrackImage):
    """
    Concrete implementation using pillow as image format.
    """

    _image: Image.Image

    def add(self, other: TrackImage) -> TrackImage:
        if isinstance(other, PilImage):
            self_image = self.as_image().convert(mode="RGBA")
            other_image = other.as_image().convert(mode="RGBA")
            return PilImage(Image.alpha_composite(self_image, other_image))
        raise ValueError(f"Cannot add {other} to {self}")

    def as_image(self) -> Image.Image:
        return self._image

    def as_base64(self) -> str:
        return serialize_image(numpy.array(self.as_image()))

    def width(self) -> int:
        return self._image.width

    def height(self) -> int:
        return self._image.height

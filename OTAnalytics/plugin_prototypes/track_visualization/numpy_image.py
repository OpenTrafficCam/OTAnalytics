from dataclasses import dataclass
from typing import Any

import numpy
from numpy import ndarray
from PIL import Image

from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_prototypes.track_visualization.cv2_image import serialize_image


@dataclass(frozen=True)
class NumpyImage(TrackImage):
    image_data: ndarray

    def add(self, other: TrackImage) -> TrackImage:
        if isinstance(other, NumpyImage):
            combined_image = weighted_alpha_blend(self.image_data, other.image_data)
            return NumpyImage(combined_image)
        raise ValueError(f"Cannot add {other} to {self}")

    def as_image(self) -> Image.Image:
        if self.color_depth() == 4:
            return Image.fromarray(self.image_data, mode="RGBA")
        return Image.fromarray(self.image_data, mode="RGB").convert(mode="RGBA")

    def as_base64(self) -> str:
        return serialize_image(self.image_data)

    def width(self) -> int:
        return self._shape()[0]

    def height(self) -> int:
        return self._shape()[1]

    def color_depth(self) -> int:
        return self._shape()[2]

    def _shape(self) -> tuple[int, int, int]:
        shape = self.image_data.shape
        if len(shape) == 2:
            return shape[1], shape[0], 1
        return shape[1], shape[0], shape[2]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NumpyImage):
            return False
        return self is other  # numpy.array_equal(self.image_data, other.image_data)


def weighted_alpha_blend(background: ndarray, foreground: ndarray) -> ndarray:
    """
    Alpha Blending mit zusätzlicher Opazitätskontrolle

    Args:
        background: Hintergrund RGBA Array
        foreground: Vordergrund RGBA Array
    """
    # Anpassung der Vordergrund-Alpha mit Opazität
    fg_adjusted = foreground.copy().astype(float)

    bg_float = background.astype(float)
    fg_float = fg_adjusted.astype(float)

    # Normalisierte Alpha-Werte
    bg_alpha = bg_float[:, :, 3:4] / 255.0
    fg_alpha = fg_float[:, :, 3:4] / 255.0

    # Alpha Blending
    combined_alpha = fg_alpha + bg_alpha * (1 - fg_alpha)
    combined_alpha = numpy.where(combined_alpha == 0, 1, combined_alpha)

    combined_rgb = (
        fg_float[:, :, :3] * fg_alpha + bg_float[:, :, :3] * bg_alpha * (1 - fg_alpha)
    ) / combined_alpha

    result = numpy.concatenate([combined_rgb, combined_alpha * 255], axis=2)
    return numpy.clip(result, 0, 255).astype(numpy.uint8)

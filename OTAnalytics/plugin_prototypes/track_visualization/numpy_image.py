from dataclasses import dataclass
from typing import Any

import numpy
from numpy import ndarray
from PIL import Image

from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_prototypes.track_visualization.cv2_image import serialize_image

# Constants for image processing
RGBA_COLOR_DEPTH = 4
GRAYSCALE_SHAPE_LENGTH = 2
DEFAULT_GRAYSCALE_DEPTH = 1
WIDTH_INDEX = 1
HEIGHT_INDEX = 0
COLOR_DEPTH_INDEX = 2
ALPHA_START = 3
ALPHA_END = 4
RGB_CHANNELS_SLICE_END = 3
MAX_ALPHA_VALUE = 255.0
MAX_COLOR_VALUE = 255
MIN_ALPHA_VALUE = 0
FULL_OPACITY = 1
MIN_COLOR_VALUE = 0


@dataclass(frozen=True, slots=True)
class NumpyImage(TrackImage):
    image_data: ndarray

    def add(self, other: TrackImage) -> TrackImage:
        if isinstance(other, NumpyImage):
            combined_image = weighted_alpha_blend(self.image_data, other.image_data)
            return NumpyImage(combined_image)
        raise ValueError(f"Cannot add {other} to {self}")

    def as_image(self) -> Image.Image:
        if self.color_depth() == RGBA_COLOR_DEPTH:
            return Image.fromarray(self.image_data, mode="RGBA")
        return Image.fromarray(self.image_data, mode="RGB").convert(mode="RGBA")

    def as_base64(self) -> str:
        return serialize_image(self.image_data)

    def width(self) -> int:
        return self._shape()[HEIGHT_INDEX]

    def height(self) -> int:
        return self._shape()[WIDTH_INDEX]

    def color_depth(self) -> int:
        return self._shape()[COLOR_DEPTH_INDEX]

    def _shape(self) -> tuple[int, int, int]:
        shape = self.image_data.shape
        if len(shape) == GRAYSCALE_SHAPE_LENGTH:
            return shape[WIDTH_INDEX], shape[HEIGHT_INDEX], DEFAULT_GRAYSCALE_DEPTH
        return shape[WIDTH_INDEX], shape[HEIGHT_INDEX], shape[COLOR_DEPTH_INDEX]

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
    bg_alpha = bg_float[:, :, ALPHA_START:ALPHA_END] / MAX_ALPHA_VALUE
    fg_alpha = fg_float[:, :, ALPHA_START:ALPHA_END] / MAX_ALPHA_VALUE

    # Alpha Blending
    combined_alpha = fg_alpha + bg_alpha * (FULL_OPACITY - fg_alpha)
    combined_alpha = numpy.where(
        combined_alpha == MIN_ALPHA_VALUE, FULL_OPACITY, combined_alpha
    )

    combined_rgb = (
        fg_float[:, :, :RGB_CHANNELS_SLICE_END] * fg_alpha
        + bg_float[:, :, :RGB_CHANNELS_SLICE_END] * bg_alpha * (FULL_OPACITY - fg_alpha)
    ) / combined_alpha

    result = numpy.concatenate(
        [combined_rgb, combined_alpha * MAX_COLOR_VALUE], axis=COLOR_DEPTH_INDEX
    )
    return numpy.clip(result, MIN_COLOR_VALUE, MAX_COLOR_VALUE).astype(numpy.uint8)

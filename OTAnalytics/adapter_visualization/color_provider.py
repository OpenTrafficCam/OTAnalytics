import random

from matplotlib import colors as mcolors

from OTAnalytics.domain.otc_classes import OtcClasses
from OTAnalytics.domain.tls8plus1_classes import Tls8plus1Classes

DEFAULT_COLOR_PALETTE: dict[str, str] = {
    OtcClasses.CAR: "#4da3ff",
    OtcClasses.CAR_WITH_TRAILER: "#9cc9ff",
    OtcClasses.MOTORCYCLIST: "#ff8a3d",
    OtcClasses.PEDESTRIAN: "#ff7eb6",
    OtcClasses.TRUCK: "#ff5a5a",
    OtcClasses.TRUCK_WITH_TRAILER: "#c084fc",
    OtcClasses.TRUCK_WITH_SEMITRAILER: "#e879f9",
    OtcClasses.BICYCLIST: "#7ee081",
    OtcClasses.BICYCLIST_WITH_TRAILER: "#b5f0a8",
    OtcClasses.CARGO_BIKE_DRIVER: "#2fbf71",
    OtcClasses.SCOOTER_DRIVER: "#5ee0e0",
    OtcClasses.DELIVERY_VAN: "#ffd23f",
    OtcClasses.DELIVERY_VAN_WITH_TRAILER: "#ffe58a",
    OtcClasses.PRIVATE_VAN: "#a8b3bf",
    OtcClasses.PRIVATE_VAN_WITH_TRAILER: "#d0d7de",
    OtcClasses.TRAIN: "#c08a5a",
    OtcClasses.BUS: "#14b8a6",
    OtcClasses.OTHER: "#7c8a99",
    Tls8plus1Classes.CAR: "#4da3ff",
    Tls8plus1Classes.CAR_WITH_TRAILER: "#9cc9ff",
    Tls8plus1Classes.MOTORCYCLIST: "#ff8a3d",
    Tls8plus1Classes.TRUCK: "#ff5a5a",
    Tls8plus1Classes.TRUCK_WITH_TRAILER: "#c084fc",
    Tls8plus1Classes.TRUCK_WITH_SEMITRAILER: "#e879f9",
    Tls8plus1Classes.BICYCLIST: "#7ee081",
    Tls8plus1Classes.DELIVERY_VAN: "#ffd23f",
    Tls8plus1Classes.BUS: "#14b8a6",
    Tls8plus1Classes.OTHER: "#7c8a99",
}


class ColorPaletteProvider:
    """Provides a color palette for all classes known from the tracks metadata.

    Uses a default palette for known values.
    Generates random colors for unknown values.
    Updates, whenever track metadata are updated.
    """

    def __init__(self, default_palette: dict[str, str]) -> None:
        self._default_palette = default_palette
        self._palette: dict[str, str] = {}
        self._numeric: dict[str, tuple[int, int, int]] = {}

    def update(self, classifications: frozenset[str]) -> None:
        for classification in classifications:
            if classification in self._default_palette.keys():
                self._palette[classification] = self._default_palette[classification]
                color = mcolors.to_hex(self._default_palette[classification])
                self._numeric[classification] = hex_to_rgb_tuple(color)
            else:
                self._palette[classification] = self._generate_random_color()

    @staticmethod
    def _generate_random_color() -> str:
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        return "#{:02X}{:02X}{:02X}".format(red, green, blue)

    def get(self) -> dict[str, str]:
        return self._palette

    def get_numeric(self) -> dict[str, tuple[int, int, int]]:
        return self._numeric


def hex_to_rgb_tuple(hex_color: str) -> tuple[int, int, int]:
    """
    Converts a hex color string to an RGB tuple of integers.

    Args:
        hex_color (str): Hex color string (e.g., "#FF5733" or "FF5733")

    Returns:
        tuple: RGB tuple (r, g, b) with values from 0-255
    """
    # Remove the '#' at the beginning, if present
    hex_color = hex_color.lstrip("#")

    # Convert each two-digit hex value to int
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return r, g, b

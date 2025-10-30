import random

from matplotlib import colors as mcolors

from OTAnalytics.domain.otc_classes import OtcClasses
from OTAnalytics.domain.tls8plus1_classes import Tls8plus1Classes

DEFAULT_COLOR_PALETTE: dict[str, str] = {
    OtcClasses.CAR: "blue",
    OtcClasses.CAR_WITH_TRAILER: "skyblue",
    OtcClasses.MOTORCYCLIST: "orange",
    OtcClasses.PEDESTRIAN: "salmon",
    OtcClasses.TRUCK: "red",
    OtcClasses.TRUCK_WITH_TRAILER: "purple",
    OtcClasses.TRUCK_WITH_SEMITRAILER: "pink",
    OtcClasses.BICYCLIST: "lime",
    OtcClasses.BICYCLIST_WITH_TRAILER: "lime",
    OtcClasses.CARGO_BIKE_DRIVER: "green",
    OtcClasses.SCOOTER_DRIVER: "white",
    OtcClasses.DELIVERY_VAN: "yellow",
    OtcClasses.DELIVERY_VAN_WITH_TRAILER: "yellow",
    OtcClasses.PRIVATE_VAN: "black",
    OtcClasses.PRIVATE_VAN_WITH_TRAILER: "black",
    OtcClasses.TRAIN: "brown",
    OtcClasses.BUS: "beige",
    Tls8plus1Classes.CAR: "blue",
    Tls8plus1Classes.CAR_WITH_TRAILER: "skyblue",
    Tls8plus1Classes.MOTORCYCLIST: "orange",
    Tls8plus1Classes.TRUCK: "red",
    Tls8plus1Classes.TRUCK_WITH_TRAILER: "purple",
    Tls8plus1Classes.TRUCK_WITH_SEMITRAILER: "pink",
    Tls8plus1Classes.BICYCLIST: "lime",
    Tls8plus1Classes.DELIVERY_VAN: "yellow",
    Tls8plus1Classes.BUS: "beige",
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
                color = mcolors.CSS4_COLORS.get(self._default_palette[classification])
                self._numeric[classification] = hex_to_rgb_tuple(str(color))
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

import random

CLASS_CAR = "car"
CLASS_CAR_TRAILER = "car_with_trailer"
CLASS_MOTORCYCLIST = "motorcyclist"
CLASS_PEDESTRIAN = "pedestrian"
CLASS_TRUCK = "truck"
CLASS_TRUCK_TRAILER = "truck_with_trailer"
CLASS_TRUCK_SEMITRAILER = "truck_with_semitrailer"
CLASS_BICYCLIST = "bicyclist"
CLASS_BICYCLIST_TRAILER = "bicyclist_with_trailer"
CLASS_CARGOBIKE = "cargobike_driver"
CLASS_SCOOTER = "scooter_driver"
CLASS_DELVAN = "delivery_van"
CLASS_DELVAN_TRAILER = "delivery_van_with_trailer"
CLASS_PRVAN = "private_van"
CLASS_PRVAN_TRAILER = "private_van_with_trailer"
CLASS_TRAIN = "train"
CLASS_BUS = "bus"
DEFAULT_COLOR_PALETTE: dict[str, str] = {
    CLASS_CAR: "blue",
    CLASS_CAR_TRAILER: "skyblue",
    CLASS_MOTORCYCLIST: "orange",
    CLASS_PEDESTRIAN: "salmon",
    CLASS_TRUCK: "red",
    CLASS_TRUCK_TRAILER: "purple",
    CLASS_TRUCK_SEMITRAILER: "pink",
    CLASS_BICYCLIST: "lime",
    CLASS_BICYCLIST_TRAILER: "lime",
    CLASS_CARGOBIKE: "green",
    CLASS_SCOOTER: "white",
    CLASS_DELVAN: "yellow",
    CLASS_DELVAN_TRAILER: "yellow",
    CLASS_PRVAN: "black",
    CLASS_PRVAN_TRAILER: "black",
    CLASS_TRAIN: "brown",
    CLASS_BUS: "beige",
}
CLASS_ORDER = [
    CLASS_PEDESTRIAN,
    CLASS_BICYCLIST,
    CLASS_BICYCLIST_TRAILER,
    CLASS_CARGOBIKE,
    CLASS_SCOOTER,
    CLASS_MOTORCYCLIST,
    CLASS_CAR,
    CLASS_CAR_TRAILER,
    CLASS_PRVAN,
    CLASS_PRVAN_TRAILER,
    CLASS_DELVAN,
    CLASS_DELVAN_TRAILER,
    CLASS_TRUCK,
    CLASS_TRUCK_TRAILER,
    CLASS_TRUCK_SEMITRAILER,
    CLASS_BUS,
    CLASS_TRAIN,
]


class ColorPaletteProvider:
    """Provides a color palette for all classes known from the tracks metadata.

    Uses a default palette for known values.
    Generates random colors for unknown values.
    Updates, whenever track metadata are updated.
    """

    def __init__(self, default_palette: dict[str, str]) -> None:
        self._default_palette = default_palette
        self._palette: dict[str, str] = {}

    def update(self, classifications: frozenset[str]) -> None:
        for classification in classifications:
            if classification in self._default_palette.keys():
                self._palette[classification] = self._default_palette[classification]
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

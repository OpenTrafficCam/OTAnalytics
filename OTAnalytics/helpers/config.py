"""
Factor for ...
E.g. (0,0) for top-left corner, (1,0) for top-right corner,
(0,1) for bottom-left corner, (1,1) for bottom-right corner
"""

ENCODING = "UTF-8"
COMPRESSED_FILETYPE = ".bz2"

TRANSFORMED_COORDS = False

bbox_factor_reference = {
    "pedestrian": (0.5, 0.5),
    "bicyclist": (0.5, 0.5),
    "car": (0.5, 0.5),
    "motorcyclist": (0.5, 0.5),
    "private_van": (0.5, 0.5),
    "bus": (0.5, 0.5),
    "train": (0.5, 0.5),
    "truck": (0.5, 0.5),
    "scooter_driver": (0.5, 0.5),
    "cargo_bike_driver": (0.5, 0.5),
    "bicyclist_with_trailer": (0.5, 0.5),
    "car_with_trailer": (0.5, 0.5),
    "private_van_with_trailer": (0.5, 0.5),
    "truck_with_trailer": (0.5, 0.5),
    "delivery_van": (0.5, 0.5),
    "delivery_van_with_trailer": (0.5, 0.5),
    "truck_with_semitrailer": (0.5, 0.5),
    "other": (0.5, 0.5)
}

maincanvas = None
sliderobject = None

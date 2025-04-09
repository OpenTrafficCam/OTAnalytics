from enum import StrEnum


class OtcClasses(StrEnum):
    TRUCK_WITH_SEMITRAILER = "truck_with_semitrailer"
    DELIVERY_VAN_WITH_TRAILER = "delivery_van_with_trailer"
    DELIVERY_VAN = "delivery_van"
    TRUCK_WITH_TRAILER = "truck_with_trailer"
    PRIVATE_VAN_WITH_TRAILER = "private_van_with_trailer"
    CAR_WITH_TRAILER = "car_with_trailer"
    BICYCLIST_WITH_TRAILER = "bicyclist_with_trailer"
    CARGO_BIKE_DRIVER = "cargo_bike_driver"
    SCOOTER_DRIVER = "scooter_driver"
    TRUCK = "truck"
    TRAIN = "train"
    BUS = "bus"
    PRIVATE_VAN = "private_van"
    MOTORCYCLIST = "motorcyclist"
    CAR = "car"
    BICYCLIST = "bicyclist"
    PEDESTRIAN = "pedestrian"
    OTHER = "other"

from OTAnalytics.plugin_number_of_tracks_to_be_validated.otc_classes import OtcClasses

SVZ_CLASSIFICATION = {
    OtcClasses.BICYCLIST: {"Gruppe A3": 0.80},
    OtcClasses.CAR: {"Gruppe A3": 0.90},
    OtcClasses.MOTORCYCLIST: {"Gruppe A3": 0.80},
    OtcClasses.PRIVATE_VAN: {"Gruppe A3": 0.90},
    OtcClasses.BUS: {"Gruppe A3": 0.80},
    # OtcClasses.TRAIN: { "Gruppe A3": 0.0},
    OtcClasses.TRUCK: {"Gruppe A3": 0.80},
    OtcClasses.SCOOTER_DRIVER: {"Gruppe A3": 0.0},
    OtcClasses.CARGO_BIKE_DRIVER: {"Gruppe A3": 0.80},
    OtcClasses.BICYCLIST_WITH_TRAILER: {"Gruppe A3": 0.80},
    OtcClasses.CAR_WITH_TRAILER: {"Gruppe A3": 0.80},
    OtcClasses.PRIVATE_VAN_WITH_TRAILER: {"Gruppe A3": 0.80},
    OtcClasses.TRUCK_WITH_TRAILER: {"Gruppe A3": 0.85},
    OtcClasses.DELIVERY_VAN: {"Gruppe A3": 0.80},
    OtcClasses.DELIVERY_VAN_WITH_TRAILER: {"Gruppe A3": 0.85},
    OtcClasses.TRUCK_WITH_SEMITRAILER: {"Gruppe A3": 0.85},
    OtcClasses.OTHER: {"Gruppe A3": 0.0},
}

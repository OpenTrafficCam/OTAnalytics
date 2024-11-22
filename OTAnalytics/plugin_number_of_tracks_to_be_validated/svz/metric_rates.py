from OTAnalytics.plugin_number_of_tracks_to_be_validated.otc_classes import OtcClasses

SVZ_RATE = "svz-rate"

SVZ_CLASSIFICATION = {
    OtcClasses.BICYCLIST: {SVZ_RATE: 0.80},
    OtcClasses.CAR: {SVZ_RATE: 0.90},
    OtcClasses.MOTORCYCLIST: {SVZ_RATE: 0.80},
    OtcClasses.PRIVATE_VAN: {SVZ_RATE: 0.90},
    OtcClasses.BUS: {SVZ_RATE: 0.80},
    OtcClasses.TRAIN: {SVZ_RATE: 0.0},
    OtcClasses.TRUCK: {SVZ_RATE: 0.80},
    OtcClasses.SCOOTER_DRIVER: {SVZ_RATE: 0.0},
    OtcClasses.CARGO_BIKE_DRIVER: {SVZ_RATE: 0.80},
    OtcClasses.BICYCLIST_WITH_TRAILER: {SVZ_RATE: 0.80},
    OtcClasses.CAR_WITH_TRAILER: {SVZ_RATE: 0.80},
    OtcClasses.PRIVATE_VAN_WITH_TRAILER: {SVZ_RATE: 0.80},
    OtcClasses.TRUCK_WITH_TRAILER: {SVZ_RATE: 0.85},
    OtcClasses.DELIVERY_VAN: {SVZ_RATE: 0.80},
    OtcClasses.DELIVERY_VAN_WITH_TRAILER: {SVZ_RATE: 0.85},
    OtcClasses.TRUCK_WITH_SEMITRAILER: {SVZ_RATE: 0.85},
    OtcClasses.OTHER: {SVZ_RATE: 0.0},
}

from OTAnalytics.domain.otc_classes import OtcClasses
from OTAnalytics.domain.tls8plus1_classes import Tls8plus1Classes

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
    Tls8plus1Classes.OTHER: {SVZ_RATE: 0.00},
    Tls8plus1Classes.CAR: {SVZ_RATE: 0.90},
    Tls8plus1Classes.BICYCLIST: {SVZ_RATE: 0.80},
    Tls8plus1Classes.MOTORCYCLIST: {SVZ_RATE: 0.80},
    Tls8plus1Classes.CAR_WITH_TRAILER: {SVZ_RATE: 0.80},
    Tls8plus1Classes.TRUCK: {SVZ_RATE: 0.80},
    Tls8plus1Classes.TRUCK_WITH_TRAILER: {SVZ_RATE: 0.85},
    Tls8plus1Classes.TRUCK_WITH_SEMITRAILER: {SVZ_RATE: 0.85},
    Tls8plus1Classes.BUS: {SVZ_RATE: 0.80},
    Tls8plus1Classes.DELIVERY_VAN: {SVZ_RATE: 0.80},
}

from OTAnalytics.application.analysis.traffic_statistics.speed_values import (
    SpeedValues,
    compute_speed_values,
)


def test_twenty_speeds_give_exact_v85() -> None:
    assert compute_speed_values([s + 0.2 for s in range(30, 50)]) == SpeedValues(
        avg=39.7, v85=46.2, count=20
    )


def test_v85_is_a_measured_speed() -> None:
    assert compute_speed_values([30.0, 50.0]) == SpeedValues(
        avg=40.0, v85=50.0, count=2
    )


def test_single_speed() -> None:
    assert compute_speed_values([69.97]) == SpeedValues(avg=70.0, v85=70.0, count=1)


def test_no_speeds_give_none() -> None:
    assert compute_speed_values([]) is None

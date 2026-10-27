from OTAnalytics.application.analysis.traffic_statistics.speed_histogram import (
    SpeedHistogram,
    SpeedValues,
)


def test_values_of_twenty_speeds_returns_avg_and_v85() -> None:
    target = SpeedHistogram()
    for speed in range(30, 50):
        target.add(speed + 0.2)

    assert target.values() == SpeedValues(avg=39.7, v85=46.5, count=20)


def test_empty_histogram_returns_none() -> None:
    assert SpeedHistogram().values() is None


def test_merge_combines_counts() -> None:
    a, b = SpeedHistogram(), SpeedHistogram()
    a.add(30.0)
    b.add(50.0)

    assert a.merge(b).values() == SpeedValues(avg=40.0, v85=50.5, count=2)


def test_merge_does_not_mutate_inputs() -> None:
    a, b = SpeedHistogram(), SpeedHistogram()
    a.add(30.0)
    b.add(50.0)

    merged = a.merge(b)

    assert merged is not a
    assert merged is not b
    assert a.count == 1
    assert b.count == 1
    assert a.bins == {30: 1}
    assert b.bins == {50: 1}


def test_single_value_avg_and_v85() -> None:
    target = SpeedHistogram()
    target.add(42.9)

    assert target.values() == SpeedValues(avg=42.9, v85=42.5, count=1)


def test_count_and_bins_expose_data() -> None:
    target = SpeedHistogram()
    target.add(30.5)
    target.add(30.9)
    target.add(31.0)

    assert target.count == 3
    assert target.bins == {30: 2, 31: 1}


def test_restore_from_bins_and_total_speed() -> None:
    restored = SpeedHistogram(bins={30: 2, 31: 1}, total_speed=92.4)

    assert restored.count == 3
    assert restored.bins == {30: 2, 31: 1}
    assert restored.total_speed == 92.4
    assert restored.values() == SpeedValues(avg=30.8, v85=31.5, count=3)

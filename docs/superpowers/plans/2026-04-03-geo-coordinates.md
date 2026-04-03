# Geo Coordinates Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thread optional `geo_x`/`geo_y` fields from ottrk/feathers files through detections, track segments, intersection calculations, events, and CSV export.

**Architecture:** Thin optional fields follow the existing `x/y/w/h` pattern at every layer. Paired-presence checks (`if GEO_X in cols and GEO_Y in cols`) gate all computation and export logic so files without geo data are unaffected. Cutting always uses pixel coordinates; geo coordinates are linearly interpolated at the intersection point using the existing `RELATIVE_POSITION` scalar.

**Tech Stack:** Python 3.11+, Polars, Pandas, pytest

---

## File Map

| File | Change |
|---|---|
| `OTAnalytics/domain/track.py` | Add `GEO_X`/`GEO_Y` constants + abstract properties on `Detection` |
| `OTAnalytics/domain/event.py` | Add `GEO_X`/`GEO_Y` constants, optional `Event` fields, `EventBuilder.add_geo_coordinate` |
| `OTAnalytics/plugin_datastore/python_track_store.py` | `PythonDetection`: add `_geo_x`/`_geo_y` optional fields |
| `OTAnalytics/plugin_datastore/track_store.py` | `PandasDetection`: add `geo_x`/`geo_y` with index-check fallback |
| `OTAnalytics/plugin_datastore/polars_track_store.py` | `PolarsDetection`: add `geo_x`/`geo_y` using `dict.get()` |
| `OTAnalytics/plugin_parser/ottrk_dataformat.py` | Add `GEO_X`/`GEO_Y` constants |
| `OTAnalytics/plugin_parser/pandas_parser.py` | Conditionally rename geo columns after main rename block |
| `OTAnalytics/domain/track_dataset/track_dataset.py` | Add `START_GEO_X/Y`, `END_GEO_X/Y` constants |
| `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py` | Add `INTERPOLATED_GEO_X/Y` constants; propagate geo in `create_track_segments`; pass through in `find_line_intersections`; interpolate in intersection block; compute in `create_events()`; pass to `PolarsEventDataset` |
| `OTAnalytics/application/export_formats/event_list.py` | Add `GEO_X`/`GEO_Y` export constants |
| `OTAnalytics/plugin_prototypes/eventlist_exporter/eventlist_exporter.py` | Add geo rounding config; conditionally include geo columns in export |
| `tests/utils/builders/track_builder.py` | Add `geo_x`/`geo_y` fields; pass through to `PythonDetection` |
| `tests/utils/builders/event_builder.py` | Add `geo_x`/`geo_y` fields; pass through to `Event` |
| `tests/unit/OTAnalytics/domain/test_track.py` | Test `Detection.geo_x`/`geo_y` abstract properties |
| `tests/unit/OTAnalytics/domain/test_event.py` | Test `Event` geo fields + `EventBuilder.add_geo_coordinate` |
| `tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py` | Test `PythonDetection` geo fields |
| `tests/unit/OTAnalytics/plugin_datastore/test_track_store.py` | Test `PandasDetection` geo fields |
| `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py` | Test `PolarsDetection` geo fields |
| `tests/unit/OTAnalytics/plugin_parser/test_pandas_parser.py` | Test geo column mapping |
| `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py` | Test segment propagation, passthrough, interpolation, create_events |
| `tests/unit/OTAnalytics/plugin_prototypes/test_eventlist_exporter.py` | Test geo columns in export |

---

### Task 1: Domain constants + `Detection` abstract interface

**Files:**
- Modify: `OTAnalytics/domain/track.py`
- Test: `tests/unit/OTAnalytics/domain/test_track.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/OTAnalytics/domain/test_track.py`:

```python
from dataclasses import dataclass
from unittest.mock import Mock

from OTAnalytics.domain.track import GEO_X, GEO_Y, Detection


@dataclass
class Given:
    detection: Detection


def create_given() -> Given:
    detection = Mock(spec=Detection)
    detection.geo_x = 449245.82
    detection.geo_y = 5699325.96
    return Given(detection=detection)


class TestDetectionGeoCoordinates:
    def test_geo_x_constant_value(self) -> None:
        assert GEO_X == "geo_x"

    def test_geo_y_constant_value(self) -> None:
        assert GEO_Y == "geo_y"

    def test_geo_x_accessible_on_detection(self) -> None:
        given = create_given()
        assert given.detection.geo_x == 449245.82

    def test_geo_y_accessible_on_detection(self) -> None:
        given = create_given()
        assert given.detection.geo_y == 5699325.96
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/domain/test_track.py::TestDetectionGeoCoordinates -v
```

Expected: FAIL — `ImportError: cannot import name 'GEO_X' from 'OTAnalytics.domain.track'`

- [ ] **Step 3: Implement**

In `OTAnalytics/domain/track.py`, after the existing constants block (after line 22, `INPUT_FILE: str = "input_file"`):

```python
GEO_X: str = "geo_x"
GEO_Y: str = "geo_y"
```

Then in the `Detection` ABC, after the `input_file` abstract property (after line 115):

```python
@property
@abstractmethod
def geo_x(self) -> float | None:
    raise NotImplementedError

@property
@abstractmethod
def geo_y(self) -> float | None:
    raise NotImplementedError
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/domain/test_track.py::TestDetectionGeoCoordinates -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/domain/track.py tests/unit/OTAnalytics/domain/test_track.py
git commit -m "feat: add GEO_X/GEO_Y constants and abstract properties to Detection"
```

---

### Task 2: `Event` geo fields + `EventBuilder.add_geo_coordinate`

**Files:**
- Modify: `OTAnalytics/domain/event.py`
- Test: `tests/unit/OTAnalytics/domain/test_event.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/OTAnalytics/domain/test_event.py`:

```python
from dataclasses import dataclass
from OTAnalytics.domain.event import GEO_X, GEO_Y, Event, SectionEventBuilder


@dataclass
class GeoEventGiven:
    geo_x: float
    geo_y: float


def create_geo_event_given() -> GeoEventGiven:
    return GeoEventGiven(geo_x=449245.82, geo_y=5699325.96)


class TestEventGeoCoordinates:
    def test_event_geo_x_defaults_to_none(self, valid_detection) -> None:
        # valid_detection fixture already exists in test_event.py
        builder = SectionEventBuilder()
        builder.add_road_user_id("1")
        builder.add_road_user_type("car")
        builder.add_event_coordinate(0.0, 0.0)
        builder.add_direction_vector(1.0, 0.0)
        builder.add_event_type("section-enter")
        builder.add_section_id("s1")
        builder.add_interpolated_occurrence(valid_detection.occurrence)
        builder.add_interpolated_event_coordinate(0.0, 0.0)
        event = builder.build(valid_detection)
        assert event.geo_x is None
        assert event.geo_y is None

    def test_event_carries_geo_coordinates(self, valid_detection) -> None:
        given = create_geo_event_given()
        builder = SectionEventBuilder()
        builder.add_road_user_id("1")
        builder.add_road_user_type("car")
        builder.add_event_coordinate(0.0, 0.0)
        builder.add_direction_vector(1.0, 0.0)
        builder.add_event_type("section-enter")
        builder.add_section_id("s1")
        builder.add_interpolated_occurrence(valid_detection.occurrence)
        builder.add_interpolated_event_coordinate(0.0, 0.0)
        builder.add_geo_coordinate(given.geo_x, given.geo_y)
        event = builder.build(valid_detection)
        assert event.geo_x == given.geo_x
        assert event.geo_y == given.geo_y

    def test_geo_x_constant(self) -> None:
        assert GEO_X == "geo_x"

    def test_geo_y_constant(self) -> None:
        assert GEO_Y == "geo_y"

    def test_to_dict_includes_geo_coordinates(self, valid_detection) -> None:
        given = create_geo_event_given()
        builder = SectionEventBuilder()
        builder.add_road_user_id("1")
        builder.add_road_user_type("car")
        builder.add_event_coordinate(0.0, 0.0)
        builder.add_direction_vector(1.0, 0.0)
        builder.add_event_type("section-enter")
        builder.add_section_id("s1")
        builder.add_interpolated_occurrence(valid_detection.occurrence)
        builder.add_interpolated_event_coordinate(0.0, 0.0)
        builder.add_geo_coordinate(given.geo_x, given.geo_y)
        event = builder.build(valid_detection)
        d = event.to_dict()
        assert d[GEO_X] == given.geo_x
        assert d[GEO_Y] == given.geo_y
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/domain/test_event.py::TestEventGeoCoordinates -v
```

Expected: FAIL — `ImportError: cannot import name 'GEO_X' from 'OTAnalytics.domain.event'`

- [ ] **Step 3: Implement**

In `OTAnalytics/domain/event.py`:

Add after the existing constants (after line 28, `INTERPOLATED_EVENT_COORDINATE`):
```python
GEO_X: str = "geo_x"
GEO_Y: str = "geo_y"
```

Add optional fields to `Event` dataclass (after `interpolated_event_coordinate: ImageCoordinate` on line 96):
```python
geo_x: float | None = None
geo_y: float | None = None
```

Update `to_dict()` (after `INTERPOLATED_EVENT_COORDINATE` line in the return dict):
```python
GEO_X: self.geo_x,
GEO_Y: self.geo_y,
```

Update `to_typed_dict()` the same way (it has the same structure).

Add method to `EventBuilder` class (after `add_interpolated_event_coordinate`):
```python
def add_geo_coordinate(
    self, geo_x: float | None, geo_y: float | None
) -> None:
    """Add geo coordinates to the event to be built.

    Args:
        geo_x: the geo x coordinate, or None if unavailable.
        geo_y: the geo y coordinate, or None if unavailable.
    """
    self.geo_x = geo_x
    self.geo_y = geo_y
```

Add `geo_x: float | None = None` and `geo_y: float | None = None` instance variables to `EventBuilder.__init__` (after `self.interpolated_event_coordinate`).

Pass them through in the `build()` call inside `SectionEventBuilder` and `SceneEventBuilder`:
```python
Event(
    ...,
    geo_x=self.geo_x,
    geo_y=self.geo_y,
)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/domain/test_event.py::TestEventGeoCoordinates -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/domain/event.py tests/unit/OTAnalytics/domain/test_event.py
git commit -m "feat: add optional geo_x/geo_y fields to Event and EventBuilder"
```

---

### Task 3: Update test helpers `TrackBuilder` and `EventBuilder`

**Files:**
- Modify: `tests/utils/builders/track_builder.py`
- Modify: `tests/utils/builders/event_builder.py`

These are test helpers only — no failing test step needed. Update them so later tasks can build geo-aware test data.

- [ ] **Step 1: Update `TrackBuilder`**

In `tests/utils/builders/track_builder.py`, add fields after `interpolated_detection`:
```python
geo_x: float | None = None
geo_y: float | None = None
```

Update `create_detection()` to pass them to `PythonDetection`:
```python
def create_detection(self) -> Detection:
    return PythonDetection(
        _classification=self.detection_class,
        _confidence=self.confidence,
        _x=float(self.x),
        _y=float(self.y),
        _w=float(self.w),
        _h=float(self.h),
        _frame=self.frame,
        _occurrence=datetime(
            self.occurrence_year,
            self.occurrence_month,
            self.occurrence_day,
            self.occurrence_hour,
            self.occurrence_minute,
            self.occurrence_second,
            self.occurrence_microsecond,
            tzinfo=timezone.utc,
        ),
        _interpolated_detection=self.interpolated_detection,
        _track_id=TrackId(self.track_id),
        _video_name=self.video_name,
        _input_file=self.input_file,
        _geo_x=self.geo_x,
        _geo_y=self.geo_y,
    )
```

- [ ] **Step 2: Update `EventBuilder`**

In `tests/utils/builders/event_builder.py`, add fields after `interpolated_event_coordinate`:
```python
geo_x: float | None = None
geo_y: float | None = None
```

Update `build_section_event()` to pass them to `Event`:
```python
return Event(
    ...,  # all existing fields unchanged
    geo_x=self.geo_x,
    geo_y=self.geo_y,
)
```

- [ ] **Step 3: Run existing tests to verify no regressions**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py tests/unit/OTAnalytics/domain/test_event.py -v
```

Expected: PASS (all existing tests still pass)

- [ ] **Step 4: Commit**

```bash
git add tests/utils/builders/track_builder.py tests/utils/builders/event_builder.py
git commit -m "feat: add geo_x/geo_y fields to TrackBuilder and EventBuilder test helpers"
```

---

### Task 4: `PythonDetection` geo fields

**Files:**
- Modify: `OTAnalytics/plugin_datastore/python_track_store.py`
- Test: `tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py`:

```python
from dataclasses import dataclass
from OTAnalytics.plugin_datastore.python_track_store import PythonDetection
from tests.utils.builders.track_builder import TrackBuilder


@dataclass
class PythonDetectionGeoGiven:
    detection_with_geo: PythonDetection
    detection_without_geo: PythonDetection


def create_python_detection_geo_given() -> PythonDetectionGeoGiven:
    builder_with = TrackBuilder(geo_x=449245.82, geo_y=5699325.96)
    builder_with.append_detection()
    builder_without = TrackBuilder()
    builder_without.append_detection()
    return PythonDetectionGeoGiven(
        detection_with_geo=builder_with.build_detections()[0],
        detection_without_geo=builder_without.build_detections()[0],
    )


class TestPythonDetectionGeoCoordinates:
    def test_geo_x_returns_value_when_set(self) -> None:
        given = create_python_detection_geo_given()
        assert given.detection_with_geo.geo_x == 449245.82

    def test_geo_y_returns_value_when_set(self) -> None:
        given = create_python_detection_geo_given()
        assert given.detection_with_geo.geo_y == 5699325.96

    def test_geo_x_returns_none_when_not_set(self) -> None:
        given = create_python_detection_geo_given()
        assert given.detection_without_geo.geo_x is None

    def test_geo_y_returns_none_when_not_set(self) -> None:
        given = create_python_detection_geo_given()
        assert given.detection_without_geo.geo_y is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py::TestPythonDetectionGeoCoordinates -v
```

Expected: FAIL — `TypeError: PythonDetection.__init__() got an unexpected keyword argument '_geo_x'`

- [ ] **Step 3: Implement**

In `OTAnalytics/plugin_datastore/python_track_store.py`, add optional fields to `PythonDetection` after `_is_finished`:

```python
_geo_x: float | None = None
_geo_y: float | None = None
```

Add properties after the `input_file` property:

```python
@property
def geo_x(self) -> float | None:
    return self._geo_x

@property
def geo_y(self) -> float | None:
    return self._geo_y
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py::TestPythonDetectionGeoCoordinates -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/python_track_store.py tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py
git commit -m "feat: add optional geo_x/geo_y fields to PythonDetection"
```

---

### Task 5: `PandasDetection` geo fields

**Files:**
- Modify: `OTAnalytics/plugin_datastore/track_store.py`
- Test: `tests/unit/OTAnalytics/plugin_datastore/test_track_store.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/OTAnalytics/plugin_datastore/test_track_store.py`:

```python
from dataclasses import dataclass
import pandas as pd
from OTAnalytics.domain import track
from OTAnalytics.plugin_datastore.track_store import PandasDetection
from datetime import datetime, timezone


@dataclass
class PandasDetectionGeoGiven:
    detection_with_geo: PandasDetection
    detection_without_geo: PandasDetection


def create_pandas_detection_geo_given() -> PandasDetectionGeoGiven:
    data_with = pd.Series(
        {
            track.CLASSIFICATION: "car",
            track.CONFIDENCE: 0.9,
            track.X: 100.0,
            track.Y: 200.0,
            track.W: 0.0,
            track.H: 0.0,
            track.FRAME: 1,
            track.INTERPOLATED_DETECTION: False,
            track.VIDEO_NAME: "cam.mp4",
            track.INPUT_FILE: "cam.otdet",
            track.GEO_X: 449245.82,
            track.GEO_Y: 5699325.96,
        },
        name=(datetime(2024, 1, 1, tzinfo=timezone.utc),),
    )
    data_without = pd.Series(
        {
            track.CLASSIFICATION: "car",
            track.CONFIDENCE: 0.9,
            track.X: 100.0,
            track.Y: 200.0,
            track.W: 0.0,
            track.H: 0.0,
            track.FRAME: 1,
            track.INTERPOLATED_DETECTION: False,
            track.VIDEO_NAME: "cam.mp4",
            track.INPUT_FILE: "cam.otdet",
        },
        name=(datetime(2024, 1, 1, tzinfo=timezone.utc),),
    )
    return PandasDetectionGeoGiven(
        detection_with_geo=PandasDetection("track-1", data_with),
        detection_without_geo=PandasDetection("track-1", data_without),
    )


class TestPandasDetectionGeoCoordinates:
    def test_geo_x_returns_value_when_column_present(self) -> None:
        given = create_pandas_detection_geo_given()
        assert given.detection_with_geo.geo_x == 449245.82

    def test_geo_y_returns_value_when_column_present(self) -> None:
        given = create_pandas_detection_geo_given()
        assert given.detection_with_geo.geo_y == 5699325.96

    def test_geo_x_returns_none_when_column_absent(self) -> None:
        given = create_pandas_detection_geo_given()
        assert given.detection_without_geo.geo_x is None

    def test_geo_y_returns_none_when_column_absent(self) -> None:
        given = create_pandas_detection_geo_given()
        assert given.detection_without_geo.geo_y is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/test_track_store.py::TestPandasDetectionGeoCoordinates -v
```

Expected: FAIL — `AttributeError: 'PandasDetection' object has no attribute 'geo_x'`

- [ ] **Step 3: Implement**

In `OTAnalytics/plugin_datastore/track_store.py`, add after the `input_file` property of `PandasDetection` (after line 114):

```python
@property
def geo_x(self) -> float | None:
    if track.GEO_X not in self._data.index:
        return None
    return self.__get_attribute(track.GEO_X)

@property
def geo_y(self) -> float | None:
    if track.GEO_Y not in self._data.index:
        return None
    return self.__get_attribute(track.GEO_Y)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/test_track_store.py::TestPandasDetectionGeoCoordinates -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/track_store.py tests/unit/OTAnalytics/plugin_datastore/test_track_store.py
git commit -m "feat: add optional geo_x/geo_y to PandasDetection with index-check fallback"
```

---

### Task 6: `PolarsDetection` geo fields

**Files:**
- Modify: `OTAnalytics/plugin_datastore/polars_track_store.py`
- Test: `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`:

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from OTAnalytics.domain import track
from OTAnalytics.plugin_datastore.polars_track_store import PolarsDetection


@dataclass
class PolarsDetectionGeoGiven:
    detection_with_geo: PolarsDetection
    detection_without_geo: PolarsDetection


def create_polars_detection_geo_given() -> PolarsDetectionGeoGiven:
    occurrence = datetime(2024, 1, 1, tzinfo=timezone.utc)
    row_with = {
        track.CLASSIFICATION: "car",
        track.CONFIDENCE: 0.9,
        track.X: 100.0,
        track.Y: 200.0,
        track.W: 0.0,
        track.H: 0.0,
        track.FRAME: 1,
        track.INTERPOLATED_DETECTION: False,
        track.VIDEO_NAME: "cam.mp4",
        track.INPUT_FILE: "cam.otdet",
        track.GEO_X: 449245.82,
        track.GEO_Y: 5699325.96,
    }
    row_without = {k: v for k, v in row_with.items() if k not in (track.GEO_X, track.GEO_Y)}
    return PolarsDetectionGeoGiven(
        detection_with_geo=PolarsDetection("track-1", row_with, occurrence),
        detection_without_geo=PolarsDetection("track-1", row_without, occurrence),
    )


class TestPolarsDetectionGeoCoordinates:
    def test_geo_x_returns_value_when_key_present(self) -> None:
        given = create_polars_detection_geo_given()
        assert given.detection_with_geo.geo_x == 449245.82

    def test_geo_y_returns_value_when_key_present(self) -> None:
        given = create_polars_detection_geo_given()
        assert given.detection_with_geo.geo_y == 5699325.96

    def test_geo_x_returns_none_when_key_absent(self) -> None:
        given = create_polars_detection_geo_given()
        assert given.detection_without_geo.geo_x is None

    def test_geo_y_returns_none_when_key_absent(self) -> None:
        given = create_polars_detection_geo_given()
        assert given.detection_without_geo.geo_y is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsDetectionGeoCoordinates -v
```

Expected: FAIL — `AttributeError: 'PolarsDetection' object has no attribute 'geo_x'`

- [ ] **Step 3: Implement**

In `OTAnalytics/plugin_datastore/polars_track_store.py`, add after the `input_file` property of `PolarsDetection`:

```python
@property
def geo_x(self) -> float | None:
    return self._data.get(track.GEO_X)

@property
def geo_y(self) -> float | None:
    return self._data.get(track.GEO_Y)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsDetectionGeoCoordinates -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/polars_track_store.py tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py
git commit -m "feat: add optional geo_x/geo_y to PolarsDetection using dict.get() fallback"
```

---

### Task 7: ottrk format constants + `PandasDetectionParser` geo mapping

**Files:**
- Modify: `OTAnalytics/plugin_parser/ottrk_dataformat.py`
- Modify: `OTAnalytics/plugin_parser/pandas_parser.py`
- Test: `tests/unit/OTAnalytics/plugin_parser/test_pandas_parser.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/OTAnalytics/plugin_parser/test_pandas_parser.py`:

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import Mock

from OTAnalytics.domain import track
from OTAnalytics.plugin_parser import ottrk_dataformat
from OTAnalytics.plugin_parser.otvision_parser import DEFAULT_TRACK_LENGTH_LIMIT
from OTAnalytics.plugin_datastore.track_store import PandasByMaxConfidence
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser


GEO_X_VALUE = 449245.82
GEO_Y_VALUE = 5699325.96

SAMPLE_METADATA_VIDEO = {
    ottrk_dataformat.FILENAME: "cam",
    ottrk_dataformat.FILETYPE: ".mp4",
}


@dataclass
class GeoParserGiven:
    parser: PandasDetectionParser
    detections_with_geo: list[dict]
    detections_without_geo: list[dict]


def _make_detection(frame: int, track_id: int, **extra: object) -> dict:
    return {
        ottrk_dataformat.CLASS: "car",
        ottrk_dataformat.CONFIDENCE: 0.9,
        ottrk_dataformat.X: float(frame * 10),
        ottrk_dataformat.Y: float(frame * 10),
        ottrk_dataformat.W: 0.0,
        ottrk_dataformat.H: 0.0,
        ottrk_dataformat.FRAME: frame,
        ottrk_dataformat.OCCURRENCE: float(1_700_000_000 + frame),
        ottrk_dataformat.INTERPOLATED_DETECTION: False,
        ottrk_dataformat.TRACK_ID: track_id,
        **extra,
    }


def create_geo_parser_given() -> GeoParserGiven:
    parser = PandasDetectionParser(
        PandasByMaxConfidence(),
        ShapelyTrackGeometryDataset.from_track_dataset,
        track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
    )
    detections_with_geo = [
        _make_detection(
            frame=i,
            track_id=1,
            **{ottrk_dataformat.GEO_X: GEO_X_VALUE, ottrk_dataformat.GEO_Y: GEO_Y_VALUE},
        )
        for i in range(1, 5)
    ]
    detections_without_geo = [
        _make_detection(frame=i, track_id=1) for i in range(1, 5)
    ]
    return GeoParserGiven(
        parser=parser,
        detections_with_geo=detections_with_geo,
        detections_without_geo=detections_without_geo,
    )


class TestPandasDetectionParserGeoCoordinates:
    def test_geo_coordinates_mapped_when_present(self) -> None:
        given = create_geo_parser_given()
        result = given.parser.parse_tracks(
            given.detections_with_geo, SAMPLE_METADATA_VIDEO, "cam.ottrk"
        )
        tracks = result.as_list()
        assert len(tracks) == 1
        first_detection = tracks[0].detections[0]
        assert first_detection.geo_x == GEO_X_VALUE
        assert first_detection.geo_y == GEO_Y_VALUE

    def test_geo_coordinates_absent_when_not_in_source(self) -> None:
        given = create_geo_parser_given()
        result = given.parser.parse_tracks(
            given.detections_without_geo, SAMPLE_METADATA_VIDEO, "cam.ottrk"
        )
        tracks = result.as_list()
        assert len(tracks) == 1
        first_detection = tracks[0].detections[0]
        assert first_detection.geo_x is None
        assert first_detection.geo_y is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/plugin_parser/test_pandas_parser.py::TestPandasDetectionParserGeoCoordinates -v
```

Expected: FAIL — `ImportError: cannot import name 'GEO_X' from 'OTAnalytics.plugin_parser.ottrk_dataformat'`

- [ ] **Step 3: Implement**

In `OTAnalytics/plugin_parser/ottrk_dataformat.py`, add after the existing constants:

```python
GEO_X: str = "geo_x"
GEO_Y: str = "geo_y"
```

In `OTAnalytics/plugin_parser/pandas_parser.py`, in `_parse_as_dataframe`, add after the existing `data.rename(...)` block (after line 85):

```python
if (
    ottrk_format.GEO_X in data.columns
    and ottrk_format.GEO_Y in data.columns
):
    data.rename(
        columns={
            ottrk_format.GEO_X: track.GEO_X,
            ottrk_format.GEO_Y: track.GEO_Y,
        },
        inplace=True,
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/plugin_parser/test_pandas_parser.py::TestPandasDetectionParserGeoCoordinates -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_parser/ottrk_dataformat.py OTAnalytics/plugin_parser/pandas_parser.py tests/unit/OTAnalytics/plugin_parser/test_pandas_parser.py
git commit -m "feat: map geo_x/geo_y columns in PandasDetectionParser when present in ottrk"
```

---

### Task 8: Segment constants + `create_track_segments` geo propagation

**Files:**
- Modify: `OTAnalytics/domain/track_dataset/track_dataset.py`
- Modify: `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`
- Test: `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`:

```python
from dataclasses import dataclass
from datetime import datetime
import polars as pl
from OTAnalytics.domain import track
from OTAnalytics.domain.track_dataset.track_dataset import (
    START_GEO_X, START_GEO_Y, END_GEO_X, END_GEO_Y,
)
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    OCCURRENCE, ROW_ID, TRACK_ID, TRACK_CLASSIFICATION, VIDEO_NAME,
    X, Y, W, H, create_track_segments,
)
from OTAnalytics.domain.track import FRAME


@dataclass
class SegmentGeoGiven:
    df_with_geo: pl.DataFrame
    df_without_geo: pl.DataFrame


def create_segment_geo_given() -> SegmentGeoGiven:
    base = {
        ROW_ID: [1, 2, 3],
        TRACK_ID: ["t1", "t1", "t1"],
        TRACK_CLASSIFICATION: ["car", "car", "car"],
        X: [10.0, 20.0, 30.0],
        Y: [10.0, 20.0, 30.0],
        W: [0.0, 0.0, 0.0],
        H: [0.0, 0.0, 0.0],
        FRAME: [1, 2, 3],
        OCCURRENCE: [
            datetime(2024, 1, 1, 0, 0, 0),
            datetime(2024, 1, 1, 0, 0, 1),
            datetime(2024, 1, 1, 0, 0, 2),
        ],
        VIDEO_NAME: ["cam.mp4", "cam.mp4", "cam.mp4"],
    }
    df_without_geo = pl.DataFrame(base)
    df_with_geo = df_without_geo.with_columns([
        pl.Series(track.GEO_X, [449200.0, 449210.0, 449220.0]),
        pl.Series(track.GEO_Y, [5699300.0, 5699310.0, 5699320.0]),
    ])
    return SegmentGeoGiven(df_with_geo=df_with_geo, df_without_geo=df_without_geo)


class TestCreateTrackSegmentsGeoCoordinates:
    def test_segments_include_geo_columns_when_both_present(self) -> None:
        given = create_segment_geo_given()
        result = create_track_segments(given.df_with_geo)
        assert START_GEO_X in result.columns
        assert START_GEO_Y in result.columns
        assert END_GEO_X in result.columns
        assert END_GEO_Y in result.columns

    def test_start_geo_x_is_previous_row_geo_x(self) -> None:
        given = create_segment_geo_given()
        result = create_track_segments(given.df_with_geo)
        # First segment: start=row0, end=row1
        assert result[START_GEO_X][0] == 449200.0
        assert result[END_GEO_X][0] == 449210.0

    def test_segments_omit_geo_columns_when_absent(self) -> None:
        given = create_segment_geo_given()
        result = create_track_segments(given.df_without_geo)
        assert START_GEO_X not in result.columns
        assert END_GEO_X not in result.columns

    def test_segments_omit_geo_columns_when_only_geo_x_present(self) -> None:
        given = create_segment_geo_given()
        df_only_x = given.df_with_geo.drop(track.GEO_Y)
        result = create_track_segments(df_only_x)
        assert START_GEO_X not in result.columns
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestCreateTrackSegmentsGeoCoordinates -v
```

Expected: FAIL — `ImportError: cannot import name 'START_GEO_X' from 'OTAnalytics.domain.track_dataset.track_dataset'`

- [ ] **Step 3: Implement**

In `OTAnalytics/domain/track_dataset/track_dataset.py`, add after `PREVIOUS_Y`:

```python
START_GEO_X: str = "start_geo_x"
START_GEO_Y: str = "start_geo_y"
END_GEO_X: str = "end_geo_x"
END_GEO_Y: str = "end_geo_y"
```

In `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`:

Add to imports from `track_dataset`:
```python
from OTAnalytics.domain.track_dataset.track_dataset import (
    ...,  # existing imports
    START_GEO_X,
    START_GEO_Y,
    END_GEO_X,
    END_GEO_Y,
)
```

In `create_track_segments`, after the existing `segments = df_sorted.with_columns([...]).drop_nulls()` block, add:

```python
if track.GEO_X in df.columns and track.GEO_Y in df.columns:
    segments = segments.with_columns(
        [
            pl.col(track.GEO_X).alias(END_GEO_X),
            pl.col(track.GEO_Y).alias(END_GEO_Y),
            pl.col(track.GEO_X).shift(1).over(TRACK_ID).alias(START_GEO_X),
            pl.col(track.GEO_Y).shift(1).over(TRACK_ID).alias(START_GEO_Y),
        ]
    ).drop_nulls(subset=[START_GEO_X, START_GEO_Y])
```

Update the final `segments.select([...])` to conditionally include geo columns:

```python
geo_cols = (
    [END_GEO_X, END_GEO_Y, START_GEO_X, START_GEO_Y]
    if START_GEO_X in segments.columns and START_GEO_Y in segments.columns
    else []
)
segments = segments.select(
    [
        ROW_ID,
        TRACK_ID,
        TRACK_CLASSIFICATION,
        END_VIDEO_NAME,
        END_FRAME,
        END_OCCURRENCE,
        END_X,
        END_Y,
        END_W,
        END_H,
        START_OCCURRENCE,
        START_X,
        START_Y,
        START_W,
        START_H,
    ]
    + geo_cols
)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestCreateTrackSegmentsGeoCoordinates -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/domain/track_dataset/track_dataset.py OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py
git commit -m "feat: propagate START/END_GEO_X/Y in create_track_segments when geo columns present"
```

---

### Task 9: `find_line_intersections` geo column passthrough

**Files:**
- Modify: `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`
- Test: `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`

- [ ] **Step 1: Write the failing test**

Add to `test_polars_geometry_store.py`:

```python
from OTAnalytics.domain.track_dataset.track_dataset import (
    START_GEO_X, START_GEO_Y, END_GEO_X, END_GEO_Y,
)
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate


@dataclass
class LineIntersectionGeoGiven:
    segments_with_geo: pl.DataFrame
    segments_without_geo: pl.DataFrame


def create_line_intersection_geo_given() -> LineIntersectionGeoGiven:
    base = {
        ROW_ID: [1],
        TRACK_ID: ["t1"],
        TRACK_CLASSIFICATION: ["car"],
        END_VIDEO_NAME: ["cam.mp4"],
        END_FRAME: [2],
        START_X: [0.0],
        START_Y: [5.0],
        END_X: [10.0],
        END_Y: [5.0],
        START_W: [0.0],
        START_H: [0.0],
        END_W: [0.0],
        END_H: [0.0],
        START_OCCURRENCE: [datetime(2024, 1, 1, 0, 0, 0)],
        END_OCCURRENCE: [datetime(2024, 1, 1, 0, 0, 1)],
    }
    without_geo = pl.DataFrame(base)
    with_geo = without_geo.with_columns([
        pl.Series(START_GEO_X, [449200.0]),
        pl.Series(START_GEO_Y, [5699300.0]),
        pl.Series(END_GEO_X, [449210.0]),
        pl.Series(END_GEO_Y, [5699310.0]),
    ])
    return LineIntersectionGeoGiven(
        segments_with_geo=with_geo,
        segments_without_geo=without_geo,
    )


class TestFindLineIntersectionsGeoPassthrough:
    def test_geo_columns_present_in_output_when_present_in_input(self) -> None:
        given = create_line_intersection_geo_given()
        result = find_line_intersections(
            given.segments_with_geo,
            "line-1",
            5.0, 0.0, 5.0, 10.0,
            RelativeOffsetCoordinate(0.0, 0.0),
        )
        assert START_GEO_X in result.columns
        assert START_GEO_Y in result.columns
        assert END_GEO_X in result.columns
        assert END_GEO_Y in result.columns

    def test_geo_columns_absent_from_output_when_absent_in_input(self) -> None:
        given = create_line_intersection_geo_given()
        result = find_line_intersections(
            given.segments_without_geo,
            "line-1",
            5.0, 0.0, 5.0, 10.0,
            RelativeOffsetCoordinate(0.0, 0.0),
        )
        assert START_GEO_X not in result.columns
        assert END_GEO_X not in result.columns
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestFindLineIntersectionsGeoPassthrough -v
```

Expected: FAIL — `AssertionError: assert 'start_geo_x' in [...]`

- [ ] **Step 3: Implement**

In `find_line_intersections` in `polars_geometry_store.py`, replace the fixed `select([...])` list with a conditional version:

```python
geo_cols = (
    [START_GEO_X, START_GEO_Y, END_GEO_X, END_GEO_Y]
    if START_GEO_X in segments_df.columns and START_GEO_Y in segments_df.columns
    else []
)
result_df = result_df.select(
    [
        ROW_ID,
        TRACK_ID,
        TRACK_CLASSIFICATION,
        END_VIDEO_NAME,
        END_FRAME,
        START_X,
        START_Y,
        END_X,
        END_Y,
        START_W,
        START_H,
        END_W,
        END_H,
        START_OCCURRENCE,
        END_OCCURRENCE,
        INTERSECTS,
        INTERSECTION_X,
        INTERSECTION_Y,
        INTERSECTION_LINE_ID,
    ]
    + geo_cols
)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestFindLineIntersectionsGeoPassthrough -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py
git commit -m "feat: pass through START/END_GEO_X/Y in find_line_intersections output"
```

---

### Task 10: Geo interpolation at intersection point

**Files:**
- Modify: `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`
- Test: `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`

- [ ] **Step 1: Write the failing test**

Add to `test_polars_geometry_store.py`:

```python
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    INTERPOLATED_GEO_X,
    INTERPOLATED_GEO_Y,
    PolarsTrackGeometryDataset,
)
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import LineSection, SectionId


@dataclass
class GeoInterpolationGiven:
    dataset_with_geo: PolarsTrackGeometryDataset
    dataset_without_geo: PolarsTrackGeometryDataset
    section: LineSection


def create_geo_interpolation_given() -> GeoInterpolationGiven:
    offset = RelativeOffsetCoordinate(0.0, 0.0)
    # Track goes horizontally from (0,5) to (10,5)
    # Section cuts vertically at x=5 — intersection at (5,5), relative_position=0.5
    base_segments = {
        ROW_ID: [1],
        TRACK_ID: ["t1"],
        TRACK_CLASSIFICATION: ["car"],
        END_VIDEO_NAME: ["myhostname_cam.mp4"],
        END_FRAME: [2],
        START_X: [0.0],
        START_Y: [5.0],
        END_X: [10.0],
        END_Y: [5.0],
        START_W: [0.0],
        START_H: [0.0],
        END_W: [0.0],
        END_H: [0.0],
        START_OCCURRENCE: [datetime(2024, 1, 1, 0, 0, 0)],
        END_OCCURRENCE: [datetime(2024, 1, 1, 0, 0, 2)],
    }
    without_geo_df = pl.DataFrame(base_segments)
    with_geo_df = without_geo_df.with_columns([
        pl.Series(START_GEO_X, [449200.0]),
        pl.Series(START_GEO_Y, [5699300.0]),
        pl.Series(END_GEO_X, [449220.0]),
        pl.Series(END_GEO_Y, [5699320.0]),
    ])
    section = LineSection(
        id=SectionId("s1"),
        name="s1",
        relative_offset_coordinates={},
        plugin_data={},
        coordinates=[Coordinate(5.0, 0.0), Coordinate(5.0, 10.0)],
    )
    return GeoInterpolationGiven(
        dataset_with_geo=PolarsTrackGeometryDataset(offset, with_geo_df),
        dataset_without_geo=PolarsTrackGeometryDataset(offset, without_geo_df),
        section=section,
    )


class TestGeoInterpolationAtIntersection:
    def test_interpolated_geo_x_at_midpoint(self) -> None:
        given = create_geo_interpolation_given()
        result = given.dataset_with_geo.intersecting_tracks([given.section])
        points = result._points
        assert INTERPOLATED_GEO_X in points.columns
        # relative_position=0.5, start=449200, end=449220 → expected=449210
        assert points[INTERPOLATED_GEO_X][0] == pytest.approx(449210.0, abs=0.01)

    def test_interpolated_geo_y_at_midpoint(self) -> None:
        given = create_geo_interpolation_given()
        result = given.dataset_with_geo.intersecting_tracks([given.section])
        points = result._points
        assert INTERPOLATED_GEO_Y in points.columns
        assert points[INTERPOLATED_GEO_Y][0] == pytest.approx(5699310.0, abs=0.01)

    def test_no_geo_columns_when_segments_lack_geo(self) -> None:
        given = create_geo_interpolation_given()
        result = given.dataset_without_geo.intersecting_tracks([given.section])
        points = result._points
        assert INTERPOLATED_GEO_X not in points.columns
        assert INTERPOLATED_GEO_Y not in points.columns
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestGeoInterpolationAtIntersection -v
```

Expected: FAIL — `ImportError: cannot import name 'INTERPOLATED_GEO_X'`

- [ ] **Step 3: Implement**

In `polars_geometry_store.py`, add constants near the top with the other intersection constants:

```python
INTERPOLATED_GEO_X: str = "interpolated_geo_x"
INTERPOLATED_GEO_Y: str = "interpolated_geo_y"
```

In `PolarsTrackGeometryDataset.intersecting_tracks`, in the intersection point computation block, after the `.filter(pl.col(RELATIVE_POSITION).is_not_null())` line and before `.drop([...])`, add:

```python
if (
    START_GEO_X in intersecting_segments.columns
    and START_GEO_Y in intersecting_segments.columns
):
    intersection_points = intersection_points.with_columns(
        [
            (
                pl.col(START_GEO_X)
                + pl.col(RELATIVE_POSITION)
                * (pl.col(END_GEO_X) - pl.col(START_GEO_X))
            ).alias(INTERPOLATED_GEO_X),
            (
                pl.col(START_GEO_Y)
                + pl.col(RELATIVE_POSITION)
                * (pl.col(END_GEO_Y) - pl.col(START_GEO_Y))
            ).alias(INTERPOLATED_GEO_Y),
        ]
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestGeoInterpolationAtIntersection -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py
git commit -m "feat: linearly interpolate geo coordinates at track-section intersection point"
```

---

### Task 11: `create_events()` + `PolarsEventDataset` geo fields

**Files:**
- Modify: `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`
- Test: `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`

- [ ] **Step 1: Write the failing test**

Add to `test_polars_geometry_store.py`:

```python
from OTAnalytics.domain.event import GEO_X as EVENT_GEO_X, GEO_Y as EVENT_GEO_Y
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    INTERPOLATED_GEO_X,
    INTERPOLATED_GEO_Y,
    PolarsIntersectionPointsDataset,
)


@dataclass
class CreateEventsGeoGiven:
    points_with_geo: PolarsIntersectionPointsDataset
    points_without_geo: PolarsIntersectionPointsDataset


def _base_points_dict() -> dict:
    return {
        TRACK_ID: ["t1"],
        TRACK_CLASSIFICATION: ["car"],
        END_VIDEO_NAME: ["myhostname_cam.mp4"],
        END_FRAME: [2],
        END_OCCURRENCE: [datetime(2024, 1, 1, 0, 0, 1)],
        START_OCCURRENCE: [datetime(2024, 1, 1, 0, 0, 0)],
        "section_id": ["s1"],
        "current_x": [5.0],
        "current_y": [5.0],
        "previous_x": [0.0],
        "previous_y": [5.0],
        "relative_position": [0.5],
    }


def create_create_events_geo_given() -> CreateEventsGeoGiven:
    base = _base_points_dict()
    without_geo = pl.DataFrame(base)
    with_geo = without_geo.with_columns([
        pl.Series(INTERPOLATED_GEO_X, [449210.0]),
        pl.Series(INTERPOLATED_GEO_Y, [5699310.0]),
    ])
    return CreateEventsGeoGiven(
        points_with_geo=PolarsIntersectionPointsDataset(with_geo),
        points_without_geo=PolarsIntersectionPointsDataset(without_geo),
    )


class TestCreateEventsGeoCoordinates:
    def test_events_carry_geo_coordinates_when_present(self) -> None:
        given = create_create_events_geo_given()
        offset = RelativeOffsetCoordinate(0.0, 0.0)
        event_dataset = given.points_with_geo.create_events(offset)
        events = list(event_dataset)
        assert len(events) == 1
        assert events[0].geo_x == pytest.approx(449210.0)
        assert events[0].geo_y == pytest.approx(5699310.0)

    def test_events_have_none_geo_when_no_geo_columns(self) -> None:
        given = create_create_events_geo_given()
        offset = RelativeOffsetCoordinate(0.0, 0.0)
        event_dataset = given.points_without_geo.create_events(offset)
        events = list(event_dataset)
        assert len(events) == 1
        assert events[0].geo_x is None
        assert events[0].geo_y is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestCreateEventsGeoCoordinates -v
```

Expected: FAIL — `AssertionError: assert None == 449210.0`

- [ ] **Step 3: Implement**

In `PolarsIntersectionPointsDataset.create_events()`, after the final `with_columns([...])` block that normalises direction vectors, add before the `.select([...])`:

```python
if (
    INTERPOLATED_GEO_X in self._points.columns
    and INTERPOLATED_GEO_Y in self._points.columns
):
    events = events.with_columns(
        [
            pl.col(INTERPOLATED_GEO_X).alias(event.GEO_X),
            pl.col(INTERPOLATED_GEO_Y).alias(event.GEO_Y),
        ]
    )
```

Add geo columns to the `.select([...])` conditionally:

```python
geo_event_cols = (
    [event.GEO_X, event.GEO_Y]
    if event.GEO_X in events.columns and event.GEO_Y in events.columns
    else []
)
events = events.select(
    [
        event.ROAD_USER_ID,
        event.ROAD_USER_TYPE,
        event.HOSTNAME,
        event.OCCURRENCE,
        event.FRAME_NUMBER,
        event.SECTION_ID,
        EVENT_COORDINATE_X,
        EVENT_COORDINATE_Y,
        event.EVENT_TYPE,
        DIRECTION_VECTOR_X,
        DIRECTION_VECTOR_Y,
        event.VIDEO_NAME,
        event.INTERPOLATED_OCCURRENCE,
        INTERPOLATED_EVENT_COORDINATE_X,
        INTERPOLATED_EVENT_COORDINATE_Y,
    ]
    + geo_event_cols
)
```

In `PolarsEventDataset.__iter__` (the row-to-`Event` loop), update the `Event(...)` construction to pass geo coordinates. The full `yield Event(...)` block becomes:

```python
yield Event(
    road_user_id=row[event.ROAD_USER_ID],
    road_user_type=row[event.ROAD_USER_TYPE],
    hostname=row[event.HOSTNAME],
    occurrence=row[event.OCCURRENCE],
    frame_number=row[event.FRAME_NUMBER],
    section_id=(
        SectionId(row[event.SECTION_ID]) if row[event.SECTION_ID] else None
    ),
    event_coordinate=ImageCoordinate(
        row[EVENT_COORDINATE_X], row[EVENT_COORDINATE_Y]
    ),
    event_type=EventType.parse(row[event.EVENT_TYPE]),
    direction_vector=DirectionVector2D(
        row[DIRECTION_VECTOR_X], row[DIRECTION_VECTOR_Y]
    ),
    video_name=row[event.VIDEO_NAME],
    interpolated_occurrence=row[event.INTERPOLATED_OCCURRENCE],
    interpolated_event_coordinate=ImageCoordinate(
        row[INTERPOLATED_EVENT_COORDINATE_X],
        row[INTERPOLATED_EVENT_COORDINATE_Y],
    ),
    geo_x=row.get(event.GEO_X),
    geo_y=row.get(event.GEO_Y),
)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestCreateEventsGeoCoordinates -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py
git commit -m "feat: propagate geo coordinates into events in create_events() and PolarsEventDataset"
```

---

### Task 12: Export — `event_list.py` + `EventListDataFrameBuilder`

**Files:**
- Modify: `OTAnalytics/application/export_formats/event_list.py`
- Modify: `OTAnalytics/plugin_prototypes/eventlist_exporter/eventlist_exporter.py`
- Test: `tests/unit/OTAnalytics/plugin_prototypes/test_eventlist_exporter.py`

- [ ] **Step 1: Write the failing test**

Replace the content of `tests/unit/OTAnalytics/plugin_prototypes/test_eventlist_exporter.py`:

```python
from dataclasses import dataclass
from typing import Iterable

from OTAnalytics.application.export_formats import event_list
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    EventListDataFrameBuilder,
)
from tests.utils.builders.event_builder import EventBuilder


@dataclass
class EventListGiven:
    events_with_geo: list
    events_without_geo: list
    events_empty: list


def create_event_list_given() -> EventListGiven:
    builder_with = EventBuilder(geo_x=449210.0, geo_y=5699310.0)
    builder_with.append_section_event()
    builder_without = EventBuilder()
    builder_without.append_section_event()
    return EventListGiven(
        events_with_geo=builder_with.build_events(),
        events_without_geo=builder_without.build_events(),
        events_empty=[],
    )


def setup_default(given: EventListGiven) -> EventListGiven:
    return given


def create_target_with_geo(given: EventListGiven) -> EventListDataFrameBuilder:
    return EventListDataFrameBuilder(given.events_with_geo, [])


def create_target_without_geo(given: EventListGiven) -> EventListDataFrameBuilder:
    return EventListDataFrameBuilder(given.events_without_geo, [])


def create_target_empty(given: EventListGiven) -> EventListDataFrameBuilder:
    return EventListDataFrameBuilder(given.events_empty, [])


class TestEventListDataFrameBuilderGeoCoordinates:
    def test_build_no_events(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_empty(given)
        assert target.build().empty

    def test_geo_columns_present_when_events_have_geo(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_with_geo(given)
        df = target.build()
        assert event_list.GEO_X in df.columns
        assert event_list.GEO_Y in df.columns

    def test_geo_x_value_correct(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_with_geo(given)
        df = target.build()
        assert df[event_list.GEO_X].iloc[0] == pytest.approx(449210.0, abs=0.001)

    def test_geo_y_value_correct(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_with_geo(given)
        df = target.build()
        assert df[event_list.GEO_Y].iloc[0] == pytest.approx(5699310.0, abs=0.001)

    def test_geo_columns_absent_when_events_have_no_geo(self) -> None:
        given = setup_default(create_event_list_given())
        target = create_target_without_geo(given)
        df = target.build()
        assert event_list.GEO_X not in df.columns
        assert event_list.GEO_Y not in df.columns
```

Add `import pytest` at the top of the file.

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/OTAnalytics/plugin_prototypes/test_eventlist_exporter.py -v
```

Expected: FAIL — `ImportError: cannot import name 'GEO_X' from 'OTAnalytics.application.export_formats.event_list'`

- [ ] **Step 3: Implement**

In `OTAnalytics/application/export_formats/event_list.py`, add after `INTERPOLATED_EVENT_COORDINATE_Y`:

```python
GEO_X: str = event.GEO_X
GEO_Y: str = event.GEO_Y
```

In `OTAnalytics/plugin_prototypes/eventlist_exporter/eventlist_exporter.py`:

Add to `NUMBER_ROUNDED_COLUMNS`:
```python
event_list.GEO_X: 3,
event_list.GEO_Y: 3,
```

Replace `return self._df.loc[:, EXPORT_COLUMNS]` in `build()` with:

```python
geo_cols = (
    [event_list.GEO_X, event_list.GEO_Y]
    if event_list.GEO_X in self._df.columns
    and event_list.GEO_Y in self._df.columns
    else []
)
return self._df.loc[:, EXPORT_COLUMNS + geo_cols]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/unit/OTAnalytics/plugin_prototypes/test_eventlist_exporter.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/application/export_formats/event_list.py OTAnalytics/plugin_prototypes/eventlist_exporter/eventlist_exporter.py tests/unit/OTAnalytics/plugin_prototypes/test_eventlist_exporter.py
git commit -m "feat: include geo_x/geo_y columns in event list CSV export when present"
```

---

### Task 13: Full regression check

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/unit tests/acceptance -v --tb=short 2>&1 | tail -40
```

Expected: All tests PASS. If any failures, investigate and fix before proceeding.

- [ ] **Step 2: Run pre-commit hooks on all changed files**

```bash
git add -u
pre-commit run --all-files
```

Expected: All hooks pass.

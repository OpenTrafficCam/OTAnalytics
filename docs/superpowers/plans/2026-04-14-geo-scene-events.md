# Geo Coordinates in Scene Events Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Propagate `geo_x`/`geo_y` coordinates onto enter-scene and leave-scene events when the underlying track data carries OTFusion geo columns.

**Architecture:** Two surgical changes: (1) `PolarsTrackDataset.__create_segments()` currently hard-selects only pixel columns and drops geo columns even when present — fix it to conditionally include `start_geo_x/y` and `end_geo_x/y`; (2) `SceneEventListBuilder.__create_event()` currently never reads geo keys from the segment dict — add `key_geo_x`/`key_geo_y` parameters mirroring the existing `key_x`/`key_y` pattern, and pass them through to `Event(geo_x=..., geo_y=...)`.

**Tech Stack:** Python, Polars, pytest (`uv run pytest`)

---

## Background: how intersection events already get geo coordinates

For reference, intersection events are handled in
`OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`.
`create_track_segments()` (line ~152) already shifts `track.GEO_X/Y` into
`START_GEO_X/Y` and `END_GEO_X/Y` columns when the underlying data has them.
`wrap_intersection_points()` then interpolates `INTERPOLATED_GEO_X/Y` along the
segment and maps those to `event.GEO_X`/`GEO_Y` on the resulting events.

Scene events go through a completely separate path (`__create_segments()` in
`polars_track_store.py` + `SceneEventListBuilder` in `eventlist.py`) that currently
ignores geo columns entirely.

---

## File Map

| File | Change |
|------|--------|
| `OTAnalytics/plugin_datastore/polars_track_store.py` | Modify `__create_segments()` to include geo shift columns and add them to `.rename()` / `.select()` |
| `OTAnalytics/application/eventlist.py` | Add `key_geo_x`/`key_geo_y` params to `__create_event()`; update callers |
| `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py` | New test class: segments carry geo columns when present, absent otherwise |
| `tests/unit/OTAnalytics/application/test_eventlist.py` | New test class: scene events carry geo coords when segment dict has them |

---

## Constants reference

These constants are defined in
`OTAnalytics/domain/track_dataset/track_dataset.py` (lines 40-43):

```python
START_GEO_X: str = "start_geo_x"
START_GEO_Y: str = "start_geo_y"
END_GEO_X: str = "end_geo_x"
END_GEO_Y: str = "end_geo_y"
```

They are **not yet imported** by either `polars_track_store.py` or
`eventlist.py` — both files will need them added to their import block.

`track.GEO_X = "geo_x"` and `track.GEO_Y = "geo_y"` are defined in
`OTAnalytics/domain/track.py`.

---

## Task 1: Propagate geo columns through `PolarsTrackDataset.__create_segments()`

**Files:**
- Modify: `OTAnalytics/plugin_datastore/polars_track_store.py:690-767`
- Test: `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`

### Step 1.1: Write the failing test

Add the following at the **end** of
`tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`.

First, add the missing imports to the existing import block at the top of the file:

```python
from datetime import datetime, timezone  # already present

# Add to the existing track_dataset import group:
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_FRAME,
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    START_FRAME,
    START_GEO_X,   # ADD
    START_GEO_Y,   # ADD
    END_GEO_X,     # ADD
    END_GEO_Y,     # ADD
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    EmptyTrackIdSet,
    IntersectionPointsDataset,
    TrackDataset,
    TrackDoesNotExistError,
    TrackIdSet,
    TrackSegmentDataset,
)
from OTAnalytics.plugin_parser import ottrk_dataformat  # already present
```

Then add the test class at the end of the file:

```python
GEO_X_VALUES = [449250.0, 449260.0, 449270.0]
GEO_Y_VALUES = [5855000.0, 5855010.0, 5855020.0]
VIDEO_NAME_VALUE = "myhostname_something.mp4"
INPUT_FILE_VALUE = "myhostname_something.ottrk"


def _build_dataset_with_geo(
    track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
) -> PolarsTrackDataset:
    """Build a PolarsTrackDataset whose internal DataFrame includes geo columns."""
    df = pl.DataFrame(
        {
            track.TRACK_ID: ["1", "1", "1"],
            track.TRACK_CLASSIFICATION: ["car", "car", "car"],
            track.CLASSIFICATION: ["car", "car", "car"],
            track.CONFIDENCE: [0.9, 0.9, 0.9],
            track.X: [10.0, 20.0, 30.0],
            track.Y: [5.0, 5.0, 5.0],
            track.W: [5.0, 5.0, 5.0],
            track.H: [5.0, 5.0, 5.0],
            track.FRAME: [1, 2, 3],
            track.OCCURRENCE: [
                datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                datetime(2022, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
                datetime(2022, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
            ],
            track.INTERPOLATED_DETECTION: [False, False, False],
            track.VIDEO_NAME: [VIDEO_NAME_VALUE] * 3,
            track.INPUT_FILE: [INPUT_FILE_VALUE] * 3,
            track.ORIGINAL_TRACK_ID: ["1", "1", "1"],
            ottrk_dataformat.FIRST: [True, False, False],
            ottrk_dataformat.FINISHED: [False, False, True],
            track.GEO_X: GEO_X_VALUES,
            track.GEO_Y: GEO_Y_VALUES,
        }
    )
    return PolarsTrackDataset.from_dataframe(df, track_geometry_factory)


def _build_dataset_without_geo(
    track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
) -> PolarsTrackDataset:
    """Build a PolarsTrackDataset without geo columns."""
    df = pl.DataFrame(
        {
            track.TRACK_ID: ["1", "1", "1"],
            track.TRACK_CLASSIFICATION: ["car", "car", "car"],
            track.CLASSIFICATION: ["car", "car", "car"],
            track.CONFIDENCE: [0.9, 0.9, 0.9],
            track.X: [10.0, 20.0, 30.0],
            track.Y: [5.0, 5.0, 5.0],
            track.W: [5.0, 5.0, 5.0],
            track.H: [5.0, 5.0, 5.0],
            track.FRAME: [1, 2, 3],
            track.OCCURRENCE: [
                datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                datetime(2022, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
                datetime(2022, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
            ],
            track.INTERPOLATED_DETECTION: [False, False, False],
            track.VIDEO_NAME: [VIDEO_NAME_VALUE] * 3,
            track.INPUT_FILE: [INPUT_FILE_VALUE] * 3,
            track.ORIGINAL_TRACK_ID: ["1", "1", "1"],
            ottrk_dataformat.FIRST: [True, False, False],
            ottrk_dataformat.FINISHED: [False, False, True],
        }
    )
    return PolarsTrackDataset.from_dataframe(df, track_geometry_factory)


@dataclass
class GivenSegmentGeo:
    dataset_with_geo: PolarsTrackDataset
    dataset_without_geo: PolarsTrackDataset


def create_given_segment_geo(
    track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
) -> GivenSegmentGeo:
    return GivenSegmentGeo(
        dataset_with_geo=_build_dataset_with_geo(track_geometry_factory),
        dataset_without_geo=_build_dataset_without_geo(track_geometry_factory),
    )


def setup_default_segment_geo(given: GivenSegmentGeo) -> GivenSegmentGeo:
    return given


class TestGetSegmentsPreservesGeoColumns:
    def test_first_segments_include_start_geo_columns(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        given = setup_default_segment_geo(
            create_given_segment_geo(track_geometry_factory)
        )

        rows: list[dict] = []
        given.dataset_with_geo.get_first_segments().apply(rows.append)

        assert rows[0][START_GEO_X] == GEO_X_VALUES[0]
        assert rows[0][START_GEO_Y] == GEO_Y_VALUES[0]

    def test_last_segments_include_end_geo_columns(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        given = setup_default_segment_geo(
            create_given_segment_geo(track_geometry_factory)
        )

        rows: list[dict] = []
        given.dataset_with_geo.get_last_segments().apply(rows.append)

        assert rows[0][END_GEO_X] == GEO_X_VALUES[-1]
        assert rows[0][END_GEO_Y] == GEO_Y_VALUES[-1]

    def test_segments_without_geo_data_have_no_geo_keys(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        given = setup_default_segment_geo(
            create_given_segment_geo(track_geometry_factory)
        )

        rows: list[dict] = []
        given.dataset_without_geo.get_first_segments().apply(rows.append)

        assert START_GEO_X not in rows[0]
        assert START_GEO_Y not in rows[0]
```

- [ ] **Step 1.2: Run test to verify it fails**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestGetSegmentsPreservesGeoColumns -v
```

Expected: 3 tests FAIL — `KeyError: 'start_geo_x'` (or the geo columns are simply absent).

- [ ] **Step 1.3: Add imports to `polars_track_store.py`**

In `OTAnalytics/plugin_datastore/polars_track_store.py`, extend the existing
import from `OTAnalytics.domain.track_dataset.track_dataset` (lines 31-48) to
include the four geo constants:

```python
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_FRAME,
    END_GEO_X,          # ADD
    END_GEO_Y,          # ADD
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    EmptyTrackIdSet,
    IntersectionPointsDataset,
    START_FRAME,
    START_GEO_X,        # ADD
    START_GEO_Y,        # ADD
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    TrackDataset,
    TrackDoesNotExistError,
    TrackIdSet,
    TrackSegmentDataset,
)
```

- [ ] **Step 1.4: Implement the fix in `__create_segments()`**

Replace the entire `__create_segments()` method (lines 690-767) with:

```python
def __create_segments(self) -> pl.DataFrame:
    """Create track segments from detections."""
    if self._dataset.is_empty():
        schema = {
            track.TRACK_ID: pl.Utf8,
            track.OCCURRENCE: pl.Datetime,
            track.TRACK_CLASSIFICATION: pl.Utf8,
            START_X: pl.Float64,
            START_Y: pl.Float64,
            START_OCCURRENCE: pl.Datetime,
            START_FRAME: pl.Int64,
            START_VIDEO_NAME: pl.Utf8,
            END_X: pl.Float64,
            END_Y: pl.Float64,
            END_OCCURRENCE: pl.Datetime,
            END_FRAME: pl.Int64,
            END_VIDEO_NAME: pl.Utf8,
        }
        return pl.DataFrame(schema=schema)

    data = self._dataset.sort([LEVEL_TRACK_ID, LEVEL_OCCURRENCE])
    has_geo = track.GEO_X in data.columns and track.GEO_Y in data.columns

    geo_start_columns = (
        [
            pl.col(track.GEO_X).shift(1).over(LEVEL_TRACK_ID).alias(START_GEO_X),
            pl.col(track.GEO_Y).shift(1).over(LEVEL_TRACK_ID).alias(START_GEO_Y),
        ]
        if has_geo
        else []
    )
    geo_rename = (
        {track.GEO_X: END_GEO_X, track.GEO_Y: END_GEO_Y} if has_geo else {}
    )
    geo_select = (
        [END_GEO_X, END_GEO_Y, START_GEO_X, START_GEO_Y] if has_geo else []
    )

    segments = (
        data.with_columns(
            [
                pl.col(track.X).shift(1).over(LEVEL_TRACK_ID).alias(START_X),
                pl.col(track.Y).shift(1).over(LEVEL_TRACK_ID).alias(START_Y),
                pl.col(track.OCCURRENCE)
                .shift(1)
                .over(LEVEL_TRACK_ID)
                .alias(START_OCCURRENCE),
                pl.col(track.FRAME)
                .shift(1)
                .over(LEVEL_TRACK_ID)
                .alias(START_FRAME),
                pl.col(track.VIDEO_NAME)
                .shift(1)
                .over(LEVEL_TRACK_ID)
                .alias(START_VIDEO_NAME),
                *geo_start_columns,
            ]
        )
        .drop_nulls(
            subset=[
                START_X,
                START_Y,
                START_OCCURRENCE,
                START_FRAME,
                START_VIDEO_NAME,
            ]
        )
        .rename(
            {
                track.X: END_X,
                track.Y: END_Y,
                track.OCCURRENCE: END_OCCURRENCE,
                track.FRAME: END_FRAME,
                track.VIDEO_NAME: END_VIDEO_NAME,
                **geo_rename,
            }
        )
        .select(
            [
                track.TRACK_ID,
                track.TRACK_CLASSIFICATION,
                START_X,
                START_Y,
                START_OCCURRENCE,
                START_FRAME,
                START_VIDEO_NAME,
                END_X,
                END_Y,
                END_OCCURRENCE,
                END_FRAME,
                END_VIDEO_NAME,
                *geo_select,
            ]
        )
    )
    return segments
```

- [ ] **Step 1.5: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestGetSegmentsPreservesGeoColumns -v
```

Expected: 3 tests PASS.

- [ ] **Step 1.6: Run the full plugin_datastore test suite to check for regressions**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/ -q
```

Expected: all tests pass.

- [ ] **Step 1.7: Commit**

```bash
git add OTAnalytics/plugin_datastore/polars_track_store.py \
        tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py
git commit -m "feat: include geo columns in PolarsTrackDataset.__create_segments()"
```

---

## Task 2: Use geo columns in `SceneEventListBuilder`

**Files:**
- Modify: `OTAnalytics/application/eventlist.py:1-143`
- Test: `tests/unit/OTAnalytics/application/test_eventlist.py`

### Step 2.1: Write the failing tests

Add the following at the **end** of
`tests/unit/OTAnalytics/application/test_eventlist.py`.

First, extend the existing import from `track_dataset` at the top of the file:

```python
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_FRAME,
    END_GEO_X,     # ADD
    END_GEO_Y,     # ADD
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    START_FRAME,
    START_GEO_X,   # ADD
    START_GEO_Y,   # ADD
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    TrackDataset,
    TrackSegmentDataset,
)
```

Then add the test class at the end of the file. Note the existing `first_segment_of()`
and `last_segment_of()` helpers in this file — the new helpers add geo keys on top:

```python
GEO_X_ENTER = 449250.0
GEO_Y_ENTER = 5855000.0
GEO_X_LEAVE = 449270.0
GEO_Y_LEAVE = 5855020.0


def first_segment_with_geo(t: Track) -> dict:
    seg = first_segment_of(t)
    seg[START_GEO_X] = GEO_X_ENTER
    seg[START_GEO_Y] = GEO_Y_ENTER
    return seg


def last_segment_with_geo(t: Track) -> dict:
    seg = last_segment_of(t)
    seg[END_GEO_X] = GEO_X_LEAVE
    seg[END_GEO_Y] = GEO_Y_LEAVE
    return seg


@dataclass
class GivenSceneGeo:
    track: Track


def create_given_scene_geo(t: Track) -> GivenSceneGeo:
    return GivenSceneGeo(track=t)


def setup_default_scene_geo(given: GivenSceneGeo) -> GivenSceneGeo:
    return given


def create_target_scene_geo(given: GivenSceneGeo) -> SceneEventListBuilder:
    return SceneEventListBuilder()


class TestSceneEventListBuilderWithGeoCoordinates:
    def test_enter_scene_event_carries_geo_coordinates(
        self, track: Track
    ) -> None:
        given = setup_default_scene_geo(create_given_scene_geo(track))
        segments = Mock(spec=TrackSegmentDataset)
        segments.apply.side_effect = lambda consumer: consumer(
            first_segment_with_geo(given.track)
        )
        builder = create_target_scene_geo(given)

        builder.add_enter_scene_events(segments)
        events = list(builder.build())

        assert events[0].geo_x == GEO_X_ENTER
        assert events[0].geo_y == GEO_Y_ENTER

    def test_leave_scene_event_carries_geo_coordinates(
        self, track: Track
    ) -> None:
        given = setup_default_scene_geo(create_given_scene_geo(track))
        segments = Mock(spec=TrackSegmentDataset)
        segments.apply.side_effect = lambda consumer: consumer(
            last_segment_with_geo(given.track)
        )
        builder = create_target_scene_geo(given)

        builder.add_leave_scene_events(segments)
        events = list(builder.build())

        assert events[0].geo_x == GEO_X_LEAVE
        assert events[0].geo_y == GEO_Y_LEAVE

    def test_enter_scene_event_has_none_geo_when_segment_lacks_geo(
        self, track: Track
    ) -> None:
        given = setup_default_scene_geo(create_given_scene_geo(track))
        segments = Mock(spec=TrackSegmentDataset)
        segments.apply.side_effect = lambda consumer: consumer(
            first_segment_of(given.track)
        )
        builder = create_target_scene_geo(given)

        builder.add_enter_scene_events(segments)
        events = list(builder.build())

        assert events[0].geo_x is None
        assert events[0].geo_y is None
```

- [ ] **Step 2.2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/application/test_eventlist.py::TestSceneEventListBuilderWithGeoCoordinates -v
```

Expected: 3 tests FAIL — events have `geo_x=None` even when segment contains geo keys.

- [ ] **Step 2.3: Add imports to `eventlist.py`**

In `OTAnalytics/application/eventlist.py`, extend the import from
`OTAnalytics.domain.track_dataset.track_dataset` (lines 13-26):

```python
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_FRAME,
    END_GEO_X,       # ADD
    END_GEO_Y,       # ADD
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    START_FRAME,
    START_GEO_X,     # ADD
    START_GEO_Y,     # ADD
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    TrackDataset,
    TrackSegmentDataset,
)
```

- [ ] **Step 2.4: Update `_create_enter_scene_event()` and `_create_leave_scene_event()`**

Replace the two caller methods in `SceneEventListBuilder` (lines 89-111):

```python
def _create_enter_scene_event(self, value: dict) -> None:
    event = self.__create_event(
        value=value,
        event_type=EventType.ENTER_SCENE,
        key_x=START_X,
        key_y=START_Y,
        key_occurrence=START_OCCURRENCE,
        key_frame=START_FRAME,
        key_video_name=START_VIDEO_NAME,
        key_geo_x=START_GEO_X,
        key_geo_y=START_GEO_Y,
    )
    self._events.append(event)

def _create_leave_scene_event(self, value: dict) -> None:
    event = self.__create_event(
        value=value,
        event_type=EventType.LEAVE_SCENE,
        key_x=END_X,
        key_y=END_Y,
        key_occurrence=END_OCCURRENCE,
        key_frame=END_FRAME,
        key_video_name=END_VIDEO_NAME,
        key_geo_x=END_GEO_X,
        key_geo_y=END_GEO_Y,
    )
    self._events.append(event)
```

- [ ] **Step 2.5: Update `__create_event()` signature and body**

Replace the `__create_event()` static method (lines 113-143) with:

```python
@staticmethod
def __create_event(
    value: dict,
    event_type: EventType,
    key_x: str,
    key_y: str,
    key_occurrence: str,
    key_frame: str,
    key_video_name: str,
    key_geo_x: str,
    key_geo_y: str,
) -> Event:
    image_coordinate = ImageCoordinate(value[key_x], value[key_y])
    occurrence = value[key_occurrence]
    return Event(
        road_user_id=value[track.TRACK_ID],
        road_user_type=value[track.TRACK_CLASSIFICATION],
        hostname=extract_hostname(value[key_video_name]),
        occurrence=occurrence,
        frame_number=value[key_frame],
        section_id=None,
        event_coordinate=image_coordinate,
        event_type=event_type,
        direction_vector=calculate_direction_vector(
            value[START_X],
            value[START_Y],
            value[END_X],
            value[END_Y],
        ),
        video_name=value[key_video_name],
        interpolated_occurrence=occurrence,
        interpolated_event_coordinate=image_coordinate,
        geo_x=value.get(key_geo_x),
        geo_y=value.get(key_geo_y),
    )
```

- [ ] **Step 2.6: Run new tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/application/test_eventlist.py::TestSceneEventListBuilderWithGeoCoordinates -v
```

Expected: 3 tests PASS.

- [ ] **Step 2.7: Run the full eventlist test suite to check for regressions**

```bash
uv run pytest tests/unit/OTAnalytics/application/test_eventlist.py -v
```

Expected: all tests pass (existing `TestSceneEventListBuilder` tests still pass —
existing `first_segment_of()`/`last_segment_of()` helpers don't include geo keys,
so `value.get(key_geo_x)` returns `None`, which is what `Event` defaults to anyway).

- [ ] **Step 2.8: Run the broader application test suite**

```bash
uv run pytest tests/unit/OTAnalytics/application/ -q
```

Expected: all tests pass.

- [ ] **Step 2.9: Commit**

```bash
git add OTAnalytics/application/eventlist.py \
        tests/unit/OTAnalytics/application/test_eventlist.py
git commit -m "feat: propagate geo coordinates to enter-scene and leave-scene events"
```

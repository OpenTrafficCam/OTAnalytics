# Geo Coordinates Support in OTAnalytics

**Date:** 2026-04-03
**Branch:** feature/9528-extend-sections-and-tracks-with-optional-geo-coordinates

## Overview

Extend OTAnalytics to process georeferenced trajectories from ottrk files. Geo
coordinates (`geo_x`, `geo_y`) are optional fields on detections, propagated
through the pipeline into events and exported alongside pixel coordinates.

The coordinate system is assumed to be UTM (based on observed values). No CRS
metadata is stored or validated — that is out of scope.

Section geo coordinates are **deferred**: sections remain pixel-only for now.
When both tracks and sections carry geo coordinates, the intersection will be
performed in geo space (future work).

Current scope: tracks carry geo coordinates → events carry geo coordinates
(including linearly interpolated intersection points). Cutting always uses pixel
coordinates.

---

## Functional Requirements

1. `Detection` domain interface gains optional `geo_x: float | None` and
   `geo_y: float | None` properties.
2. ottrk JSON parser reads `geo_x`/`geo_y` from detection dicts when present.
3. Feathers (`.feather`) format carries `geo_x`/`geo_y` columns when present.
4. `create_track_segments` propagates `START_GEO_X/Y` and `END_GEO_X/Y` when
   both geo columns are present.
5. When a track segment with geo coordinates intersects a section, the geo
   coordinate at the intersection point is linearly interpolated using the same
   `RELATIVE_POSITION` scalar as pixel interpolation.
6. `Event` gains optional `geo_x: float | None = None` and
   `geo_y: float | None = None` fields.
7. Event list CSV export includes `geo_x` and `geo_y` columns when at least one
   event carries geo coordinates (both columns added together or not at all).

---

## Design

### Section 1: Domain Layer

**`domain/track.py`**
- Add constants: `GEO_X = "geo_x"`, `GEO_Y = "geo_y"`
- Add two abstract properties to `Detection`:
  ```python
  @property
  @abstractmethod
  def geo_x(self) -> float | None: ...

  @property
  @abstractmethod
  def geo_y(self) -> float | None: ...
  ```
- `Detection.to_dict()` always includes `geo_x` and `geo_y` (serialized as
  `None` when absent — no paired check needed at the property level).

**`domain/event.py`**
- Add constants: `GEO_X = "geo_x"`, `GEO_Y = "geo_y"`
- Add optional fields to frozen `Event` dataclass:
  ```python
  geo_x: float | None = None
  geo_y: float | None = None
  ```
- Update `to_dict()` and `to_typed_dict()` to include `geo_x`/`geo_y`.
- Add method to `EventBuilder`:
  ```python
  def add_geo_coordinate(self, geo_x: float | None, geo_y: float | None) -> None:
      self.geo_x = geo_x
      self.geo_y = geo_y
  ```

---

### Section 2: Detection Implementations

Each implementation provides `geo_x`/`geo_y` as independent `float | None`
properties. Paired-presence enforcement happens at computation layers, not here.

**`plugin_datastore/python_track_store.py` — `PythonDetection`**
- Add optional dataclass fields: `_geo_x: float | None = None`,
  `_geo_y: float | None = None`
- Implement the two abstract properties returning those fields.

**`plugin_datastore/track_store.py` — `PandasDetection`**
- Implement with index-check fallback (same pattern as `is_finished`):
  ```python
  @property
  def geo_x(self) -> float | None:
      if track.GEO_X not in self._data.index:
          return None
      return self.__get_attribute(track.GEO_X)
  ```

**`plugin_datastore/polars_track_store.py` — `PolarsDetection`**
- Implement using dict `.get()` which returns `None` when key is absent:
  ```python
  @property
  def geo_x(self) -> float | None:
      return self._data.get(track.GEO_X)
  ```

---

### Section 3: Parser Layer

**`plugin_parser/ottrk_dataformat.py`**
- Add: `GEO_X = "geo_x"`, `GEO_Y = "geo_y"`

**`plugin_parser/pandas_parser.py` — `PandasDetectionParser`**
- After building the detections DataFrame, rename geo columns when **both** are
  present:
  ```python
  if (
      ottrk_dataformat.GEO_X in df.columns
      and ottrk_dataformat.GEO_Y in df.columns
  ):
      df = df.rename(columns={
          ottrk_dataformat.GEO_X: track.GEO_X,
          ottrk_dataformat.GEO_Y: track.GEO_Y,
      })
  ```
  Files without geo fields parse unchanged.

**`plugin_parser/feathers_parser.py` — `FeathersParser`**
- No changes. `pl.read_ipc(file)` reads all columns; `PolarsTrackDataset
  .from_dataframe` passes them through. Geo columns are carried automatically.

**`plugin_parser/convert_ottrk_to_feathers.py`**
- No changes. Geo columns travel in the DataFrame from parse to write and are
  included in the output feather automatically.

---

### Section 4: DataFrame / Polars Layer

**`domain/track_dataset/track_dataset.py`**
- Add constants: `START_GEO_X`, `START_GEO_Y`, `END_GEO_X`, `END_GEO_Y`

**`plugin_datastore/track_geometry_store/polars_geometry_store.py`**
- Add constants: `INTERPOLATED_GEO_X`, `INTERPOLATED_GEO_Y`

**`create_track_segments`**
- Conditionally propagate geo columns when **both** are present:
  ```python
  if track.GEO_X in df.columns and track.GEO_Y in df.columns:
      segments = segments.with_columns([
          pl.col(track.GEO_X).alias(END_GEO_X),
          pl.col(track.GEO_Y).alias(END_GEO_Y),
          pl.col(track.GEO_X).shift(1).over(TRACK_ID).alias(START_GEO_X),
          pl.col(track.GEO_Y).shift(1).over(TRACK_ID).alias(START_GEO_Y),
      ])
  ```
  Include `START_GEO_X/Y`, `END_GEO_X/Y` in the final `select()` only when
  present.

**`find_line_intersections`**
- Conditionally include `START_GEO_X/Y`, `END_GEO_X/Y` in the `select()` output
  when both are present in `segments_df`:
  ```python
  if START_GEO_X in segments_df.columns and START_GEO_Y in segments_df.columns:
      # append START_GEO_X, START_GEO_Y, END_GEO_X, END_GEO_Y to select list
  ```

**Intersection point computation block** (inside
`PolarsTrackGeometryDataset.intersecting_tracks`)
- After `RELATIVE_POSITION` is computed, conditionally interpolate geo coords
  when **both** segment geo columns are present:
  ```python
  if (
      START_GEO_X in intersecting_segments.columns
      and START_GEO_Y in intersecting_segments.columns
  ):
      intersection_points = intersection_points.with_columns([
          (
              pl.col(START_GEO_X)
              + pl.col(RELATIVE_POSITION) * (pl.col(END_GEO_X) - pl.col(START_GEO_X))
          ).alias(INTERPOLATED_GEO_X),
          (
              pl.col(START_GEO_Y)
              + pl.col(RELATIVE_POSITION) * (pl.col(END_GEO_Y) - pl.col(START_GEO_Y))
          ).alias(INTERPOLATED_GEO_Y),
      ])
  ```

---

### Section 5: Event Creation and Export Layer

**`PolarsIntersectionPointsDataset.create_events()`**
- Conditionally extend the polars expression chain when **both** interpolated geo
  columns are present:
  ```python
  if (
      INTERPOLATED_GEO_X in self._points.columns
      and INTERPOLATED_GEO_Y in self._points.columns
  ):
      events = events.with_columns([
          pl.col(INTERPOLATED_GEO_X).alias(event.GEO_X),
          pl.col(INTERPOLATED_GEO_Y).alias(event.GEO_Y),
      ])
  ```
  Include `event.GEO_X`, `event.GEO_Y` in the final `select()` only when
  present.

**`PolarsEventDataset`** (row-to-Event conversion)
- Pass geo fields from row dict — `.get()` returns `None` when absent, which
  maps cleanly to the default `None` on `Event`:
  ```python
  Event(
      ...,
      geo_x=row.get(event.GEO_X),
      geo_y=row.get(event.GEO_Y),
  )
  ```

**`application/export_formats/event_list.py`**
- Add: `GEO_X = event.GEO_X`, `GEO_Y = event.GEO_Y`

**`plugin_prototypes/eventlist_exporter/eventlist_exporter.py`**
- Add geo columns to rounding config: `event_list.GEO_X: 3`,
  `event_list.GEO_Y: 3` (3 decimal places ≈ 1 mm precision for UTM)
- In `build()`, append both geo columns together or neither:
  ```python
  geo_cols = (
      [event_list.GEO_X, event_list.GEO_Y]
      if event_list.GEO_X in self._df.columns
      and event_list.GEO_Y in self._df.columns
      else []
  )
  return self._df.loc[:, EXPORT_COLUMNS + geo_cols]
  ```

---

## Testing

Each layer gets a focused unit test:

| Layer | What to test |
|---|---|
| `Detection` implementations | `geo_x`/`geo_y` return correct value when present; return `None` when column absent |
| `pandas_parser` | DataFrame with `geo_x`/`geo_y` maps them; DataFrame without them parses cleanly |
| `create_track_segments` | Segments carry `START/END_GEO_X/Y` when geo present; absent otherwise |
| `find_line_intersections` | Geo columns pass through when present |
| Intersection point computation | `INTERPOLATED_GEO_X/Y` correct using linear interpolation with known `RELATIVE_POSITION` |
| `create_events` | `Event.geo_x`/`geo_y` populated when geo present; `None` otherwise |
| `EventListDataFrameBuilder` | CSV includes geo columns when present; omits them when absent |

---

## Out of Scope

- Section geo coordinates (deferred)
- Cutting in geo space when sections also have geo coordinates (deferred)
- CRS metadata storage or validation
- UI display of geo coordinates

# Geo-Coordinate-Based Intersection Events

**Date:** 2026-04-13
**Branch:** `feature/9528-extend-sections-and-tracks-with-optional-geo-coordinates`

---

## Problem

OTFusion produces ottrk files where each detection carries `geo_x`/`geo_y` (UTM coordinates) in
addition to `x`/`y` (BEV pixel coordinates). When users load such a file into OTAnalytics and
compute intersection events, the current pipeline detects intersections in BEV pixel space and
then interpolates geo coordinates onto the resulting events. This works, but it means the
intersection geometry is computed in pixel space even though geo coordinates are available and
more semantically meaningful.

Additionally, the `otfusion` metadata block in the ottrk file (`geo_bounds`, `bev_size`,
`padding`) is not parsed or stored anywhere in OTAnalytics today.

---

## Goals

1. When tracks have geo coordinates present, use geo coordinates for intersection detection.
2. Events generated from such tracks carry correct `geo_x`/`geo_y` values.
3. Works transparently for both GUI and CLI without extra user configuration.
4. Non-fusion ottrks (no geo columns, no otfusion metadata) continue to work exactly as before.

---

## Context

### OTFusion BEV coordinate system

OTFusion projects multi-camera detections onto a bird's-eye-view (BEV) image. Each detection has:

- `x`, `y` — position in BEV pixel space
- `geo_x`, `geo_y` — position in UTM geo space (world coordinates + geo offset)

The BEV image is what users see in the OTAnalytics GUI when loading a fusion ottrk. Sections are
therefore drawn in BEV pixel space.

### Otfusion metadata block (from ottrk file)

```json
"otfusion": {
    "geo_bounds": {
        "min_x": <float>,
        "min_y": <float>,
        "max_x": <float>,
        "max_y": <float>
    },
    "bev_size": [<width>, <height>],
    "padding": <int>,
    "crs": "<WKT string or null>"
}
```

`geo_bounds` is `world_bounds` shifted element-wise by `geo_offset`, so it maps directly to the
same coordinate space as the per-detection `geo_x`/`geo_y` values.

### Pixel → geo conversion

Given a section coordinate `(pixel_x, pixel_y)` in BEV space:

```
geo_x = geo_min_x + (pixel_x - padding) * (geo_max_x - geo_min_x) / (bev_width  - 2 * padding)
geo_y = geo_max_y - (pixel_y - padding) * (geo_max_y - geo_min_y) / (bev_height - 2 * padding)
```

(Image y increases downward; UTM y increases northward — hence the inversion.)

---

## Architecture

The feature touches four layers, each with a focused change:

```
ottrk file
    ↓ parse
OtfusionMetadata (new dataclass)
    ↓ stored on
PolarsTrackDataset.otfusion_metadata: OtfusionMetadata | None
    ↓ used in
PolarsTrackDataset.intersection_points()
    — converts section pixel coords → geo coords using pixel_to_geo()
    — passes use_geo=True to geometry functions
    ↓
find_line_intersections(..., use_geo=False)
    — when use_geo=True: uses START_GEO_X/Y + END_GEO_X/Y from segments_df
    — receives section geo endpoints instead of pixel endpoints
    ↓
PolarsIntersectionPointsDataset.create_events()
    — geo interpolation already implemented; no changes needed
```

**Fallback condition:** if `otfusion_metadata is None` or segments lack `START_GEO_X`, the
pipeline falls back to the existing image-space intersection (no regression for non-fusion files).

GUI and CLI both route through `CreateIntersectionEvents` → `SimpleCreateIntersectionEvents` →
`PolarsTrackDataset.intersection_points()`. No changes are needed in either UI layer.

---

## Component Design

### 1. `OtfusionMetadata` dataclass (new)

**Location:** `OTAnalytics/domain/otfusion.py` (new module)

```python
@dataclass(frozen=True)
class OtfusionMetadata:
    geo_min_x: float
    geo_min_y: float
    geo_max_x: float
    geo_max_y: float
    bev_width: int
    bev_height: int
    padding: int


def pixel_to_geo(
    x: float, y: float, metadata: OtfusionMetadata
) -> tuple[float, float]:
    geo_x = (
        metadata.geo_min_x
        + (x - metadata.padding)
        * (metadata.geo_max_x - metadata.geo_min_x)
        / (metadata.bev_width - 2 * metadata.padding)
    )
    geo_y = (
        metadata.geo_max_y
        - (y - metadata.padding)
        * (metadata.geo_max_y - metadata.geo_min_y)
        / (metadata.bev_height - 2 * metadata.padding)
    )
    return geo_x, geo_y
```

### 2. Parsing (`plugin_parser/`)

**`ottrk_dataformat.py`** — add constants:

```python
OTFUSION = "otfusion"
GEO_BOUNDS = "geo_bounds"
GEO_BOUNDS_MIN_X = "min_x"
GEO_BOUNDS_MIN_Y = "min_y"
GEO_BOUNDS_MAX_X = "max_x"
GEO_BOUNDS_MAX_Y = "max_y"
BEV_SIZE = "bev_size"
BEV_PADDING = "padding"
```

**`pandas_parser.py`** — add a helper that reads the `metadata["otfusion"]` block and returns
`OtfusionMetadata | None`. Called from `parse_tracks()`. The result is stored on the returned
`PolarsTrackDataset`.

### 3. `PolarsTrackDataset` (`plugin_datastore/polars_track_store.py`)

Add optional field:

```python
otfusion_metadata: OtfusionMetadata | None = None
```

Modify `intersection_points()`:

```python
def intersection_points(
    self, sections: list[Section], offset: RelativeOffsetCoordinate
) -> IntersectionPointsDataset:
    geometry_dataset = self._get_geometry_dataset_for(offset)
    return geometry_dataset.wrap_intersection_points(sections, self.otfusion_metadata)
```

### 4. `wrap_intersection_points()` (`polars_geometry_store.py`)

Accepts `otfusion_metadata: OtfusionMetadata | None`. For each section line segment:

- If `otfusion_metadata` is set and `START_GEO_X` is in `segments_df.columns`:
  convert section pixel endpoints → geo via `pixel_to_geo()`, set `use_geo=True`
- Otherwise: use pixel endpoints as-is, `use_geo=False`

### 5. `find_line_intersections()` (`polars_geometry_store.py`)

Add `use_geo: bool = False` parameter. When `True`, the parametric intersection math uses
`START_GEO_X`, `END_GEO_X`, `START_GEO_Y`, `END_GEO_Y` from `segments_df` instead of
`START_X`, `END_X`, `START_Y`, `END_Y`. The `RELATIVE_POSITION` calculation and all downstream
logic are unchanged.

### 6. `create_events()` — no changes

Already interpolates geo coordinates using `RELATIVE_POSITION` over `START_GEO_X/Y` and
`END_GEO_X/Y`. When `use_geo=True`, the intersection point is already in geo space, so the
interpolated geo values are consistent.

---

## Testing

| Test | Location | What it verifies |
|------|----------|-----------------|
| `pixel_to_geo()` with known values | `tests/unit/domain/test_otfusion.py` | Round-trip: BEV pixel of a known detection → reproduces its `geo_x/geo_y` |
| `OtfusionMetadata` parsing | `tests/unit/plugin_parser/test_pandas_parser.py` | Raw metadata dict → correct `OtfusionMetadata` fields; missing block → `None` |
| `find_line_intersections()` with `use_geo=True` | `tests/unit/plugin_datastore/track_geometry_store/` | Geo-space section endpoints + geo segments → correct intersection geo coordinates |
| Full intersection pipeline (integration) | `tests/integration/` | `PolarsTrackDataset` with geo columns + `otfusion_metadata` + `LineSection` → event has correct `geo_x/geo_y` |
| Fallback (no metadata / no geo columns) | existing test suite + new regression test | Image-space intersection still works; no `AttributeError` or `KeyError` |

---

## Open Question: Multiple OTFusion Files via `add_all()`

`PolarsTrackDataset.add_all()` merges multiple track datasets. If two OTFusion files with
different `geo_bounds` are merged, the strategy for combining `otfusion_metadata` is undefined.
For the initial implementation, `add_all()` should use the first non-`None` `otfusion_metadata`
it encounters. If all loaded files originate from the same OTFusion run (the common case), this
is correct. A stricter validation (assert all non-None values are equal) can be added later.

---

## What Does Not Change

- `Section` domain object — stays image-coordinate-only
- GUI layer (`customtkinter_gui`, `nicegui_gui`) — no changes needed
- CLI layer — no changes needed
- `create_events()` — no changes needed
- Non-fusion ottrk files — full backward compatibility

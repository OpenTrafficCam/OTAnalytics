# Georeference Metadata Format Update Design

**Date:** 2026-04-14
**Branch:** feature/9528-extend-sections-and-tracks-with-optional-geo-coordinates

## Summary

The ottrk file format produced by OTFusion has changed. The metadata block previously
keyed as `"otfusion"` is now keyed as `"georeference"`, and the BEV size field has
changed from a list `[w, h]` to a dict `{"width": w, "height": h}`. A `crs` string
field is also now stored in the domain model. No backwards compatibility is required.

## Format Changes

| Field | Old | New |
|---|---|---|
| Block key | `"otfusion"` | `"georeference"` |
| BEV size key | `"bev_size"` (list `[w, h]`) | `"birds_eye_view_size"` (dict `{width, height}`) |
| Geo bounds | `"geo_bounds": {min_x, min_y, max_x, max_y}` | unchanged |
| Padding | `"padding"` | unchanged |
| CRS | `"crs"` (present but not stored) | `"crs"` — now stored in domain model |

## Approach

Option A: Rename file and all references cleanly. No compatibility shims.

- `domain/otfusion.py` → `domain/georeference.py`
- `OtfusionMetadata` → `GeoreferenceMetadata`
- All imports, variable names, and docstrings updated accordingly.

## Components

### 1. `OTAnalytics/domain/georeference.py` (renamed from `otfusion.py`)

- Rename `OtfusionMetadata` → `GeoreferenceMetadata`
- Add `crs: str` field to the frozen dataclass
- `pixel_to_geo` stays in the same file; its `metadata` parameter type updates to `GeoreferenceMetadata`

```python
@dataclass(frozen=True)
class GeoreferenceMetadata:
    geo_min_x: float
    geo_min_y: float
    geo_max_x: float
    geo_max_y: float
    bev_width: int
    bev_height: int
    padding: int
    crs: str
```

### 2. `OTAnalytics/plugin_parser/ottrk_dataformat.py`

Replace the OTFusion constants block:

| Old constant | New constant |
|---|---|
| `OTFUSION = "otfusion"` | `GEOREFERENCE = "georeference"` |
| `BEV_SIZE = "bev_size"` | `BIRDS_EYE_VIEW_SIZE = "birds_eye_view_size"` |
| _(none)_ | `BIRDS_EYE_VIEW_WIDTH = "width"` |
| _(none)_ | `BIRDS_EYE_VIEW_HEIGHT = "height"` |

Constants `GEO_BOUNDS`, `GEO_BOUNDS_MIN_X`, `GEO_BOUNDS_MIN_Y`, `GEO_BOUNDS_MAX_X`,
`GEO_BOUNDS_MAX_Y`, `BEV_PADDING`, and `CRS` are unchanged.

Section comment: `# OTFusion metadata` → `# Georeference metadata`.

### 3. `OTAnalytics/plugin_parser/otvision_parser.py`

- Update import to `from OTAnalytics.domain.georeference import GeoreferenceMetadata`
- Rename `_parse_otfusion_metadata` → `_parse_georeference_metadata`
- Return type: `GeoreferenceMetadata | None`
- Parse block using `GEOREFERENCE` key
- Parse BEV size using `BIRDS_EYE_VIEW_SIZE` dict with `BIRDS_EYE_VIEW_WIDTH` / `BIRDS_EYE_VIEW_HEIGHT` sub-keys
- Parse and store `CRS` from the block into `GeoreferenceMetadata.crs`
- Update all call sites within the file

### 4. Cascade updates (~10 files)

All files that import or reference `OtfusionMetadata` / `otfusion_metadata`:

- `OTAnalytics/plugin_datastore/polars_track_store.py`
- `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`
- `OTAnalytics/application/use_cases/load_track_files.py`
- `OTAnalytics/domain/track_repository.py`
- `OTAnalytics/application/datastore.py`
- `OTAnalytics/plugin_prototypes/track_visualization/track_viz.py`
- `OTAnalytics/plugin_ui/customtkinter_gui/frame_project.py`
- `OTAnalytics/plugin_ui/customtkinter_gui/custom_containers.py`

For each: update import path (`domain.otfusion` → `domain.georeference`), class name
(`OtfusionMetadata` → `GeoreferenceMetadata`), variable names (`otfusion_metadata` →
`georeference_metadata`), and any docstrings that mention "OTFusion metadata".

### 5. Tests

- `tests/unit/OTAnalytics/domain/test_otfusion.py` → `test_georeference.py`
  - Update import and all `OtfusionMetadata` references to `GeoreferenceMetadata`
  - Add `crs` argument to all `GeoreferenceMetadata` constructor calls (use the real CRS
    string from the sample file or a placeholder string for unit tests)
- `tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py`
  - Update parser test fixtures to use new format keys (`georeference`,
    `birds_eye_view_size` dict) and assert that `crs` is populated on the result
- `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`
- `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`
  - Update class name and variable name references

## Error Handling

- `_parse_georeference_metadata` returns `None` when the `"georeference"` key is absent
  (non-OTFusion files). This mirrors the existing behaviour.
- Missing sub-keys (`geo_bounds`, `birds_eye_view_size`, `padding`, `crs`) raise `KeyError`
  — no silent recovery; a malformed georeference block is a data error.

## Out of Scope

- CRS-aware coordinate transformation (using the CRS string for projection math)
- Backwards compatibility with the old `"otfusion"` block key

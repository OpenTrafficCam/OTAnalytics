# Georeference Metadata Format Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `OtfusionMetadata` domain model and its `"otfusion"` ottrk block with `GeoreferenceMetadata` and the new `"georeference"` block, including the updated `birds_eye_view_size` dict format and a new `crs` field.

**Architecture:** Rename `domain/otfusion.py` → `domain/georeference.py` and `OtfusionMetadata` → `GeoreferenceMetadata` throughout. Update `ottrk_dataformat.py` constants to match the new block key and BEV size structure. Propagate changes through the parser, application layer, and datastores via mechanical renames.

**Tech Stack:** Python, polars, pytest (`uv run pytest`), dataclasses.

---

## File Map

| Action | File |
|---|---|
| Create | `OTAnalytics/domain/georeference.py` |
| Delete | `OTAnalytics/domain/otfusion.py` |
| Modify | `OTAnalytics/plugin_parser/ottrk_dataformat.py` |
| Modify | `OTAnalytics/plugin_parser/otvision_parser.py` |
| Modify | `OTAnalytics/application/datastore.py` |
| Modify | `OTAnalytics/application/use_cases/load_track_files.py` |
| Modify | `OTAnalytics/domain/track_repository.py` |
| Modify | `OTAnalytics/plugin_datastore/polars_track_store.py` |
| Modify | `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py` |
| Create | `tests/unit/OTAnalytics/domain/test_georeference.py` |
| Delete | `tests/unit/OTAnalytics/domain/test_otfusion.py` |
| Modify | `tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py` |
| Modify | `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py` |
| Modify | `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py` |

---

## Task 1: Replace domain module — create `georeference.py`, delete `otfusion.py`

**Files:**
- Create: `OTAnalytics/domain/georeference.py`
- Create: `tests/unit/OTAnalytics/domain/test_georeference.py`
- Delete: `OTAnalytics/domain/otfusion.py`
- Delete: `tests/unit/OTAnalytics/domain/test_otfusion.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/OTAnalytics/domain/test_georeference.py` with this content:

```python
import pytest
from pytest import approx

from OTAnalytics.domain.georeference import GeoreferenceMetadata, pixel_to_geo

# Real values from test_fusion_output_2026-04-14_16-34-59.ottrk.json
GEO_MIN_X = 449199.096512522
GEO_MIN_Y = 5699274.275524861
GEO_MAX_X = 449294.8688478645
GEO_MAX_Y = 5699370.047860203
BEV_WIDTH = 983
BEV_HEIGHT = 983
PADDING = 20
SAMPLE_CRS = "EPSG:25833"


@pytest.fixture
def sample_metadata() -> GeoreferenceMetadata:
    return GeoreferenceMetadata(
        geo_min_x=GEO_MIN_X,
        geo_min_y=GEO_MIN_Y,
        geo_max_x=GEO_MAX_X,
        geo_max_y=GEO_MAX_Y,
        bev_width=BEV_WIDTH,
        bev_height=BEV_HEIGHT,
        padding=PADDING,
        crs=SAMPLE_CRS,
    )


def test_pixel_to_geo_known_detection(sample_metadata: GeoreferenceMetadata) -> None:
    # Known detection from the sample ottrk file:
    # pixel (287.7537676212576, 441.6960590287385) -> geo (449226.28994, 5699327.21984)
    geo_x, geo_y = pixel_to_geo(287.7537676212576, 441.6960590287385, sample_metadata)
    assert geo_x == approx(449226.28994160134, rel=1e-6)
    assert geo_y == approx(5699327.2198470775, rel=1e-6)


def test_pixel_to_geo_top_left_corner(sample_metadata: GeoreferenceMetadata) -> None:
    # Padding pixel maps to geo_min_x, geo_max_y (top-left in geo = min_x, max_y)
    geo_x, geo_y = pixel_to_geo(PADDING, PADDING, sample_metadata)
    assert geo_x == approx(GEO_MIN_X, rel=1e-9)
    assert geo_y == approx(GEO_MAX_Y, rel=1e-9)


def test_pixel_to_geo_bottom_right_corner(sample_metadata: GeoreferenceMetadata) -> None:
    # (bev_width - padding, bev_height - padding) maps to geo_max_x, geo_min_y
    geo_x, geo_y = pixel_to_geo(
        BEV_WIDTH - PADDING, BEV_HEIGHT - PADDING, sample_metadata
    )
    assert geo_x == approx(GEO_MAX_X, rel=1e-9)
    assert geo_y == approx(GEO_MIN_Y, rel=1e-9)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/domain/test_georeference.py -v
```

Expected: `ModuleNotFoundError: No module named 'OTAnalytics.domain.georeference'`

- [ ] **Step 3: Create `OTAnalytics/domain/georeference.py`**

```python
"""Domain model for georeference BEV coordinate metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeoreferenceMetadata:
    """Geo-referencing metadata from an OTFusion ottrk file.

    Describes the affine mapping between BEV pixel coordinates and UTM
    geo coordinates for a single OTFusion output file.

    Attributes:
        geo_min_x: West boundary in UTM easting (metres).
        geo_min_y: South boundary in UTM northing (metres).
        geo_max_x: East boundary in UTM easting (metres).
        geo_max_y: North boundary in UTM northing (metres).
        bev_width: Width of the BEV image in pixels.
        bev_height: Height of the BEV image in pixels.
        padding: Pixel padding applied to all edges of the BEV image.
        crs: Coordinate reference system as a WKT or authority string.
    """

    geo_min_x: float
    geo_min_y: float
    geo_max_x: float
    geo_max_y: float
    bev_width: int
    bev_height: int
    padding: int
    crs: str


def pixel_to_geo(
    x: float, y: float, metadata: GeoreferenceMetadata
) -> tuple[float, float]:
    """Convert a BEV pixel coordinate to UTM geo coordinate.

    Args:
        x: Pixel x coordinate (column, increases rightward).
        y: Pixel y coordinate (row, increases downward).
        metadata: Georeference metadata containing geo bounds and image size.

    Returns:
        Tuple (geo_x, geo_y) in the same UTM coordinate system as the
        per-detection geo_x/geo_y fields.
    """
    scale_x = (metadata.geo_max_x - metadata.geo_min_x) / (
        metadata.bev_width - 2 * metadata.padding
    )
    scale_y = (metadata.geo_max_y - metadata.geo_min_y) / (
        metadata.bev_height - 2 * metadata.padding
    )
    geo_x = metadata.geo_min_x + (x - metadata.padding) * scale_x
    geo_y = metadata.geo_max_y - (y - metadata.padding) * scale_y
    return geo_x, geo_y
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/domain/test_georeference.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Delete old domain files**

```bash
git rm OTAnalytics/domain/otfusion.py
git rm tests/unit/OTAnalytics/domain/test_otfusion.py
```

- [ ] **Step 6: Commit**

```bash
git add OTAnalytics/domain/georeference.py tests/unit/OTAnalytics/domain/test_georeference.py
git commit -m "feat: replace OtfusionMetadata with GeoreferenceMetadata domain model"
```

---

## Task 2: Update `ottrk_dataformat.py` constants

**Files:**
- Modify: `OTAnalytics/plugin_parser/ottrk_dataformat.py`

- [ ] **Step 1: Replace the georeference constants block**

In `OTAnalytics/plugin_parser/ottrk_dataformat.py`, replace the lines:

```python
# OTFusion metadata
OTFUSION: str = "otfusion"
GEO_BOUNDS: str = "geo_bounds"
GEO_BOUNDS_MIN_X: str = "min_x"
GEO_BOUNDS_MIN_Y: str = "min_y"
GEO_BOUNDS_MAX_X: str = "max_x"
GEO_BOUNDS_MAX_Y: str = "max_y"
BEV_SIZE: str = "bev_size"
BEV_PADDING: str = "padding"
CRS: str = "crs"
```

with:

```python
# Georeference metadata
GEOREFERENCE: str = "georeference"
GEO_BOUNDS: str = "geo_bounds"
GEO_BOUNDS_MIN_X: str = "min_x"
GEO_BOUNDS_MIN_Y: str = "min_y"
GEO_BOUNDS_MAX_X: str = "max_x"
GEO_BOUNDS_MAX_Y: str = "max_y"
BIRDS_EYE_VIEW_SIZE: str = "birds_eye_view_size"
BIRDS_EYE_VIEW_WIDTH: str = "width"
BIRDS_EYE_VIEW_HEIGHT: str = "height"
BEV_PADDING: str = "padding"
CRS: str = "crs"
```

- [ ] **Step 2: Commit**

```bash
git add OTAnalytics/plugin_parser/ottrk_dataformat.py
git commit -m "feat: update ottrk_dataformat constants for georeference block"
```

---

## Task 3: Update `otvision_parser.py` and its test

**Files:**
- Modify: `OTAnalytics/plugin_parser/otvision_parser.py`
- Modify: `tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py`

- [ ] **Step 1: Update the test first**

In `tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py`:

1. Replace the import on line 17:
```python
# old
from OTAnalytics.domain.otfusion import OtfusionMetadata
# new
from OTAnalytics.domain.georeference import GeoreferenceMetadata
```

2. Replace `SAMPLE_OTFUSION_METADATA_DICT` (lines 269–281) with:
```python
SAMPLE_GEOREFERENCE_METADATA_DICT = {
    ottrk_dataformat.GEOREFERENCE: {
        ottrk_dataformat.GEO_BOUNDS: {
            ottrk_dataformat.GEO_BOUNDS_MIN_X: 449199.096512522,
            ottrk_dataformat.GEO_BOUNDS_MIN_Y: 5699274.275524861,
            ottrk_dataformat.GEO_BOUNDS_MAX_X: 449294.8688478645,
            ottrk_dataformat.GEO_BOUNDS_MAX_Y: 5699370.047860203,
        },
        ottrk_dataformat.BIRDS_EYE_VIEW_SIZE: {
            ottrk_dataformat.BIRDS_EYE_VIEW_WIDTH: 983,
            ottrk_dataformat.BIRDS_EYE_VIEW_HEIGHT: 983,
        },
        ottrk_dataformat.BEV_PADDING: 20,
        ottrk_dataformat.CRS: "EPSG:25833",
    }
}
```

3. Replace `TestParseOtfusionMetadata` (lines 284–299) with:
```python
class TestParseGeoreferenceMetadata:
    def test_returns_metadata_when_georeference_block_present(self) -> None:
        result = OttrkParser._parse_georeference_metadata(
            SAMPLE_GEOREFERENCE_METADATA_DICT
        )
        assert result == GeoreferenceMetadata(
            geo_min_x=449199.096512522,
            geo_min_y=5699274.275524861,
            geo_max_x=449294.8688478645,
            geo_max_y=5699370.047860203,
            bev_width=983,
            bev_height=983,
            padding=20,
            crs="EPSG:25833",
        )

    def test_returns_none_when_georeference_block_absent(self) -> None:
        result = OttrkParser._parse_georeference_metadata({"video": {}})
        assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py::TestParseGeoreferenceMetadata -v
```

Expected: `AttributeError: type object 'OttrkParser' has no attribute '_parse_georeference_metadata'`

- [ ] **Step 3: Update `otvision_parser.py`**

1. Replace the import (near line 27):
```python
# old
from OTAnalytics.domain.otfusion import OtfusionMetadata
# new
from OTAnalytics.domain.georeference import GeoreferenceMetadata
```

2. In the `parse` method (around line 605), rename the variable and method call:
```python
# old
otfusion_metadata = self._parse_otfusion_metadata(
    ottrk_dict[ottrk_format.METADATA]
)
return TrackParseResult(
    tracks, detection_metadata, video_metadata, otfusion_metadata
)
# new
georeference_metadata = self._parse_georeference_metadata(
    ottrk_dict[ottrk_format.METADATA]
)
return TrackParseResult(
    tracks, detection_metadata, video_metadata, georeference_metadata
)
```

3. Replace the `_parse_otfusion_metadata` classmethod (lines 649–672) with:
```python
@classmethod
def _parse_georeference_metadata(
    cls, metadata: dict
) -> GeoreferenceMetadata | None:
    """Parse the georeference block from ottrk metadata.

    Args:
        metadata: The full metadata dict from an ottrk file.

    Returns:
        GeoreferenceMetadata if the georeference block is present, otherwise None.
    """
    georeference = metadata.get(ottrk_format.GEOREFERENCE)
    if georeference is None:
        return None
    bounds = georeference[ottrk_format.GEO_BOUNDS]
    bev_size = georeference[ottrk_format.BIRDS_EYE_VIEW_SIZE]
    return GeoreferenceMetadata(
        geo_min_x=bounds[ottrk_format.GEO_BOUNDS_MIN_X],
        geo_min_y=bounds[ottrk_format.GEO_BOUNDS_MIN_Y],
        geo_max_x=bounds[ottrk_format.GEO_BOUNDS_MAX_X],
        geo_max_y=bounds[ottrk_format.GEO_BOUNDS_MAX_Y],
        bev_width=bev_size[ottrk_format.BIRDS_EYE_VIEW_WIDTH],
        bev_height=bev_size[ottrk_format.BIRDS_EYE_VIEW_HEIGHT],
        padding=georeference[ottrk_format.BEV_PADDING],
        crs=georeference[ottrk_format.CRS],
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_parser/otvision_parser.py \
        tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py
git commit -m "feat: update otvision_parser to parse georeference block"
```

---

## Task 4: Update `datastore.py` and `load_track_files.py`

**Files:**
- Modify: `OTAnalytics/application/datastore.py`
- Modify: `OTAnalytics/application/use_cases/load_track_files.py`

- [ ] **Step 1: Update `datastore.py`**

1. Replace the import (around line 21):
```python
# old
from OTAnalytics.domain.otfusion import OtfusionMetadata
# new
from OTAnalytics.domain.georeference import GeoreferenceMetadata
```

2. In `TrackParseResult` dataclass (around line 53–55), rename the field:
```python
# old
otfusion_metadata: OtfusionMetadata | None = None
# new
georeference_metadata: GeoreferenceMetadata | None = None
```

3. In `TracksParseResult` dataclass (around line 61–63), rename the field:
```python
# old
otfusion_metadata: OtfusionMetadata | None = None
# new
georeference_metadata: GeoreferenceMetadata | None = None
```

4. In the `TracksParseResult.from_results` classmethod (around lines 81–88), update the variable names:
```python
# old
otfusion_metadata = next(
    (r.otfusion_metadata for r in results if r.otfusion_metadata is not None),
    None,
)
return TracksParseResult(
    tracks, detections_metadata, videos_metadata, otfusion_metadata
)
# new
georeference_metadata = next(
    (
        r.georeference_metadata
        for r in results
        if r.georeference_metadata is not None
    ),
    None,
)
return TracksParseResult(
    tracks, detections_metadata, videos_metadata, georeference_metadata
)
```

- [ ] **Step 2: Update `load_track_files.py`**

Find the line (around line 61):
```python
self._track_repository.apply_otfusion_metadata(parse_result.otfusion_metadata)
```
Replace with:
```python
self._track_repository.apply_georeference_metadata(
    parse_result.georeference_metadata
)
```

- [ ] **Step 3: Run the affected tests**

```bash
uv run pytest tests/unit/OTAnalytics/application/ -v
```

Expected: All tests pass (these files have no direct unit tests for the renamed fields, the integration is verified in later tasks).

- [ ] **Step 4: Commit**

```bash
git add OTAnalytics/application/datastore.py \
        OTAnalytics/application/use_cases/load_track_files.py
git commit -m "feat: rename otfusion_metadata to georeference_metadata in application layer"
```

---

## Task 5: Update `track_repository.py`

**Files:**
- Modify: `OTAnalytics/domain/track_repository.py`

- [ ] **Step 1: Update `track_repository.py`**

1. Replace the import (around line 9):
```python
# old
from OTAnalytics.domain.otfusion import OtfusionMetadata
# new
from OTAnalytics.domain.georeference import GeoreferenceMetadata
```

2. Rename the method and update its body (around lines 153–163):
```python
# old
def apply_otfusion_metadata(self, metadata: OtfusionMetadata | None) -> None:
    """Attach OTFusion geo-referencing metadata to the track dataset.
    ...
    """
    if metadata is None:
        return
    if hasattr(self._dataset, "with_otfusion_metadata"):
        self._dataset = self._dataset.with_otfusion_metadata(metadata)

# new
def apply_georeference_metadata(self, metadata: GeoreferenceMetadata | None) -> None:
    """Attach geo-referencing metadata to the track dataset.

    Args:
        metadata: The georeference metadata to attach, or None to skip.
    """
    if metadata is None:
        return
    if hasattr(self._dataset, "with_georeference_metadata"):
        self._dataset = self._dataset.with_georeference_metadata(metadata)
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/unit/OTAnalytics/domain/ -v
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add OTAnalytics/domain/track_repository.py
git commit -m "feat: rename apply_otfusion_metadata to apply_georeference_metadata"
```

---

## Task 6: Update `polars_track_store.py` and its test

**Files:**
- Modify: `OTAnalytics/plugin_datastore/polars_track_store.py`
- Modify: `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`

- [ ] **Step 1: Update the test first**

In `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`:

1. Replace the import (around line 10):
```python
# old
from OTAnalytics.domain.otfusion import OtfusionMetadata
# new
from OTAnalytics.domain.georeference import GeoreferenceMetadata
```

2. Replace `SAMPLE_OTFUSION_METADATA` (around lines 690–698):
```python
SAMPLE_GEOREFERENCE_METADATA = GeoreferenceMetadata(
    geo_min_x=449199.0,
    geo_min_y=5699274.0,
    geo_max_x=449294.0,
    geo_max_y=5699370.0,
    bev_width=983,
    bev_height=983,
    padding=20,
    crs="EPSG:25833",
)
```

3. Replace `TestPolarsTrackDatasetOtfusionMetadata` (around lines 701–720):
```python
class TestPolarsTrackDatasetGeoreferenceMetadata:
    def test_georeference_metadata_is_none_by_default(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        assert dataset.georeference_metadata is None

    def test_with_georeference_metadata_returns_new_dataset_with_metadata(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        updated = dataset.with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        assert updated.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_with_georeference_metadata_does_not_mutate_original(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        dataset.with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        assert dataset.georeference_metadata is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsTrackDatasetGeoreferenceMetadata -v
```

Expected: `AttributeError: 'PolarsTrackDataset' object has no attribute 'georeference_metadata'`

- [ ] **Step 3: Update `polars_track_store.py`**

1. Replace the import (around line 28):
```python
# old
from OTAnalytics.domain.otfusion import OtfusionMetadata
# new
from OTAnalytics.domain.georeference import GeoreferenceMetadata
```

2. Replace the `otfusion_metadata` property (around lines 352–355):
```python
# old
@property
def otfusion_metadata(self) -> OtfusionMetadata | None:
    """OTFusion geo-referencing metadata, or None for non-fusion datasets."""
    return self._otfusion_metadata

# new
@property
def georeference_metadata(self) -> GeoreferenceMetadata | None:
    """Geo-referencing metadata, or None for non-fusion datasets."""
    return self._georeference_metadata
```

3. Replace the `with_otfusion_metadata` method (around lines 357–373):
```python
# old
def with_otfusion_metadata(
    self, metadata: OtfusionMetadata | None
) -> "PolarsTrackDataset":
    """Return a new dataset with the given OtfusionMetadata attached.
    ...
    """
    return PolarsTrackDataset(
        dataset=self._dataset,
        geometry_datasets=self._geometry_datasets,
        calculator=self._calculator,
        otfusion_metadata=metadata,
    )

# new
def with_georeference_metadata(
    self, metadata: GeoreferenceMetadata | None
) -> "PolarsTrackDataset":
    """Return a new dataset with the given GeoreferenceMetadata attached.

    Args:
        metadata: The georeference metadata to attach.

    Returns:
        A new PolarsTrackDataset with the metadata attached.
    """
    return PolarsTrackDataset(
        dataset=self._dataset,
        geometry_datasets=self._geometry_datasets,
        calculator=self._calculator,
        georeference_metadata=metadata,
    )
```

4. In `__init__` (around lines 382–399), rename the parameter and attribute:
```python
# old (parameter)
otfusion_metadata: OtfusionMetadata | None = None,
# new
georeference_metadata: GeoreferenceMetadata | None = None,
```
```python
# old (assignment)
self._otfusion_metadata = otfusion_metadata
# new
self._georeference_metadata = georeference_metadata
```

5. In `wrap_intersection_points` call (around line 619), rename the argument:
```python
# old
sections, self._otfusion_metadata
# new
sections, self._georeference_metadata
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/polars_track_store.py \
        tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py
git commit -m "feat: rename otfusion_metadata to georeference_metadata in PolarsTrackDataset"
```

---

## Task 7: Update `polars_geometry_store.py` and its test

**Files:**
- Modify: `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`
- Modify: `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`

- [ ] **Step 1: Update the test first**

In `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`:

1. Replace the import (around line 13):
```python
# old
from OTAnalytics.domain.otfusion import OtfusionMetadata
# new
from OTAnalytics.domain.georeference import GeoreferenceMetadata
```

2. Rename `_make_otfusion_metadata` → `_make_georeference_metadata` and update
   the docstring and return type (around lines 1156–1172). The method body creates
   an `OtfusionMetadata` — replace with `GeoreferenceMetadata` and add `crs`:

```python
def _make_georeference_metadata(self) -> GeoreferenceMetadata:
    """Metadata where pixel (100, 100) maps to geo (449250, 5699325).

    Using:
      scale_x = (449300 - 449200) / (200 - 40) = 100 / 160 = 0.625
      scale_y = (5699350 - 5699300) / (200 - 40) = 50 / 160 = 0.3125
      pixel_x=100 -> geo_x = 449200 + (100-20)*0.625 = 449200 + 50 = 449250  ✓
      pixel_y=100 -> geo_y = 5699350 - (100-20)*0.3125 = 5699350 - 25 = 5699325  ✓
    """
    return GeoreferenceMetadata(
        geo_min_x=449200.0,
        geo_min_y=5699300.0,
        geo_max_x=449300.0,
        geo_max_y=5699350.0,
        bev_width=200,
        bev_height=200,
        padding=20,
        crs="EPSG:25833",
    )
```

3. Update all call sites of `_make_otfusion_metadata` within the same file to
   `_make_georeference_metadata`.

4. Replace the docstring on `TestWrapIntersectionPointsWithGeo` (around line 1116):
```python
# old
"""When otfusion_metadata is provided and segments have geo columns,
section pixel coords are converted to geo and intersection uses geo math."""
# new
"""When georeference_metadata is provided and segments have geo columns,
section pixel coords are converted to geo and intersection uses geo math."""
```

5. Replace the docstring on `TestWrapIntersectionPointsFallback` (around line 1217):
```python
# old
"""Ensures non-fusion files (no geo columns, no OtfusionMetadata) are unaffected."""
# new
"""Ensures non-fusion files (no geo columns, no GeoreferenceMetadata) are unaffected."""
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestWrapIntersectionPointsWithGeo -v
```

Expected: `ImportError` or `AttributeError` related to `OtfusionMetadata` still being referenced in `polars_geometry_store.py`.

- [ ] **Step 3: Update `polars_geometry_store.py`**

1. Replace the import (around line 23):
```python
# old
from OTAnalytics.domain.otfusion import OtfusionMetadata, pixel_to_geo
# new
from OTAnalytics.domain.georeference import GeoreferenceMetadata, pixel_to_geo
```

2. In `wrap_intersection_points` signature (around line 1313), rename the parameter:
```python
# old
otfusion_metadata: OtfusionMetadata | None = None,
# new
georeference_metadata: GeoreferenceMetadata | None = None,
```

3. Update the docstring for that parameter (around line 1323):
```python
# old
otfusion_metadata: OTFusion geo-referencing metadata. When present
    and geo columns exist, enables geo-space intersection detection.
# new
georeference_metadata: Geo-referencing metadata. When present
    and geo columns exist, enables geo-space intersection detection.
```

4. Update the docstring on line 1317 (class-level comment):
```python
# old
When otfusion_metadata is provided and the segments DataFrame contains
# new
When georeference_metadata is provided and the segments DataFrame contains
```

5. In the method body, rename all occurrences of `otfusion_metadata` to
   `georeference_metadata` (the `use_geo` assignment around line 1344, the
   `assert` around line 1362, and the two `pixel_to_geo` calls on lines 1363–1369).

- [ ] **Step 4: Run all geometry store tests**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/ -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py \
        tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py
git commit -m "feat: rename otfusion_metadata to georeference_metadata in polars_geometry_store"
```

---

## Task 8: Full test suite verification

- [ ] **Step 1: Run the full test suite**

```bash
uv run pytest tests/unit/ -v
```

Expected: All tests pass. If any fail, read the error message — it will name a file still importing from `OTAnalytics.domain.otfusion` or using the old class name. Fix that file, re-run.

- [ ] **Step 2: Confirm no remaining references to old names**

```bash
grep -r "OtfusionMetadata\|domain\.otfusion\|otfusion_metadata\|with_otfusion_metadata\|apply_otfusion_metadata\|_parse_otfusion_metadata\|OTFUSION\b\|BEV_SIZE\b" \
    OTAnalytics/ tests/ --include="*.py"
```

Expected: no output (zero matches).

- [ ] **Step 3: Commit**

```bash
git commit -m "feat: complete georeference metadata rename — no otfusion references remain"
```

# Geo-Coordinate-Based Intersection Events Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When OTFusion tracks carry `geo_x`/`geo_y` coordinates, use geo space (instead of BEV pixel space) for intersection detection and propagate geo coordinates onto the resulting events.

**Architecture:** Parse `OtfusionMetadata` from the ottrk `metadata.otfusion` block; store it on `PolarsTrackDataset`; convert section pixel endpoints to geo before calling `find_line_intersections`; use track `START_GEO_X/Y`/`END_GEO_X/Y` columns for the intersection math when geo is available. Non-fusion files fall back to existing image-space detection unchanged.

**Tech Stack:** Python 3.11+, Polars, frozen dataclasses, pytest, `uv run pytest`

---

## File Map

| Action | File | Responsibility |
|--------|------|---------------|
| **Create** | `OTAnalytics/domain/otfusion.py` | `OtfusionMetadata` dataclass + `pixel_to_geo()` |
| **Modify** | `OTAnalytics/plugin_parser/ottrk_dataformat.py` | Add `otfusion` block constants |
| **Modify** | `OTAnalytics/application/datastore.py` | Add `otfusion_metadata` to `TrackParseResult`, `TracksParseResult`; update `parse_files()` |
| **Modify** | `OTAnalytics/plugin_parser/otvision_parser.py` | `OttrkParser.parse()` parses and stores `OtfusionMetadata` |
| **Modify** | `OTAnalytics/domain/track_repository.py` | New `apply_otfusion_metadata()` method |
| **Modify** | `OTAnalytics/plugin_datastore/polars_track_store.py` | `otfusion_metadata` field; `with_otfusion_metadata()`; update `intersection_points()` |
| **Modify** | `OTAnalytics/application/use_cases/load_track_files.py` | Pass `otfusion_metadata` to repository |
| **Modify** | `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py` | `find_line_intersections(use_geo)`, `wrap_intersection_points(otfusion_metadata)` |
| **Create** | `tests/unit/OTAnalytics/domain/test_otfusion.py` | Unit tests for `OtfusionMetadata` + `pixel_to_geo()` |
| **Modify** | `tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py` | Tests for otfusion metadata parsing |
| **Modify** | `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py` | Tests for `otfusion_metadata` field |
| **Modify** | `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py` | Tests for geo-mode intersection |

---

## Task 1: `OtfusionMetadata` domain class and `pixel_to_geo()`

**Files:**
- Create: `OTAnalytics/domain/otfusion.py`
- Create: `tests/unit/OTAnalytics/domain/test_otfusion.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/OTAnalytics/domain/test_otfusion.py
from dataclasses import dataclass
import pytest
from pytest import approx
from OTAnalytics.domain.otfusion import OtfusionMetadata, pixel_to_geo

# Real values from test_fusion_output_2026-04-13_14-36-10.ottrk.json
GEO_MIN_X = 449199.096512522
GEO_MIN_Y = 5699274.275524861
GEO_MAX_X = 449294.8688478645
GEO_MAX_Y = 5699370.047860203
BEV_WIDTH = 983
BEV_HEIGHT = 983
PADDING = 20


@pytest.fixture
def sample_metadata() -> OtfusionMetadata:
    return OtfusionMetadata(
        geo_min_x=GEO_MIN_X,
        geo_min_y=GEO_MIN_Y,
        geo_max_x=GEO_MAX_X,
        geo_max_y=GEO_MAX_Y,
        bev_width=BEV_WIDTH,
        bev_height=BEV_HEIGHT,
        padding=PADDING,
    )


def test_pixel_to_geo_known_detection(sample_metadata: OtfusionMetadata) -> None:
    # Known detection from the sample ottrk file:
    # pixel (287.7537676212576, 441.6960590287385) -> geo (449226.28994, 5699327.21984)
    geo_x, geo_y = pixel_to_geo(287.7537676212576, 441.6960590287385, sample_metadata)
    assert geo_x == approx(449226.28994160134, rel=1e-6)
    assert geo_y == approx(5699327.2198470775, rel=1e-6)


def test_pixel_to_geo_top_left_corner(sample_metadata: OtfusionMetadata) -> None:
    # Padding pixel maps to geo_min_x, geo_max_y (top-left in geo = min_x, max_y)
    geo_x, geo_y = pixel_to_geo(PADDING, PADDING, sample_metadata)
    assert geo_x == approx(GEO_MIN_X, rel=1e-9)
    assert geo_y == approx(GEO_MAX_Y, rel=1e-9)


def test_pixel_to_geo_bottom_right_corner(sample_metadata: OtfusionMetadata) -> None:
    # (bev_width - padding, bev_height - padding) maps to geo_max_x, geo_min_y
    geo_x, geo_y = pixel_to_geo(BEV_WIDTH - PADDING, BEV_HEIGHT - PADDING, sample_metadata)
    assert geo_x == approx(GEO_MAX_X, rel=1e-9)
    assert geo_y == approx(GEO_MIN_Y, rel=1e-9)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/OTAnalytics/domain/test_otfusion.py -v
```

Expected: `ModuleNotFoundError: No module named 'OTAnalytics.domain.otfusion'`

- [ ] **Step 3: Implement `OtfusionMetadata` and `pixel_to_geo()`**

Create `OTAnalytics/domain/otfusion.py`:

```python
"""Domain model for OTFusion BEV coordinate metadata."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OtfusionMetadata:
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
    """

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
    """Convert a BEV pixel coordinate to UTM geo coordinate.

    Args:
        x: Pixel x coordinate (column, increases rightward).
        y: Pixel y coordinate (row, increases downward).
        metadata: OTFusion metadata containing geo bounds and image size.

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

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/OTAnalytics/domain/test_otfusion.py -v
```

Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/domain/otfusion.py tests/unit/OTAnalytics/domain/test_otfusion.py
git commit -m "feat: add OtfusionMetadata domain class and pixel_to_geo conversion"
```

---

## Task 2: Add `otfusion` constants and parse from `OttrkParser`

**Files:**
- Modify: `OTAnalytics/plugin_parser/ottrk_dataformat.py`
- Modify: `OTAnalytics/application/datastore.py`
- Modify: `OTAnalytics/plugin_parser/otvision_parser.py`
- Modify: `tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py`

- [ ] **Step 1: Write the failing tests**

Open `tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py` and add:

```python
# Add these imports at the top with the other imports:
from OTAnalytics.domain.otfusion import OtfusionMetadata
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format


# Add these test functions:
SAMPLE_OTFUSION_METADATA_DICT = {
    ottrk_format.OTFUSION: {
        ottrk_format.GEO_BOUNDS: {
            ottrk_format.GEO_BOUNDS_MIN_X: 449199.096512522,
            ottrk_format.GEO_BOUNDS_MIN_Y: 5699274.275524861,
            ottrk_format.GEO_BOUNDS_MAX_X: 449294.8688478645,
            ottrk_format.GEO_BOUNDS_MAX_Y: 5699370.047860203,
        },
        ottrk_format.BEV_SIZE: [983, 983],
        ottrk_format.BEV_PADDING: 20,
        ottrk_format.CRS: "EPSG:25833",
    }
}


class TestParseOtfusionMetadata:
    def test_returns_metadata_when_otfusion_block_present(self) -> None:
        result = OttrkParser._parse_otfusion_metadata(SAMPLE_OTFUSION_METADATA_DICT)
        assert result == OtfusionMetadata(
            geo_min_x=449199.096512522,
            geo_min_y=5699274.275524861,
            geo_max_x=449294.8688478645,
            geo_max_y=5699370.047860203,
            bev_width=983,
            bev_height=983,
            padding=20,
        )

    def test_returns_none_when_otfusion_block_absent(self) -> None:
        result = OttrkParser._parse_otfusion_metadata({"video": {}})
        assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py::TestParseOtfusionMetadata -v
```

Expected: `AttributeError: type object 'OttrkParser' has no attribute '_parse_otfusion_metadata'`

- [ ] **Step 3: Add constants to `ottrk_dataformat.py`**

Append to `OTAnalytics/plugin_parser/ottrk_dataformat.py`:

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

- [ ] **Step 4: Add `otfusion_metadata` to `TrackParseResult` and `TracksParseResult`**

In `OTAnalytics/application/datastore.py`, update both dataclasses (they are `frozen=True` so add the new field with a default):

```python
# Add this import at the top of the file (with other domain imports):
from OTAnalytics.domain.otfusion import OtfusionMetadata

# Change TrackParseResult from:
@dataclass(frozen=True)
class TrackParseResult:
    tracks: TrackDataset
    detection_metadata: DetectionMetadata
    video_metadata: VideoMetadata

# To:
@dataclass(frozen=True)
class TrackParseResult:
    tracks: TrackDataset
    detection_metadata: DetectionMetadata
    video_metadata: VideoMetadata
    otfusion_metadata: OtfusionMetadata | None = None

# Change TracksParseResult from:
@dataclass(frozen=True)
class TracksParseResult:
    tracks: TrackDataset
    detections_metadata: list[DetectionMetadata]
    videos_metadata: list[VideoMetadata]

# To:
@dataclass(frozen=True)
class TracksParseResult:
    tracks: TrackDataset
    detections_metadata: list[DetectionMetadata]
    videos_metadata: list[VideoMetadata]
    otfusion_metadata: OtfusionMetadata | None = None
```

Also update `TrackParser.parse_files()` to collect `otfusion_metadata`:

```python
def parse_files(self, files: list[Path]) -> TracksParseResult:
    if not files:
        raise ValueError("No files to parse")
    results = [self.parse(file) for file in files]
    tracks = combine_track_datasets(results)
    detections_metadata = [result.detection_metadata for result in results]
    videos_metadata = [result.video_metadata for result in results]
    otfusion_metadata = next(
        (r.otfusion_metadata for r in results if r.otfusion_metadata is not None),
        None,
    )
    return TracksParseResult(tracks, detections_metadata, videos_metadata, otfusion_metadata)
```

- [ ] **Step 5: Add `_parse_otfusion_metadata` and update `OttrkParser.parse()`**

In `OTAnalytics/plugin_parser/otvision_parser.py`:

Add import at top with other imports:
```python
from OTAnalytics.domain.otfusion import OtfusionMetadata
from OTAnalytics.plugin_parser import ottrk_dataformat as ottrk_format  # already imported as ottrk_format
```

Add class method to `OttrkParser`:
```python
@classmethod
def _parse_otfusion_metadata(cls, metadata: dict) -> OtfusionMetadata | None:
    """Parse the OTFusion geo-referencing block from ottrk metadata.

    Args:
        metadata: The full metadata dict from an ottrk file.

    Returns:
        OtfusionMetadata if the otfusion block is present, otherwise None.
    """
    otfusion = metadata.get(ottrk_format.OTFUSION)
    if otfusion is None:
        return None
    bounds = otfusion[ottrk_format.GEO_BOUNDS]
    bev_size = otfusion[ottrk_format.BEV_SIZE]
    return OtfusionMetadata(
        geo_min_x=bounds[ottrk_format.GEO_BOUNDS_MIN_X],
        geo_min_y=bounds[ottrk_format.GEO_BOUNDS_MIN_Y],
        geo_max_x=bounds[ottrk_format.GEO_BOUNDS_MAX_X],
        geo_max_y=bounds[ottrk_format.GEO_BOUNDS_MAX_Y],
        bev_width=bev_size[0],
        bev_height=bev_size[1],
        padding=otfusion[ottrk_format.BEV_PADDING],
    )
```

Update `OttrkParser.parse()` to pass `otfusion_metadata` to `TrackParseResult`:
```python
def parse(self, ottrk_file: Path) -> TrackParseResult:
    ottrk_dict = parse_json_bz2(ottrk_file)
    fixed_ottrk = self._format_fixer.fix(ottrk_dict)
    dets_list: list[dict] = fixed_ottrk[ottrk_format.DATA][
        ottrk_format.DATA_DETECTIONS
    ]
    metadata_video = ottrk_dict[ottrk_format.METADATA][ottrk_format.VIDEO]
    video_metadata = self.parse_video_metadata(metadata_video)
    id_generator = self.create_id_generator_from(ottrk_dict[ottrk_format.METADATA])
    tracks = self._detection_parser.parse_tracks(
        dets_list, metadata_video, str(ottrk_file), id_generator
    )
    detection_metadata = self.parse_metadata(ottrk_dict[ottrk_format.METADATA])
    otfusion_metadata = self._parse_otfusion_metadata(
        ottrk_dict[ottrk_format.METADATA]
    )
    return TrackParseResult(tracks, detection_metadata, video_metadata, otfusion_metadata)
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py::TestParseOtfusionMetadata -v
```

Expected: 2 PASSED

- [ ] **Step 7: Run full test suite to check no regressions**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/ -v
```

Expected: all PASSED

- [ ] **Step 8: Commit**

```bash
git add OTAnalytics/plugin_parser/ottrk_dataformat.py \
        OTAnalytics/application/datastore.py \
        OTAnalytics/plugin_parser/otvision_parser.py \
        tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py
git commit -m "feat: parse OtfusionMetadata from ottrk and propagate through TrackParseResult"
```

---

## Task 3: Thread `OtfusionMetadata` to `PolarsTrackDataset` via repository

**Files:**
- Modify: `OTAnalytics/plugin_datastore/polars_track_store.py`
- Modify: `OTAnalytics/domain/track_repository.py`
- Modify: `OTAnalytics/application/use_cases/load_track_files.py`
- Modify: `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`

- [ ] **Step 1: Write the failing test**

Open `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py` and add:

```python
# Add this import with the other imports at the top:
from OTAnalytics.domain.otfusion import OtfusionMetadata

SAMPLE_OTFUSION_METADATA = OtfusionMetadata(
    geo_min_x=449199.0,
    geo_min_y=5699274.0,
    geo_max_x=449294.0,
    geo_max_y=5699370.0,
    bev_width=983,
    bev_height=983,
    padding=20,
)


class TestPolarsTrackDatasetOtfusionMetadata:
    def test_otfusion_metadata_is_none_by_default(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        assert dataset.otfusion_metadata is None

    def test_with_otfusion_metadata_returns_new_dataset_with_metadata(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        updated = dataset.with_otfusion_metadata(SAMPLE_OTFUSION_METADATA)
        assert updated.otfusion_metadata == SAMPLE_OTFUSION_METADATA

    def test_with_otfusion_metadata_does_not_mutate_original(
        self, track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY
    ) -> None:
        dataset = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        dataset.with_otfusion_metadata(SAMPLE_OTFUSION_METADATA)
        assert dataset.otfusion_metadata is None
```

Note: the test class uses a `track_geometry_factory` fixture. Check whether it already exists in this file or in `conftest.py` using `grep -n "track_geometry_factory" tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`. If it doesn't exist, add this fixture to the test file:

```python
@pytest.fixture
def track_geometry_factory() -> POLARS_TRACK_GEOMETRY_FACTORY:
    return PolarsTrackGeometryDataset.from_track_dataset
```

- [ ] **Step 2: Run the failing test**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsTrackDatasetOtfusionMetadata -v
```

Expected: `AttributeError: 'PolarsTrackDataset' object has no attribute 'otfusion_metadata'`

- [ ] **Step 3: Add `otfusion_metadata` field and `with_otfusion_metadata()` to `PolarsTrackDataset`**

In `OTAnalytics/plugin_datastore/polars_track_store.py`:

Add import at top:
```python
from OTAnalytics.domain.otfusion import OtfusionMetadata
```

Update `PolarsTrackDataset.__init__()` (currently at line 347) to add the new parameter:
```python
def __init__(
    self,
    track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    dataset: pl.DataFrame | None = None,
    geometry_datasets: (
        dict[RelativeOffsetCoordinate, PolarsTrackGeometryDataset] | None
    ) = None,
    calculator: PolarsTrackClassificationCalculator = DEFAULT_CLASSIFICATOR,
    otfusion_metadata: OtfusionMetadata | None = None,
):
    # ... existing body unchanged ...
    self._otfusion_metadata = otfusion_metadata
```

Add property:
```python
@property
def otfusion_metadata(self) -> OtfusionMetadata | None:
    return self._otfusion_metadata
```

Add method (after the `otfusion_metadata` property):
```python
def with_otfusion_metadata(
    self, metadata: OtfusionMetadata | None
) -> "PolarsTrackDataset":
    """Return a new dataset with the given OtfusionMetadata attached.

    Args:
        metadata: Geo-referencing metadata for BEV pixel → UTM conversion.

    Returns:
        New PolarsTrackDataset with all existing data and the provided metadata.
    """
    return PolarsTrackDataset(
        track_geometry_factory=self._track_geometry_factory,
        dataset=self._dataset,
        geometry_datasets=self._geometry_datasets,
        calculator=self._calculator,
        otfusion_metadata=metadata,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsTrackDatasetOtfusionMetadata -v
```

Expected: 3 PASSED

- [ ] **Step 5: Add `apply_otfusion_metadata()` to `TrackRepository`**

In `OTAnalytics/domain/track_repository.py`:

Add import at the top with other imports:
```python
from OTAnalytics.domain.otfusion import OtfusionMetadata
```

Add method to `TrackRepository` (after the existing `add_all()` method):
```python
def apply_otfusion_metadata(
    self, metadata: OtfusionMetadata | None
) -> None:
    """Attach OTFusion geo-referencing metadata to the track dataset.

    Args:
        metadata: Geo-referencing metadata parsed from an OTFusion ottrk
            file. If None, this call has no effect.
    """
    if metadata is None:
        return
    if hasattr(self._dataset, "with_otfusion_metadata"):
        self._dataset = self._dataset.with_otfusion_metadata(metadata)
```

- [ ] **Step 6: Update `LoadTrackFiles` to pass metadata to repository**

In `OTAnalytics/application/use_cases/load_track_files.py`, update `__call__()`:

```python
# Replace this line:
self._track_repository.add_all(parse_result.tracks)

# With these two lines:
self._track_repository.add_all(parse_result.tracks)
self._track_repository.apply_otfusion_metadata(parse_result.otfusion_metadata)
```

- [ ] **Step 7: Run the full unit test suite**

```bash
uv run pytest tests/unit/ -v --tb=short
```

Expected: all PASSED

- [ ] **Step 8: Commit**

```bash
git add OTAnalytics/plugin_datastore/polars_track_store.py \
        OTAnalytics/domain/track_repository.py \
        OTAnalytics/application/use_cases/load_track_files.py \
        tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py
git commit -m "feat: thread OtfusionMetadata from TrackRepository into PolarsTrackDataset"
```

---

## Task 4: Update `find_line_intersections()` with `use_geo` flag

**Files:**
- Modify: `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`
- Modify: `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`

- [ ] **Step 1: Write the failing test**

Add to `test_polars_geometry_store.py`:

```python
# Add with other imports at the top:
from OTAnalytics.domain.track_dataset.track_dataset import (
    START_GEO_X, START_GEO_Y, END_GEO_X, END_GEO_Y,
)


def _create_segments_df_with_geo() -> pl.DataFrame:
    """Single track segment in both pixel and geo coordinate space.

    Pixel: (100, 0) -> (100, 200)   — vertical segment at x=100
    Geo:   (449250.0, 5699320.0) -> (449250.0, 5699340.0)  — vertical geo segment
    Section line (geo): (449240.0, 5699325.0) -> (449260.0, 5699325.0) — horizontal
    Expected intersection geo: (449250.0, 5699325.0)
    """
    from datetime import datetime, timezone

    occ_start = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    occ_end = datetime(2023, 1, 1, 0, 0, 1, tzinfo=timezone.utc)
    return pl.DataFrame(
        {
            "row_id": [1],
            "track_id": ["track_1"],
            "track_classification": ["car"],
            "end_video_name": ["video.mp4"],
            "end_frame": [1],
            "start_x": [100.0],
            "start_y": [0.0],
            "end_x": [100.0],
            "end_y": [200.0],
            "start_w": [0.0],
            "start_h": [0.0],
            "end_w": [0.0],
            "end_h": [0.0],
            "start_occurrence": [occ_start],
            "end_occurrence": [occ_end],
            START_GEO_X: [449250.0],
            START_GEO_Y: [5699320.0],
            END_GEO_X: [449250.0],
            END_GEO_Y: [5699340.0],
        }
    )


class TestFindLineIntersectionsUseGeo:
    def test_intersects_in_geo_space(self) -> None:
        segments_df = _create_segments_df_with_geo()
        # Horizontal section line in geo space crossing the vertical track segment
        result = find_line_intersections(
            segments_df,
            line_id="section_1",
            start_x=449240.0,
            start_y=5699325.0,
            end_x=449260.0,
            end_y=5699325.0,
            offset=RelativeOffsetCoordinate(0.0, 0.0),
            use_geo=True,
        )
        intersecting = result.filter(pl.col(INTERSECTS))
        assert len(intersecting) == 1
        row = intersecting.row(0, named=True)
        assert row[INTERSECTION_X] == approx(449250.0, rel=1e-6)
        assert row[INTERSECTION_Y] == approx(5699325.0, rel=1e-6)

    def test_no_intersection_in_geo_space_when_lines_miss(self) -> None:
        segments_df = _create_segments_df_with_geo()
        # Section line that does NOT cross the track segment in geo space
        result = find_line_intersections(
            segments_df,
            line_id="section_1",
            start_x=449260.0,
            start_y=5699345.0,
            end_x=449280.0,
            end_y=5699345.0,
            offset=RelativeOffsetCoordinate(0.0, 0.0),
            use_geo=True,
        )
        assert result.filter(pl.col(INTERSECTS)).is_empty()
```

- [ ] **Step 2: Run the failing tests**

```bash
uv run pytest "tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestFindLineIntersectionsUseGeo" -v
```

Expected: `TypeError: find_line_intersections() got an unexpected keyword argument 'use_geo'`

- [ ] **Step 3: Add `use_geo` to `find_line_intersections()` in `polars_geometry_store.py`**

Update `find_line_intersections()` to add the `use_geo` parameter:

```python
def find_line_intersections(
    segments_df: pl.DataFrame,
    line_id: str,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    offset: RelativeOffsetCoordinate | None = None,
    use_geo: bool = False,
) -> pl.DataFrame:
    """
    Find intersections between track segments and a line segment.

    Args:
        segments_df: DataFrame with track segments.
        line_id: Identifier for the line.
        start_x, start_y, end_x, end_y: Line segment coordinates. When
            use_geo is True, these must be in the same geo coordinate system
            as the START_GEO_X/Y and END_GEO_X/Y columns.
        offset: Offset for segment endpoints. Ignored when use_geo is True
            because point-based geo detections carry no bounding box.
        use_geo: When True, use START_GEO_X/Y and END_GEO_X/Y columns from
            segments_df for intersection math instead of START_X/Y and
            END_X/Y. Requires geo columns to be present.

    Returns:
        DataFrame with intersection information and points.
    """
    if segments_df.is_empty():
        return segments_df

    if offset is None:
        offset = RelativeOffsetCoordinate(x=0.0, y=0.0)

    if use_geo:
        result_df = _calculate_intersection_points_geo(
            segments_df, start_x, start_y, end_x, end_y
        )
    else:
        result_df = calculate_intersection_points(
            segments_df, start_x, start_y, end_x, end_y, offset
        )

    geo_cols = (
        [START_GEO_X, START_GEO_Y, END_GEO_X, END_GEO_Y]
        if START_GEO_X in segments_df.columns and START_GEO_Y in segments_df.columns
        else []
    )
    result_df = result_df.with_columns(
        [
            pl.when(pl.col(INTERSECTS))
            .then(pl.lit(line_id))
            .otherwise(None)
            .alias(INTERSECTION_LINE_ID)
        ]
    ).select(
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
    return result_df
```

Add the private helper `_calculate_intersection_points_geo()` directly above `find_line_intersections()`:

```python
def _calculate_intersection_points_geo(
    segments_df: pl.DataFrame,
    line_x1: float,
    line_y1: float,
    line_x2: float,
    line_y2: float,
) -> pl.DataFrame:
    """Intersection math using START_GEO_X/Y and END_GEO_X/Y without offset.

    Mirrors calculate_intersection_points() but operates on geo columns.
    No offset is applied because point-based OTFusion detections have w=h=0.

    Args:
        segments_df: DataFrame containing START_GEO_X/Y and END_GEO_X/Y.
        line_x1, line_y1, line_x2, line_y2: Section line endpoints in geo space.

    Returns:
        DataFrame with INTERSECTS, INTERSECTION_X, INTERSECTION_Y columns
        (coordinates are in geo space).
    """
    line_dx = line_x2 - line_x1
    line_dy = line_y2 - line_y1

    result_df = segments_df.with_columns(
        [
            pl.col(START_GEO_X).alias("seg_x1"),
            pl.col(START_GEO_Y).alias("seg_y1"),
            pl.col(END_GEO_X).alias("seg_x2"),
            pl.col(END_GEO_Y).alias("seg_y2"),
        ]
    )
    result_df = result_df.with_columns(
        [
            pl.lit(line_dx).alias("line_dx"),
            pl.lit(line_dy).alias("line_dy"),
            (pl.col("seg_x2") - pl.col("seg_x1")).alias("seg_dx"),
            (pl.col("seg_y2") - pl.col("seg_y1")).alias("seg_dy"),
        ]
    )
    result_df = result_df.with_columns(
        [
            (
                -pl.col("line_dx") * pl.col("seg_dy")
                + pl.col("line_dy") * pl.col("seg_dx")
            ).alias(DENOMINATOR)
        ]
    )
    result_df = result_df.with_columns(
        [(pl.col(DENOMINATOR).abs() > 1e-10).alias(NON_PARALLEL)]
    )
    result_df = result_df.with_columns(
        [
            pl.when(pl.col(NON_PARALLEL))
            .then(
                (
                    -(pl.col("seg_x1") - line_x1) * pl.col("seg_dy")
                    + (pl.col("seg_y1") - line_y1) * pl.col("seg_dx")
                )
                / pl.col(DENOMINATOR)
            )
            .otherwise(None)
            .alias(UA),
            pl.when(pl.col(NON_PARALLEL))
            .then(
                (
                    pl.col("line_dx") * (pl.col("seg_y1") - line_y1)
                    - pl.col("line_dy") * (pl.col("seg_x1") - line_x1)
                )
                / pl.col(DENOMINATOR)
            )
            .otherwise(None)
            .alias(UB),
        ]
    )
    result_df = result_df.with_columns(
        [
            (
                pl.col(NON_PARALLEL)
                & pl.col(UA).is_not_null()
                & pl.col(UB).is_not_null()
                & (pl.col(UA) >= 0)
                & (pl.col(UA) <= 1)
                & (pl.col(UB) >= 0)
                & (pl.col(UB) <= 1)
            ).alias(INTERSECTS)
        ]
    )
    result_df = result_df.with_columns(
        [
            pl.when(pl.col(INTERSECTS))
            .then(line_x1 + pl.col(UA) * line_dx)
            .otherwise(None)
            .alias(INTERSECTION_X),
            pl.when(pl.col(INTERSECTS))
            .then(line_y1 + pl.col(UA) * line_dy)
            .otherwise(None)
            .alias(INTERSECTION_Y),
        ]
    )
    return result_df
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest "tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestFindLineIntersectionsUseGeo" -v
```

Expected: 2 PASSED

- [ ] **Step 5: Run the full geometry store test suite**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/ -v
```

Expected: all PASSED

- [ ] **Step 6: Commit**

```bash
git add OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py \
        tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py
git commit -m "feat: add use_geo flag to find_line_intersections for geo-space intersection"
```

---

## Task 5: Update `wrap_intersection_points()` and `PolarsTrackDataset.intersection_points()`

**Files:**
- Modify: `OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py`
- Modify: `OTAnalytics/plugin_datastore/polars_track_store.py`
- Modify: `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`
- Modify: `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`

- [ ] **Step 1: Write the failing integration test for `wrap_intersection_points`**

Add to `test_polars_geometry_store.py`:

```python
# Add with other imports:
from OTAnalytics.domain.otfusion import OtfusionMetadata
from OTAnalytics.plugin_datastore.track_geometry_store.polars_geometry_store import (
    INTERPOLATED_GEO_X,
    INTERPOLATED_GEO_Y,
)
from OTAnalytics.domain.section import SectionId


class TestWrapIntersectionPointsWithGeo:
    """When otfusion_metadata is provided and segments have geo columns,
    section pixel coords are converted to geo and intersection uses geo math."""

    def _make_geometry_dataset(self) -> PolarsTrackGeometryDataset:
        """Single track: pixel (100, 0) -> (100, 200), geo (449250, 5699320) -> (449250, 5699340)."""
        from datetime import datetime, timezone
        occ_start = datetime(2023, 1, 1, tzinfo=timezone.utc)
        occ_end = datetime(2023, 1, 1, 0, 0, 1, tzinfo=timezone.utc)
        segments = pl.DataFrame({
            "row_id": [1],
            "track_id": ["t1"],
            "track_classification": ["car"],
            "end_video_name": ["v.mp4"],
            "end_frame": [1],
            "start_x": [100.0], "start_y": [0.0],
            "end_x": [100.0], "end_y": [200.0],
            "start_w": [0.0], "start_h": [0.0],
            "end_w": [0.0], "end_h": [0.0],
            "start_occurrence": [occ_start],
            "end_occurrence": [occ_end],
            START_GEO_X: [449250.0], START_GEO_Y: [5699320.0],
            END_GEO_X: [449250.0], END_GEO_Y: [5699340.0],
        })
        return PolarsTrackGeometryDataset(
            offset=RelativeOffsetCoordinate(0.0, 0.0),
            segments_df=segments,
        )

    def _make_otfusion_metadata(self) -> OtfusionMetadata:
        """Metadata where pixel (100, 100) maps to geo (449250, 5699325).

        Using:
          scale_x = (449300 - 449200) / (200 - 40) = 100 / 160 = 0.625
          scale_y = (5699350 - 5699300) / (200 - 40) = 50 / 160 = 0.3125
          pixel_x=100 -> geo_x = 449200 + (100-20)*0.625 = 449200 + 50 = 449250  ✓
          pixel_y=100 -> geo_y = 5699350 - (100-20)*0.3125 = 5699350 - 25 = 5699325  ✓
        """
        return OtfusionMetadata(
            geo_min_x=449200.0,
            geo_min_y=5699300.0,
            geo_max_x=449300.0,
            geo_max_y=5699350.0,
            bev_width=200,
            bev_height=200,
            padding=20,
        )

    def _make_section(self, pixel_start: tuple, pixel_end: tuple) -> Section:
        """Section with given pixel-space coordinates."""
        section = Mock(spec=LineSection)
        section.id = SectionId("s1")
        section.get_coordinates.return_value = [
            Coordinate(pixel_start[0], pixel_start[1]),
            Coordinate(pixel_end[0], pixel_end[1]),
        ]
        section.relative_offset_coordinates = {
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(0.0, 0.0)
        }
        section.get_type.return_value = SectionType.LINE
        return section

    def test_geo_intersection_uses_converted_section_coordinates(self) -> None:
        # Section at pixel (80, 100) -> (120, 100), which converts to geo
        # geo_x1 = 449200 + (80-20)*0.625  = 449200 + 37.5 = 449237.5
        # geo_x2 = 449200 + (120-20)*0.625 = 449200 + 62.5 = 449262.5
        # geo_y  = 5699350 - (100-20)*0.3125 = 5699350 - 25 = 5699325
        # This horizontal geo line crosses the vertical geo track segment at (449250, 5699325)
        geometry_dataset = self._make_geometry_dataset()
        section = self._make_section(pixel_start=(80, 100), pixel_end=(120, 100))
        metadata = self._make_otfusion_metadata()

        result = geometry_dataset.wrap_intersection_points([section], metadata)

        assert not result.empty
        events = result.create_events(RelativeOffsetCoordinate(0.0, 0.0))
        event_list = list(events)
        assert len(event_list) == 1
        evt = event_list[0]
        assert evt.geo_x == approx(449250.0, rel=1e-4)
        assert evt.geo_y == approx(5699325.0, rel=1e-4)

    def test_no_geo_metadata_falls_back_to_pixel_intersection(self) -> None:
        # Without metadata, the section pixel coords are used as-is for pixel intersection
        geometry_dataset = self._make_geometry_dataset()
        # Section at pixel x=100 (vertical) crossing horizontal track... but track is also at x=100
        # Use a section that crosses the pixel track: (0, 100) -> (200, 100) crosses (100,0)-(100,200)
        section = self._make_section(pixel_start=(0, 100), pixel_end=(200, 100))
        result = geometry_dataset.wrap_intersection_points([section], None)
        assert not result.empty
```

- [ ] **Step 2: Run the failing test**

```bash
uv run pytest "tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestWrapIntersectionPointsWithGeo" -v
```

Expected: `TypeError: wrap_intersection_points() takes 2 positional arguments but 3 were given`

- [ ] **Step 3: Update `wrap_intersection_points()` in `polars_geometry_store.py`**

Change the signature and add geo-path logic. The method starts at line 1192.

Update the signature:
```python
def wrap_intersection_points(
    self,
    sections: list[Section],
    otfusion_metadata: "OtfusionMetadata | None" = None,
) -> IntersectionPointsDataset:
```

Add the import at the top of `polars_geometry_store.py`:
```python
from OTAnalytics.domain.otfusion import OtfusionMetadata, pixel_to_geo
```

Inside `wrap_intersection_points()`, determine whether to use geo mode once (before the loop):
```python
use_geo = (
    otfusion_metadata is not None
    and not self._segments_df.is_empty()
    and START_GEO_X in self._segments_df.columns
)
```

Then in the per-leg loop, compute section geo coordinates when `use_geo=True`:
```python
for i in range(len(coordinates) - 1):
    if use_geo:
        px_start_x, px_start_y = coordinates[i].x, coordinates[i].y
        px_end_x, px_end_y = coordinates[i + 1].x, coordinates[i + 1].y
        leg_start_x, leg_start_y = pixel_to_geo(px_start_x, px_start_y, otfusion_metadata)
        leg_end_x, leg_end_y = pixel_to_geo(px_end_x, px_end_y, otfusion_metadata)
    else:
        leg_start_x, leg_start_y = coordinates[i].x, coordinates[i].y
        leg_end_x, leg_end_y = coordinates[i + 1].x, coordinates[i + 1].y

    intersections = find_line_intersections(
        self._segments_df,
        section.id.serialize(),
        leg_start_x,
        leg_start_y,
        leg_end_x,
        leg_end_y,
        offset,
        use_geo=use_geo,
    )
```

When computing `RELATIVE_POSITION` inside `wrap_intersection_points()`, the existing code uses pixel-space distances for `INTERSECTION_LENGTH` and `SEGMENT_LENGTH`. For `use_geo=True`, `INTERSECTION_X/Y` are geo coordinates. Update the `.with_columns()` that computes `INTERSECTION_LENGTH_X/Y` and `SEGMENT_LENGTH_X/Y`:

```python
# Replace the existing with_columns blocks that compute SEGMENT_LENGTH_X/Y
# and INTERSECTION_LENGTH_X/Y with the following conditional logic:

if use_geo:
    intersection_points = (
        intersecting_segments.with_columns(
            [
                (pl.col(END_X) + pl.col(END_W) * offset.x).alias(CURRENT_X),
                (pl.col(END_Y) + pl.col(END_H) * offset.y).alias(CURRENT_Y),
                (pl.col(START_X) + pl.col(START_W) * offset.x).alias(PREVIOUS_X),
                (pl.col(START_Y) + pl.col(START_H) * offset.y).alias(PREVIOUS_Y),
            ]
        )
        .with_columns(
            [
                (pl.col(END_GEO_X) - pl.col(START_GEO_X)).alias(SEGMENT_LENGTH_X),
                (pl.col(END_GEO_Y) - pl.col(START_GEO_Y)).alias(SEGMENT_LENGTH_Y),
            ]
        )
        .with_columns(
            [
                (
                    pl.col(SEGMENT_LENGTH_X) ** 2 + pl.col(SEGMENT_LENGTH_Y) ** 2
                ).sqrt().alias(SEGMENT_LENGTH)
            ]
        )
        .with_columns(
            [
                (pl.col(INTERSECTION_X) - pl.col(START_GEO_X)).alias(INTERSECTION_LENGTH_X),
                (pl.col(INTERSECTION_Y) - pl.col(START_GEO_Y)).alias(INTERSECTION_LENGTH_Y),
            ]
        )
        .with_columns(
            [
                (
                    pl.col(INTERSECTION_LENGTH_X) ** 2
                    + pl.col(INTERSECTION_LENGTH_Y) ** 2
                ).sqrt().alias(INTERSECTION_LENGTH)
            ]
        )
        .with_columns(
            [
                pl.when(
                    (pl.col(SEGMENT_LENGTH_X) == 0) & (pl.col(SEGMENT_LENGTH_Y) == 0)
                )
                .then(None)
                .otherwise(pl.col(INTERSECTION_LENGTH) / pl.col(SEGMENT_LENGTH))
                .alias(RELATIVE_POSITION)
            ]
        )
        .filter(pl.col(RELATIVE_POSITION).is_not_null())
        .drop([SEGMENT_LENGTH_X, SEGMENT_LENGTH_Y, SEGMENT_LENGTH,
               INTERSECTION_LENGTH_X, INTERSECTION_LENGTH_Y, INTERSECTION_LENGTH])
        .with_columns(pl.lit(section.id.id).alias(SECTION_ID))
    )
else:
    intersection_points = (
        # ... existing code unchanged ...
    )
```

The existing geo interpolation block after `intersection_points` is computed (lines 1326-1343) is unchanged — it already adds `INTERPOLATED_GEO_X/Y` from `START_GEO_X + RELATIVE_POSITION * (END_GEO_X - START_GEO_X)`.

- [ ] **Step 4: Update `PolarsTrackDataset.intersection_points()` to pass `otfusion_metadata`**

In `OTAnalytics/plugin_datastore/polars_track_store.py`, update the method at line 583:

```python
def intersection_points(
    self, sections: list[Section], offset: RelativeOffsetCoordinate
) -> IntersectionPointsDataset:
    geometry_dataset = self._get_geometry_dataset_for(offset)
    return geometry_dataset.wrap_intersection_points(sections, self._otfusion_metadata)
```

- [ ] **Step 5: Run the new tests**

```bash
uv run pytest "tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestWrapIntersectionPointsWithGeo" -v
```

Expected: 2 PASSED

- [ ] **Step 6: Run the full test suite**

```bash
uv run pytest tests/unit/ -v --tb=short
```

Expected: all PASSED

- [ ] **Step 7: Commit**

```bash
git add OTAnalytics/plugin_datastore/track_geometry_store/polars_geometry_store.py \
        OTAnalytics/plugin_datastore/polars_track_store.py \
        tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py \
        tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py
git commit -m "feat: use geo coordinates for intersection detection when OtfusionMetadata is available"
```

---

## Task 6: Fallback regression test and final verification

**Files:**
- Modify: `tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py`

- [ ] **Step 1: Write regression test verifying non-fusion files are unchanged**

Add to `test_polars_geometry_store.py`:

```python
class TestWrapIntersectionPointsFallback:
    """Ensures non-fusion files (no geo columns, no OtfusionMetadata) are unaffected."""

    def test_no_metadata_no_geo_columns_uses_pixel_intersection(self) -> None:
        """Standard pixel-space intersection still works when no otfusion metadata."""
        from datetime import datetime, timezone
        occ_start = datetime(2023, 1, 1, tzinfo=timezone.utc)
        occ_end = datetime(2023, 1, 1, 0, 0, 1, tzinfo=timezone.utc)
        segments = pl.DataFrame({
            "row_id": [1],
            "track_id": ["t1"],
            "track_classification": ["car"],
            "end_video_name": ["v.mp4"],
            "end_frame": [1],
            "start_x": [100.0], "start_y": [0.0],
            "end_x": [100.0], "end_y": [200.0],
            "start_w": [0.0], "start_h": [0.0],
            "end_w": [0.0], "end_h": [0.0],
            "start_occurrence": [occ_start],
            "end_occurrence": [occ_end],
        })
        geometry_dataset = PolarsTrackGeometryDataset(
            offset=RelativeOffsetCoordinate(0.0, 0.0),
            segments_df=segments,
        )
        section = Mock(spec=LineSection)
        section.id = SectionId("s1")
        section.get_coordinates.return_value = [
            Coordinate(0.0, 100.0),
            Coordinate(200.0, 100.0),
        ]
        section.relative_offset_coordinates = {
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(0.0, 0.0)
        }
        section.get_type.return_value = SectionType.LINE

        result = geometry_dataset.wrap_intersection_points([section], None)

        assert not result.empty
        events = list(result.create_events(RelativeOffsetCoordinate(0.0, 0.0)))
        assert len(events) == 1
        evt = events[0]
        assert evt.geo_x is None
        assert evt.geo_y is None
```

- [ ] **Step 2: Run the regression test**

```bash
uv run pytest "tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py::TestWrapIntersectionPointsFallback" -v
```

Expected: 1 PASSED

- [ ] **Step 3: Run the entire test suite**

```bash
uv run pytest tests/ -v --tb=short -q
```

Expected: all PASSED, no regressions

- [ ] **Step 4: Commit**

```bash
git add tests/unit/OTAnalytics/plugin_datastore/track_geometry_store/test_polars_geometry_store.py
git commit -m "test: add fallback regression test for non-fusion pixel-space intersection"
```

---

## Self-Review Checklist

After completing all tasks, verify:

- [ ] `pixel_to_geo()` round-trips correctly for known detection coordinates
- [ ] `OttrkParser._parse_otfusion_metadata()` returns `None` for non-fusion files
- [ ] `PolarsTrackDataset.otfusion_metadata` is `None` by default
- [ ] Geo-mode intersection uses `START_GEO_X/Y` / `END_GEO_X/Y` from the segments DataFrame
- [ ] Events produced from geo-mode intersection carry correct `geo_x`/`geo_y`
- [ ] Events from non-fusion tracks have `geo_x=None`, `geo_y=None`
- [ ] GUI and CLI paths are covered (both call `LoadTrackFiles` → same use-case code)
- [ ] No changes to `Section` domain object, GUI layer, CLI layer, or `create_events()`

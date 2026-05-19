# Polars Bulk Merge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `PolarsTrackDataset.merge_all` for efficient bulk concat and wire `FeathersParser._combine_track_datasets` to use it, keeping georeference metadata validation in one place.

**Architecture:** A new `merge_all` classmethod on `PolarsTrackDataset` validates all georeference metadata upfront then does a single `pl.concat`. `FeathersParser._combine_track_datasets` is a thin override that delegates to `merge_all` for the all-Polars case and falls back to `super()` otherwise.

**Tech Stack:** Python, polars, pytest, TDD (write failing tests first, then implement).

---

## File Map

| Action | File |
|--------|------|
| Modify | `OTAnalytics/plugin_datastore/polars_track_store.py` — add `merge_all` classmethod |
| Modify | `OTAnalytics/plugin_parser/feathers_parser.py` — add `_combine_track_datasets` override, restore `cast` import |
| Modify | `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py` — add `GivenMergeAll` + `TestPolarsTrackDatasetMergeAll` |
| Modify | `tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py` — add `GivenFeathersParserMismatchedGeoreference` + mismatched metadata test |

---

## Task 1: `PolarsTrackDataset.merge_all` — TDD

**Files:**
- Test: `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`
- Modify: `OTAnalytics/plugin_datastore/polars_track_store.py`

### Step 1.1 — Write the failing tests

Add the following block **at the end** of `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py` (after the last existing class):

```python
@dataclass
class GivenMergeAll:
    dataset_a: PolarsTrackDataset
    dataset_b: PolarsTrackDataset


def create_given_merge_all(
    track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    car_track: Track,
    pedestrian_track: Track,
) -> GivenMergeAll:
    ds_a = PolarsTrackDataset.from_list(
        [car_track], track_geometry_factory
    ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
    ds_b = PolarsTrackDataset.from_list(
        [pedestrian_track], track_geometry_factory
    ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
    return GivenMergeAll(dataset_a=ds_a, dataset_b=ds_b)


def setup_default_merge_all(given: GivenMergeAll) -> GivenMergeAll:
    return given


def create_target_merge_all(given: GivenMergeAll) -> PolarsTrackDataset:
    return PolarsTrackDataset.merge_all([given.dataset_a, given.dataset_b])


class TestPolarsTrackDatasetMergeAll:
    def test_raises_on_empty_list(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    ) -> None:
        with pytest.raises(ValueError, match="No datasets to merge"):
            PolarsTrackDataset.merge_all([])

    def test_combines_tracks_from_all_datasets(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        given = setup_default_merge_all(
            create_given_merge_all(track_geometry_factory, car_track, pedestrian_track)
        )
        target = create_target_merge_all(given)

        assert len(target) == 2

    def test_result_carries_shared_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        given = setup_default_merge_all(
            create_given_merge_all(track_geometry_factory, car_track, pedestrian_track)
        )
        target = create_target_merge_all(given)

        assert target.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_raises_on_incompatible_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        different_metadata = GeoreferenceMetadata(
            geo_min_x=0.0,
            geo_min_y=0.0,
            geo_max_x=1.0,
            geo_max_y=1.0,
            birds_eye_view_width=100,
            birds_eye_view_height=100,
            padding=0,
            crs="EPSG:4326",
        )
        ds_a = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        ds_b = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(different_metadata)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            PolarsTrackDataset.merge_all([ds_a, ds_b])

    def test_result_has_none_metadata_when_all_datasets_have_none(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        ds_a = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        ds_b = PolarsTrackDataset.from_list([pedestrian_track], track_geometry_factory)

        result = PolarsTrackDataset.merge_all([ds_a, ds_b])

        assert result.georeference_metadata is None

    def test_all_empty_datasets_returns_empty_with_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
    ) -> None:
        ds_a = PolarsTrackDataset(
            track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        ds_b = PolarsTrackDataset(
            track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = PolarsTrackDataset.merge_all([ds_a, ds_b])

        assert result.empty
        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_single_dataset_returns_equivalent_result(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        ds = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = PolarsTrackDataset.merge_all([ds])

        assert len(result) == 1
        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA
```

- [ ] **Step 1.2 — Run the failing tests**

```
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsTrackDatasetMergeAll -v
```

Expected: all 7 tests **FAIL** with `AttributeError: type object 'PolarsTrackDataset' has no attribute 'merge_all'`

- [ ] **Step 1.3 — Implement `merge_all`**

In `OTAnalytics/plugin_datastore/polars_track_store.py`, add `merge_all` as a classmethod **after `from_dataframe` and before `add_all`** (i.e., after line 449):

```python
    @classmethod
    def merge_all(
        cls,
        datasets: Sequence["PolarsTrackDataset"],
    ) -> "PolarsTrackDataset":
        if not datasets:
            raise ValueError("No datasets to merge")

        expected_metadata = datasets[0].georeference_metadata
        for ds in datasets[1:]:
            if ds.georeference_metadata != expected_metadata:
                raise IncompatibleGeoreferenceMetadataError(
                    "Cannot merge datasets with different georeference metadata: "
                    f"expected {expected_metadata!r}, got {ds.georeference_metadata!r}"
                )

        factory = datasets[0].track_geometry_factory
        calculator = datasets[0].calculator

        non_empty = [ds for ds in datasets if not ds._dataset.is_empty()]
        if not non_empty:
            return cls(
                factory,
                calculator=calculator,
                georeference_metadata=expected_metadata,
            )

        geo_cols = [
            c
            for c in [track.GEO_X, track.GEO_Y]
            if all(c in ds._dataset.columns for ds in non_empty)
        ]
        selected_columns = COLUMNS + geo_cols

        frames = [
            drop_row_id(ds._dataset).select(selected_columns) for ds in non_empty
        ]
        merged = pl.concat(frames).sort(INDEX_NAMES)
        merged = _assign_track_classification(merged, calculator)

        return cls.from_dataframe(
            merged,
            factory,
            calculator=calculator,
            georeference_metadata=expected_metadata,
        )
```

Note: `Sequence`, `COLUMNS`, `INDEX_NAMES`, `drop_row_id`, `_assign_track_classification`, and `IncompatibleGeoreferenceMetadataError` are all already present in `polars_track_store.py`. No new imports needed.

- [ ] **Step 1.4 — Run the tests and verify they pass**

```
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsTrackDatasetMergeAll -v
```

Expected: all 7 tests **PASS**

- [ ] **Step 1.5 — Run the full polars store test suite (regression check)**

```
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py -v
```

Expected: all tests pass.

- [ ] **Step 1.6 — Commit**

```bash
git add tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py \
        OTAnalytics/plugin_datastore/polars_track_store.py
git commit -m "feat(OP#9528): add PolarsTrackDataset.merge_all for efficient bulk concat"
```

---

## Task 2: `FeathersParser._combine_track_datasets` — TDD

**Files:**
- Test: `tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py`
- Modify: `OTAnalytics/plugin_parser/feathers_parser.py`

### Background

The base class `_combine_track_datasets` calls `add_all` iteratively, which also raises `IncompatibleGeoreferenceMetadataError` on mismatched metadata. The new test in Step 2.1 will therefore **pass before the override is added** (via the base class). After adding the override in Step 2.3, the test must still pass — this is the regression guard. The override adds efficiency, not new behaviour.

- [ ] **Step 2.1 — Write the regression test for mismatched metadata**

First, in `tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py`, extend the existing import:

```python
from OTAnalytics.domain.track_dataset.track_dataset import (
    IncompatibleGeoreferenceMetadataError,
    TrackDataset,
)
```

Then add the following **at module level**, right before the `create_target` function (after `GivenFeathersParserWithGeoreference`):

```python
DIFFERENT_GEOREF_METADATA_DICT = {
    ottrk_format.GEO_BOUNDS: {
        ottrk_format.GEO_BOUNDS_MIN_X: 0.0,
        ottrk_format.GEO_BOUNDS_MIN_Y: 0.0,
        ottrk_format.GEO_BOUNDS_MAX_X: 1.0,
        ottrk_format.GEO_BOUNDS_MAX_Y: 1.0,
    },
    ottrk_format.BIRDS_EYE_VIEW_SIZE: {
        ottrk_format.BIRDS_EYE_VIEW_WIDTH: 100,
        ottrk_format.BIRDS_EYE_VIEW_HEIGHT: 100,
    },
    ottrk_format.BEV_PADDING: 0,
    ottrk_format.CRS: "EPSG:4326",
}


@dataclass
class GivenFeathersParserMismatchedGeoreference:
    feather_files: tuple[Path, ...]


def create_given_feathers_parser_mismatched_georeference(
    test_data_tmp_dir: Path,
) -> GivenFeathersParserMismatchedGeoreference:
    base_sidecar: dict[str, Any] = {
        "detection_metadata": {"detection_classes": ["car"]},
        "video_metadata": {
            "path": "test_video.mp4",
            "recorded_start_date": GIVEN_RECORDED_START_DATE,
            "recorded_fps": 30.0,
            "number_of_frames": 900,
        },
    }
    sidecar_a = {**base_sidecar, ottrk_format.GEOREFERENCE: SAMPLE_GEOREFERENCE_METADATA_DICT}
    sidecar_b = {**base_sidecar, ottrk_format.GEOREFERENCE: DIFFERENT_GEOREF_METADATA_DICT}

    file_a = test_data_tmp_dir / "mismatch_a.feather"
    file_b = test_data_tmp_dir / "mismatch_b.feather"
    polars.DataFrame(SINGLE_ROW).write_ipc(file_a)
    polars.DataFrame(SINGLE_ROW).write_ipc(file_b)
    (test_data_tmp_dir / "mismatch_a_metadata.json").write_text(json.dumps(sidecar_a))
    (test_data_tmp_dir / "mismatch_b_metadata.json").write_text(json.dumps(sidecar_b))

    return GivenFeathersParserMismatchedGeoreference(
        feather_files=(file_a, file_b),
    )


def setup_default_feathers_parser_mismatched_georeference(
    given: GivenFeathersParserMismatchedGeoreference,
) -> GivenFeathersParserMismatchedGeoreference:
    return given
```

Then add the following test method **inside `TestFeathersParser`** (at the end of the class, after `test_parse_files_with_no_metadata_yields_none`):

```python
    def test_parse_files_raises_on_mismatched_georeference_metadata(
        self, test_data_tmp_dir: Path
    ) -> None:
        given = setup_default_feathers_parser_mismatched_georeference(
            create_given_feathers_parser_mismatched_georeference(test_data_tmp_dir)
        )
        target = create_target()

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            target.parse_files(list(given.feather_files))
```

- [ ] **Step 2.2 — Run the test and verify it passes via base class**

```
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py::TestFeathersParser::test_parse_files_raises_on_mismatched_georeference_metadata -v
```

Expected: **PASS** (base class raises `IncompatibleGeoreferenceMetadataError` via `add_all`).

- [ ] **Step 2.3 — Implement `FeathersParser._combine_track_datasets`**

In `OTAnalytics/plugin_parser/feathers_parser.py`:

**a) Restore `cast` in the `typing` import:**

Change:
```python
from typing import Optional
```
To:
```python
from typing import Optional, cast
```

**b) Add the `_combine_track_datasets` method at the end of the `FeathersParser` class** (after `_parse_detection_metadata`):

```python
    def _combine_track_datasets(
        self, parse_results: list[TrackParseResult]
    ) -> TrackDataset:
        datasets = [r.tracks for r in parse_results]
        if all(isinstance(ds, PolarsTrackDataset) for ds in datasets):
            return PolarsTrackDataset.merge_all(
                cast(list[PolarsTrackDataset], datasets)
            )
        return super()._combine_track_datasets(parse_results)
```

- [ ] **Step 2.4 — Run the full feathers parser test suite**

```
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py -v
```

Expected: all tests pass.

- [ ] **Step 2.5 — Run the full unit test suite (final regression check)**

```
uv run pytest tests/unit/ -v
```

Expected: all tests pass.

- [ ] **Step 2.6 — Commit**

```bash
git add tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py \
        OTAnalytics/plugin_parser/feathers_parser.py
git commit -m "feat(OP#9528): override FeathersParser._combine_track_datasets to use merge_all"
```

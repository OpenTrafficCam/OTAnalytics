# Georeference Metadata Containment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `GeoreferenceMetadata` an internal property of the `TrackDataset` so the application/use-case and domain repository layers are unaware of it, and so cross-file metadata consistency is enforced automatically inside `PolarsTrackDataset.add_all`.

**Architecture:** Add `georeference_metadata` (property, default `None`) and `with_georeference_metadata` (method, default `NotImplementedError`) to the abstract `TrackDataset`. Polars meaningfully implements both; Pandas/Python inherit the defaults. `PolarsTrackDataset.add_all` enforces a single validation rule (empty current inherits incoming; populated current must have matching metadata-presence and value). `OttrkParser.parse` and `FeathersParser.parse` embed metadata into the returned dataset, so `TrackParser.parse_files` no longer needs an explicit cross-file policy. Delete the leaky `TrackRepository.apply_georeference_metadata` and the corresponding call in `LoadTrackFiles`.

**Tech Stack:** Python 3, `polars`, `pytest`, `uv`.

---

## Spec

This plan implements `docs/superpowers/specs/2026-05-18-georeference-metadata-containment-design.md`.

---

## Conventions

- **Run tests with `uv run pytest`** (never bare `pytest`).
- **Unit tests use the Given dataclass + create_given/setup_default/create_target factory pattern.**
- Each task ends with a commit. Commit messages start with `OP#9528:`. **Do not add a `Co-Authored-By` trailer.**
- For any production-code step below, the shown code is the actual code to write — no further interpretation needed.
- For **test** code snippets that contain `# existing fixtures` style comments, the snippet shows the assertion shape; wire the fixtures/parameters to match the surrounding `Given` / `setup_default` / `create_target` factory already defined in that test file. If a needed factory parameter (e.g. `georeference_metadata`) is missing, extend the factory rather than inlining ad-hoc setup.

---

## Task 1: Add `IncompatibleGeoreferenceMetadataError` + abstract members to `TrackDataset`

**Files:**
- Modify: `OTAnalytics/domain/track_dataset/track_dataset.py`
- Test: `tests/unit/OTAnalytics/domain/track_dataset/test_track_dataset.py` (create if absent)

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/OTAnalytics/domain/track_dataset/test_track_dataset.py` with:

```python
import pytest

from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.track_dataset.track_dataset import (
    IncompatibleGeoreferenceMetadataError,
    TrackDataset,
)


SAMPLE_METADATA = GeoreferenceMetadata(
    geo_min_x=0.0,
    geo_min_y=0.0,
    geo_max_x=100.0,
    geo_max_y=100.0,
    birds_eye_view_width=10,
    birds_eye_view_height=10,
    padding=0,
    crs="EPSG:25833",
)


class _MinimalTrackDataset(TrackDataset):
    """Concrete subclass that overrides only the methods touched by this test."""

    track_ids = None  # type: ignore[assignment]
    first_occurrence = None  # type: ignore[assignment]
    last_occurrence = None  # type: ignore[assignment]
    classifications = frozenset()  # type: ignore[assignment]
    empty = True  # type: ignore[assignment]

    def __len__(self) -> int:
        return 0

    def add_all(self, other):  # type: ignore[override]
        raise NotImplementedError

    def get_for(self, id):  # type: ignore[override]
        return None

    def remove(self, track_id):  # type: ignore[override]
        return self

    def remove_multiple(self, track_ids):  # type: ignore[override]
        return self

    def clear(self):  # type: ignore[override]
        return self

    def split_finished(self):  # type: ignore[override]
        return self, self

    def as_list(self):  # type: ignore[override]
        return []

    def intersecting_tracks(self, sections, offset):  # type: ignore[override]
        return None

    def intersection_points(self, sections, offset):  # type: ignore[override]
        return None

    def contained_by_sections(self, sections, offset):  # type: ignore[override]
        return {}

    def split(self, chunks):  # type: ignore[override]
        return [self]

    def filter_by_min_detection_length(self, length):  # type: ignore[override]
        return self

    def calculate_geometries_for(self, offsets):  # type: ignore[override]
        return None

    def get_first_segments(self):  # type: ignore[override]
        return None

    def get_last_segments(self):  # type: ignore[override]
        return None

    def cut_with_section(self, section, offset):  # type: ignore[override]
        return self, None

    def get_max_confidences_for(self, track_ids):  # type: ignore[override]
        return {}

    def revert_cuts_for(self, original_track_ids):  # type: ignore[override]
        return self, None, None

    def remove_by_original_ids(self, original_ids):  # type: ignore[override]
        return self, None


class TestTrackDatasetGeoreferenceDefaults:
    def test_georeference_metadata_default_is_none(self) -> None:
        dataset = _MinimalTrackDataset()
        assert dataset.georeference_metadata is None

    def test_with_georeference_metadata_raises_not_implemented(self) -> None:
        dataset = _MinimalTrackDataset()
        with pytest.raises(NotImplementedError) as info:
            dataset.with_georeference_metadata(SAMPLE_METADATA)
        assert "_MinimalTrackDataset" in str(info.value)


class TestIncompatibleGeoreferenceMetadataError:
    def test_can_be_raised_and_carries_message(self) -> None:
        with pytest.raises(IncompatibleGeoreferenceMetadataError) as info:
            raise IncompatibleGeoreferenceMetadataError("boom")
        assert str(info.value) == "boom"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
uv run pytest tests/unit/OTAnalytics/domain/track_dataset/test_track_dataset.py -v
```
Expected: ImportError for `IncompatibleGeoreferenceMetadataError` / attribute errors for `georeference_metadata` / `with_georeference_metadata`.

- [ ] **Step 3: Add the imports, exception, and default members**

In `OTAnalytics/domain/track_dataset/track_dataset.py` add `from OTAnalytics.domain.georeference import GeoreferenceMetadata` near the existing imports (e.g. just after the `from OTAnalytics.domain.geometry import …` block at line 13–17).

Just before `class TrackDataset(ABC):` (currently at line 153) add:

```python
class IncompatibleGeoreferenceMetadataError(Exception):
    """Raised when merging datasets with incompatible georeference metadata."""
```

Inside `class TrackDataset(ABC):` (line 153), insert these two members at the top of the body, before `track_ids`:

```python
    @property
    def georeference_metadata(self) -> "GeoreferenceMetadata | None":
        return None

    def with_georeference_metadata(
        self, metadata: "GeoreferenceMetadata | None"
    ) -> "TrackDataset":
        raise NotImplementedError(
            f"{type(self).__name__} does not support georeference metadata"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/domain/track_dataset/test_track_dataset.py -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/domain/track_dataset/track_dataset.py \
       tests/unit/OTAnalytics/domain/track_dataset/test_track_dataset.py
git commit -m "OP#9528: add georeference defaults and incompatibility error to TrackDataset"
```

---

## Task 2: Add validation rule to `PolarsTrackDataset.add_all`

This includes the bugfix where the empty-current early return at `polars_track_store.py:451` currently drops incoming metadata.

**Files:**
- Modify: `OTAnalytics/plugin_datastore/polars_track_store.py:447-491`
- Test: `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`

- [ ] **Step 1: Write the failing tests**

Locate `class TestPolarsTrackDatasetGeoreferenceMetadata:` (`test_polars_track_store.py:706`). Add the following test class **immediately after it** (the existing `SAMPLE_GEOREFERENCE_METADATA` constant at line 694 is reusable). Use the file's existing `track_geometry_factory` fixture and the `car_track` / `pedestrian_track` fixtures used elsewhere in this file.

```python
ALTERNATE_GEOREFERENCE_METADATA = GeoreferenceMetadata(
    geo_min_x=1.0,
    geo_min_y=1.0,
    geo_max_x=101.0,
    geo_max_y=101.0,
    birds_eye_view_width=983,
    birds_eye_view_height=983,
    padding=20,
    crs="EPSG:25833",
)


class TestPolarsTrackDatasetAddAllGeoreferenceValidation:
    def test_add_all_to_empty_inherits_incoming_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        empty = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        incoming = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = empty.add_all(incoming)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_add_all_to_empty_with_no_incoming_metadata_keeps_none(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        empty = PolarsTrackDataset(track_geometry_factory=track_geometry_factory)
        incoming = PolarsTrackDataset.from_list([car_track], track_geometry_factory)

        result = empty.add_all(incoming)

        assert result.georeference_metadata is None

    def test_add_all_with_matching_metadata_succeeds(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = current.add_all(incoming)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_add_all_with_mismatched_metadata_raises(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(ALTERNATE_GEOREFERENCE_METADATA)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            current.add_all(incoming)

    def test_add_all_populated_without_metadata_and_incoming_with_metadata_raises(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            current.add_all(incoming)

    def test_add_all_populated_with_metadata_and_incoming_without_metadata_raises(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            current.add_all(incoming)

    def test_add_all_both_without_metadata_succeeds(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        current = PolarsTrackDataset.from_list([car_track], track_geometry_factory)
        incoming = PolarsTrackDataset.from_list(
            [pedestrian_track], track_geometry_factory
        )

        result = current.add_all(incoming)

        assert result.georeference_metadata is None
```

If the imports at the top of the test file do not already include `IncompatibleGeoreferenceMetadataError`, add it:

```python
from OTAnalytics.domain.track_dataset.track_dataset import (
    ...,
    IncompatibleGeoreferenceMetadataError,
)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsTrackDatasetAddAllGeoreferenceValidation -v
```
Expected: FAILs — metadata is dropped on empty merge and validation does not exist.

- [ ] **Step 3: Modify `PolarsTrackDataset.add_all` to enforce the rule**

In `OTAnalytics/plugin_datastore/polars_track_store.py` ensure the file imports `IncompatibleGeoreferenceMetadataError`. The existing import line is around the top of the file:

```python
from OTAnalytics.domain.track_dataset.track_dataset import (
    ...
    IncompatibleGeoreferenceMetadataError,
)
```

Replace the body of `add_all` (currently lines 447–491). The new implementation:

1. Compute the incoming dataset's metadata up front (must be available even when `other` is not a `PolarsTrackDataset`).
2. Empty current → return a new dataset with the incoming metadata inherited.
3. Populated current → validate metadata equality; raise on mismatch.
4. Preserve current metadata on the merged result.

New code:

```python
    def add_all(self, other: Iterable[Track]) -> "PolarsTrackDataset":
        new_tracks = self.__get_tracks(other)
        if new_tracks.is_empty():
            return self

        incoming_metadata = (
            other.georeference_metadata
            if isinstance(other, PolarsTrackDataset)
            else None
        )

        if self._dataset.is_empty():
            return PolarsTrackDataset.from_dataframe(
                new_tracks,
                self.track_geometry_factory,
                calculator=self.calculator,
                georeference_metadata=incoming_metadata,
            )

        if self._georeference_metadata != incoming_metadata:
            raise IncompatibleGeoreferenceMetadataError(
                "Cannot merge dataset with georeference metadata "
                f"{incoming_metadata!r} into dataset with georeference metadata "
                f"{self._georeference_metadata!r}"
            )

        # Ensure new_tracks has track classification before concatenating
        new_tracks_with_classification = _assign_track_classification(
            new_tracks, self.calculator
        )

        # Get all tracks (existing + new) and assign classification.
        # Preserve optional geo columns when both DataFrames carry them.
        geo_cols = [
            c
            for c in [track.GEO_X, track.GEO_Y]
            if c in self._dataset.columns
            and c in new_tracks_with_classification.columns
        ]
        selected_columns = COLUMNS + geo_cols
        combined_tracks = pl.concat(
            [
                drop_row_id(self._dataset).select(selected_columns),
                drop_row_id(new_tracks_with_classification).select(selected_columns),
            ]
        ).sort(INDEX_NAMES)

        # Re-assign track classification to the combined dataset
        updated_dataset = _assign_track_classification(combined_tracks, self.calculator)

        updated_geometry_dataset = self._add_to_geometry_dataset(
            PolarsTrackDataset.from_dataframe(
                updated_dataset, self.track_geometry_factory
            )
        )

        return PolarsTrackDataset.from_dataframe(
            updated_dataset,
            self.track_geometry_factory,
            updated_geometry_dataset,
            georeference_metadata=self._georeference_metadata,
        )
```

Notes:
- The German planning comments in the prior implementation are intentionally removed; their content is encoded in the new logic and tested above.
- Incoming metadata for a non-`PolarsTrackDataset` `other` is `None` because non-Polars backends don't carry metadata (Task 1's default property).

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsTrackDatasetAddAllGeoreferenceValidation -v
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py -v
```
Expected: all new tests PASS; pre-existing tests still PASS.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/polars_track_store.py \
       tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py
git commit -m "OP#9528: validate georeference metadata when merging PolarsTrackDatasets"
```

---

## Task 3: Preserve metadata across `PolarsTrackDataset` lifecycle operations

The spec requires that `remove`, `remove_multiple`, `filter_by_min_detection_length`, `split_finished`, `revert_cuts_for`, `remove_by_original_ids`, and `_subset_by_ids` all preserve metadata. `split` already does (line 937). `clear` intentionally drops it.

**Files:**
- Modify: `OTAnalytics/plugin_datastore/polars_track_store.py` (multiple locations)
- Test: `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`

- [ ] **Step 1: Write the failing tests**

Append to `class TestPolarsTrackDatasetGeoreferenceMetadata:` in `test_polars_track_store.py` (right after `test_split_preserves_georeference_metadata`):

```python
    def test_remove_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = dataset.remove(car_track.id)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_remove_multiple_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = dataset.remove_multiple(PolarsTrackIdSet([car_track.id.id]))

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_filter_by_min_detection_length_preserves_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
        pedestrian_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track, pedestrian_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = dataset.filter_by_min_detection_length(1)

        assert result.georeference_metadata == SAMPLE_GEOREFERENCE_METADATA

    def test_clear_drops_georeference_metadata(
        self,
        track_geometry_factory: POLARS_TRACK_GEOMETRY_FACTORY,
        car_track: Track,
    ) -> None:
        dataset = PolarsTrackDataset.from_list(
            [car_track], track_geometry_factory
        ).with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

        result = dataset.clear()

        assert result.georeference_metadata is None
```

Ensure `PolarsTrackIdSet` is imported in the test file (it already is at the top).

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py::TestPolarsTrackDatasetGeoreferenceMetadata -v
```
Expected: the four new tests FAIL (`clear`'s test will pass already; the other three FAIL because metadata is currently dropped).

- [ ] **Step 3: Add `georeference_metadata` to preserving constructions**

In `OTAnalytics/plugin_datastore/polars_track_store.py` apply the edits below. Each edit adds `georeference_metadata=self._georeference_metadata` to a `PolarsTrackDataset(...)` constructor or `from_dataframe(...)` call.

**`remove` (lines 543–550):**

```python
    def remove(self, track_id: TrackId) -> "PolarsTrackDataset":
        filtered_data = self._dataset.filter(pl.col(LEVEL_TRACK_ID) != unpack(track_id))
        return PolarsTrackDataset(
            self.track_geometry_factory,
            filtered_data,
            self._geometry_datasets,
            self.calculator,
            georeference_metadata=self._georeference_metadata,
        )
```

**`remove_multiple` (lines 552–562):**

```python
    def remove_multiple(self, track_ids: TrackIdSet) -> "PolarsTrackDataset":
        track_id_strings = self.__to_raw_ids(track_ids)
        filtered_data = self._dataset.filter(
            ~pl.col(LEVEL_TRACK_ID).is_in(track_id_strings)
        )
        return PolarsTrackDataset(
            self.track_geometry_factory,
            filtered_data,
            self._geometry_datasets,
            self.calculator,
            georeference_metadata=self._georeference_metadata,
        )
```

**`split_finished` empty helper (line 509–511):**

```python
    def split_finished(self) -> tuple[TrackDataset, TrackDataset]:
        empty = PolarsTrackDataset(
            self.track_geometry_factory,
            calculator=self.calculator,
            georeference_metadata=self._georeference_metadata,
        )
```

(`split_finished` then returns `self`/`empty` combinations; both carry metadata correctly because `self` already has it and `empty` now inherits it.)

**`_subset_by_ids` (lines 942–954):**

```python
    def _subset_by_ids(self, track_ids: list[str]) -> "PolarsTrackDataset":
        if not track_ids:
            return PolarsTrackDataset(
                self.track_geometry_factory,
                calculator=self.calculator,
                georeference_metadata=self._georeference_metadata,
            )
        subset = self._dataset.filter(pl.col(LEVEL_TRACK_ID).is_in(track_ids))
        geometries = self._get_geometries_for(track_ids)
        return PolarsTrackDataset.from_dataframe(
            subset,
            self.track_geometry_factory,
            geometries,
            calculator=self.calculator,
            georeference_metadata=self._georeference_metadata,
        )
```

**`filter_by_min_detection_length` (lines 824–844):**

```python
    def filter_by_min_detection_length(self, length: int) -> TrackDataset:
        if self._dataset.is_empty():
            return self

        detection_counts = self._dataset.group_by(LEVEL_TRACK_ID).agg(
            pl.len().alias("count")
        )

        valid_track_ids = (
            detection_counts.filter(pl.col("count") >= length)
            .get_column(LEVEL_TRACK_ID)
            .to_list()
        )

        filtered_dataset = self._dataset.filter(
            pl.col(LEVEL_TRACK_ID).is_in(valid_track_ids)
        )

        return PolarsTrackDataset(
            self.track_geometry_factory,
            filtered_dataset,
            calculator=self.calculator,
            georeference_metadata=self._georeference_metadata,
        )
```

**`revert_cuts_for` (lines 893–902):**

```python
        return (
            PolarsTrackDataset.from_dataframe(
                result,
                self.track_geometry_factory,
                geometry_dataset=self._geometry_datasets,
                calculator=self.calculator,
                georeference_metadata=self._georeference_metadata,
            ),
            ids_to_revert,
            ids_to_revert,
        )
```

**`cut_with_section` return (lines 818–822):**

```python
        return (
            PolarsTrackDataset.from_dataframe(
                result,
                self.track_geometry_factory,
                calculator=self.calculator,
                georeference_metadata=self._georeference_metadata,
            ),
            original_track_ids,
        )
```

(Verify the existing call: open `polars_track_store.py:818` and confirm the construction is `PolarsTrackDataset.from_dataframe(result, self.track_geometry_factory)` — extend it to include `calculator` and `georeference_metadata`.)

**`remove_by_original_ids` (lines 978–982):**

```python
        updated_track_dataset = PolarsTrackDataset(
            dataset=filtered_dataset,
            calculator=self.calculator,
            track_geometry_factory=self.track_geometry_factory,
            georeference_metadata=self._georeference_metadata,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_datastore/polars_track_store.py \
       tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py
git commit -m "OP#9528: preserve georeference metadata across PolarsTrackDataset operations"
```

---

## Task 4: `OttrkParser.parse` embeds metadata into the returned dataset

**Files:**
- Modify: `OTAnalytics/plugin_parser/otvision_parser.py:582-609`
- Test: `tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py`

- [ ] **Step 1: Write the failing test**

Locate the parser test file. Add a test that drives `OttrkParser.parse` end-to-end with the existing `SAMPLE_GEOREFERENCE_METADATA_DICT` fixture and asserts the **resulting `TrackParseResult.tracks` carries the metadata** (rather than `parse_result.georeference_metadata`). Use the file's existing setup pattern.

```python
def test_parse_embeds_georeference_metadata_in_tracks(
    self,
    # ... existing fixtures matching the pattern in this file
) -> None:
    given = setup_default(...)
    target = create_target(given)

    parse_result = target.parse(given.ottrk_file)

    assert parse_result.tracks.georeference_metadata == GEOREF_METADATA
```

(Tests in this file already follow the Given dataclass + create_target factory pattern with reusable `GEOREF_METADATA` / `SAMPLE_GEOREFERENCE_METADATA_DICT` — reuse them directly.)

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py -v -k test_parse_embeds_georeference_metadata_in_tracks
```
Expected: FAIL — `parse_result.tracks.georeference_metadata` is `None` because the parser does not attach metadata to the dataset.

- [ ] **Step 3: Modify `OttrkParser.parse` to attach metadata**

Replace the body of `OttrkParser.parse` (`otvision_parser.py:582-609`):

```python
    def parse(self, ottrk_file: Path) -> TrackParseResult:
        """Parse ottrk file and convert its content to domain level objects namely
        `Track`s.

        Args:
            ottrk_file (Path): the track file.

        Returns:
            TrackParseResult: contains tracks and track metadata.
        """
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
        georeference_metadata = self._parse_georeference_metadata(
            ottrk_dict[ottrk_format.METADATA]
        )
        if georeference_metadata is not None:
            tracks = tracks.with_georeference_metadata(georeference_metadata)
        return TrackParseResult(tracks, detection_metadata, video_metadata)
```

Notes:
- The `georeference_metadata` argument is dropped from the `TrackParseResult(...)` call. Task 6 deletes the field from the dataclass; until then, the call relies on the field's default `None`. This still type-checks because the dataclass has `georeference_metadata: GeoreferenceMetadata | None = None`.

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_parser/otvision_parser.py \
       tests/unit/OTAnalytics/plugin_parser/test_otvision_parser.py
git commit -m "OP#9528: embed georeference metadata in OttrkParser parse result"
```

---

## Task 5: `FeathersParser.parse` embeds metadata; remove its `parse_files` override

**Files:**
- Modify: `OTAnalytics/plugin_parser/feathers_parser.py:97-203`
- Test: `tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py`

- [ ] **Step 1: Write the failing tests**

In `test_feathers_parser.py`, add (or update, if a similar test already exists) tests that:

1. `FeathersParser.parse` returns a `TrackParseResult` whose `tracks.georeference_metadata` matches the metadata in the sidecar JSON.
2. `FeathersParser.parse_files` is no longer overridden — the inherited base-class behavior is used (test by parsing two files with matching metadata and checking `result.tracks.georeference_metadata`).

```python
def test_parse_embeds_georeference_metadata_in_tracks(
    self,
    # existing fixtures
) -> None:
    given = setup_default(...)
    target = create_target(given)

    parse_result = target.parse(given.feather_file)

    assert parse_result.tracks.georeference_metadata == GEOREF_METADATA


def test_parse_files_with_matching_metadata_carries_through(
    self,
    # existing fixtures
) -> None:
    given = setup_default(feather_files=[feather_a, feather_b], metadata=GEOREF_METADATA)
    target = create_target(given)

    parse_result = target.parse_files([feather_a, feather_b])

    assert parse_result.tracks.georeference_metadata == GEOREF_METADATA
```

(Use the existing file fixtures and `GEOREF_METADATA` symbol from this test module.)

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py -v
```
Expected: FAIL.

- [ ] **Step 3: Modify `FeathersParser`**

In `OTAnalytics/plugin_parser/feathers_parser.py`:

1. **Delete** the override `parse_files` (lines 97–158). The base class `TrackParser.parse_files` will be inherited and will use the new `add_all` validation automatically.
2. **Update** `FeathersParser.parse` (lines 160–203) to attach metadata to the dataset before returning. Replace the body:

```python
    def parse(self, file: Path) -> TrackParseResult:
        """Parse feather file and its metadata to create TrackParseResult.

        Args:
            file: Path to the feather file

        Returns:
            TrackParseResult: Contains tracks, detection metadata, and video metadata

        Raises:
            FileNotFoundError: If the feather file or metadata file is not found
        """
        file = use_feather_file(file)

        if not file.exists():
            raise FileNotFoundError(f"Feather file not found: {file}")
        metadata_file = file.parent / f"{file.stem}{METADATA_SUFFIX}"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        df = pl.read_ipc(file)
        metadata = parse_json(metadata_file)

        calculator = PolarsByMaxConfidence()
        tracks: TrackDataset = PolarsTrackDataset.from_dataframe(
            df, self._track_geometry_factory, calculator=calculator
        )

        video_metadata = self._parse_video_metadata(metadata[KEY_VIDEO_METADATA])
        detection_metadata = self._parse_detection_metadata(
            metadata[KEY_DETECTION_METADATA]
        )
        georeference_metadata = self._parse_georeference_metadata(metadata)
        if georeference_metadata is not None:
            tracks = tracks.with_georeference_metadata(georeference_metadata)

        return TrackParseResult(tracks, detection_metadata, video_metadata)
```

3. Remove now-unused imports introduced by the deleted `parse_files`:
   - If `GeoreferenceMetadata` is no longer referenced anywhere else in `feathers_parser.py`, remove its import.
   - `_parse_georeference_metadata` is still needed by the new `parse`.

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_parser/feathers_parser.py \
       tests/unit/OTAnalytics/plugin_parser/test_feathers_parser.py
git commit -m "OP#9528: embed georeference metadata in FeathersParser; inherit parse_files"
```

---

## Task 6: Drop `georeference_metadata` fields from `TrackParseResult` and `TracksParseResult`; simplify `TrackParser.parse_files`

This is the only task that changes the public parser dataclasses. Tasks 4 and 5 already stopped supplying these fields at construction. Tasks 7 and 8 update consumers.

**Files:**
- Modify: `OTAnalytics/application/parser/track_parser.py`
- Test: `tests/unit/OTAnalytics/application/parser/test_track_parser.py`

- [ ] **Step 1: Write the failing tests**

Add tests for the new cross-file validation behavior, using existing factory patterns in the test file. Reuse the file's `GEOREF_METADATA` / `SAMPLE_GEOREFERENCE_METADATA_DICT` symbols.

```python
class TestTrackParserParseFilesValidation:
    def test_parse_files_with_consistent_metadata_succeeds(
        self,
        # existing fixtures
    ) -> None:
        given = setup_default(
            file_results=[
                result_with_metadata(GEOREF_METADATA),
                result_with_metadata(GEOREF_METADATA),
            ]
        )
        target = create_target(given)

        result = target.parse_files([given.file_a, given.file_b])

        assert result.tracks.georeference_metadata == GEOREF_METADATA

    def test_parse_files_with_mismatched_metadata_raises(
        self,
        # existing fixtures
    ) -> None:
        given = setup_default(
            file_results=[
                result_with_metadata(GEOREF_METADATA),
                result_with_metadata(ALTERNATE_GEOREF_METADATA),
            ]
        )
        target = create_target(given)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            target.parse_files([given.file_a, given.file_b])

    def test_parse_files_with_partial_metadata_raises(
        self,
        # existing fixtures
    ) -> None:
        given = setup_default(
            file_results=[
                result_with_metadata(GEOREF_METADATA),
                result_without_metadata(),
            ]
        )
        target = create_target(given)

        with pytest.raises(IncompatibleGeoreferenceMetadataError):
            target.parse_files([given.file_a, given.file_b])

    def test_parse_files_with_no_metadata_anywhere_yields_none(
        self,
        # existing fixtures
    ) -> None:
        given = setup_default(
            file_results=[result_without_metadata(), result_without_metadata()]
        )
        target = create_target(given)

        result = target.parse_files([given.file_a, given.file_b])

        assert result.tracks.georeference_metadata is None
```

Also: **find and delete** any existing test in this file that asserts on `result.georeference_metadata` (field-level access on `TrackParseResult` / `TracksParseResult`). It should now be `result.tracks.georeference_metadata`. The existing tests added by commit 23748833 may need this rewrite — read the file and update each assertion accordingly.

Helper functions `result_with_metadata` / `result_without_metadata` should construct real `TrackParseResult` objects backed by `PolarsTrackDataset` instances (with or without metadata attached). Pattern:

```python
def result_with_metadata(metadata: GeoreferenceMetadata) -> TrackParseResult:
    tracks = PolarsTrackDataset.from_list(
        [SOME_TRACK], track_geometry_factory
    ).with_georeference_metadata(metadata)
    return TrackParseResult(
        tracks=tracks,
        detection_metadata=DetectionMetadata(frozenset(["car"])),
        video_metadata=SOME_VIDEO_METADATA,
    )
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/application/parser/test_track_parser.py -v
```
Expected: FAIL on new tests; FAIL on legacy field-access tests once they reference the no-longer-present field.

- [ ] **Step 3: Drop the fields and simplify `parse_files`**

Replace the body of `OTAnalytics/application/parser/track_parser.py` (full replacement is short enough to show in entirety):

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.video import VideoMetadata


@dataclass(frozen=True)
class DetectionMetadata:
    detection_classes: frozenset[str]


@dataclass(frozen=True)
class TrackParseResult:
    tracks: TrackDataset
    detection_metadata: DetectionMetadata
    video_metadata: VideoMetadata


@dataclass(frozen=True)
class TracksParseResult:
    tracks: TrackDataset
    detections_metadata: list[DetectionMetadata]
    videos_metadata: list[VideoMetadata]


def combine_track_datasets(results: list[TrackParseResult]) -> TrackDataset:
    if not results:
        raise ValueError("No results to combine")
    tracks = results[0].tracks
    for result in results[1:]:
        tracks = tracks.add_all(result.tracks)
    return tracks


class TrackParser(ABC):
    def parse_files(self, files: list[Path]) -> TracksParseResult:
        if not files:
            raise ValueError("No files to parse")
        results = [self.parse(file) for file in files]
        tracks = combine_track_datasets(results)
        detections_metadata = [result.detection_metadata for result in results]
        videos_metadata = [result.video_metadata for result in results]
        return TracksParseResult(tracks, detections_metadata, videos_metadata)

    @abstractmethod
    def parse(self, file: Path) -> TrackParseResult:
        raise NotImplementedError
```

Two notable changes vs. the previous version:
1. `GeoreferenceMetadata` import is removed.
2. `combine_track_datasets` reassigns `tracks = tracks.add_all(result.tracks)` instead of relying on `tracks.add_all(...)` returning self-mutated state. The previous code (`tracks.add_all(result.tracks)`) was a latent bug — `add_all` returns a new dataset; the original `tracks` reference was being kept. This task fixes it as a side effect.

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/application/parser/test_track_parser.py -v
uv run pytest tests/ -v -x  # full sweep to catch downstream references
```

Expected: target tests PASS; full suite will likely FAIL on `convert_ottrk_to_feathers`, `LoadTrackFiles`, and any test that constructs `TracksParseResult(...)` with a positional `georeference_metadata` argument or reads `result.georeference_metadata`. Those failures are addressed in Tasks 7 & 8.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/application/parser/track_parser.py \
       tests/unit/OTAnalytics/application/parser/test_track_parser.py
git commit -m "OP#9528: validate georeference across files via add_all; drop field from parse results"
```

---

## Task 7: Update `convert_ottrk_to_feathers` to read metadata from `tracks`

**Files:**
- Modify: `OTAnalytics/plugin_parser/convert_ottrk_to_feathers.py:75-89`
- Test: `tests/unit/OTAnalytics/plugin_parser/test_convert_ottrk_to_feathers.py`

- [ ] **Step 1: Write the failing test**

If there isn't already a test exercising `create_metadata_dict`, add one that builds a `TrackParseResult` with metadata attached to its `tracks` and verifies the serialized dict contains the georeference block:

```python
def test_create_metadata_dict_serializes_georeference_from_tracks() -> None:
    tracks = PolarsTrackDataset.from_list(
        [SOME_TRACK], track_geometry_factory
    ).with_georeference_metadata(GEOREF_METADATA)
    parse_result = TrackParseResult(
        tracks=tracks,
        detection_metadata=DetectionMetadata(frozenset(["car"])),
        video_metadata=SOME_VIDEO_METADATA,
    )

    metadata_dict = create_metadata_dict(parse_result)

    assert ottrk_format.GEOREFERENCE in metadata_dict
```

If existing tests reference `parse_result.georeference_metadata`, update them to read from `parse_result.tracks.georeference_metadata`.

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_convert_ottrk_to_feathers.py -v
```
Expected: FAIL (the dict won't contain the georeference block because the field is gone, or compilation fails because the field doesn't exist).

- [ ] **Step 3: Read metadata from `tracks`**

In `OTAnalytics/plugin_parser/convert_ottrk_to_feathers.py:75-89`, replace `create_metadata_dict`:

```python
def create_metadata_dict(parse_result: TrackParseResult) -> Dict[str, Any]:
    """Create a metadata dictionary from TrackParseResult."""
    metadata: Dict[str, Any] = {
        KEY_DETECTION_METADATA: {
            KEY_DETECTION_CLASSES: list(
                parse_result.detection_metadata.detection_classes
            )
        },
        KEY_VIDEO_METADATA: parse_result.video_metadata.to_dict(),
    }
    georeference = parse_result.tracks.georeference_metadata
    if georeference is not None:
        metadata[ottrk_format.GEOREFERENCE] = _serialize_georeference_metadata(
            georeference
        )
    return metadata
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_convert_ottrk_to_feathers.py -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_parser/convert_ottrk_to_feathers.py \
       tests/unit/OTAnalytics/plugin_parser/test_convert_ottrk_to_feathers.py
git commit -m "OP#9528: read georeference metadata from tracks in convert_ottrk_to_feathers"
```

---

## Task 8: Remove `TrackRepository.apply_georeference_metadata` and update `LoadTrackFiles`

**Files:**
- Modify: `OTAnalytics/domain/track_repository.py:153-165`
- Modify: `OTAnalytics/application/use_cases/load_track_files.py:33-70`
- Test: `tests/unit/OTAnalytics/application/use_cases/test_load_track_files.py`

- [ ] **Step 1: Rewrite the existing test**

In `test_load_track_files.py:145-158`, replace `test_load_with_georeference_metadata_update` with a test that asserts the dataset passed to `track_repository.add_all` carries the expected metadata. The exact assertion depends on how the `Given` factory exposes the parse result; the pattern is:

```python
def test_load_passes_dataset_with_georeference_metadata_to_repository(self) -> None:
    given = setup(
        track_ids=[TrackId("1")],
        video_files=[Path("video1.mp4")],
        track_files=[some_file],
        existing_track_files=[],
        classes={"class1", "class2"},
        georeference_metadata=GEOREF_METADATA,
    )
    target = create_target(given)

    target([some_file])

    add_all_call = given.track_repository.add_all.call_args
    dataset_arg = add_all_call.args[0]
    assert dataset_arg.georeference_metadata == GEOREF_METADATA
```

`setup` must construct the `TracksParseResult` with a `tracks` field that already has metadata attached (Task 4 makes this the parser's behavior). If the existing `setup` builds a `TracksParseResult` with a mocked `tracks` field, configure the mock so its `georeference_metadata` returns `GEOREF_METADATA`.

Also delete any code in this test file that calls `given.track_repository.apply_georeference_metadata` (only the one assertion in the renamed test).

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/OTAnalytics/application/use_cases/test_load_track_files.py -v
```
Expected: FAIL — `apply_georeference_metadata` is still being called by production code, or attribute is missing on the Mock now that the test no longer pre-configures it.

- [ ] **Step 3: Remove the repository method and the use-case call**

In `OTAnalytics/domain/track_repository.py`:

1. Delete lines 153–165 (the `apply_georeference_metadata` method).
2. Delete line 8 import: `from OTAnalytics.domain.georeference import GeoreferenceMetadata`.

In `OTAnalytics/application/use_cases/load_track_files.py`:

1. Delete lines 62–64 (the `apply_georeference_metadata` call). The `__call__` body becomes:

```python
    def __call__(self, files: list[Path]) -> None:
        """
        Load and parse the given track file together with the corresponding video file.

        Args:
            files (Path): files in ottrk format.
        """
        if not files:
            return
        parent_folder = files[0].parent
        files_to_load = [
            file for file in files if not self._is_file_already_loaded(file)
        ]
        self._log_already_loaded_files(files, files_to_load)
        if not files_to_load:
            return
        logger().info(f"Loading {len(files_to_load)} track files and videos...")
        parse_result = self._track_parser.parse_files(files_to_load)
        for video_metadata in parse_result.videos_metadata:
            self._videos_metadata.update(video_metadata)

        videos = [
            self._video_parser.parse(
                parent_folder / video_metadata.path, video_metadata
            )
            for video_metadata in parse_result.videos_metadata
        ]
        self._video_repository.add_all(videos)
        self._track_repository.add_all(parse_result.tracks)
        self._track_file_repository.add_all(files_to_load)
        for detection_metadata in parse_result.detections_metadata:
            self._tracks_metadata.update_detection_classes(
                detection_metadata.detection_classes
            )
        logger().info(f"Loaded {len(files_to_load)} track files and videos...")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/application/use_cases/test_load_track_files.py -v
uv run pytest tests/unit/OTAnalytics/domain -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/domain/track_repository.py \
       OTAnalytics/application/use_cases/load_track_files.py \
       tests/unit/OTAnalytics/application/use_cases/test_load_track_files.py
git commit -m "OP#9528: remove apply_georeference_metadata; metadata flows via add_all"
```

---

## Task 9: Cross-load mismatch propagation test (integration-style)

This locks in the safety property end-to-end: two consecutive `LoadTrackFiles` calls with mismatched metadata raise `IncompatibleGeoreferenceMetadataError`.

**Files:**
- Test: `tests/unit/OTAnalytics/application/use_cases/test_load_track_files.py`

- [ ] **Step 1: Write the failing test**

Append to `test_load_track_files.py`:

```python
def test_two_loads_with_mismatched_metadata_raise(
    self,
) -> None:
    repository = TrackRepository(
        PolarsTrackDataset(
            track_geometry_factory=POLARS_TRACK_GEOMETRY_FACTORY_FIXTURE
        )
    )
    parser_first = Mock(spec=TrackParser)
    parser_first.parse_files.return_value = TracksParseResult(
        tracks=PolarsTrackDataset.from_list(
            [SOME_TRACK], POLARS_TRACK_GEOMETRY_FACTORY_FIXTURE
        ).with_georeference_metadata(GEOREF_METADATA),
        detections_metadata=[DetectionMetadata(frozenset(["car"]))],
        videos_metadata=[SOME_VIDEO_METADATA],
    )
    # ... wire up remaining required mocks (video_repository, video_parser, etc.)
    target_first = create_target_with(repository=repository, parser=parser_first, ...)
    target_first([Path("a.ottrk")])

    parser_second = Mock(spec=TrackParser)
    parser_second.parse_files.return_value = TracksParseResult(
        tracks=PolarsTrackDataset.from_list(
            [OTHER_TRACK], POLARS_TRACK_GEOMETRY_FACTORY_FIXTURE
        ).with_georeference_metadata(ALTERNATE_GEOREF_METADATA),
        detections_metadata=[DetectionMetadata(frozenset(["car"]))],
        videos_metadata=[SOME_VIDEO_METADATA],
    )
    target_second = create_target_with(repository=repository, parser=parser_second, ...)

    with pytest.raises(IncompatibleGeoreferenceMetadataError):
        target_second([Path("b.ottrk")])
```

(Adapt to the test file's existing `Given` / `create_target` factories. If the file uses Mock for `track_repository`, instead replace it with a real `TrackRepository` for this single test so `add_all` actually runs and raises.)

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/OTAnalytics/application/use_cases/test_load_track_files.py -v -k mismatched
```
Expected: FAIL initially during test scaffolding, then PASS once everything is wired up.

- [ ] **Step 3: Already implemented**

Production code is already complete from Task 8. The test is the only deliverable.

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/OTAnalytics/application/use_cases/test_load_track_files.py -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/unit/OTAnalytics/application/use_cases/test_load_track_files.py
git commit -m "OP#9528: integration test for mismatched georeference across loads"
```

---

## Task 10: Non-Polars `with_georeference_metadata` raises (regression coverage)

Confirms the default abstract behavior holds on real Pandas / Python implementations.

**Files:**
- Test: `tests/unit/OTAnalytics/plugin_datastore/test_track_store.py` (Pandas)
- Test: `tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py` (Python)

- [ ] **Step 1: Write the failing tests**

In each of the two test files above (use whichever exists; create the test class adjacent to the existing dataset test classes for that backend):

```python
class TestPandasTrackDatasetGeoreferenceUnsupported:
    def test_with_georeference_metadata_raises_not_implemented(
        self, track_geometry_factory
    ) -> None:
        dataset = PandasTrackDataset(track_geometry_factory=track_geometry_factory)
        with pytest.raises(NotImplementedError):
            dataset.with_georeference_metadata(SAMPLE_GEOREFERENCE_METADATA)

    def test_georeference_metadata_property_returns_none(
        self, track_geometry_factory
    ) -> None:
        dataset = PandasTrackDataset(track_geometry_factory=track_geometry_factory)
        assert dataset.georeference_metadata is None
```

Mirror the same two tests for `PythonTrackDataset` in the python test file.

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore/test_track_store.py tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py -v -k Georeference
```
Expected: PASS already (because Task 1 placed defaults on the abstract base — non-Polars backends inherit them). If for some reason an old `__init__` parameter or local override shadows the property, FAIL — then remove the override.

- [ ] **Step 3: No production change expected**

If the tests pass in step 2, skip directly to step 4. If they fail, investigate the failing backend and remove any local `georeference_metadata` override that returns something other than the default.

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_datastore -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/unit/OTAnalytics/plugin_datastore/test_track_store.py \
       tests/unit/OTAnalytics/plugin_datastore/test_python_track_store.py
git commit -m "OP#9528: lock in non-Polars backends' default georeference behavior"
```

---

## Task 11: Final whole-suite sweep

**Files:** none (verification only).

- [ ] **Step 1: Run the full test suite**

```bash
uv run pytest
```
Expected: PASS. Any pre-existing test that referenced `TracksParseResult.georeference_metadata` or `TrackRepository.apply_georeference_metadata` and was not updated in tasks 6–8 will fail here. Fix each (read from `tracks.georeference_metadata`; remove apply assertions) and append a single commit.

- [ ] **Step 2: Run linters / type-checks if the project uses them**

```bash
uv run mypy OTAnalytics
```
Expected: PASS. The `apply_georeference_metadata` and parser field deletions can leave stale imports — clean them up.

- [ ] **Step 3: Commit any cleanups**

```bash
git add -A
git commit -m "OP#9528: clean up stragglers from georeference containment refactor"
```

(If no fixes are needed, skip the commit.)

---

## Spec Coverage Map

| Spec section | Implemented in |
|---|---|
| `TrackDataset` gains property + method with defaults | Task 1 |
| `IncompatibleGeoreferenceMetadataError` | Task 1 |
| `PolarsTrackDataset.add_all` validation rule | Task 2 |
| Empty-current early-return metadata bugfix | Task 2 |
| Lifecycle preservation (`remove`, `remove_multiple`, `filter_by_min_detection_length`, `split_finished`, `revert_cuts_for`, `remove_by_original_ids`, `_subset_by_ids`, `cut_with_section`) | Task 3 |
| `clear()` drops metadata | Task 3 (test only — existing behavior) |
| `OttrkParser.parse` embeds metadata | Task 4 |
| `FeathersParser.parse` embeds metadata; override deleted | Task 5 |
| `TrackParseResult` / `TracksParseResult` lose field | Task 6 |
| `TrackParser.parse_files` simplified | Task 6 |
| `convert_ottrk_to_feathers` reads from `tracks` | Task 7 |
| `TrackRepository.apply_georeference_metadata` deleted | Task 8 |
| `LoadTrackFiles` no longer applies metadata | Task 8 |
| End-to-end mismatch propagation | Task 9 |
| Non-Polars backends raise | Task 10 |
| Stragglers / full sweep | Task 11 |

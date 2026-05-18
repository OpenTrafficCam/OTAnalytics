# Georeference Metadata Containment Design

**Date:** 2026-05-18
**Issue:** OP#9528
**Status:** Approved (pending writing of implementation plan)

## Problem

`GeoreferenceMetadata` currently leaks out of the Polars storage layer and into
the domain repository and the application use-case layer:

- `TrackRepository.apply_georeference_metadata` (`OTAnalytics/domain/track_repository.py:153`)
  duck-types the dataset via `hasattr(self._dataset, "with_georeference_metadata")`.
- `LoadTrackFiles` (`OTAnalytics/application/use_cases/load_track_files.py:62`)
  reads `parse_result.georeference_metadata` and applies it to the repository
  in a step separate from `add_all`.
- `TrackParser.parse_files` (`OTAnalytics/application/parser/track_parser.py:48`)
  silently picks the first non-`None` per-file metadata as the single source of
  truth, swallowing any disagreement between files.

The fragility shows in two concrete places:

1. Different ottrk files in a batch could carry incompatible metadata; the
   first-wins policy hides that.
2. A repository can be "upgraded" with metadata after the fact, leading to
   detections that have no geo coordinates being treated as part of a
   georeferenced dataset.

## Goal

Contain georeference knowledge inside the `TrackDataset`. The application and
domain layers stay georef-ignorant. Cross-file consistency is enforced
automatically by the merge operation (`add_all`), and the metadata flows
implicitly through the dataset rather than being passed separately.

## Non-Goals

- Designing a UI for the new error path. The error is allowed to propagate to
  whatever already handles unexpected exceptions during a load. A dedicated UI
  surface can be added in a follow-up if the generic handler is too coarse.
- Adding meaningful georef support to Pandas / Python backends. They explicitly
  do not implement `with_georeference_metadata`.

## Design

### TrackDataset Interface

The abstract `TrackDataset` (`OTAnalytics/domain/track_dataset/track_dataset.py`)
gains two members with backend-friendly defaults:

```python
class TrackDataset(ABC):
    @property
    def georeference_metadata(self) -> GeoreferenceMetadata | None:
        return None

    def with_georeference_metadata(
        self, metadata: GeoreferenceMetadata | None
    ) -> "TrackDataset":
        raise NotImplementedError(
            f"{type(self).__name__} does not support georeference metadata"
        )
```

- `PolarsTrackDataset` and `FilterPolarsTrackDataset` already override both;
  no change needed beyond the interface declaration.
- `PandasTrackDataset`, `PythonTrackDataset`, and their filter wrappers inherit
  the defaults. Attempting to attach metadata raises loudly — the parser will
  surface the misconfiguration rather than silently drop the metadata.

### New Exception Type

In the same module:

```python
class IncompatibleGeoreferenceMetadataError(Exception):
    """Raised when merging datasets with incompatible georeference metadata."""
```

### Validation Rule in `PolarsTrackDataset.add_all`

Let `current = self` and `incoming` = the dataset being added.

```
if current.is_empty():
    inherit incoming.georeference_metadata into the new dataset
else:
    if current.georeference_metadata != incoming.georeference_metadata:
        raise IncompatibleGeoreferenceMetadataError(
            f"Cannot merge dataset with georeference {incoming.georeference_metadata} "
            f"into dataset with georeference {current.georeference_metadata}"
        )
```

This single rule covers all merge cases:

| current empty? | current metadata | incoming metadata | outcome |
|----------------|------------------|-------------------|---------|
| yes            | None (implicit)  | None              | OK, result has None |
| yes            | None (implicit)  | yes               | OK, result inherits incoming |
| no             | None             | None              | OK, result has None |
| no             | None             | yes               | **Error** |
| no             | yes              | None              | **Error** |
| no             | yes              | yes (equal)       | OK |
| no             | yes              | yes (different)   | **Error** |

The bug at `polars_track_store.py:451` (the empty-current early return drops
the incoming dataset's metadata) is fixed as part of implementing this rule.

### Lifecycle Preservation in `PolarsTrackDataset`

Operations that return a new dataset must preserve metadata:

- `remove`, `remove_multiple`
- `revert_cuts_for`, `remove_by_original_ids`
- `filter_by_min_detection_length`
- `split`, `split_finished`

`clear()` returns a fresh empty dataset and intentionally drops metadata; this
is the desired behavior for `TrackRepository.clear()`.

### Parser Changes

`TrackParseResult` and `TracksParseResult` (`OTAnalytics/application/parser/track_parser.py`)
lose the `georeference_metadata` field. Consumers read
`result.tracks.georeference_metadata` instead.

`OttrkParser.parse` (`OTAnalytics/plugin_parser/otvision_parser.py:582`) attaches
metadata to the dataset before returning:

```python
tracks = self._detection_parser.parse_tracks(...)
georef = self._parse_georeference_metadata(...)
if georef is not None:
    tracks = tracks.with_georeference_metadata(georef)
return TrackParseResult(tracks, detection_metadata, video_metadata)
```

`FeathersParser.parse` (`OTAnalytics/plugin_parser/feathers_parser.py:160`) does
the analogous embedding. Its overridden `parse_files` (line 97) — which
re-implements the first-wins policy — is **deleted** so it inherits the
validating base implementation.

`TrackParser.parse_files` is simplified:

```python
def parse_files(self, files: list[Path]) -> TracksParseResult:
    if not files:
        raise ValueError("No files to parse")
    results = [self.parse(file) for file in files]
    tracks = combine_track_datasets(results)   # add_all does the validation
    detections_metadata = [r.detection_metadata for r in results]
    videos_metadata = [r.video_metadata for r in results]
    return TracksParseResult(tracks, detections_metadata, videos_metadata)
```

`combine_track_datasets` stays as-is; the chained `add_all` calls now police
the cross-file invariant.

`convert_ottrk_to_feathers.create_metadata_dict` (`OTAnalytics/plugin_parser/convert_ottrk_to_feathers.py:85`)
reads `parse_result.tracks.georeference_metadata` instead of
`parse_result.georeference_metadata`.

### Repository and Use-Case Changes

`TrackRepository.apply_georeference_metadata` and its import of
`GeoreferenceMetadata` are deleted.

`LoadTrackFiles.__call__` (`OTAnalytics/application/use_cases/load_track_files.py:33`)
drops the `apply_georeference_metadata` call and the
`GeoreferenceMetadata` import. The metadata now flows through
`track_repository.add_all(parse_result.tracks)`.

### Error Propagation

If two `LoadTrackFiles` invocations supply files with mismatched metadata, the
error path is:

```
LoadTrackFiles.__call__
  └─ track_repository.add_all
       └─ dataset.add_all (PolarsTrackDataset)
            └─ raises IncompatibleGeoreferenceMetadataError
```

The exception propagates out of `LoadTrackFiles` to whichever command handler
invoked it. No translation layer is added in this scope.

### Streaming Parser

`StreamingParser._parse_tracks` (`OTAnalytics/plugin_parser/streaming_parser.py:113`)
already uses `remaining_tracks.add_all(parse_result.tracks)`. Once `parse`
embeds metadata in each per-file dataset, the streaming path validates georef
consistency automatically with no further change.

## Testing

### `PolarsTrackDataset.add_all` (in `tests/unit/OTAnalytics/plugin_datastore/test_polars_track_store.py`)

- Adding to an empty dataset inherits incoming metadata.
- Empty + empty (both None) succeeds.
- Populated + matching metadata succeeds.
- Populated + mismatched metadata raises `IncompatibleGeoreferenceMetadataError`.
- Populated without metadata + incoming with metadata raises.
- Populated with metadata + incoming without metadata raises (symmetric).

### Lifecycle preservation

- `remove`, `remove_multiple`, `filter_by_min_detection_length`, `split`,
  `split_finished`, `revert_cuts_for`, `remove_by_original_ids` preserve
  metadata across the operation.
- `clear()` drops metadata.

### Non-Polars backends

- `PandasTrackDataset.with_georeference_metadata` raises
  `NotImplementedError`.
- `PythonTrackDataset.with_georeference_metadata` raises
  `NotImplementedError`.
- Their `georeference_metadata` property returns `None`.

### Parser-level (in `tests/unit/OTAnalytics/application/parser/test_track_parser.py`)

- `parse_files` with consistent metadata across files succeeds; result dataset
  carries the metadata.
- `parse_files` with mismatched metadata raises
  `IncompatibleGeoreferenceMetadataError`.
- `parse_files` with some files carrying metadata and some not raises.
- `parse_files` with no metadata in any file succeeds, result dataset metadata
  is `None`.
- `parse_files` with a single file succeeds regardless of metadata presence.

### `LoadTrackFiles` (in `tests/unit/OTAnalytics/application/use_cases/test_load_track_files.py`)

- Replace the existing assertion on `apply_georeference_metadata.assert_called_once_with(...)`
  (line 156) with an assertion that the dataset passed to
  `track_repository.add_all` carries the expected metadata.
- New: two consecutive `LoadTrackFiles` calls with mismatched metadata
  propagate `IncompatibleGeoreferenceMetadataError`.

### Removals / updates

- Delete tests of `TrackRepository.apply_georeference_metadata`.
- Update `convert_ottrk_to_feathers` tests to read
  `parse_result.tracks.georeference_metadata`.
- Update any test asserting on `TracksParseResult.georeference_metadata` to
  read from `result.tracks.georeference_metadata`.

## Files Touched

**Production:**

- `OTAnalytics/domain/track_dataset/track_dataset.py` (add interface members + exception)
- `OTAnalytics/domain/track_repository.py` (remove `apply_georeference_metadata`)
- `OTAnalytics/application/parser/track_parser.py` (drop fields, simplify `parse_files`)
- `OTAnalytics/application/use_cases/load_track_files.py` (drop the apply call)
- `OTAnalytics/plugin_datastore/polars_track_store.py` (validation rule + empty-merge fix + preservation across operations)
- `OTAnalytics/plugin_parser/otvision_parser.py` (embed metadata in `parse`)
- `OTAnalytics/plugin_parser/feathers_parser.py` (embed metadata in `parse`; delete overridden `parse_files`)
- `OTAnalytics/plugin_parser/convert_ottrk_to_feathers.py` (read metadata from `tracks`)

**Tests:** as listed above.

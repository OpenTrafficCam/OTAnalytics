# Design: Bulk Polars Track Dataset Merging

**Date:** 2026-05-19
**Branch:** feature/9528-extend-sections-and-tracks-with-optional-geo-coordinates

## Problem

`TrackParser._combine_track_datasets` merges a list of `TrackParseResult` objects by calling `add_all` iteratively — one dataset at a time. For `PolarsTrackDataset`, each `add_all` call does a `pl.concat` of two DataFrames. When parsing many feather files, `pl.concat` on a list of N DataFrames at once is significantly more efficient than N-1 pairwise concatenations.

`FeathersParser` had an incomplete/erroneous attempt at overriding `_combine_track_datasets` to use bulk concat. The broken implementation called `.data` (non-existent attribute), never used the `georeference_metadata` it collected, and had no return statement for the polars branch.

The attempted override also reproduced georeference metadata validation logic that already lives in `PolarsTrackDataset.add_all`, creating a duplication smell. The root cause: the override was trying to own validation logic that belongs in the data layer.

## Decision

Add `PolarsTrackDataset.merge_all` — a classmethod that performs bulk validation and concat in one place — and make `FeathersParser._combine_track_datasets` a thin orchestrator that delegates to it.

## Design

### `PolarsTrackDataset.merge_all` (`polars_track_store.py`)

```python
@classmethod
def merge_all(cls, datasets: Sequence["PolarsTrackDataset"]) -> "PolarsTrackDataset":
```

**Signature:** accepts `Sequence[PolarsTrackDataset]` only. Accepting the base `TrackDataset` type was rejected because non-Polars implementations would require falling back to `__iter__`, hiding a performance cliff behind the same method name. The call site is responsible for the type check.

**Algorithm:**

1. Raise `ValueError("No datasets to merge")` if `datasets` is empty.
2. Validate georeference metadata: `datasets[0].georeference_metadata` must equal every other dataset's `georeference_metadata`. Raise `IncompatibleGeoreferenceMetadataError` if any differ. All datasets are validated (including those with empty DataFrames) — a file parsed with georeference metadata is incompatible with one without, even if it produced zero tracks.
3. Use `track_geometry_factory` and `calculator` from `datasets[0]` as the template for the result.
4. Filter to datasets whose internal `pl.DataFrame` is non-empty (`not ds._dataset.is_empty()`).
5. If none remain after filtering, return `PolarsTrackDataset(factory, calculator=calculator, georeference_metadata=metadata)`.
6. Determine `geo_cols` as the **intersection**: only include `GEO_X`/`GEO_Y` if present in **all** non-empty DataFrames (same policy as `add_all`).
7. For each non-empty dataset, call `drop_row_id(ds._dataset).select(COLUMNS + geo_cols)`. Pass the resulting list to a single `pl.concat` call. Sort by `INDEX_NAMES`.
8. Call `_assign_track_classification` on the merged frame.
9. Return `cls.from_dataframe(merged, factory, calculator=calculator, georeference_metadata=metadata)`.

**Note:** `merge_all` does not attempt to preserve or update existing geometry datasets — it builds a fresh one via `from_dataframe`. This is correct for parse-time assembly. `add_all` (the incremental path) retains its separate geometry-update logic and is unchanged.

### `FeathersParser._combine_track_datasets` (`feathers_parser.py`)

Replace the broken override with:

```python
def _combine_track_datasets(self, parse_results: list[TrackParseResult]) -> TrackDataset:
    datasets = [r.tracks for r in parse_results]
    if all(isinstance(ds, PolarsTrackDataset) for ds in datasets):
        return PolarsTrackDataset.merge_all(cast(list[PolarsTrackDataset], datasets))
    return super()._combine_track_datasets(parse_results)
```

No georeference validation logic lives in `FeathersParser`. The override is purely an orchestrator: check types, delegate to the appropriate path.

## What is NOT changed

- `PolarsTrackDataset.add_all` — unchanged. It remains the incremental path for repository updates and preserves its geometry-dataset update logic.
- `TrackParser._combine_track_datasets` — unchanged. The base implementation continues to serve all non-Polars parsers.
- `TrackDataset` base class — no interface changes.

## Testing

- `PolarsTrackDataset.merge_all` with identical georeference metadata across all datasets → merged result carries the shared metadata.
- `PolarsTrackDataset.merge_all` with mismatched georeference metadata → raises `IncompatibleGeoreferenceMetadataError`.
- `PolarsTrackDataset.merge_all` where all datasets have no georeference metadata → merged result has `None`.
- `PolarsTrackDataset.merge_all` where some datasets have empty DataFrames → empty ones are skipped in concat but still validated; result carries shared metadata.
- `PolarsTrackDataset.merge_all([])` → raises `ValueError`.
- `FeathersParser._combine_track_datasets` with all-Polars parse results → delegates to `merge_all`.
- `FeathersParser._combine_track_datasets` with mixed types → falls back to `super()`.

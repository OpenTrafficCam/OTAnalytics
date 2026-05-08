# Export Filepath Standardization Design

**Date:** 2026-05-08
**Issue:** OP#9548 (incomplete filenames with multiple dots) revealed a class of bugs caused by misleading specification field naming
**Scope:** Targeted clarity improvements + shared utility to prevent recurrence

## Problem Statement

The codebase had a bug class where `Path.with_suffix()` was called on values that semantically were filename stems, not paths with extensions to replace. When a stem like `video.00000_2025-08-28_15-00-00` was passed to `.with_suffix(".csv")`, the result was `video.csv` — losing the entire timestamp portion.

The root causes are:
1. **Misleading field naming:** Specifications used `save_path: Path` for what was actually a stem (directory + filename without extension), encouraging developers to call `Path` methods that assume a full path
2. **No shared utility:** Each exporter built paths inline, leading to inconsistent (and sometimes buggy) implementations

OP#9548 fixed the symptom in `cli.py` but missed `plugin_parser/track_export.py`, which had the same bug pattern. The bug was found again in production after the initial fix.

## Solution Overview

Targeted, minimal changes that fix the root cause without unnecessary refactoring:

1. **Add a shared path-building utility** to centralize the correct pattern
2. **Rename `save_path` to explicit `export_directory` + `export_filename_stem`** in the specifications where the misleading name caused the bug
3. **Leave specifications alone** where the current naming is correct (e.g., `EventExportSpecification.file` is genuinely a full path)
4. **Optional cleanup:** rename `mode` → `export_mode` for naming consistency in road user assignment exporter, and remove dead code (`MultiExportTracks`)

This is a focused change. We do NOT introduce a `BaseExportSpecification` base class or force aesthetic consistency across all exporters.

## Design Details

### 1. Shared Path Building Utility

Create new module: `OTAnalytics/application/export_path_builder.py`

```python
from pathlib import Path


def build_export_path(
    export_directory: Path,
    export_filename_stem: str,
    file_suffix: str,
) -> Path:
    """Build an export file path from directory, stem, and suffix.

    This is the canonical way to construct export file paths in OTAnalytics.
    It centralizes the pattern to prevent recurrence of the multi-dot
    truncation bug (OP#9548).

    DO NOT use ``Path.with_suffix()`` to attach an extension to an export
    stem. ``with_suffix()`` replaces the substring after the last dot, so a
    stem like ``video.00000_2025-08-28_15-00-00`` becomes ``video`` plus the
    new suffix — silently losing the timestamp.

    Args:
        export_directory: Parent directory where the file will be written.
        export_filename_stem: Filename without any extension, possibly
            containing multiple dots (e.g., a timestamped video name).
        file_suffix: Format suffix to append, including the leading dot
            (e.g., ".csv", ".tracks_metadata.json").

    Returns:
        ``export_directory / (export_filename_stem + file_suffix)``.

    Example:
        >>> build_export_path(
        ...     Path("/output"),
        ...     "video.00000_2025-08-28_15-00-00",
        ...     ".tracks.csv",
        ... )
        PosixPath('/output/video.00000_2025-08-28_15-00-00.tracks.csv')
    """
    return export_directory / (export_filename_stem + file_suffix)
```

**Why this pattern:** `Path.with_suffix()` replaces the substring after the last dot. Concatenating to `name` and joining with `parent` preserves the full stem regardless of how many dots it contains.

### 2. Rename `save_path` → `export_directory` + `export_filename_stem`

In the **three specifications** where `save_path` is semantically a stem:

#### `TrackExportSpecification` (`OTAnalytics/application/use_cases/track_export.py`)

```python
@dataclass(frozen=True)
class TrackExportSpecification:
    export_directory: Path
    export_filename_stem: str
    export_format: list[TrackFileFormat]
    export_mode: ExportMode
```

#### `TrackStatisticsExportSpecification` (`OTAnalytics/application/use_cases/track_statistics_export.py`)

```python
@dataclass(frozen=True)
class TrackStatisticsExportSpecification:
    export_directory: Path
    export_filename_stem: str
    format: str
    export_mode: ExportMode
```

#### `ExportSpecification` for road user assignments (`OTAnalytics/application/use_cases/road_user_assignment_export.py`)

```python
@dataclass(frozen=True)
class ExportSpecification:
    export_directory: Path
    export_filename_stem: str
    format: str
    export_mode: ExportMode  # also rename: mode → export_mode (see §5)
```

**Contract for these specs:**
```
Output file = export_directory / (export_filename_stem + file_suffix)
```

### 3. Update Exporter Implementations

Each affected exporter:
- Receives the new fields via the specification
- Calls `build_export_path()` to construct file paths
- No longer uses `.with_suffix()` on stems

#### `CsvTrackExport` (`OTAnalytics/plugin_parser/track_export.py`)

```python
class CsvTrackExport(ExportTracks):
    PRIMARY_SUFFIX = ".tracks.csv"
    DERIVED_SUFFIXES = (".tracks_metadata.json", ".videos_metadata.json")

    def export(self, specification: TrackExportSpecification) -> None:
        self._update_iterative_metadata()

        append = specification.export_mode.is_subsequent_write()
        dataframe = set_column_order(self._get_data())

        primary_path = build_export_path(
            specification.export_directory,
            specification.export_filename_stem,
            self.PRIMARY_SUFFIX,
        )
        write_mode: Literal["w", "a"] = "a" if append else "w"
        dataframe.to_csv(primary_path, index=False, header=not append, mode=write_mode)

        if specification.export_mode.is_final_write():
            for suffix, payload in zip(
                self.DERIVED_SUFFIXES,
                (self._iterative_tracks_metadata, self._iterative_videos_metadata),
            ):
                path = build_export_path(
                    specification.export_directory,
                    specification.export_filename_stem,
                    suffix,
                )
                write_json(payload, path)

            self._iterative_tracks_metadata.clear()
            self._iterative_videos_metadata.clear()
```

Apply the same pattern to:
- `TrackStatisticsCsvExporter` (single primary suffix `.csv`)
- `RoadUserAssignmentCsvExporter` (single primary suffix `.csv`)

### 4. CLI Updates (`OTAnalytics/plugin_ui/cli.py`)

Helper methods change from passing a single `save_path` to passing `export_directory` and `export_filename_stem`:

```python
async def _do_export_tracks(
    self,
    export_directory: Path,
    export_filename_stem: str,
    export_mode: ExportMode,
) -> None:
    logger().info("Start tracks export")
    specification = TrackExportSpecification(
        export_directory=export_directory,
        export_filename_stem=export_filename_stem,
        export_format=self._run_config.track_export_format,
        export_mode=export_mode,
    )
    await asyncio.to_thread(self._export_tracks.export, specification)
    logger().info("Finished tracks export")
    await self._after_track_export(export_directory, export_filename_stem)
```

The existing inline `save_path.parent / (save_path.name + suffix)` patterns in `cli.py` (added in OP#9548 for events, counts, road user assignments, and track statistics) are replaced with `build_export_path()` calls. This removes duplication and uses the shared, documented utility.

### 5. Optional Naming Consistency

Rename `mode` → `export_mode` in `ExportSpecification` (road user assignments) so all four affected specs use the same field name for the same concept. Trivial change, included for grep-ability.

### 6. Optional Dead Code Removal

`MultiExportTracks` in `OTAnalytics/application/use_cases/track_export.py` is unreferenced outside of its own test file. It can be deleted, along with its tests. This is independent of the rest of the change and can land as a separate commit.

## What Is Explicitly Out of Scope

To keep this change focused and avoid the overengineering trap:

- **No `BaseExportSpecification` class.** The specifications have legitimately different shapes (`CountingSpecificationDto` is a domain DTO, `EventExportSpecification.file` is a full path) and forcing inheritance would obscure those differences.
- **No changes to `EventExportSpecification`.** Its `file: Path` field is genuinely a full path (the CLI builds it via `build_export_path()` before constructing the spec). Renaming would just churn.
- **No changes to `CountingSpecificationDto`.** It is a domain DTO used by OTCloud for live counting (with `output_file="none"`, no actual file output). Changing its constructor would break OTCloud's `count_data_updater.py` for no benefit to the bug class we're fixing.
- **No "single format per specification" rule.** Separate concern; not what caused the bug.
- **No format-specific output declarations on the spec.** Suffixes belong in the exporter implementations that produce them; this is already where they live.

## Impact on OTCloud

OTCloud (`/Users/rseng/dev/OpenTrafficCam/OTCloud`) imports a small subset of OTAnalytics export-related symbols. Audited usage:

| Symbol | Used by OTCloud? | Affected by this change? |
|--------|------------------|--------------------------|
| `CountingSpecificationDto` | ✅ `plugin_live_application/traffic_count_handling/count_data_updater.py` | ❌ Not changed |
| `CountingSpecificationDto` | ✅ `plugin_plotter/track_plotter.py` (return type only) | ❌ Not changed |
| `TrackExportSpecification` | ❌ Not used | n/a |
| `TrackStatisticsExportSpecification` | ❌ Not used | n/a |
| `EventExportSpecification` | ❌ Not used | n/a |
| `ExportSpecification` (road user) | ❌ Not used | n/a |
| `MultiExportTracks` | ❌ Not used | n/a (safe to remove) |

**Conclusion:** This change has **no breaking impact on OTCloud**, because OTCloud only consumes `CountingSpecificationDto`, which we are deliberately leaving untouched.

OTCloud pins `OTAnalytics==0.7.3` and explicitly upgrades, so any future incompatibility would be picked up at OTCloud's upgrade step regardless.

## Future Work

These items are out of scope for this change but could be revisited later:

1. **Reconsider `CountingSpecificationDto`'s dual purpose.** It is both a counting parameter DTO (used in-process by OTCloud for live counting) and an export specification (used by OTAnalytics CLI for file output). Splitting these responsibilities would clarify intent — but requires a coordinated change with OTCloud and is not driven by the multi-dot bug.

2. **Consider unifying `EventExportSpecification.file: Path` with the directory + stem pattern.** Currently the CLI builds the full path before constructing the spec. If event exporters ever need to produce derived files (analogous to `CsvTrackExport`'s metadata files), this restructuring would be needed. Until that requirement appears, leaving it alone is YAGNI-correct.

3. **Audit other `Path.with_suffix()` calls.** `feathers_parser.py` uses `with_suffix()` for input file lookup, not output path construction; current usage looks safe but a brief audit during this work is cheap insurance.

## Testing

- **Unit test for `build_export_path()`** with an input stem containing multiple dots (e.g., `video.00000_2025-08-28_15-00-00`) and assert that the full stem is preserved in the output path.
- **Update existing exporter tests** to use the new field names (`export_directory`, `export_filename_stem`) and add at least one test per affected exporter that uses a multi-dot stem to lock in the regression fix.
- **Manual integration test:** rerun the original failing command and verify all output filenames preserve the timestamp portion:
  ```
  uv run -m OTAnalytics --cli --track-export --track-statistics-export \
      --config <path-to-otconfig-with-multi-dot-name>
  ```

## Migration Plan

Suggested commit sequence (each commit should leave the build green):

1. Add `OTAnalytics/application/export_path_builder.py` with `build_export_path()` and tests.
2. Update `TrackExportSpecification` and `CsvTrackExport` to use the new fields and the utility. Update the CLI helper that constructs this spec.
3. Repeat for `TrackStatisticsExportSpecification` / `TrackStatisticsCsvExporter`.
4. Repeat for `ExportSpecification` (road user) / `RoadUserAssignmentCsvExporter`. Rename `mode` → `export_mode` in the same commit.
5. Replace inline `parent / (name + suffix)` patterns in `cli.py` (events, counts) with `build_export_path()` calls.
6. (Optional) Delete `MultiExportTracks` and its test in a separate commit.

Each commit is independently reviewable and revertable.

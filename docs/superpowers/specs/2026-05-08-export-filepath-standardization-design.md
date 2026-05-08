# Export Filepath Standardization Design

**Date:** 2026-05-08
**Issue:** OP#9548 (incomplete filenames with multiple dots) revealed inconsistent filepath building across exporters
**Scope:** Standardize how all exporters build output file paths

## Problem Statement

The codebase has multiple exporters (tracks, events, counts, statistics, assignments) that each build output filepaths differently:
- Some use `Path.with_suffix()` (bug-prone with multiple dots in filename)
- Some use manual `parent / (name + suffix)` construction
- Inconsistency makes bugs easy to miss and hard to prevent in future

Example bug: When video name is `video.00000_2025-08-28_15-00-00`, Path.with_suffix() would truncate it to `video` + suffix, losing the entire `00000_2025-08-28_15-00-00` portion.

## Solution Overview

Standardize filepath building by:
1. Making export specifications explicit about their three components: directory, filename stem, and format
2. Centralizing path building logic in a shared utility function
3. Removing dead code (`MultiExportTracks` unused)
4. Enforcing single format per specification for clarity

## Design Details

### 1. Base Specification Class

Create `BaseExportSpecification` in `application/use_cases/` as the parent for all exporters:

```python
@dataclass
class BaseExportSpecification:
    export_directory: Path          # Parent directory where files are written
    export_filename_stem: str       # Filename without any extension/format
    export_mode: ExportMode         # OVERWRITE, APPEND, etc.
    # Subclasses define their specific export format
```

**Contract:**
```
Actual output file = export_directory / (export_filename_stem + file_suffix)
```

**Example:**
```python
spec = TrackExportSpecification(
    export_directory=Path("/output"),
    export_filename_stem="video.00000_2025-08-28_15-00-00",
    export_format=TrackFileFormat.CSV,
    export_mode=OVERWRITE
)

# Produces files like:
# /output/video.00000_2025-08-28_15-00-00.tracks.csv
# /output/video.00000_2025-08-28_15-00-00.tracks_metadata.json
# /output/video.00000_2025-08-28_15-00-00.videos_metadata.json
```

All export specifications inherit from `BaseExportSpecification`:

```python
@dataclass
class TrackExportSpecification(BaseExportSpecification):
    export_format: TrackFileFormat  # Single format per spec

@dataclass
class EventExportSpecification(BaseExportSpecification):
    format: str

@dataclass
class TrackStatisticsExportSpecification(BaseExportSpecification):
    format: str

@dataclass
class CountingSpecificationDto(BaseExportSpecification):
    start: datetime
    end: datetime
    interval_in_minutes: int
    modes: list[str]
    output_format: str
```

### 2. Shared Path Building Utility

Create new module: `application/export_path_builder.py`

```python
from pathlib import Path

def build_export_path(
    export_directory: Path,
    export_filename_stem: str,
    file_suffix: str
) -> Path:
    """Build export file path from three explicit components.

    This function centralizes the path building logic to prevent bugs
    like truncation when filenames contain multiple dots.

    Args:
        export_directory: Parent directory (e.g., Path("/output"))
        export_filename_stem: Filename without format (e.g., "video.timestamp")
        file_suffix: Format suffix (e.g., ".csv", ".json")

    Returns:
        export_directory / (export_filename_stem + file_suffix)

    Example:
        build_export_path(
            Path("/output"),
            "video.00000_2025-08-28_15-00-00",
            ".csv"
        )
        → Path("/output/video.00000_2025-08-28_15-00-00.csv")
    """
    return export_directory / (export_filename_stem + file_suffix)
```

**Why this pattern prevents bugs:**
- `Path.with_suffix()` replaces only the last dot-separated segment
- `parent / (name + suffix)` preserves the full stem regardless of dots
- Centralizing logic prevents inconsistent implementations

### 3. Exporter Implementation Pattern

Each exporter:
1. Declares its primary output file suffix
2. Declares any derived output file suffixes (metadata, etc.)
3. Uses `build_export_path()` to construct all file paths

**Example: CsvTrackExport**

```python
class CsvTrackExport(ExportTracks):
    """Exports tracks to CSV format.

    Primary output: .tracks.csv
    Derived outputs: .tracks_metadata.json, .videos_metadata.json
    """

    PRIMARY_SUFFIX = ".tracks.csv"
    DERIVED_SUFFIXES = [".tracks_metadata.json", ".videos_metadata.json"]

    def export(self, specification: TrackExportSpecification) -> None:
        # Build primary output path
        primary_path = build_export_path(
            specification.export_directory,
            specification.export_filename_stem,
            self.PRIMARY_SUFFIX
        )

        # Write primary output
        dataframe.to_csv(primary_path, index=False, ...)

        # Write derived outputs on final write
        if specification.export_mode.is_final_write():
            for suffix in self.DERIVED_SUFFIXES:
                derived_path = build_export_path(
                    specification.export_directory,
                    specification.export_filename_stem,
                    suffix
                )
                write_json(data, derived_path)
```

**Pattern applies to all exporters:**
- Events exporter: primary `.events.csv`
- Track statistics exporter: primary `.track_statistics.csv`
- Road user assignment exporter: primary `.road_user_assignments.csv`
- Counts exporter: primary `.counts_15min.csv` (or other interval)

### 4. Single Format Per Specification

Each specification has a single `export_format` (not a list):

```python
@dataclass
class TrackExportSpecification(BaseExportSpecification):
    export_format: TrackFileFormat  # Single format: CSV or FEATHER
```

**Rationale:**
- Clearer contract: one spec = one primary output file
- Prevents confusion about path building logic
- If multiple formats needed, create multiple specifications
- `MultiExportTracks` is removed (was unused, only in tests)

### 5. CLI Layer Updates

Update `OTAnalytics/plugin_ui/cli.py`:

1. Change parameter names from `save_path` to `export_directory` and `export_filename_stem`
2. Create specifications with explicit components
3. Remove `MultiExportTracks` references (dead code)
4. If multi-format export needed in future, loop explicitly:

```python
async def export_to_multiple_formats(self, export_directory, export_filename_stem):
    for format in desired_formats:
        spec = TrackExportSpecification(
            export_directory=export_directory,
            export_filename_stem=export_filename_stem,
            export_format=format,
            export_mode=OVERWRITE
        )
        await asyncio.to_thread(self._export_tracks.export, spec)
```

## Benefits

1. **Bug prevention:** Centralized path building eliminates the `.with_suffix()` bug class
2. **Clarity:** Three explicit components remove ambiguity about what goes where
3. **Maintainability:** Single path building utility is easier to audit and test
4. **Consistency:** All exporters follow the same pattern
5. **Future-proofing:** Adding a new exporter or format requires no path building logic

## Scope: Exporters Included

This standardization applies to all exporters in the system:
- **Track export** (CSV, feather formats)
- **Track statistics export** (CSV)
- **Event export** (multiple formats via provider)
- **Road user assignment export** (CSV)
- **Counts export** (CSV)

## Migration Path

1. Create `BaseExportSpecification` with all three components
2. Create `build_export_path()` utility
3. Update each exporter implementation (tracks, events, statistics, assignments, counts)
4. Update CLI to use explicit components
5. Update tests to use new specification format
6. Remove `MultiExportTracks` (dead code, only in tests)

## Testing

- Unit tests verify `build_export_path()` with multiple dots in filename
- Each exporter test verifies correct output files created with correct names
- Integration test with actual video filename containing multiple dots

## Assumptions

- `export_mode` will continue to be passed via specification
- Exporters can be refactored independently without coordination
- Performance is not affected (no data sharing needed between exports)

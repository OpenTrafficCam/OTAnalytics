# Export Filepath Standardization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate the multi-dot filename truncation bug class (OP#9548) by introducing a shared path-building utility and renaming the misleading `save_path` field in three export specifications to explicit `export_directory: Path` + `export_filename_stem: str`.

**Architecture:** A single utility function `build_export_path(directory, stem, suffix)` centralizes the correct concatenation pattern (`directory / (stem + suffix)`). Three export specifications (`TrackExportSpecification`, `TrackStatisticsExportSpecification`, `ExportSpecification` for road user assignments) are restructured to make the directory + stem distinction explicit. Each exporter exposes its primary file suffix as a class attribute (e.g., `PRIMARY_SUFFIX = ".tracks.csv"`). The CLI passes the directory and stem to specs instead of a pre-built full path; factories use the utility to compose the final path. `EventExportSpecification` and `CountingSpecificationDto` are explicitly left untouched (the former is genuinely a full path; the latter is consumed by OTCloud and would break it).

**Tech Stack:** Python 3.12+, `pathlib.Path`, `dataclasses`, pytest, `uv` package manager.

**Spec reference:** `docs/superpowers/specs/2026-05-08-export-filepath-standardization-design.md`

---

## File Structure

### Files to create
- `OTAnalytics/application/export_path_builder.py` — the new utility module
- `tests/unit/OTAnalytics/application/test_export_path_builder.py` — tests for the utility

### Files to modify
- `OTAnalytics/application/use_cases/track_export.py` — replace `save_path` with `export_directory` + `export_filename_stem` on `TrackExportSpecification`; remove `MultiExportTracks` (Task 7)
- `OTAnalytics/plugin_parser/track_export.py` — `CsvTrackExport.export` uses new fields and the utility; expose `PRIMARY_SUFFIX` and `DERIVED_SUFFIXES`
- `OTAnalytics/application/use_cases/track_statistics_export.py` — replace `save_path` on `TrackStatisticsExportSpecification`; update `CacheTrackStatisticsException` signature
- `OTAnalytics/plugin_parser/track_statistics_export.py` — `TrackStatisticsCsvExporter` exposes `PRIMARY_SUFFIX`; factory builds output file via the utility; `CachedTrackStatisticsExporterFactory` cache key updated
- `OTAnalytics/application/use_cases/road_user_assignment_export.py` — replace `save_path` on `ExportSpecification`; rename `mode` → `export_mode`
- `OTAnalytics/plugin_parser/road_user_assignment_export.py` — `RoadUserAssignmentCsvExporter` exposes `PRIMARY_SUFFIX`; factory builds output file via the utility
- `OTAnalytics/plugin_ui/cli.py` — pass `export_directory` and `export_filename_stem` instead of pre-built full paths; replace inline `parent / (name + suffix)` patterns with `build_export_path()` calls
- `tests/unit/OTAnalytics/plugin_parser/test_track_export.py` — update test to use new fields; add multi-dot regression test
- `tests/unit/OTAnalytics/plugin_parser/test_track_statistics_export.py` (if it exists; otherwise the use_cases version) — update affected tests
- `tests/unit/OTAnalytics/plugin_parser/test_road_user_assignment_export.py` — update affected tests
- `tests/unit/OTAnalytics/application/use_cases/test_track_export.py` — update or delete `TestMultiExportTracks` (Task 7)
- `tests/unit/OTAnalytics/application/use_cases/test_track_statistics_export.py` — update affected tests
- `tests/unit/OTAnalytics/application/use_cases/test_road_user_assignment_export.py` — update affected tests
- `tests/unit/OTAnalytics/plugin_ui/test_cli.py` — update affected tests; pin the multi-dot regression test

---

## Conventions Used in This Plan

- **Tests follow the project pattern:** `@dataclass class Given:` holding all collaborators, a `setup()` (or `setup_default()`) factory, and a `create_target(given)` factory for the system under test. New tests added by this plan must follow this pattern when adding non-trivial test logic.
- **Run tests with `uv run pytest`** — never plain `pytest`.
- **Each task ends with a commit.** Commit messages start with `OP#9548:` (the issue this plan resolves) or `refactor:` for non-bug changes. **Never include `Co-Authored-By` lines** (per the user's saved memory).
- **Type-annotate every signature.** Google-style docstrings on public functions/classes/modules. Imports at top of file, sorted by `isort --profile black`.
- **Constants** for `CONTEXT_FILE_TYPE_*` already exist in `OTAnalytics/application/config.py` and are reused; do not duplicate the literal strings.

---

## Task 1: Add `build_export_path()` Utility

**Why first:** Subsequent tasks depend on this utility being importable and tested.

**Files:**
- Create: `OTAnalytics/application/export_path_builder.py`
- Create: `tests/unit/OTAnalytics/application/test_export_path_builder.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/OTAnalytics/application/test_export_path_builder.py`:

```python
from pathlib import Path

import pytest

from OTAnalytics.application.export_path_builder import build_export_path


class TestBuildExportPath:
    def test_simple_stem(self) -> None:
        result = build_export_path(Path("/output"), "video", ".csv")

        assert result == Path("/output/video.csv")

    def test_stem_with_multiple_dots_is_preserved(self) -> None:
        """Regression test for OP#9548.

        Path.with_suffix() would truncate this stem; build_export_path must not.
        """
        stem = "video.00000_2025-08-28_15-00-00"

        result = build_export_path(Path("/output"), stem, ".tracks.csv")

        assert result == Path(
            "/output/video.00000_2025-08-28_15-00-00.tracks.csv"
        )

    def test_compound_suffix(self) -> None:
        result = build_export_path(
            Path("/output"), "video", ".tracks_metadata.json"
        )

        assert result == Path("/output/video.tracks_metadata.json")

    def test_relative_directory(self) -> None:
        result = build_export_path(Path("data"), "video", ".csv")

        assert result == Path("data/video.csv")

    def test_nested_directory(self) -> None:
        result = build_export_path(
            Path("/output/sub/dir"), "video", ".csv"
        )

        assert result == Path("/output/sub/dir/video.csv")

    def test_empty_stem_raises(self) -> None:
        with pytest.raises(ValueError):
            build_export_path(Path("/output"), "", ".csv")

    def test_suffix_without_leading_dot_raises(self) -> None:
        with pytest.raises(ValueError):
            build_export_path(Path("/output"), "video", "csv")
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/application/test_export_path_builder.py -v
```

Expected: All tests fail with `ModuleNotFoundError: No module named 'OTAnalytics.application.export_path_builder'`.

- [ ] **Step 3: Implement the utility module**

Create `OTAnalytics/application/export_path_builder.py`:

```python
"""Centralized export file path construction.

This module provides the canonical helper for composing export file paths in
OTAnalytics. It exists to prevent recurrence of the multi-dot truncation bug
(OP#9548): ``Path.with_suffix()`` replaces the substring after the last dot, so
applying it to a stem like ``video.00000_2025-08-28_15-00-00`` silently loses
the trailing ``00000_2025-08-28_15-00-00`` portion. Concatenating ``stem`` and
``suffix`` and joining with the parent directory preserves the full stem
regardless of how many dots it contains.
"""

from pathlib import Path


def build_export_path(
    export_directory: Path,
    export_filename_stem: str,
    file_suffix: str,
) -> Path:
    """Build an export file path from directory, stem, and suffix.

    DO NOT use ``Path.with_suffix()`` to attach an extension to an export
    stem. ``with_suffix()`` replaces the substring after the last dot, so a
    stem like ``video.00000_2025-08-28_15-00-00`` becomes ``video`` plus the
    new suffix - silently losing the timestamp portion.

    Args:
        export_directory: Parent directory where the file will be written.
        export_filename_stem: Filename without any extension, possibly
            containing multiple dots (e.g., a timestamped video name). Must
            be non-empty.
        file_suffix: Format suffix to append, including the leading dot
            (e.g., ``".csv"``, ``".tracks_metadata.json"``).

    Returns:
        ``export_directory / (export_filename_stem + file_suffix)``.

    Raises:
        ValueError: If ``export_filename_stem`` is empty or ``file_suffix``
            does not start with a dot.

    Example:
        >>> build_export_path(
        ...     Path("/output"),
        ...     "video.00000_2025-08-28_15-00-00",
        ...     ".tracks.csv",
        ... )
        PosixPath('/output/video.00000_2025-08-28_15-00-00.tracks.csv')
    """
    if not export_filename_stem:
        raise ValueError("export_filename_stem must not be empty")
    if not file_suffix.startswith("."):
        raise ValueError(
            f"file_suffix must start with '.', got {file_suffix!r}"
        )
    return export_directory / (export_filename_stem + file_suffix)
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/application/test_export_path_builder.py -v
```

Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/application/export_path_builder.py \
        tests/unit/OTAnalytics/application/test_export_path_builder.py

git commit -m "OP#9548: Add build_export_path utility to prevent multi-dot truncation"
```

---

## Task 2: Update `TrackExportSpecification` + `CsvTrackExport`

**Goal:** Replace `save_path: Path` with `export_directory: Path` + `export_filename_stem: str` on the spec, expose `PRIMARY_SUFFIX` / `DERIVED_SUFFIXES` on the exporter, and route all path building through `build_export_path`.

**Files:**
- Modify: `OTAnalytics/application/use_cases/track_export.py`
- Modify: `OTAnalytics/plugin_parser/track_export.py`
- Modify: `tests/unit/OTAnalytics/plugin_parser/test_track_export.py`
- Modify: `tests/unit/OTAnalytics/application/use_cases/test_track_export.py` (existing `TestMultiExportTracks` references will need updating; a thorough cleanup happens in Task 7)
- Modify: `tests/unit/OTAnalytics/plugin_ui/test_cli.py` (CLI test for tracks export)

- [ ] **Step 1: Add a failing regression test for `CsvTrackExport`**

Append the following test to `tests/unit/OTAnalytics/plugin_parser/test_track_export.py` (the existing `TestCsvTrackExport` class):

```python
    def test_export_preserves_filename_stem_with_multiple_dots(
        self,
        track_builder: TrackBuilder,
        track_geometry_factory: TRACK_GEOMETRY_FACTORY,
        test_data_tmp_dir: Path,
    ) -> None:
        """Regression test for OP#9548.

        When the filename stem contains multiple dots, all output files
        (.tracks.csv, .tracks_metadata.json, .videos_metadata.json) must
        preserve the full stem.
        """
        mock_tracks_metadata = Mock(spec=TracksMetadata)
        mock_tracks_metadata.to_dict.return_value = {"tracks": "metadata"}
        mock_videos_metadata = Mock(spec=VideosMetadata)
        mock_videos_metadata.to_dict.return_value = {"videos": "metadata"}
        track_builder = append_sample_data(track_builder)
        track_repository = Mock(spec=TrackRepository)
        track_dataset = PandasTrackDataset.from_list(
            tracks=[track_builder.build_track()],
            track_geometry_factory=track_geometry_factory,
        )
        track_repository.get_all.return_value = track_dataset
        use_case = CsvTrackExport(
            track_repository, mock_tracks_metadata, mock_videos_metadata
        )
        stem = "video.00000_2025-08-28_15-00-00"
        specification = TrackExportSpecification(
            export_directory=test_data_tmp_dir,
            export_filename_stem=stem,
            export_format=[TrackFileFormat.CSV],
            export_mode=OVERWRITE,
        )

        use_case.export(specification=specification)

        assert (test_data_tmp_dir / f"{stem}.tracks.csv").exists()
        assert (test_data_tmp_dir / f"{stem}.tracks_metadata.json").exists()
        assert (test_data_tmp_dir / f"{stem}.videos_metadata.json").exists()
```

Also update the existing `test_export` in the same class — replace `save_path=export_file` with the new fields:

```python
        export_file_stem = "exported_tracks"
        actual_file = test_data_tmp_dir / f"{export_file_stem}.tracks.csv"
        specification = TrackExportSpecification(
            export_directory=test_data_tmp_dir,
            export_filename_stem=export_file_stem,
            export_format=[TrackFileFormat.CSV],
            export_mode=OVERWRITE,
        )
```

(Remove the now-unused `export_file = test_data_tmp_dir / "exported_tracks"` line and replace it with the stem-only variant.)

- [ ] **Step 2: Run the new test to confirm it fails**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_track_export.py -v
```

Expected: `test_export_preserves_filename_stem_with_multiple_dots` fails with `TypeError: __init__() got an unexpected keyword argument 'export_directory'` (the spec still uses `save_path`). The other test will fail similarly.

- [ ] **Step 3: Update `TrackExportSpecification`**

In `OTAnalytics/application/use_cases/track_export.py`, replace lines 17–21:

```python
@dataclass(frozen=True)
class TrackExportSpecification:
    export_directory: Path
    export_filename_stem: str
    export_format: list[TrackFileFormat]
    export_mode: ExportMode
```

(Keep all other content in the file unchanged for now; `MultiExportTracks` is removed in Task 7.)

- [ ] **Step 4: Update `CsvTrackExport` to use the new fields and the utility**

In `OTAnalytics/plugin_parser/track_export.py`, add an import at the top (preserving import groups):

```python
from OTAnalytics.application.export_path_builder import build_export_path
```

Replace the `CsvTrackExport.export` method (lines 46–65) with:

```python
    PRIMARY_SUFFIX = ".tracks.csv"
    DERIVED_SUFFIXES = (".tracks_metadata.json", ".videos_metadata.json")

    def export(self, specification: TrackExportSpecification) -> None:
        self._update_iterative_metadata()

        append = specification.export_mode.is_subsequent_write()
        dataframe = self._get_data()
        dataframe = set_column_order(dataframe)
        output_path = build_export_path(
            specification.export_directory,
            specification.export_filename_stem,
            self.PRIMARY_SUFFIX,
        )
        write_mode: Literal["w", "a"] = "a" if append else "w"
        dataframe.to_csv(
            output_path, index=False, header=not append, mode=write_mode
        )

        if specification.export_mode.is_final_write():
            tracks_metadata_path = build_export_path(
                specification.export_directory,
                specification.export_filename_stem,
                ".tracks_metadata.json",
            )
            write_json(self._iterative_tracks_metadata, tracks_metadata_path)

            videos_metadata_path = build_export_path(
                specification.export_directory,
                specification.export_filename_stem,
                ".videos_metadata.json",
            )
            write_json(self._iterative_videos_metadata, videos_metadata_path)

            self._iterative_tracks_metadata.clear()
            self._iterative_videos_metadata.clear()
```

(`PRIMARY_SUFFIX` / `DERIVED_SUFFIXES` are class attributes placed at the top of the class body; insert them right after the class docstring on line 27.)

- [ ] **Step 5: Update CLI `_do_export_tracks` to construct the spec with new fields**

In `OTAnalytics/plugin_ui/cli.py`, replace the `_do_export_tracks` method (lines 346–355):

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
            export_format=[TrackFileFormat.CSV, TrackFileFormat.OTTRK],
            export_mode=export_mode,
        )
        await asyncio.to_thread(self._export_tracks.export, specification)
        logger().info("Finished tracks export")
        await self._after_track_export(export_directory, export_filename_stem)

    async def _after_track_export(
        self, export_directory: Path, export_filename_stem: str
    ) -> None:
        """Hook to execute after tracks export."""
        pass
```

Also update the call site in `_export_analysis` (line 180). Find:

```python
        if self._run_config.do_export_tracks:
            await self._do_export_tracks(save_base_path, export_mode)
```

Replace with:

```python
        if self._run_config.do_export_tracks:
            await self._do_export_tracks(
                self._run_config.save_dir,
                self._run_config.save_stem,
                export_mode,
            )
```

- [ ] **Step 6: Update the CLI test for tracks export**

In `tests/unit/OTAnalytics/plugin_ui/test_cli.py`, find any test that calls `cli._do_export_tracks(save_path, ...)` and update it to pass `(directory, stem, ...)` instead. Search for `_do_export_tracks(`. Update each invocation analogously to the test in Step 1.

If a multi-dot regression test does not yet exist for `_do_export_tracks` in `test_cli.py`, add one following the pattern of `test_do_export_track_statistics_preserves_filename_with_multiple_dots` (already present near line 1095). The new test asserts that the CLI calls `self._export_tracks.export` with a `TrackExportSpecification` containing the unmangled stem.

Concrete code for the new test (place near other `test_do_export_*_preserves_filename_with_multiple_dots` tests):

```python
    @pytest.mark.asyncio
    @pytest.mark.parametrize("mode", [CliMode.STREAM, CliMode.BULK])
    async def test_do_export_tracks_preserves_filename_with_multiple_dots(
        self,
        mode: CliMode,
        test_data_tmp_dir: Path,
        mock_cli_stream_dependencies: dict[str, Mock],
        mock_cli_bulk_dependencies: dict[str, Mock],
    ) -> None:
        filename_with_dots = (
            "first5min_FOOBAR1234_1998_04_26-1500.00000_1998-04-26_15-00-00"
        )
        if mode == CliMode.STREAM:
            dependencies = mock_cli_stream_dependencies
        else:
            dependencies = mock_cli_bulk_dependencies

        run_config = Mock()
        cli: OTAnalyticsCli = self.init_cli_with(
            mode, dependencies, dependencies, run_config
        )

        await cli._do_export_tracks(
            test_data_tmp_dir, filename_with_dots, OVERWRITE
        )

        expected_specification = TrackExportSpecification(
            export_directory=test_data_tmp_dir,
            export_filename_stem=filename_with_dots,
            export_format=[TrackFileFormat.CSV, TrackFileFormat.OTTRK],
            export_mode=OVERWRITE,
        )
        dependencies[self.EXPORT_TRACKS].export.assert_called_with(
            expected_specification
        )
```

- [ ] **Step 7: Update `TestMultiExportTracks` in `tests/unit/OTAnalytics/application/use_cases/test_track_export.py`**

The existing tests construct `TrackExportSpecification(save_path=...)`. Find each occurrence and replace with the new field names. Use `export_directory=Path("/some/dir")` and `export_filename_stem="some_stem"` to keep the tests deterministic. (These tests will be removed entirely in Task 7 if you elect that optional cleanup.)

- [ ] **Step 8: Run all affected tests**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_track_export.py \
              tests/unit/OTAnalytics/application/use_cases/test_track_export.py \
              tests/unit/OTAnalytics/plugin_ui/test_cli.py -v
```

Expected: All tests PASS, including the new multi-dot regression tests.

- [ ] **Step 9: Commit**

```bash
git add OTAnalytics/application/use_cases/track_export.py \
        OTAnalytics/plugin_parser/track_export.py \
        OTAnalytics/plugin_ui/cli.py \
        tests/unit/OTAnalytics/plugin_parser/test_track_export.py \
        tests/unit/OTAnalytics/application/use_cases/test_track_export.py \
        tests/unit/OTAnalytics/plugin_ui/test_cli.py

git commit -m "OP#9548: Replace save_path with export_directory + export_filename_stem on TrackExportSpecification"
```

---

## Task 3: Update `TrackStatisticsExportSpecification` + Factories + Exporter

**Goal:** Same field rename, plus push the `.track_statistics.csv` suffix knowledge from the CLI into the exporter.

**Files:**
- Modify: `OTAnalytics/application/use_cases/track_statistics_export.py`
- Modify: `OTAnalytics/plugin_parser/track_statistics_export.py`
- Modify: `OTAnalytics/plugin_ui/cli.py`
- Modify: `tests/unit/OTAnalytics/application/use_cases/test_track_statistics_export.py`
- Modify: `tests/unit/OTAnalytics/plugin_ui/test_cli.py`

- [ ] **Step 1: Add a failing regression test**

In `tests/unit/OTAnalytics/plugin_ui/test_cli.py`, the existing `test_do_export_track_statistics_preserves_filename_with_multiple_dots` test expects:

```python
        expected_specification = TrackStatisticsExportSpecification(
            save_path=expected_track_statistics_path,
            format="CSV",
            export_mode=OVERWRITE,
        )
```

Update it to assert the new fields:

```python
        expected_specification = TrackStatisticsExportSpecification(
            export_directory=test_data_tmp_dir,
            export_filename_stem=filename_with_dots,
            format="CSV",
            export_mode=OVERWRITE,
        )
```

Also update the test to drop `expected_track_statistics_path`. Update the call:

```python
        await cli._do_export_track_statistics(
            test_data_tmp_dir, filename_with_dots, OVERWRITE
        )
```

- [ ] **Step 2: Run the test to confirm it fails**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/test_cli.py::TestOTAnalyticsCli::test_do_export_track_statistics_preserves_filename_with_multiple_dots -v
```

Expected: FAIL with `TypeError: __init__() got an unexpected keyword argument 'export_directory'`.

- [ ] **Step 3: Update `TrackStatisticsExportSpecification`**

In `OTAnalytics/application/use_cases/track_statistics_export.py`, replace lines 84–88:

```python
@dataclass(frozen=True)
class TrackStatisticsExportSpecification:
    export_directory: Path
    export_filename_stem: str
    format: str
    export_mode: ExportMode
```

Update `CacheTrackStatisticsException.__init__` (lines 75–86) — its signature uses `save_path: Path`. Replace:

```python
class CacheTrackStatisticsException(Exception):

    def __init__(
        self,
        message: str,
        export_directory: Path,
        export_filename_stem: str,
        format: str,
        export_mode: ExportMode,
    ) -> None:
        super().__init__(
            message
            + f"Error occurred when exporting {format} to "
            + f"{export_directory}/{export_filename_stem} using "
            + f"export mode {export_mode}"
        )
```

(Note the f-string fix: the existing message had `{export_mode}` inside a non-f-string concatenation, so the actual mode never interpolated. Restore the leading `f` on that line as shown.)

- [ ] **Step 4: Update `CachedTrackStatisticsExporterFactory`**

In `OTAnalytics/plugin_parser/track_statistics_export.py`, the cache key uses `(specification.save_path, specification.format)`. Replace it (around lines 89–137) with a key based on the new fields:

```python
class CachedTrackStatisticsExporterFactory(TrackStatisticsExporterFactory):

    def __init__(self, other: TrackStatisticsExporterFactory) -> None:
        self.other = other
        self._cache: dict[tuple[Path, str, str], TrackStatisticsExporter] = (
            dict()
        )

    def get_supported_formats(self) -> Iterable[ExportFormat]:
        return self.other.get_supported_formats()

    def create(
        self, specification: TrackStatisticsExportSpecification
    ) -> TrackStatisticsExporter:
        export_mode = specification.export_mode

        key = (
            specification.export_directory,
            specification.export_filename_stem,
            specification.format,
        )
        key_exists = key in self._cache.keys()

        exporter: TrackStatisticsExporter
        if export_mode.is_first_write():
            if key_exists:
                raise CacheTrackStatisticsException(
                    "TrackStatisticsExporter already exists for format+file"
                    " upon first write!"
                    " Maybe previous export was not finished or cache was not"
                    " cleared properly.",
                    specification.export_directory,
                    specification.export_filename_stem,
                    specification.format,
                    export_mode,
                )

            exporter = self.other.create(specification)
            self._cache[key] = exporter

        else:
            if not key_exists:
                raise CacheTrackStatisticsException(
                    "TrackStatisticsExporter missing in cache for format+file"
                    " upon subsequent write!"
                    " Maybe the cache was cleared too early.",
                    specification.export_directory,
                    specification.export_filename_stem,
                    specification.format,
                    export_mode,
                )
            exporter = self._cache[key]

        if export_mode.is_final_write():
            del self._cache[key]

        return exporter
```

- [ ] **Step 5: Update `TrackStatisticsCsvExporter` and `SimpleTrackStatisticsExporterFactory`**

Add `PRIMARY_SUFFIX` to `TrackStatisticsCsvExporter` and have the factory build the output file via the utility.

At the top of `OTAnalytics/plugin_parser/track_statistics_export.py`, add imports:

```python
from OTAnalytics.application.config import CONTEXT_FILE_TYPE_TRACK_STATISTICS
from OTAnalytics.application.export_path_builder import build_export_path
```

Update the class (replacing lines 19–30):

```python
class TrackStatisticsCsvExporter(TrackStatisticsExporter):
    PRIMARY_SUFFIX = f".{CONTEXT_FILE_TYPE_TRACK_STATISTICS}.csv"

    @property
    def format(self) -> ExportFormat:
        return ExportFormat("csv", ".csv")

    def _serialize(self, dtos: dict) -> None:
        logger().info(f"Exporting track statistics to {self._outputfile}")

        DataFrame([dtos]).to_csv(self._outputfile, index=False)

        logger().info(f"Track statistics saved at {self._outputfile}")
```

Update `SimpleTrackStatisticsExporterFactory.create` (around lines 56–70). Replace the `create` method body:

```python
    def create(
        self, specification: TrackStatisticsExportSpecification
    ) -> TrackStatisticsExporter:
        """
        Create the exporter for the given track statistic export specification.

        Args:
            specification (TrackStatisticsExportSpecification): specification of
                the Exporter.

        Returns:
            TrackStatisticsExporter: Exporter to export track statistics.
        """
        output_file = build_export_path(
            specification.export_directory,
            specification.export_filename_stem,
            TrackStatisticsCsvExporter.PRIMARY_SUFFIX,
        )
        return self._factories[specification.format](
            TrackStatisticsBuilder(), output_file
        )
```

(The `_formats` dict and lambda factory function stay unchanged.)

- [ ] **Step 6: Update the CLI `_do_export_track_statistics`**

In `OTAnalytics/plugin_ui/cli.py`, replace the method (around lines 361–377):

```python
    async def _do_export_track_statistics(
        self,
        export_directory: Path,
        export_filename_stem: str,
        export_mode: ExportMode,
    ) -> None:
        logger().info("Create track statistics ...")
        specification = TrackStatisticsExportSpecification(
            export_directory=export_directory,
            export_filename_stem=export_filename_stem,
            format="CSV",
            export_mode=export_mode,
        )
        await asyncio.to_thread(
            self._export_track_statistics.export, specification
        )
        track_statistics_path = build_export_path(
            export_directory,
            export_filename_stem,
            TrackStatisticsCsvExporter.PRIMARY_SUFFIX,
        )
        await self._after_track_statistics_export(track_statistics_path)
```

Add the imports needed for this change (top of file):

```python
from OTAnalytics.application.export_path_builder import build_export_path
from OTAnalytics.plugin_parser.track_statistics_export import (
    TrackStatisticsCsvExporter,
)
```

Update the call site in `_export_analysis` (line 183):

```python
        if self._run_config.do_export_track_statistics:
            await self._do_export_track_statistics(
                self._run_config.save_dir,
                self._run_config.save_stem,
                export_mode,
            )
```

(Note: importing `TrackStatisticsCsvExporter` from `plugin_parser` into `plugin_ui` is a layering concession we accept here so the CLI can derive the after-export hook path. An alternative — passing the suffix as a constant — is acceptable too, but the import keeps a single source of truth for the suffix.)

- [ ] **Step 7: Update existing tests for `TrackStatisticsExportSpecification`**

Search `tests/unit/OTAnalytics/application/use_cases/test_track_statistics_export.py` and replace every `TrackStatisticsExportSpecification(save_path=...)` with the new fields. Use `export_directory=test_data_tmp_dir` and `export_filename_stem="track_statistics_test"` (or similar) where the tests previously used a full path.

Where tests previously asserted `specification.save_path`, assert on `specification.export_directory` and `specification.export_filename_stem` instead.

If `CachedTrackStatisticsExporterFactory` has tests, update them to use the new cache-key tuple.

- [ ] **Step 8: Run all affected tests**

```bash
uv run pytest tests/unit/OTAnalytics/application/use_cases/test_track_statistics_export.py \
              tests/unit/OTAnalytics/plugin_parser/test_track_statistics_export.py \
              tests/unit/OTAnalytics/plugin_ui/test_cli.py -v
```

(`test_track_statistics_export.py` may not exist under `plugin_parser/`; if so, that path is silently skipped — the use_cases path is the canonical one.)

Expected: All tests PASS. The multi-dot CLI regression test passes against the updated spec fields.

- [ ] **Step 9: Commit**

```bash
git add OTAnalytics/application/use_cases/track_statistics_export.py \
        OTAnalytics/plugin_parser/track_statistics_export.py \
        OTAnalytics/plugin_ui/cli.py \
        tests/unit/OTAnalytics/application/use_cases/test_track_statistics_export.py \
        tests/unit/OTAnalytics/plugin_ui/test_cli.py

git commit -m "OP#9548: Replace save_path with export_directory + export_filename_stem on TrackStatisticsExportSpecification"
```

---

## Task 4: Update `ExportSpecification` (road user) + Factory + Exporter; rename `mode` → `export_mode`

**Goal:** Apply the same restructuring to road user assignment exports, and harmonize the `mode` field name with the rest of the codebase.

**Files:**
- Modify: `OTAnalytics/application/use_cases/road_user_assignment_export.py`
- Modify: `OTAnalytics/plugin_parser/road_user_assignment_export.py`
- Modify: `OTAnalytics/plugin_ui/cli.py`
- Modify: `tests/unit/OTAnalytics/application/use_cases/test_road_user_assignment_export.py`
- Modify: `tests/unit/OTAnalytics/plugin_parser/test_road_user_assignment_export.py`
- Modify: `tests/unit/OTAnalytics/plugin_ui/test_cli.py`

- [ ] **Step 1: Update `ExportSpecification`**

In `OTAnalytics/application/use_cases/road_user_assignment_export.py`, replace lines 213–217:

```python
@dataclass(frozen=True)
class ExportSpecification:
    export_directory: Path
    export_filename_stem: str
    format: str
    export_mode: ExportMode
```

Update `ExportRoadUserAssignments.export` (around lines 255–258) to use the renamed field:

```python
    def export(self, specification: ExportSpecification) -> None:
        road_user_assignments = self._get_all_assignments.get()
        exporter = self._exporter_factory.create(specification)
        exporter.export(road_user_assignments, specification.export_mode)
```

- [ ] **Step 2: Update `SimpleRoadUserAssignmentExporterFactory` and `RoadUserAssignmentCsvExporter`**

In `OTAnalytics/plugin_parser/road_user_assignment_export.py`, add imports (at the top, in the proper isort group):

```python
from OTAnalytics.application.config import CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS
from OTAnalytics.application.export_path_builder import build_export_path
```

Replace the class definition (lines 19–36):

```python
class RoadUserAssignmentCsvExporter(RoadUserAssignmentExporter):
    """
    A RoadUserAssignmentExporter exporting to .csv format.
    Allows to either overwrite or append data to the excel file.
    Export modes OVERWRITE and INITIAL_MERGE will write the column header.
    Other export modes will only append data.
    """

    PRIMARY_SUFFIX = f".{CONTEXT_FILE_TYPE_ROAD_USER_ASSIGNMENTS}.csv"

    @property
    def format(self) -> ExportFormat:
        return ExportFormat("csv", ".csv")

    def _serialize(self, dtos: list[dict], export_mode: ExportMode) -> None:
        append = export_mode.is_subsequent_write()
        write_mode: Literal["w", "a"] = "a" if append else "w"
        DataFrame(dtos, columns=ROAD_USER_ASSIGNMENT_DICT_KEYS).to_csv(
            self._outputfile, index=False, header=not append, mode=write_mode
        )
```

Replace `SimpleRoadUserAssignmentExporterFactory.create` (around lines 66–78):

```python
    def create(self, specification: ExportSpecification) -> RoadUserAssignmentExporter:
        """
        Create the exporter for the given road user assignment export specification.

        Args:
            specification (ExportSpecification): specification of the Exporter.

        Returns:
            RoadUserAssignmentExporter: Exporter to export road user assignments.
        """
        output_file = build_export_path(
            specification.export_directory,
            specification.export_filename_stem,
            RoadUserAssignmentCsvExporter.PRIMARY_SUFFIX,
        )
        return self._factories[specification.format](
            RoadUserAssignmentBuilder(), output_file
        )
```

- [ ] **Step 3: Update CLI for road user assignment export**

In `OTAnalytics/plugin_ui/cli.py`, the `_export_events` method currently builds a full assignment path inline. Replace lines 287–297:

```python
        specification = ExportSpecification(
            export_directory=save_path.parent,
            export_filename_stem=save_path.name,
            format=CSV_FORMAT.name,
            export_mode=export_mode,
        )
        await asyncio.to_thread(
            self._export_road_user_assignments.export, specification
        )
        assignment_path = build_export_path(
            save_path.parent,
            save_path.name,
            RoadUserAssignmentCsvExporter.PRIMARY_SUFFIX,
        )
        logger().info(f"Road user assignment saved at '{assignment_path}'")
        await self._after_road_user_assignment_export(assignment_path)
```

Add an import at the top of `cli.py`:

```python
from OTAnalytics.plugin_parser.road_user_assignment_export import (
    CSV_FORMAT,
    RoadUserAssignmentCsvExporter,
)
```

(The existing `CSV_FORMAT` import remains; we just make sure `RoadUserAssignmentCsvExporter` is also imported.)

Note: `_export_events` receives `save_path: Path` from `_export_analysis`. Inside the method, `save_path.parent` is the directory and `save_path.name` is the stem. Keep this pattern within `_export_events` for now; do not refactor the `_export_events` signature in this task to avoid scope creep. (Task 5 handles full CLI cleanup.)

- [ ] **Step 4: Update existing tests for `ExportSpecification`**

In `tests/unit/OTAnalytics/application/use_cases/test_road_user_assignment_export.py`, find every `ExportSpecification(save_path=..., format=..., mode=...)` and replace with the new fields. Specifically, line 139's `specification.save_path = Mock()` needs to become `specification.export_directory = Mock()` plus a corresponding `specification.export_filename_stem = "..."`.

In `tests/unit/OTAnalytics/plugin_parser/test_road_user_assignment_export.py`, the test on line 31 builds `save_path = test_data_tmp_dir / "road_user_assignments.csv"` and passes it to the exporter constructor. The exporter's constructor still takes `output_file: Path`, so this test is unchanged at the exporter level — the only change is if the test exercises the factory. If not, it remains as-is. Verify with:

```bash
uv run pytest tests/unit/OTAnalytics/plugin_parser/test_road_user_assignment_export.py -v
```

If failing, it is most likely because the tests use `mode=` (the old field name). Update any such usage to `export_mode=`.

- [ ] **Step 5: Run all affected tests**

```bash
uv run pytest tests/unit/OTAnalytics/application/use_cases/test_road_user_assignment_export.py \
              tests/unit/OTAnalytics/plugin_parser/test_road_user_assignment_export.py \
              tests/unit/OTAnalytics/plugin_ui/test_cli.py -v
```

Expected: All tests PASS. Existing road user assignment tests continue to work; the renamed `mode` → `export_mode` field is correctly referenced everywhere.

- [ ] **Step 6: Commit**

```bash
git add OTAnalytics/application/use_cases/road_user_assignment_export.py \
        OTAnalytics/plugin_parser/road_user_assignment_export.py \
        OTAnalytics/plugin_ui/cli.py \
        tests/unit/OTAnalytics/application/use_cases/test_road_user_assignment_export.py \
        tests/unit/OTAnalytics/plugin_parser/test_road_user_assignment_export.py \
        tests/unit/OTAnalytics/plugin_ui/test_cli.py

git commit -m "OP#9548: Replace save_path with export_directory + export_filename_stem on ExportSpecification (road user)"
```

---

## Task 5: Replace inline `parent / (name + suffix)` in CLI events and counts paths

**Goal:** All inline path-building patterns in `cli.py` route through `build_export_path()`, leaving a single canonical implementation in the codebase.

**Files:**
- Modify: `OTAnalytics/plugin_ui/cli.py`

- [ ] **Step 1: Confirm current state of inline patterns**

Search `cli.py` for the inline pattern:

```bash
grep -n "save_path.parent / (" OTAnalytics/plugin_ui/cli.py
```

Expected matches: events (lines around 272), counts (lines around 325). The earlier tasks already removed the road user assignment and track statistics inlines.

- [ ] **Step 2: Replace events path building**

Locate `_export_events` (around line 262). Replace the inline path build (lines 272–274):

```python
            actual_save_path = build_export_path(
                save_path.parent,
                save_path.name,
                f".events{event_list_exporter.get_extension()}",
            )
```

- [ ] **Step 3: Replace counts path building**

Locate `_do_export_counts` (around line 309). Replace the inline path build (lines 325–328):

```python
            output_file = build_export_path(
                save_path.parent,
                save_path.name,
                f".{CONTEXT_FILE_TYPE_COUNTS}_{count_interval}"
                f"{DEFAULT_COUNT_INTERVAL_TIME_UNIT}.{DEFAULT_COUNTS_FILE_TYPE}",
            )
```

- [ ] **Step 4: Run the full CLI test suite**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/test_cli.py -v
```

Expected: All tests PASS, including the existing `test_do_export_counts_preserves_filename_with_multiple_dots`.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/plugin_ui/cli.py

git commit -m "refactor: Route CLI inline export path building through build_export_path"
```

---

## Task 6: Final Integration Verification (manual)

**Goal:** Reproduce the original failing scenario end-to-end and confirm all output files preserve the timestamped stem.

**Files:** None modified. Manual run.

- [ ] **Step 1: Run the full unit test suite**

```bash
uv run pytest -x --timeout=120 tests/unit/OTAnalytics -q
```

Expected: 0 failures.

- [ ] **Step 2: Reproduce the original failing CLI command**

The reference reproduction (from the bug report):

```bash
rm -rf /Users/rseng/temp/incomplete-filenames-if-video-name-has-multiple-dots/output_of_pipeline \
       /Users/rseng/temp/incomplete-filenames-if-video-name-has-multiple-dots/logs

uv run -m OTAnalytics --cli --track-export --track-statistics-export \
    --config /Users/rseng/temp/incomplete-filenames-if-video-name-has-multiple-dots/first5min_MIOP001048_2025_08_28-1500.00000_2025-08-28_15-00-00.otconfig
```

If the test fixture directory does not exist on this machine, skip Step 2 and rely on the unit-test suite plus the regression tests added in Task 2 / Task 3.

- [ ] **Step 3: Verify all generated output files preserve the full stem**

```bash
ls /Users/rseng/temp/incomplete-filenames-if-video-name-has-multiple-dots \
    | grep -E '\.(tracks\.csv|tracks_metadata\.json|videos_metadata\.json|track_statistics\.csv|road_user_assignments\.csv|events\.csv|counts_15min\.csv)$'
```

Expected: Every matching output file name starts with `first5min_MIOP001048_2025_08_28-1500.00000_2025-08-28_15-00-00`. None should truncate after `1500`.

- [ ] **Step 4: No commit needed.**

This is a verification step. If any output file is still truncated, return to the relevant task and identify the missed code path before proceeding.

---

## Task 7 (Optional): Remove `MultiExportTracks` Dead Code

**Goal:** Remove unused class. Independent of the bug fix; can be skipped or done in a follow-up.

**Files:**
- Modify: `OTAnalytics/application/use_cases/track_export.py` (delete `MultiExportTracks` class)
- Modify: `tests/unit/OTAnalytics/application/use_cases/test_track_export.py` (delete `TestMultiExportTracks`)

- [ ] **Step 1: Verify `MultiExportTracks` is unused outside its tests**

```bash
grep -rn "MultiExportTracks" OTAnalytics --include="*.py"
grep -rn "MultiExportTracks" tests --include="*.py"
```

Expected: Only references should be the class definition + the test class. No production import.

- [ ] **Step 2: Delete `MultiExportTracks` from `OTAnalytics/application/use_cases/track_export.py`**

Remove lines 33–57 (the `class MultiExportTracks(...)` block).

- [ ] **Step 3: Delete `TestMultiExportTracks` from `tests/unit/OTAnalytics/application/use_cases/test_track_export.py`**

Remove the entire `class TestMultiExportTracks` block and any imports that become unused (`MultiExportTracks` itself).

- [ ] **Step 4: Run the test suite to confirm nothing broke**

```bash
uv run pytest tests/unit/OTAnalytics/application/use_cases/test_track_export.py -v
```

Expected: PASS (or "no tests collected" if `TestMultiExportTracks` was the only class — fine).

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/application/use_cases/track_export.py \
        tests/unit/OTAnalytics/application/use_cases/test_track_export.py

git commit -m "refactor: Remove unused MultiExportTracks"
```

---

## Self-Review (run before declaring complete)

After all tasks complete, run the self-review checks below.

- [ ] **Spec coverage scan**

For each requirement in `docs/superpowers/specs/2026-05-08-export-filepath-standardization-design.md`:

| Spec section | Implemented in |
|---|---|
| §1 Shared utility | Task 1 |
| §2 `TrackExportSpecification` rename | Task 2 |
| §2 `TrackStatisticsExportSpecification` rename | Task 3 |
| §2 `ExportSpecification` (road user) rename | Task 4 |
| §3 `CsvTrackExport` updates | Task 2 |
| §3 `TrackStatisticsCsvExporter` updates | Task 3 |
| §3 `RoadUserAssignmentCsvExporter` updates | Task 4 |
| §4 CLI updates (tracks, statistics) | Tasks 2, 3 |
| §4 CLI updates (events, counts) | Task 5 |
| §5 `mode` → `export_mode` rename | Task 4 |
| §6 Remove `MultiExportTracks` | Task 7 (optional) |
| Out-of-scope: `EventExportSpecification`, `CountingSpecificationDto` | NOT modified — confirmed by `git diff main -- OTAnalytics/application/use_cases/export_events.py OTAnalytics/application/analysis/traffic_counting_specification.py` returning empty |

- [ ] **Run the full unit test suite**

```bash
uv run pytest -x --timeout=120 tests/unit/OTAnalytics -q
```

Expected: 0 failures.

- [ ] **Confirm OTCloud impact is zero**

```bash
git diff main -- OTAnalytics/application/use_cases/export_events.py \
                 OTAnalytics/application/analysis/traffic_counting_specification.py
```

Expected: empty diff. Both files are out of scope and remain untouched.

- [ ] **Manual smoke test (if Task 6 was skipped)**

Re-run the original reproduction command from Task 6 Step 2 and verify file names.

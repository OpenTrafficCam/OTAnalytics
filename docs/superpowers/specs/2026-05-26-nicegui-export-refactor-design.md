# NiceGUI export refactor — design

**Date:** 2026-05-26
**Branch:** `bug/9548-incomplete-filenames-in-otanalytics-if-video-name-has-multiple-dots`
**Ticket:** OP#9548
**Status:** Design approved; awaiting implementation plan.

## Background

Commit `8d89b20b` refactored the export pipeline to specify outputs as
`(export_directory, export_filename_stem, export_format_extension, export_format)`
instead of an explicit file `Path`. Exporters now compose the final filename
themselves as:

```
<export_directory>/<export_filename_stem>.<CONTEXT_FILE_TYPE>.<extension>
```

For counts the context is dynamic: `counts_<interval>min`.

The CustomTkinter UI (`ctk_ui_factory.py`, `toplevel_export_file.py`,
`toplevel_export_counts.py`) was updated alongside the refactor: after the user
selects a file, the CTK code strips `.<CONTEXT>.<EXT>` from the chosen name and
hands a stem back to the new DTOs.

The NiceGUI UI was *partially* updated and is currently broken:

- `NiceGuiUiFactory.configure_export_file` calls
  `ExportFileDto.from_file_path(...)`, which sets `file_stem = path.stem`. For a
  filename like `mydata.events.csv` this stores `mydata.events` as the stem;
  the exporter then appends `.events.csv` again, producing
  `mydata.events.events.csv`.
- `ExportCountsDialog.get_specification()` still passes
  `output_file=...` to `CountingSpecificationDto`, but that field no longer
  exists on the DTO — counts export blows up on instantiation.
- Both `configure_export_file` and `configure_export_counts` raise
  `CancelAddFlow` on cancel, but the dummy viewmodel handles `CancelExportFile`
  and `CancelExportCounts` respectively; the cancellation exception is never
  caught.
- `ExportCountsDialog.get_selected_filename` is annotated `-> str` but returns
  a `Path`.

In addition, the NiceGUI side is allowed to add a stronger guarantee than the
CTK side: the user must not be able to *enter* a filename that fails to end
with `<CONTEXT_FILE_TYPE>.<extension>`. CTK strips the suffix after-the-fact;
NiceGUI will make the suffix structurally inviolable.

## Goal

Adapt the NiceGUI export flows to the refactored DTO contract and enforce — in
the UI itself — that exported filenames always end with the context-aware
suffix.

## Non-goals

- No changes to `ExportFileDto`, `CountingSpecificationDto`, or any exporter
  implementation. The contract introduced by the refactor stands as-is.
- No changes to the CustomTkinter UI.
- No renaming or relocating of `FileChooserDialog` test markers
  (`MARKER_FORMAT`, `MARKER_FILENAME`, `MARKER_DIRECTORY`).

## Filename contract recap

| Export | Final filename pattern |
| --- | --- |
| Events | `<stem>.events.<ext>` |
| Road user assignments | `<stem>.road_user_assignments.<ext>` |
| Track statistics | `<stem>.track_statistics.<ext>` |
| Counts | `<stem>.counts_<interval>min.<ext>` |
| otconfig (plain save) | `<stem>.otconfig` |
| otflow (plain save) | `<stem>.otflow` |

## Design

### Approach: locked-suffix UI

Replace the single editable filename field with **a stem field + a non-editable
suffix badge**. The badge displays the part that must remain, and updates
automatically when the format dropdown (or, for counts, the interval) changes.
The user can only edit the stem; the constraint becomes structurally
impossible to violate.

This is preferred over validation-on-submit because:

- The constraint is communicated visually to the user.
- There is no validation predicate to keep in sync with the exporter code.
- It does not silently rewrite user input on submit (which Approach C would).

### `FileChooserDialog` — three modes

`FileChooserDialog` is shared by three callers in `NiceGuiUiFactory`. It gains
two parameters to express *which* lock applies:

```python
FileChooserDialog(
    ...,
    context_file_type: str = "",
    enforce_suffix: bool = True,
)
```

| Caller | `enforce_suffix` | `context_file_type` | Locked suffix shown |
| --- | --- | --- | --- |
| `askopenfilename` | `False` | `""` | none (legacy field) |
| `ask_for_save_file_path` | `True` | `""` | `.<ext>` (format-driven) |
| `configure_export_file` | `True` | non-empty | `.<context>.<ext>` |

Internals:

- New `_filename_stem_field: FormFieldText` (initial value = `initial_file_stem`).
- New `_filename_suffix_field`: read-only `ui.input` styled as a chip (preferred
  over `ui.label` because NiceGUI styles read-only inputs consistently with the
  editable one beside them, preserving visual alignment).
- `_build_locked_suffix() -> str`: returns `f".{self._context_file_type}{ext}"`
  when `context_file_type` is non-empty, otherwise `ext`. `ext` is normalised
  with `ensure_dot_in_extension`.
- `_update_file_extension` updates the suffix badge only; the stem is
  preserved.
- `_browse_directory`, on file pick, strips the matching suffix from the
  picked name via `strip_extension` from `adapter_ui.helpers`. If the suffix
  doesn't match, fall back to `Path(name).stem` so we never silently mutate the
  wrong characters.
- New accessors:
  - `get_file_stem() -> str` — raw stem (no suffix).
  - `get_export_format_extension() -> str` — leading-dot extension.
  - `get_directory() -> Path`.
- `get_file_path() -> Path` composes `directory / (stem + suffix)` when
  `enforce_suffix`, otherwise the existing `directory / filename`.

### `ExportCountsDialog` — same pattern

`ExportCountsDialog` does not share `FileChooserDialog`, but applies the same
shape:

- Stem field + locked suffix badge.
- Suffix expression:
  `f".{CONTEXT_FILE_TYPE_COUNTS}_{interval}{DEFAULT_COUNT_INTERVAL_TIME_UNIT}{ext}"`.
- Subscribe `on_value_change` on both the interval field and the format
  dropdown so the badge updates live.
- Seed the stem from `viewmodel.get_save_path_suggestion(...)` with the context
  portion stripped via `strip_extension`.

### Factory wiring

#### `configure_export_file`

```python
async def configure_export_file(
    self,
    title: str,
    export_format_extensions: dict[str, str],
    context_file_type: str,
    viewmodel: ViewModel,
) -> ExportFileDto:
    default_ext = next(iter(export_format_extensions.values())).lstrip(".")
    suggestion = viewmodel.get_save_path_suggestion(default_ext, context_file_type)
    initial_stem = strip_extension(suggestion.stem, f".{context_file_type}")
    dialog = FileChooserDialog(
        resource_manager=self._resource_manager,
        title=title,
        file_extensions=export_format_extensions,
        initial_file_stem=initial_stem,
        initial_dir=suggestion.parent,
        context_file_type=context_file_type,
        enforce_suffix=True,
    )
    result = await dialog.result
    if result == DialogResult.APPLY:
        return ExportFileDto(
            export_directory=dialog.get_directory(),
            file_stem=dialog.get_file_stem(),
            export_format_extension=dialog.get_export_format_extension(),
            export_format=dialog.get_format(),
        )
    raise CancelExportFile()
```

The DTO is constructed directly from typed accessors; `ExportFileDto.from_file_path`
is no longer used here because it would re-introduce the context suffix into
the stem.

#### `ask_for_save_file_path`

Pass `enforce_suffix=True, context_file_type=""` so otconfig / otflow saves get
the format-driven `.<ext>` lock.

#### `askopenfilename`

Pass `enforce_suffix=False`. Behaviour unchanged.

#### `configure_export_counts`

`ExportCountsDialog.get_specification()` returns:

```python
file_path = self.get_file_path()
return CountingSpecificationDto(
    start=self._start_datetime.value,
    end=self._end_datetime.value,
    interval_in_minutes=self._interval.value,
    modes=[self._modes[0]] if self._modes else [],
    output_format=self._default_format,
    export_directory=file_path.parent,
    export_filename_stem=self._filename_stem_field.value,
    export_mode=OVERWRITE,
    counting_event=CountingEvent.parse(self._counting_event_field.value),
)
```

The factory's cancel branch raises `CancelExportCounts` (not `CancelAddFlow`).

## Shared helpers

Reused from `OTAnalytics.adapter_ui.helpers` (introduced by the refactor
commit):

- `strip_extension(file_name, extension)` — **fix folded into this work** (see
  next section).
- `ensure_dot_in_extension(extension)`.

No new helpers are introduced by this work.

### Latent defect in `strip_extension` (folded fix)

The current implementation is:

```python
def strip_extension(file_name: str, extension: str) -> str:
    if file_name.endswith(extension):
        return file_name.rstrip(extension)
    return file_name
```

`str.rstrip(extension)` removes any *character in the set* `extension`, not the
literal suffix. For example:

```python
strip_extension("my_data.track_statistics.csv", ".track_statistics.csv")
# returns "my_d", not "my_data"
```

It happens to work today for simple stems whose characters don't appear in the
extension (e.g. `mydata`), but it silently corrupts stems that do (any stem
containing characters from `track_statistics`, `road_user_assignments`,
`events`, etc., plus the format extension characters).

Both the CustomTkinter and NiceGUI sides will rely on this helper. The fix is a
one-line change to use `str.removesuffix` (available since Python 3.9):

```python
def strip_extension(file_name: str, extension: str) -> str:
    return file_name.removesuffix(extension)
```

`removesuffix` is a no-op when the suffix isn't present, so the explicit
`endswith` branch is no longer needed.

A unit test in `tests/unit/OTAnalytics/adapter_ui/test_helpers.py` is added (or
extended) to cover:

- `strip_extension("my_data.track_statistics.csv", ".track_statistics.csv") == "my_data"`.
- `strip_extension("mydata.events.csv", ".events.csv") == "mydata"`.
- `strip_extension("unrelated.csv", ".events.csv") == "unrelated.csv"`.
- `strip_extension("aaa", "a") == "aa"` (suffix matches literally, not as a set).

This fix is in scope because both NiceGUI factory wiring and CTK already depend
on the helper, and the design's correctness depends on it behaving as named.

## Bundled bug fixes

Surfaced by the work; fixed in the same change:

1. `NiceGuiUiFactory.configure_export_file` raised `CancelAddFlow` on cancel →
   `CancelExportFile`.
2. `NiceGuiUiFactory.configure_export_counts` raised `CancelAddFlow` on cancel
   → `CancelExportCounts`.
3. `ExportCountsDialog.get_selected_filename` mis-annotated as `-> str` while
   returning a `Path` → annotation corrected (or method removed if unused).
4. `ExportCountsDialog.get_specification()` passed `output_file=` to a DTO that
   no longer has that field → switched to `export_directory` /
   `export_filename_stem`.

## Tests

All test files follow the project Given dataclass / `create_given` /
`setup_default` / `create_target` factory pattern. All runs go through
`uv run pytest`.

### `tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py`

- `test_locked_suffix_in_export_mode` — `context_file_type="events"`, format
  `csv` ⇒ suffix label `.events.csv`; `get_file_path()` returns
  `<dir>/<stem>.events.csv`; `get_file_stem()` returns only `<stem>`.
- `test_locked_suffix_in_save_mode` — `context_file_type=""`, formats
  `{"otconfig": "otconfig", "otflow": "otflow"}` ⇒ label `.otconfig` initially;
  switching to `otflow` updates the label to `.otflow`; stem field unchanged.
- `test_no_suffix_in_open_mode` — `enforce_suffix=False` ⇒ no suffix badge;
  legacy behaviour preserved.
- `test_format_change_updates_suffix_not_stem` — parametrised over both
  enforce modes.
- `test_browse_strips_matching_suffix` — picker returns `mydata.events.csv`,
  stem field becomes `mydata`.
- `test_browse_keeps_unrelated_name_as_stem` — picker returns a name that
  doesn't match the locked suffix; falls back to `Path(name).stem`.

### `tests/unit/OTAnalytics/plugin_ui/test_export_counts_dialog.py`

- `test_suffix_reflects_interval_and_format` — interval 15→30 updates label
  `.counts_15min.csv` → `.counts_30min.csv`; switching to Excel →
  `.counts_30min.xlsx`.
- `test_get_specification_uses_new_dto_contract` — returned
  `CountingSpecificationDto` carries `export_directory` and
  `export_filename_stem`; no `output_file`.
- `test_initial_stem_strips_context_from_suggestion` — given a
  `get_save_path_suggestion` returning `…/mydata.counts_15min.csv`, the stem
  field shows `mydata`.

### `tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py`

Created if missing.

- `test_configure_export_file_returns_dto_with_correct_stem` — `file_stem`
  equals the typed stem; `as_file_path()` round-trips to
  `<dir>/<stem>.<context>.<ext>`.
- `test_configure_export_file_raises_cancel_export_file_on_cancel`.
- `test_configure_export_counts_raises_cancel_export_counts_on_cancel`.
- `test_ask_for_save_file_path_for_otconfig_locks_extension`.

## Files touched

- `OTAnalytics/adapter_ui/helpers.py` — `strip_extension` fix
  (`rstrip` → `removesuffix`).
- `OTAnalytics/plugin_ui/nicegui_gui/dialogs/file_chooser_dialog.py` —
  stem/suffix split, new accessors, three modes.
- `OTAnalytics/plugin_ui/nicegui_gui/dialogs/export_counts_dialog.py` —
  stem/suffix split, dynamic suffix from interval+format, new
  `get_specification`, return-type fix.
- `OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py` — factory wiring for all
  three `FileChooserDialog` modes, DTO construction without
  `from_file_path`, correct cancel exception types.
- `tests/unit/OTAnalytics/adapter_ui/test_helpers.py` — `strip_extension`
  coverage extended.
- `tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py` — extended.
- `tests/unit/OTAnalytics/plugin_ui/test_export_counts_dialog.py` — extended.
- `tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py` — new (if
  it does not already exist).

## Risks

- `FormFieldText` may need a read-only style helper. If the underlying
  NiceGUI `ui.input` is set to `props("readonly")` or similar, the
  styling is straightforward; if not, a small wrapper is added in the same
  file. This is a known-shape risk, not an architectural one.
- The suggested-stem peeling depends on
  `viewmodel.get_save_path_suggestion(...)` actually producing
  `<base>/<stem>.<context>.<ext>`. The `Application.suggest_save_path` docstring
  promises exactly this format, so the dependency is on documented behaviour
  rather than an implementation detail.
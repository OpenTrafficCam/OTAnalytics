# NiceGUI Export Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adapt the NiceGUI export flows to the refactored `ExportFileDto` /
`CountingSpecificationDto` contract introduced in commit `8d89b20b`, and enforce
in the UI that exported filenames always end with `<context_file_type>.<extension>`.

**Architecture:** Replace the single editable filename field in
`FileChooserDialog` and `ExportCountsDialog` with a *stem field + non-editable
suffix badge*. The badge expression is parameterised so the same dialog covers
three modes: open (no lock), plain save (`.<ext>`), context export
(`.<context>.<ext>`). Counts uses the same shape but composes a dynamic suffix
from interval + format.

**Tech Stack:** Python 3.12, NiceGUI, pytest (`uv run pytest`), nicegui.testing.

**Companion spec:**
`docs/superpowers/specs/2026-05-26-nicegui-export-refactor-design.md` (commit
`67694b2d`).

**Conventions reminders for the implementer:**

- All tests run via `uv run pytest`.
- Tests use the project's Given dataclass / `create_given` / `setup_default` /
  `create_target` factory pattern. Where existing tests in the file do *not*
  use this pattern (e.g. `test_file_chooser_dialog.py` uses simple fixtures),
  match the existing style of that test file rather than rewriting unrelated
  tests.
- Commit messages start with `OP#9548:` (matches branch convention).
- Do **not** add `Co-Authored-By` lines.
- Type-annotate all function signatures (parameters + return).
- Imports at the top of the file, isort-grouped.
- No `Path` returned where `-> str` is annotated, and vice versa.
- The pre-existing pre-commit mypy errors in `export_counts_dialog.py` will
  *go away* during this work — tasks order them early on purpose.

---

## File Structure

| File | Status | Responsibility |
| --- | --- | --- |
| `OTAnalytics/adapter_ui/helpers.py` | Modify | Fix `strip_extension` to use `removesuffix`. |
| `tests/unit/OTAnalytics/adapter_ui/test_helpers.py` | Modify | Add `strip_extension` tests. |
| `OTAnalytics/plugin_ui/nicegui_gui/dialogs/file_chooser_dialog.py` | Modify | Add stem/suffix split, `context_file_type` + `enforce_suffix` params, new accessors. |
| `tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py` | Modify | New tests for the three modes + suffix/stem behaviour. |
| `OTAnalytics/plugin_ui/nicegui_gui/dialogs/export_counts_dialog.py` | Modify | Stem/suffix split with dynamic suffix; fix `get_specification()` + return type. |
| `tests/unit/OTAnalytics/plugin_ui/test_export_counts_dialog.py` | Modify | Update existing tests to new contract + add suffix/stem tests. |
| `OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py` | Modify | Pass new dialog params; construct `ExportFileDto` directly; correct cancel exception types. |
| `tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py` | Create | New tests for factory wiring & cancel exception types. |

---

## Task 1: Fix `strip_extension` helper

**Why first:** Both NiceGUI factory wiring and the dialogs depend on this
helper. The current `rstrip` implementation silently corrupts stems whose
characters overlap with the suffix.

**Files:**
- Modify: `OTAnalytics/adapter_ui/helpers.py:46-61`
- Test: `tests/unit/OTAnalytics/adapter_ui/test_helpers.py`

- [ ] **Step 1: Add failing tests for the literal-suffix behaviour**

Append to `tests/unit/OTAnalytics/adapter_ui/test_helpers.py`:

```python
from OTAnalytics.adapter_ui.helpers import strip_extension


@pytest.mark.parametrize(
    "file_name,extension,expected",
    [
        ("mydata.events.csv", ".events.csv", "mydata"),
        (
            "my_data.track_statistics.csv",
            ".track_statistics.csv",
            "my_data",
        ),
        (
            "trip_summary.road_user_assignments.csv",
            ".road_user_assignments.csv",
            "trip_summary",
        ),
        ("unrelated.csv", ".events.csv", "unrelated.csv"),
        ("aaa", "a", "aa"),
        ("", ".events.csv", ""),
        ("mydata.events.csv", "", "mydata.events.csv"),
    ],
)
def test_strip_extension_removes_literal_suffix(
    file_name: str, extension: str, expected: str
) -> None:
    assert strip_extension(file_name, extension) == expected
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/adapter_ui/test_helpers.py::test_strip_extension_removes_literal_suffix -v
```

Expected: at least three FAILs — `mydata` becomes empty / wrong; `my_data`
becomes `my_d`; `trip_summary` similarly corrupted by `rstrip`.

- [ ] **Step 3: Replace the implementation**

Edit `OTAnalytics/adapter_ui/helpers.py` lines 46–61:

```python
def strip_extension(file_name: str, extension: str) -> str:
    """Strip the supported file extension from the file name if present.

    Args:
        file_name: The file name.
        extension: The extension to strip (literal, including leading dot).

    Returns:
        The file name without the extension if it ends with that suffix,
        otherwise the original file name unchanged.
    """
    return file_name.removesuffix(extension)
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/adapter_ui/test_helpers.py -v
```

Expected: all parametrised cases PASS, plus the existing
`test_ensure_file_extension_is_appended` cases remain PASS.

- [ ] **Step 5: Commit**

```bash
git add OTAnalytics/adapter_ui/helpers.py \
        tests/unit/OTAnalytics/adapter_ui/test_helpers.py
git commit -m "OP#9548: Fix strip_extension to remove literal suffix not char set"
```

---

## Task 2: Add `context_file_type` and `enforce_suffix` to `FileChooserDialog`

**Why second:** Establishes the dialog API needed by the factory rewrite.
Keeps the legacy single-field path alive (open mode) so we don't break
`askopenfilename` until the factory tasks switch it intentionally.

**Files:**
- Modify: `OTAnalytics/plugin_ui/nicegui_gui/dialogs/file_chooser_dialog.py`
- Test: `tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py`

- [ ] **Step 1: Write the failing tests for the new modes**

Append to `tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py`:

```python
TEST_CONTEXT_FILE_TYPE = "events"


@pytest.fixture
def file_chooser_dialog_export(resource_manager: Mock) -> FileChooserDialog:
    return FileChooserDialog(
        resource_manager=resource_manager,
        title=TEST_TITLE,
        file_extensions=TEST_FILE_EXTENSIONS,
        initial_file_stem=TEST_INITIAL_FILE_STEM,
        context_file_type=TEST_CONTEXT_FILE_TYPE,
        enforce_suffix=True,
    )


@pytest.fixture
def file_chooser_dialog_save(resource_manager: Mock) -> FileChooserDialog:
    return FileChooserDialog(
        resource_manager=resource_manager,
        title=TEST_TITLE,
        file_extensions={"otconfig": "otconfig", "otflow": "otflow"},
        initial_file_stem=TEST_INITIAL_FILE_STEM,
        context_file_type="",
        enforce_suffix=True,
    )


@pytest.fixture
def file_chooser_dialog_open(resource_manager: Mock) -> FileChooserDialog:
    return FileChooserDialog(
        resource_manager=resource_manager,
        title=TEST_TITLE,
        file_extensions=TEST_FILE_EXTENSIONS,
        initial_file_stem="",
        enforce_suffix=False,
    )


class TestFileChooserDialogModes:
    @pytest.mark.asyncio
    async def test_export_mode_locked_suffix(
        self, user: User, file_chooser_dialog_export: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_export.build().open()

        await user.open(ENDPOINT_NAME)

        assert (
            file_chooser_dialog_export._filename_stem_field.value
            == TEST_INITIAL_FILE_STEM
        )
        assert (
            file_chooser_dialog_export._filename_suffix_field.value == ".events.csv"
        )
        assert file_chooser_dialog_export.get_file_stem() == TEST_INITIAL_FILE_STEM
        assert (
            file_chooser_dialog_export.get_export_format_extension() == ".csv"
        )
        assert (
            file_chooser_dialog_export.get_file_path()
            == Path.home() / f"{TEST_INITIAL_FILE_STEM}.events.csv"
        )

    @pytest.mark.asyncio
    async def test_save_mode_locked_extension_follows_format(
        self, user: User, file_chooser_dialog_save: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_save.build().open()

        await user.open(ENDPOINT_NAME)

        assert (
            file_chooser_dialog_save._filename_suffix_field.value == ".otconfig"
        )
        # Switch the format dropdown
        user.find(marker=MARKER_FORMAT).click()
        user.find("otflow").click()

        assert (
            file_chooser_dialog_save._filename_suffix_field.value == ".otflow"
        )
        assert (
            file_chooser_dialog_save._filename_stem_field.value
            == TEST_INITIAL_FILE_STEM
        )

    @pytest.mark.asyncio
    async def test_open_mode_has_no_suffix_field(
        self, user: User, file_chooser_dialog_open: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_open.build().open()

        await user.open(ENDPOINT_NAME)

        assert file_chooser_dialog_open._filename_suffix_field is None
        # Legacy single field is still present
        assert file_chooser_dialog_open._filename_field is not None
```

- [ ] **Step 2: Run the new tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py::TestFileChooserDialogModes -v
```

Expected: ImportError / AttributeError on `context_file_type`,
`enforce_suffix`, `_filename_stem_field`, `_filename_suffix_field`,
`get_file_stem`, `get_export_format_extension`.

- [ ] **Step 3: Rewrite `FileChooserDialog`**

Replace the contents of
`OTAnalytics/plugin_ui/nicegui_gui/dialogs/file_chooser_dialog.py` with:

```python
from pathlib import Path
from typing import Any

from nicegui import ui

from OTAnalytics.adapter_ui.helpers import ensure_dot_in_extension, strip_extension
from OTAnalytics.application.resources.resource_manager import (
    FileChooserDialogKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker import LocalFilePicker
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    FormFieldSelect,
    FormFieldText,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import (
    MissingInstanceError,
)

MARKER_FORMAT = "marker-format"
MARKER_FILENAME = "marker-filename"
MARKER_FILENAME_STEM = "marker-filename-stem"
MARKER_FILENAME_SUFFIX = "marker-filename-suffix"
MARKER_DIRECTORY = "marker-directory"


class FileChooserDialog(BaseDialog):
    """Dialog for choosing a file to save or open.

    The dialog operates in three modes depending on the combination of
    ``enforce_suffix`` and ``context_file_type``:

    - ``enforce_suffix=False`` (open mode): a single editable filename field is
      shown. Used by ``askopenfilename``.
    - ``enforce_suffix=True`` and empty ``context_file_type`` (plain save
      mode): a stem field plus a non-editable suffix badge that mirrors the
      currently selected format extension.
    - ``enforce_suffix=True`` and non-empty ``context_file_type`` (context
      export mode): the suffix badge mirrors ``.<context_file_type>.<ext>``.
    """

    def __init__(
        self,
        resource_manager: ResourceManager,
        title: str,
        file_extensions: dict[str, str],
        initial_file_stem: str,
        initial_dir: Path = Path.home(),
        extension_options: dict[str, list[str] | None] | None = None,
        context_file_type: str = "",
        enforce_suffix: bool = True,
    ) -> None:
        super().__init__(resource_manager)
        self._title = title
        self._file_extensions = file_extensions
        self._initial_file_stem = initial_file_stem
        self._initial_dir = initial_dir
        self._extension_options = extension_options
        self._context_file_type = context_file_type
        self._enforce_suffix = enforce_suffix

        self._format_field = FormFieldSelect(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_FORMAT),
            options=list(file_extensions.keys()),
            initial_value=(
                list(file_extensions.keys())[0] if file_extensions else None
            ),
            on_value_change=self._on_format_change,
            marker=MARKER_FORMAT,
        )

        self._filename_field: FormFieldText | None = None
        self._filename_stem_field: FormFieldText | None = None
        self._filename_suffix_field: FormFieldText | None = None

        if self._enforce_suffix:
            self._filename_stem_field = FormFieldText(
                label_text=self.resource_manager.get(
                    FileChooserDialogKeys.LABEL_FILENAME
                ),
                initial_value=initial_file_stem,
                marker=MARKER_FILENAME_STEM,
            )
            self._filename_suffix_field = FormFieldText(
                label_text="",
                initial_value=self._build_locked_suffix(),
                readonly=True,
                marker=MARKER_FILENAME_SUFFIX,
            )
        else:
            self._filename_field = FormFieldText(
                label_text=self.resource_manager.get(
                    FileChooserDialogKeys.LABEL_FILENAME
                ),
                initial_value=(
                    f"{initial_file_stem}"
                    f"{self._get_extension_for_current_format()}"
                ),
                marker=MARKER_FILENAME,
            )

        self._directory_field = FormFieldText(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_DIRECTORY),
            initial_value=str(initial_dir),
            on_value_change=self._update_directory,
            marker=MARKER_DIRECTORY,
        )

    def build_content(self) -> None:
        ui.label(self._title).classes("text-xl")

        with ui.column().classes("w-full"):
            self._format_field.build()
            if self._enforce_suffix:
                assert self._filename_stem_field is not None
                assert self._filename_suffix_field is not None
                with ui.row().classes("w-full no-wrap items-end"):
                    self._filename_stem_field.build()
                    self._filename_suffix_field.build()
            else:
                assert self._filename_field is not None
                self._filename_field.build()
            self._directory_field.build()

            with ui.row():
                ui.button(
                    self.resource_manager.get(FileChooserDialogKeys.LABEL_BROWSE),
                    on_click=self._browse_directory,
                )

    def _on_format_change(self, _: Any) -> None:
        if self._enforce_suffix:
            assert self._filename_suffix_field is not None
            self._filename_suffix_field.set_value(self._build_locked_suffix())
        else:
            assert self._filename_field is not None
            current_filename = self._filename_field.value
            filename_stem = Path(current_filename).stem
            new_extension = self._get_extension_for_current_format()
            self._filename_field.set_value(f"{filename_stem}{new_extension}")

    def _build_locked_suffix(self) -> str:
        ext = ensure_dot_in_extension(self._get_extension_for_current_format())
        if self._context_file_type:
            return f".{self._context_file_type}{ext}"
        return ext

    def _get_extension_for_current_format(self) -> str:
        if not self._file_extensions:
            return ""
        try:
            selected_format = self._format_field.value
        except MissingInstanceError:
            selected_format = list(self._file_extensions.keys())[0]
        return ensure_dot_in_extension(self._file_extensions[selected_format])

    def _update_directory(self, e: Any) -> None:
        try:
            new_path = Path(e.value).expanduser()
            if new_path.exists() and new_path.is_dir():
                self._initial_dir = new_path
            else:
                self._directory_field.set_value(str(self._initial_dir))
        except Exception:
            self._directory_field.set_value(str(self._initial_dir))

    async def _browse_directory(self) -> None:
        picker = LocalFilePicker(
            directory=Path(self._directory_field.value),
            show_hidden_files=False,
            show_files_only_of_type=None,
            show_only_directories=False,
            extension_options=self._extension_options,
        )
        result = await picker
        if result and result[0]:
            selected_path = result[0]
            if selected_path.is_dir():
                self._directory_field.set_value(str(selected_path))
            else:
                self._directory_field.set_value(str(selected_path.parent))
                self._set_filename_from_picked(selected_path.name)

    def _set_filename_from_picked(self, picked_name: str) -> None:
        if self._enforce_suffix:
            assert self._filename_stem_field is not None
            suffix = self._build_locked_suffix()
            if picked_name.endswith(suffix):
                self._filename_stem_field.set_value(
                    strip_extension(picked_name, suffix)
                )
            else:
                self._filename_stem_field.set_value(Path(picked_name).stem)
        else:
            assert self._filename_field is not None
            self._filename_field.set_value(picked_name)

    def get_directory(self) -> Path:
        return Path(self._directory_field.value)

    def get_file_stem(self) -> str:
        if self._enforce_suffix:
            assert self._filename_stem_field is not None
            return self._filename_stem_field.value
        assert self._filename_field is not None
        return Path(self._filename_field.value).stem

    def get_export_format_extension(self) -> str:
        return ensure_dot_in_extension(self._get_extension_for_current_format())

    def get_file_path(self) -> Path:
        if self._enforce_suffix:
            assert self._filename_stem_field is not None
            assert self._filename_suffix_field is not None
            return self.get_directory() / (
                self._filename_stem_field.value
                + self._filename_suffix_field.value
            )
        assert self._filename_field is not None
        return self.get_directory() / self._filename_field.value

    def get_format(self) -> str:
        if not self._file_extensions:
            return ""
        return self._format_field.value
```

Notes for the implementer:

- `FormFieldText.readonly=True` translates to `props=readonly` on the
  underlying `ui.input` — see
  `OTAnalytics/plugin_ui/nicegui_gui/nicegui/elements/forms.py:184-194`.
- The single-field path (`_filename_field`) is preserved so existing tests
  and `askopenfilename` keep working.
- `_on_format_change` replaces the previous `_update_file_extension` (renamed
  because it now does the format-driven work for both modes).

- [ ] **Step 4: Run the new tests to verify they pass**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py::TestFileChooserDialogModes -v
```

Expected: 3 PASS.

- [ ] **Step 5: Update the existing legacy tests for the renamed handler**

The pre-existing `test_format_change_updates_extension` test relies on the
legacy `_filename_field`. It still works because the default constructor
omits the new parameters, leaving the dialog in `enforce_suffix=True` mode —
which now uses `_filename_stem_field`, not `_filename_field`. Update the
fixtures so the legacy tests explicitly opt into open mode:

In `tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py`, change
both legacy fixtures to:

```python
@pytest.fixture
def file_chooser_dialog(resource_manager: Mock) -> FileChooserDialog:
    return FileChooserDialog(
        resource_manager=resource_manager,
        title=TEST_TITLE,
        file_extensions=TEST_FILE_EXTENSIONS,
        initial_file_stem=TEST_INITIAL_FILE_STEM,
        enforce_suffix=False,
    )


@pytest.fixture
def file_chooser_dialog_with_dir(resource_manager: Mock) -> FileChooserDialog:
    with patch.object(Path, "exists", return_value=True):
        return FileChooserDialog(
            resource_manager=resource_manager,
            title=TEST_TITLE,
            file_extensions=TEST_FILE_EXTENSIONS,
            initial_file_stem=TEST_INITIAL_FILE_STEM,
            initial_dir=TEST_DIRECTORY,
            enforce_suffix=False,
        )
```

This keeps the legacy tests on the now-legacy single-field code path.

- [ ] **Step 6: Run all FileChooserDialog tests**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py -v
```

Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add OTAnalytics/plugin_ui/nicegui_gui/dialogs/file_chooser_dialog.py \
        tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py
git commit -m "OP#9548: Add stem+locked-suffix mode to FileChooserDialog"
```

---

## Task 3: Add browse-strips-suffix test for `FileChooserDialog`

**Why split out:** The browse-handler path uses `LocalFilePicker`, which needs
mocking; isolating it keeps Task 2 reviewable.

**Files:**
- Test: `tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py`

- [ ] **Step 1: Add tests for `_set_filename_from_picked`**

Append to `TestFileChooserDialogModes`:

```python
    @pytest.mark.asyncio
    async def test_browse_strips_matching_suffix_in_export_mode(
        self, user: User, file_chooser_dialog_export: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_export.build().open()

        await user.open(ENDPOINT_NAME)

        file_chooser_dialog_export._set_filename_from_picked(
            "trip_summary.events.csv"
        )

        assert (
            file_chooser_dialog_export._filename_stem_field.value
            == "trip_summary"
        )

    @pytest.mark.asyncio
    async def test_browse_keeps_unrelated_name_as_stem(
        self, user: User, file_chooser_dialog_export: FileChooserDialog
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            file_chooser_dialog_export.build().open()

        await user.open(ENDPOINT_NAME)

        file_chooser_dialog_export._set_filename_from_picked("unrelated.xlsx")

        assert (
            file_chooser_dialog_export._filename_stem_field.value
            == "unrelated"
        )
```

- [ ] **Step 2: Run the new tests**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py::TestFileChooserDialogModes::test_browse_strips_matching_suffix_in_export_mode tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py::TestFileChooserDialogModes::test_browse_keeps_unrelated_name_as_stem -v
```

Expected: 2 PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py
git commit -m "OP#9548: Test browse-handler suffix stripping in FileChooserDialog"
```

---

## Task 4: Rewrite `ExportCountsDialog` to the new contract

**Why now:** This task clears the existing pre-commit mypy errors
(`output_file=...` no longer exists, `get_selected_filename` mis-annotated).
After this task, pre-commit can run cleanly.

**Files:**
- Modify: `OTAnalytics/plugin_ui/nicegui_gui/dialogs/export_counts_dialog.py`
- Test: `tests/unit/OTAnalytics/plugin_ui/test_export_counts_dialog.py`

- [ ] **Step 1: Update the existing tests to the new contract**

Replace the body of `test_get_specification` and
`test_different_export_format` in
`tests/unit/OTAnalytics/plugin_ui/test_export_counts_dialog.py` (lines
80–149) so they no longer reference `specification.output_file`:

```python
    @pytest.mark.asyncio
    async def test_get_specification(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
        resource_manager: ResourceManager,
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            export_counts_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        user.find(MARKER_DIRECTORY).type(str(Path(TEST_OUTPUT_FILE).parent))
        user.find(MARKER_FILENAME_STEM).type("test_file")
        user.find(marker=MARKER_APPLY).click()

        specification = export_counts_dialog.get_specification()

        assert specification.start == TEST_START
        assert specification.end == TEST_END
        assert specification.output_format == TEST_DEFAULT_FORMAT
        assert specification.export_directory == Path(TEST_OUTPUT_FILE).parent
        assert specification.export_filename_stem == "test_file"
        assert specification.export_mode == OVERWRITE
        assert specification.interval_in_minutes == TEST_INTERVAL

    @pytest.mark.asyncio
    async def test_different_export_format(
        self,
        user: User,
        resource_manager: ResourceManager,
        viewmodel: Mock,
    ) -> None:
        export_counts_dialog = ExportCountsDialog(
            resource_manager=resource_manager,
            viewmodel=viewmodel,
            start=TEST_START,
            end=TEST_END,
            default_format="Excel",
            modes=TEST_MODES,
            export_formats=TEST_EXPORT_FORMATS,
        )

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            export_counts_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        user.find(MARKER_DIRECTORY).type(
            str(Path(TEST_EXCEL_OUTPUT_FILE).parent)
        )
        user.find(MARKER_FILENAME_STEM).type("test_file")
        user.find(marker=MARKER_APPLY).click()

        specification = export_counts_dialog.get_specification()

        assert specification.output_format == "Excel"
        assert specification.export_directory == Path(TEST_EXCEL_OUTPUT_FILE).parent
        assert specification.export_filename_stem == "test_file"
```

Also update the import at the top of the file to include the new marker:

```python
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.export_counts_dialog import (
    MARKER_DIRECTORY,
    MARKER_FILENAME,
    MARKER_FILENAME_STEM,
    MARKER_FILENAME_SUFFIX,
    MARKER_INTERVAL,
    ExportCountsDialog,
)
```

And update `test_validation_error_empty_filename` to target the stem field:

```python
        user.find(MARKER_DIRECTORY).type(str(Path(TEST_OUTPUT_FILE).parent))
        user.find(MARKER_FILENAME_STEM).clear()
```

And `test_validation_error_missing_dates`:

```python
        user.find(MARKER_DIRECTORY).type(str(Path(TEST_OUTPUT_FILE).parent))
        user.find(MARKER_FILENAME_STEM).type("test_file")
```

Then add new tests:

```python
    @pytest.mark.asyncio
    async def test_suffix_reflects_interval_and_format(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
    ) -> None:
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            export_counts_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        assert (
            export_counts_dialog._filename_suffix_field.value
            == ".counts_15min.csv"
        )

        user.find(marker=MARKER_INTERVAL).clear().type("30")

        assert (
            export_counts_dialog._filename_suffix_field.value
            == ".counts_30min.csv"
        )

    @pytest.mark.asyncio
    async def test_initial_stem_strips_context_from_suggestion(
        self,
        user: User,
        resource_manager: ResourceManager,
    ) -> None:
        viewmodel = MagicMock(spec=ViewModel)
        viewmodel.get_save_path_suggestion.return_value = Path(
            "/tmp/mydata.counts_15min.csv"
        )
        dialog = ExportCountsDialog(
            resource_manager=resource_manager,
            viewmodel=viewmodel,
            start=TEST_START,
            end=TEST_END,
            default_format=TEST_DEFAULT_FORMAT,
            modes=TEST_MODES,
            export_formats=TEST_EXPORT_FORMATS,
        )

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            dialog.build().open()

        await user.open(ENDPOINT_NAME)

        assert dialog._filename_stem_field.value == "mydata"
```

- [ ] **Step 2: Run the updated tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/test_export_counts_dialog.py -v
```

Expected: failures due to `_filename_stem_field`, `_filename_suffix_field`,
`MARKER_FILENAME_STEM`, `MARKER_FILENAME_SUFFIX`, `export_directory`,
`export_filename_stem` not yet existing.

- [ ] **Step 3: Rewrite `ExportCountsDialog`**

Replace
`OTAnalytics/plugin_ui/nicegui_gui/dialogs/export_counts_dialog.py` with:

```python
from datetime import datetime
from pathlib import Path
from typing import Any

from nicegui import ui

from OTAnalytics.adapter_ui.helpers import ensure_dot_in_extension, strip_extension
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
    CountingSpecificationDto,
)
from OTAnalytics.application.config import (
    CONTEXT_FILE_TYPE_COUNTS,
    DEFAULT_COUNT_INTERVAL_TIME_UNIT,
)
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.resources.resource_manager import (
    ExportCountsDialogKeys,
    FileChooserDialogKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.file_utils import select_output_directory
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    DateTimeForm,
    FormFieldInteger,
    FormFieldSelect,
    FormFieldText,
)

MARKER_START_DATE = "marker-start-date"
MARKER_START_TIME = "marker-start-time"
MARKER_END_DATE = "marker-end-date"
MARKER_END_TIME = "marker-end-time"
MARKER_DIRECTORY = "marker-directory"
MARKER_FILENAME = "marker-filename"
MARKER_FILENAME_STEM = "marker-filename-stem"
MARKER_FILENAME_SUFFIX = "marker-filename-suffix"
MARKER_INTERVAL = "marker-interval"
MARKER_COUNTING_EVENT = "marker-counting-event"

DEFAULT_INTERVAL_MINUTES = 15


class ExportCountsDialog(BaseDialog):
    """Dialog for configuring counts export.

    Uses a stem field plus a non-editable suffix badge that reflects
    ``.counts_<interval>min.<ext>``. Interval and format changes update the
    badge live.
    """

    def __init__(
        self,
        resource_manager: ResourceManager,
        viewmodel: ViewModel,
        start: datetime | None,
        end: datetime | None,
        default_format: str,
        modes: list,
        export_formats: dict[str, str],
        initial_dir: Path = Path.home(),
    ) -> None:
        super().__init__(resource_manager)
        self._viewmodel = viewmodel
        self._export_formats = export_formats
        self._default_format = default_format
        self._modes = modes
        self._initial_dir = initial_dir

        self._start_datetime = DateTimeForm(
            label_date_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_START_DATE
            ),
            label_time_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_START_TIME
            ),
            initial_value=start,
            marker_date=MARKER_START_DATE,
            marker_time=MARKER_START_TIME,
        )

        self._end_datetime = DateTimeForm(
            label_date_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_END_DATE
            ),
            label_time_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_END_TIME
            ),
            initial_value=end,
            marker_date=MARKER_END_DATE,
            marker_time=MARKER_END_TIME,
        )

        self._interval = FormFieldInteger(
            label_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_INTERVAL_MINUTES
            ),
            initial_value=DEFAULT_INTERVAL_MINUTES,
            min_value=1,
            on_value_change=self._on_interval_or_format_change,
            marker=MARKER_INTERVAL,
        )

        suggestion = self._viewmodel.get_save_path_suggestion(
            self._extension_for_default_format().lstrip("."),
            self._context_for_current_interval(DEFAULT_INTERVAL_MINUTES),
        )
        initial_stem = strip_extension(
            suggestion.stem,
            f".{self._context_for_current_interval(DEFAULT_INTERVAL_MINUTES)}",
        )

        self._directory_field = FormFieldText(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_DIRECTORY),
            initial_value=str(suggestion.parent or initial_dir),
            on_value_change=self._update_directory,
            marker=MARKER_DIRECTORY,
        )

        self._filename_stem_field = FormFieldText(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_FILENAME),
            initial_value=initial_stem,
            marker=MARKER_FILENAME_STEM,
        )
        self._filename_suffix_field = FormFieldText(
            label_text="",
            initial_value=self._build_locked_suffix(DEFAULT_INTERVAL_MINUTES),
            readonly=True,
            marker=MARKER_FILENAME_SUFFIX,
        )

        self._format_field = FormFieldSelect(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_FORMAT),
            options=list(export_formats.keys()),
            initial_value=default_format,
            on_value_change=self._on_interval_or_format_change,
            marker="marker-format",
        )

        self._counting_event_field = FormFieldSelect(
            label_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_COUNTING_EVENT
            ),
            options=[event.value for event in CountingEvent],
            initial_value=CountingEvent.START.value,
            marker=MARKER_COUNTING_EVENT,
        )

    def build_content(self) -> None:
        ui.label(
            self.resource_manager.get(ExportCountsDialogKeys.LABEL_EXPORT_COUNTS)
        ).classes("text-xl")

        with ui.column().classes("w-full"):
            ui.label(
                self.resource_manager.get(ExportCountsDialogKeys.LABEL_TIME_RANGE)
            ).classes("text-lg")
            self._start_datetime.build()
            self._end_datetime.build()
            self._interval.build()
            self._counting_event_field.build()

            ui.label(
                self.resource_manager.get(ExportCountsDialogKeys.LABEL_OUTPUT_FILE)
            ).classes("text-lg")
            self._format_field.build()
            with ui.row().classes("w-full no-wrap items-end"):
                self._filename_stem_field.build()
                self._filename_suffix_field.build()
            self._directory_field.build()
            with ui.row():
                ui.button(
                    self.resource_manager.get(FileChooserDialogKeys.LABEL_BROWSE),
                    on_click=self._select_output_file,
                )

    def _extension_for_default_format(self) -> str:
        return ensure_dot_in_extension(self._export_formats[self._default_format])

    def _current_extension(self) -> str:
        try:
            selected_format = self._format_field.value
        except Exception:
            selected_format = self._default_format
        return ensure_dot_in_extension(self._export_formats[selected_format])

    def _context_for_current_interval(self, interval: int) -> str:
        return f"{CONTEXT_FILE_TYPE_COUNTS}_{interval}{DEFAULT_COUNT_INTERVAL_TIME_UNIT}"

    def _build_locked_suffix(self, interval: int) -> str:
        return f".{self._context_for_current_interval(interval)}{self._current_extension()}"

    def _on_interval_or_format_change(self, _: Any) -> None:
        try:
            interval = self._interval.value
        except Exception:
            interval = DEFAULT_INTERVAL_MINUTES
        self._filename_suffix_field.set_value(self._build_locked_suffix(interval))

    def _update_directory(self, e: Any) -> None:
        try:
            new_path = Path(e.value).expanduser()
            if new_path.exists() and new_path.is_dir():
                self._initial_dir = new_path
            else:
                self._directory_field.set_value(str(self._initial_dir))
        except Exception:
            self._directory_field.set_value(str(self._initial_dir))

    async def _select_output_file(self) -> None:
        await select_output_directory(
            directory=Path(self._directory_field.value),
            set_directory_callback=self._directory_field.set_value,
        )

    def get_file_path(self) -> Path:
        return Path(self._directory_field.value) / (
            self._filename_stem_field.value + self._filename_suffix_field.value
        )

    def get_selected_directory(self) -> Path:
        return Path(self._directory_field.value)

    def get_selected_filename(self) -> str:
        return (
            self._filename_stem_field.value + self._filename_suffix_field.value
        )

    def get_specification(self) -> CountingSpecificationDto:
        if not self._filename_stem_field.value:
            raise ValueError("No output file selected")

        if not self._start_datetime.value or not self._end_datetime.value:
            raise ValueError("Start and end times must be specified")

        file_path = self.get_file_path()
        return CountingSpecificationDto(
            start=self._start_datetime.value,
            end=self._end_datetime.value,
            interval_in_minutes=self._interval.value,
            modes=[self._modes[0]] if self._modes else [],
            output_format=self._format_field.value,
            export_directory=file_path.parent,
            export_filename_stem=self._filename_stem_field.value,
            export_mode=OVERWRITE,
            counting_event=CountingEvent.parse(
                self._counting_event_field.value
            ),
        )
```

Notes for the implementer:

- The format dropdown was previously inferred from `default_format` only and
  not user-selectable; the new code adds an explicit `FormFieldSelect`,
  matching `FileChooserDialog`. This keeps the locked-suffix UX consistent
  across dialogs.
- `MARKER_FILENAME` is kept exported (even though no field uses it any more)
  because other tests import it; do not remove the constant.
- `output_format` now flows from the user-selected format, not just the
  `default_format` arg.

- [ ] **Step 4: Run all `ExportCountsDialog` tests**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/test_export_counts_dialog.py -v
```

Expected: all PASS.

- [ ] **Step 5: Run mypy on the dialog to confirm prior errors are gone**

```bash
uv run mypy OTAnalytics/plugin_ui/nicegui_gui/dialogs/export_counts_dialog.py
```

Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add OTAnalytics/plugin_ui/nicegui_gui/dialogs/export_counts_dialog.py \
        tests/unit/OTAnalytics/plugin_ui/test_export_counts_dialog.py
git commit -m "OP#9548: Rewrite ExportCountsDialog with locked suffix + new DTO contract"
```

---

## Task 5: Wire `NiceGuiUiFactory.configure_export_file` to the new DTO contract

**Files:**
- Modify: `OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py:177-198`
- Create: `tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py`

- [ ] **Step 1: Create the test file**

Create
`tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py`:

```python
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from OTAnalytics.adapter_ui.cancel_export_counts import CancelExportCounts
from OTAnalytics.adapter_ui.cancel_export_file import CancelExportFile
from OTAnalytics.adapter_ui.file_export_dto import ExportFileDto
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import DialogResult
from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import NiceGuiUiFactory


@pytest.fixture
def resource_manager() -> ResourceManager:
    return ResourceManager()


@pytest.fixture
def viewmodel() -> Mock:
    vm = MagicMock(spec=ViewModel)
    vm.get_save_path_suggestion.return_value = Path("/tmp/mydata.events.csv")
    return vm


@pytest.fixture
def factory(resource_manager: ResourceManager) -> NiceGuiUiFactory:
    return NiceGuiUiFactory(resource_manager=resource_manager)


class TestConfigureExportFile:
    @pytest.mark.asyncio
    async def test_returns_dto_with_correct_stem(
        self,
        factory: NiceGuiUiFactory,
        viewmodel: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        dialog_instance = MagicMock()
        dialog_instance.result = AsyncMock(return_value=DialogResult.APPLY)()
        dialog_instance.get_directory.return_value = Path("/tmp")
        dialog_instance.get_file_stem.return_value = "mydata"
        dialog_instance.get_export_format_extension.return_value = ".csv"
        dialog_instance.get_format.return_value = "CSV"

        monkeypatch.setattr(
            "OTAnalytics.plugin_ui.nicegui_gui.ui_factory.FileChooserDialog",
            lambda **kwargs: dialog_instance,
        )

        result = await factory.configure_export_file(
            title="Export events",
            export_format_extensions={"CSV": ".csv"},
            context_file_type="events",
            viewmodel=viewmodel,
        )

        assert result == ExportFileDto(
            export_directory=Path("/tmp"),
            file_stem="mydata",
            export_format_extension=".csv",
            export_format="CSV",
        )
        assert result.as_file_path() == Path("/tmp/mydata.csv")

    @pytest.mark.asyncio
    async def test_raises_cancel_export_file_on_cancel(
        self,
        factory: NiceGuiUiFactory,
        viewmodel: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        dialog_instance = MagicMock()
        dialog_instance.result = AsyncMock(return_value=DialogResult.CANCEL)()
        monkeypatch.setattr(
            "OTAnalytics.plugin_ui.nicegui_gui.ui_factory.FileChooserDialog",
            lambda **kwargs: dialog_instance,
        )

        with pytest.raises(CancelExportFile):
            await factory.configure_export_file(
                title="Export events",
                export_format_extensions={"CSV": ".csv"},
                context_file_type="events",
                viewmodel=viewmodel,
            )


class TestConfigureExportCounts:
    @pytest.mark.asyncio
    async def test_raises_cancel_export_counts_on_cancel(
        self,
        factory: NiceGuiUiFactory,
        viewmodel: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        dialog_instance = MagicMock()
        dialog_instance.result = AsyncMock(return_value=DialogResult.CANCEL)()
        monkeypatch.setattr(
            "OTAnalytics.plugin_ui.nicegui_gui.ui_factory.ExportCountsDialog",
            lambda **kwargs: dialog_instance,
        )

        with pytest.raises(CancelExportCounts):
            await factory.configure_export_counts(
                start=None,
                end=None,
                default_format="CSV",
                modes=[],
                export_formats={"CSV": ".csv"},
                viewmodel=viewmodel,
            )
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py -v
```

Expected: failures — `configure_export_file` still raises `CancelAddFlow`,
`configure_export_counts` still raises `CancelAddFlow`, and `ExportFileDto`
is constructed via `from_file_path` (so `file_stem` would be wrong if the
dialog wasn't mocked).

- [ ] **Step 3: Rewrite `configure_export_file`**

In `OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py`, replace lines 177–198
with:

```python
    async def configure_export_file(
        self,
        title: str,
        export_format_extensions: dict[str, str],
        context_file_type: str,
        viewmodel: ViewModel,
    ) -> ExportFileDto:
        default_ext = next(
            iter(export_format_extensions.values())
        ).lstrip(".")
        suggestion = viewmodel.get_save_path_suggestion(
            default_ext, context_file_type
        )
        initial_stem = strip_extension(
            suggestion.stem, f".{context_file_type}"
        )
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

Also add the imports at the top of the file (alphabetically sorted into
their groups):

```python
from OTAnalytics.adapter_ui.cancel_export_counts import CancelExportCounts
from OTAnalytics.adapter_ui.cancel_export_file import CancelExportFile
from OTAnalytics.adapter_ui.helpers import strip_extension
```

- [ ] **Step 4: Update `configure_export_counts` cancel exception**

Find the `configure_export_counts` method (around line 200) and change
`raise CancelAddFlow()` to:

```python
        raise CancelExportCounts()
```

- [ ] **Step 5: Run the factory tests**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py -v
```

Expected: 3 PASS.

- [ ] **Step 6: Commit**

```bash
git add OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py \
        tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py
git commit -m "OP#9548: Wire NiceGuiUiFactory to new export DTO + cancel types"
```

---

## Task 6: Wire `ask_for_save_file_path` and `askopenfilename` to the new modes

**Files:**
- Modify: `OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py:85-175`
- Test: `tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py`

- [ ] **Step 1: Add the factory wiring tests**

Append to `tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py`:

```python
class TestAskForSaveFilePath:
    @pytest.mark.asyncio
    async def test_passes_enforce_suffix_true_and_empty_context(
        self,
        factory: NiceGuiUiFactory,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured_kwargs: dict = {}

        def fake_dialog(**kwargs):
            captured_kwargs.update(kwargs)
            d = MagicMock()
            d.result = AsyncMock(return_value=DialogResult.APPLY)()
            d.get_file_path.return_value = Path("/tmp/mydata.otconfig")
            return d

        monkeypatch.setattr(
            "OTAnalytics.plugin_ui.nicegui_gui.ui_factory.FileChooserDialog",
            fake_dialog,
        )

        await factory.ask_for_save_file_path(
            title="Save",
            filetypes=[("otconfig", "*.otconfig")],
            defaultextension=".otconfig",
            initialfile="mydata.otconfig",
            initialdir=Path("/tmp"),
        )

        assert captured_kwargs["enforce_suffix"] is True
        assert captured_kwargs["context_file_type"] == ""


class TestAskOpenFilename:
    @pytest.mark.asyncio
    async def test_passes_enforce_suffix_false(
        self,
        factory: NiceGuiUiFactory,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured_kwargs: dict = {}

        def fake_dialog(**kwargs):
            captured_kwargs.update(kwargs)
            d = MagicMock()
            d.result = AsyncMock(return_value=DialogResult.APPLY)()
            d.get_file_path.return_value = Path("/tmp/some.ottrk")
            return d

        monkeypatch.setattr(
            "OTAnalytics.plugin_ui.nicegui_gui.ui_factory.FileChooserDialog",
            fake_dialog,
        )

        await factory.askopenfilename(
            title="Open",
            filetypes=[("ottrk", "*.ottrk")],
            defaultextension=".ottrk",
        )

        assert captured_kwargs["enforce_suffix"] is False
```

- [ ] **Step 2: Run the new tests to verify they fail**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py -v
```

Expected: failures — the current factory code doesn't pass
`context_file_type` or `enforce_suffix` to `FileChooserDialog`.

- [ ] **Step 3: Update `askopenfilename`**

In `OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py`, locate the
`FileChooserDialog(...)` call inside `askopenfilename` (around line 95) and
add `enforce_suffix=False`:

```python
        dialog = FileChooserDialog(
            resource_manager=self._resource_manager,
            title=title,
            file_extensions=file_extensions,
            initial_file_stem="",
            extension_options=extension_options,
            enforce_suffix=False,
        )
```

- [ ] **Step 4: Update `ask_for_save_file_path`**

In `OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py`, locate the
`FileChooserDialog(...)` call inside `ask_for_save_file_path` (around line
164) and pass the new params:

```python
        dialog = FileChooserDialog(
            resource_manager=self._resource_manager,
            title=title,
            file_extensions=file_extensions,
            initial_file_stem=Path(initialfile).stem,
            initial_dir=initialdir,
            context_file_type="",
            enforce_suffix=True,
        )
```

- [ ] **Step 5: Run the full factory test file**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py -v
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py \
        tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py
git commit -m "OP#9548: Pass enforce_suffix and context to FileChooserDialog from factory"
```

---

## Task 7: Verify the whole NiceGUI test surface and pre-commit

**Why:** Catch any cross-file fallout (resource keys, marker imports, leftover
`from_file_path` usage) before declaring done.

- [ ] **Step 1: Run the full NiceGUI plugin test tree**

```bash
uv run pytest tests/unit/OTAnalytics/plugin_ui -v
```

Expected: all PASS. If failures surface, fix at the smallest scope and
re-run.

- [ ] **Step 2: Run pre-commit on the touched files**

```bash
uv run pre-commit run --files \
    OTAnalytics/adapter_ui/helpers.py \
    OTAnalytics/plugin_ui/nicegui_gui/dialogs/file_chooser_dialog.py \
    OTAnalytics/plugin_ui/nicegui_gui/dialogs/export_counts_dialog.py \
    OTAnalytics/plugin_ui/nicegui_gui/ui_factory.py \
    tests/unit/OTAnalytics/adapter_ui/test_helpers.py \
    tests/unit/OTAnalytics/plugin_ui/test_file_chooser_dialog.py \
    tests/unit/OTAnalytics/plugin_ui/test_export_counts_dialog.py \
    tests/unit/OTAnalytics/plugin_ui/nicegui_gui/test_ui_factory.py
```

Expected: all hooks PASS (mypy, black, isort, flake8). If any hook fails
because it modified files, re-stage and re-run.

- [ ] **Step 3: Run the full project mypy to confirm no regression**

```bash
uv run mypy OTAnalytics tests
```

Expected: no errors. The pre-existing 4 errors in
`export_counts_dialog.py` / `test_export_counts_dialog.py` should be gone.

- [ ] **Step 4: Manually sanity-check the GUI (golden path)**

This is a UI feature — type-check and unit tests verify code correctness, not
the user experience. Start the dev server, open a project with tracks, and
exercise each export:

```bash
uv run python OTAnalytics/main.py
```

Trigger each of these and confirm the dialog shows a stem field next to a
greyed/read-only suffix badge with the expected text:

- Export Events → suffix `.events.csv`.
- Export Road User Assignments → suffix `.road_user_assignments.csv`.
- Export Track Statistics → suffix `.track_statistics.csv`.
- Export Counts → suffix `.counts_15min.csv`; bump the interval to 30 and
  confirm the badge updates to `.counts_30min.csv`.
- Save Configuration → suffix `.otconfig`; switch the format to otflow and
  confirm the badge becomes `.otflow`.

If a flow cannot be exercised (e.g. no tracks available in the test data),
state that explicitly rather than claiming success.

- [ ] **Step 5: Commit (if any pre-commit auto-fixes were applied)**

If pre-commit modified files, stage the changes and commit:

```bash
git add -u
git commit -m "OP#9548: Apply pre-commit fixes"
```

If no changes, skip this step.

---

## Self-review notes (for the implementer's reference)

These were verified by the plan author against the spec; the implementer
does not need to re-check unless they suspect drift.

- Every spec section maps to a task: helper fix → Task 1; FileChooserDialog
  three modes → Tasks 2–3 + Task 6; ExportCountsDialog rewrite → Task 4;
  factory wiring → Tasks 5–6; bundled bug fixes → Tasks 4 (mypy errors,
  return type) + 5 (cancel exception types).
- Type/name consistency: `FormFieldText` accepts `readonly: bool`
  (`forms.py:210`); `set_value` exists (`forms.py:135-143`); all new field
  names (`_filename_stem_field`, `_filename_suffix_field`,
  `MARKER_FILENAME_STEM`, `MARKER_FILENAME_SUFFIX`) are used consistently
  across tasks.
- No placeholders: every code step contains the actual code to write.
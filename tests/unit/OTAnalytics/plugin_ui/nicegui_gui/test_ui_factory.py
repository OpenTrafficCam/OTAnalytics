from dataclasses import dataclass
from typing import Callable

from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import build_file_extensions

OTCONFIG_FILETYPES = [("otconfig file", "*.otconfig")]
DOTTED_FILETYPES = [("CSV", ".csv")]
BARE_FILETYPES = [("CSV", "csv")]
MIXED_FILETYPES = [
    ("otflow file", "*.otflow"),
    ("otconfig file", "*.otconfig"),
]


@dataclass
class GivenFileExtensions:
    filetypes: list[tuple[str, str]]


def create_given(
    filetypes: list[tuple[str, str]] = OTCONFIG_FILETYPES,
) -> GivenFileExtensions:
    return GivenFileExtensions(filetypes=filetypes)


def create_target() -> Callable[..., dict[str, str]]:
    return build_file_extensions


class TestBuildFileExtensions:
    def test_strips_wildcard_from_glob_pattern(self) -> None:
        """A ``*.otconfig`` pattern must yield a bare ``otconfig`` extension.

        Leaving the wildcard in place caused saved files to be named
        ``project.*otconfig.otconfig`` (regression for OP#9548).
        """
        given = create_given(OTCONFIG_FILETYPES)
        target = create_target()

        result = target(given.filetypes)

        assert result == {"otconfig file": "otconfig"}

    def test_strips_leading_dot_extension(self) -> None:
        given = create_given(DOTTED_FILETYPES)
        target = create_target()

        result = target(given.filetypes)

        assert result == {"CSV": "csv"}

    def test_keeps_bare_extension_unchanged(self) -> None:
        given = create_given(BARE_FILETYPES)
        target = create_target()

        result = target(given.filetypes)

        assert result == {"CSV": "csv"}

    def test_cleans_every_filetype(self) -> None:
        given = create_given(MIXED_FILETYPES)
        target = create_target()

        result = target(given.filetypes)

        assert result == {"otflow file": "otflow", "otconfig file": "otconfig"}

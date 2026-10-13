"""Local-filesystem implementations of the input file providers."""

from pathlib import Path

from OTAnalytics.adapter_ui.ui_factory import UiFactory
from OTAnalytics.application.config import SUPPORTED_VIDEO_FILE_TYPES
from OTAnalytics.application.orthophoto import ProvideOrthophoto
from OTAnalytics.application.use_cases.provide_input_files import (
    ProvideTrackFiles,
    ProvideVideoFiles,
)

ALL_FILE_ENDINGS = "All File Endings"
ORTHOPHOTO_EXTENSIONS = [".tif", ".tiff"]
ORTHOPHOTO_FILE_TYPES = [
    (f"orthophoto ({extension})", f"*{extension}")
    for extension in ORTHOPHOTO_EXTENSIONS
]
ORTHOPHOTO_DEFAULT_EXTENSION = ORTHOPHOTO_EXTENSIONS[0]
NO_FILE_CHOSEN = ""


class LocalTrackFileProvider(ProvideTrackFiles):
    """Asks the user to pick ottrk files from the local filesystem.

    Args:
        ui_factory (UiFactory): builds the file chooser for the active front-end.
    """

    def __init__(self, ui_factory: UiFactory) -> None:
        self._ui_factory = ui_factory

    async def provide(self) -> list[Path]:
        return await self._ui_factory.askopenfilenames(
            title="Load track files",
            filetypes=[("tracks file", "*.ottrk")],
        )


class LocalVideoFileProvider(ProvideVideoFiles):
    """Asks the user to pick video files from the local filesystem.

    Args:
        ui_factory (UiFactory): builds the file chooser for the active front-end.
    """

    def __init__(self, ui_factory: UiFactory) -> None:
        self._ui_factory = ui_factory

    async def provide(self) -> list[Path]:
        return await self._ui_factory.askopenfilenames(
            title="Load video files",
            filetypes=[("video file", SUPPORTED_VIDEO_FILE_TYPES)],
            extension_options=_extension_options(SUPPORTED_VIDEO_FILE_TYPES),
        )


class LocalOrthophotoProvider(ProvideOrthophoto):
    """Asks the user for the Orthophoto of Geo-only Track Files being loaded.

    Args:
        ui_factory (UiFactory): builds the file chooser for the active front-end.
    """

    def __init__(self, ui_factory: UiFactory) -> None:
        self._ui_factory = ui_factory

    async def provide(self) -> Path | None:
        chosen = await self._ui_factory.askopenfilename(
            title="Choose the orthophoto for these track files",
            filetypes=ORTHOPHOTO_FILE_TYPES,
            defaultextension=ORTHOPHOTO_DEFAULT_EXTENSION,
            extension_options=_extension_options(ORTHOPHOTO_EXTENSIONS),
        )
        if chosen == NO_FILE_CHOSEN:
            return None
        return Path(chosen)


def _extension_options(extensions: list[str]) -> dict[str, list[str] | None]:
    """One entry offering every given extension, then one per extension.

    Without these options the file picker falls back to its otflow/otconfig filter
    and hides every other file.
    """
    options: dict[str, list[str] | None] = {ALL_FILE_ENDINGS: list(extensions)}
    for extension in extensions:
        options[extension] = [extension]
    return options

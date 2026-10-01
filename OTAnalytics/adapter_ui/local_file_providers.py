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
ORTHOPHOTO_FILE_TYPES = [("orthophoto", "*.tif"), ("orthophoto", "*.tiff")]
ORTHOPHOTO_DEFAULT_EXTENSION = ".tif"
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
            extension_options=_video_extension_options(),
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
        )
        if chosen == NO_FILE_CHOSEN:
            return None
        return Path(chosen)


def _video_extension_options() -> dict[str, list[str] | None]:
    """One entry offering every supported type, then one per type."""
    options: dict[str, list[str] | None] = {
        ALL_FILE_ENDINGS: list(SUPPORTED_VIDEO_FILE_TYPES)
    }
    for extension in SUPPORTED_VIDEO_FILE_TYPES:
        options[extension] = [extension]
    return options

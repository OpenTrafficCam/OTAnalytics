"""Obtaining the track and video files a user wants loaded.

The seam that lets input files come from somewhere other than the local
filesystem. Each implementation owns its own way of asking the user what to
load, so nothing downstream — neither `LoadTrackFiles` nor the view model —
needs to know where the files came from.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class ProvideTrackFiles(ABC):
    """Obtains the track files to load."""

    @abstractmethod
    async def provide(self) -> list[Path]:
        """Ask the user which track files to load.

        Returns:
            list[Path]: the files to load, empty if the user chose none.
        """
        raise NotImplementedError


class ProvideVideoFiles(ABC):
    """Obtains the video files to load."""

    @abstractmethod
    async def provide(self) -> list[Path]:
        """Ask the user which video files to load.

        Returns:
            list[Path]: the files to load, empty if the user chose none.
        """
        raise NotImplementedError

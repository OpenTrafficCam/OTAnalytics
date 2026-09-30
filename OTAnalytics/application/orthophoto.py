"""Everything a project needs to place Geo-only Track Files on its Orthophoto."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

from OTAnalytics.application.state import CurrentOrthophoto
from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.orthophoto import (
    Orthophoto,
    OrthophotoLocked,
    OrthophotoNotFound,
    OrthophotoRequired,
)
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track_repository import TrackRepository

# The CRS OTFusion's default geo offset shifts local world coordinates into.
# Files written before OTFusion declared its CRS (OTCloud OP#10404) are assumed
# to be in it.
FALLBACK_GEO_CRS = "EPSG:25833"
ORTHOPHOTO_REQUIRED = (
    "These track files place road users only by geo coordinates, so they need an"
    " orthophoto to be shown and counted. Nothing was loaded."
)
ORTHOPHOTO_LOCKED = (
    "An orthophoto can only be chosen for a project without sections or tracks,"
    " because sections are drawn on it. Start a new project to use this"
    " orthophoto. Nothing was loaded."
)
MIXED_TRACK_FILES = (
    "This project shows an orthophoto, so it can only hold track files that place"
    " road users by geo coordinates. Track files with their own video belong in a"
    " separate project. Nothing was loaded."
)


class ProvideOrthophotoGeoreference(ABC):
    """Tells where the project's Orthophoto lies, in the tracks' CRS."""

    @abstractmethod
    def for_crs(self, crs: str) -> GeoreferenceMetadata:
        """The pixel-geo mapping of the current Orthophoto.

        Args:
            crs (str): the CRS of the tracks' geo coordinates.

        Returns:
            GeoreferenceMetadata: bounds in `crs` and the image size.

        Raises:
            OrthophotoRequired: if the project has no Orthophoto.
        """
        raise NotImplementedError


class NoOrthophotoGeoreference(ProvideOrthophotoGeoreference):
    """For parsers that are never given an Orthophoto."""

    def for_crs(self, crs: str) -> GeoreferenceMetadata:
        raise OrthophotoRequired(ORTHOPHOTO_REQUIRED)


ReadOrthophotoGeoreference = Callable[[Path, str], GeoreferenceMetadata]


class CurrentOrthophotoGeoreference(ProvideOrthophotoGeoreference):
    """The mapping of whichever Orthophoto the project currently shows.

    Cached per file and CRS: every parsed file asks, and reading a GeoTIFF's
    header is not free. Called from the parsing worker thread; it only reads
    state and fills a dict, which is safe there.

    Args:
        current_orthophoto (CurrentOrthophoto): the project's Orthophoto.
        read_georeference (ReadOrthophotoGeoreference): reads a file's mapping.
    """

    def __init__(
        self,
        current_orthophoto: CurrentOrthophoto,
        read_georeference: ReadOrthophotoGeoreference,
    ) -> None:
        self._current_orthophoto = current_orthophoto
        self._read_georeference = read_georeference
        self._cache: dict[tuple[Path, str], GeoreferenceMetadata] = {}

    def for_crs(self, crs: str) -> GeoreferenceMetadata:
        if (orthophoto := self._current_orthophoto.get()) is None:
            raise OrthophotoRequired(ORTHOPHOTO_REQUIRED)
        key = (orthophoto.file, crs)
        if key not in self._cache:
            self._cache[key] = self._read_georeference(orthophoto.file, crs)
        return self._cache[key]


class ProvideOrthophoto(ABC):
    """Asks the user for an Orthophoto while loading, where that is possible."""

    @abstractmethod
    async def provide(self) -> Path | None:
        """Ask for the Orthophoto of the track files being loaded.

        Returns:
            Path | None: the chosen file, or None when there is none.
        """
        raise NotImplementedError


class NoOrthophotoToProvide(ProvideOrthophoto):
    """Where the Orthophoto can only come from the otconfig, as in S3 mode."""

    async def provide(self) -> Path | None:
        return None


class ChooseOrthophoto:
    """Makes a file the project's Orthophoto, while that is still possible.

    Sections are stored as pixels on the Orthophoto (ADR 0005), so once any exist,
    or tracks were placed on it, a different image would silently move them.
    """

    def __init__(
        self,
        current_orthophoto: CurrentOrthophoto,
        section_repository: SectionRepository,
        track_repository: TrackRepository,
    ) -> None:
        self._current_orthophoto = current_orthophoto
        self._section_repository = section_repository
        self._track_repository = track_repository

    def choose(self, file: Path) -> None:
        """Show `file` behind the project's tracks.

        Args:
            file (Path): the GeoTIFF.

        Raises:
            OrthophotoLocked: if the project has sections or tracks.
        """
        if self._has_sections_or_tracks():
            raise OrthophotoLocked(ORTHOPHOTO_LOCKED)
        self._current_orthophoto.set(Orthophoto(file=file))

    def _has_sections_or_tracks(self) -> bool:
        return bool(self._section_repository.get_all()) or (
            not self._track_repository.get_all().empty
        )


class ResolveMissingOrthophoto:
    """Gets an Orthophoto for Geo-only Track Files that arrived without one."""

    def __init__(
        self, provide_orthophoto: ProvideOrthophoto, choose_orthophoto: ChooseOrthophoto
    ) -> None:
        self._provide_orthophoto = provide_orthophoto
        self._choose_orthophoto = choose_orthophoto

    async def resolve(self) -> None:
        """Ask for an Orthophoto and make it the project's.

        Raises:
            OrthophotoRequired: if none is provided.
            OrthophotoLocked: if the project can no longer take one.
        """
        if (file := await self._provide_orthophoto.provide()) is None:
            raise OrthophotoRequired(ORTHOPHOTO_REQUIRED)
        self._choose_orthophoto.choose(file)


class ObtainOrthophoto(ABC):
    """Makes the Orthophoto an otconfig declares available as a local file."""

    @abstractmethod
    async def obtain(self, reference: Path, base_folder: Path) -> Path:
        """Obtain the declared Orthophoto.

        Args:
            reference (Path): the path the otconfig declares.
            base_folder (Path): the otconfig's folder.

        Returns:
            Path: the local file.

        Raises:
            OrthophotoNotFound: if it cannot be obtained.
        """
        raise NotImplementedError


class LocalObtainOrthophoto(ObtainOrthophoto):
    """The Orthophoto lies on disk next to the otconfig, as videos do."""

    async def obtain(self, reference: Path, base_folder: Path) -> Path:
        file = base_folder / reference
        if not file.exists():
            raise OrthophotoNotFound(
                f"The project's orthophoto '{file}' does not exist. Nothing was"
                " loaded."
            )
        return file

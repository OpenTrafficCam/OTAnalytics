"""Everything a project needs to place Geo-only Track Files on its Orthophoto."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

from OTAnalytics.application.state import CurrentOrthophoto
from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.orthophoto import (
    MixedTrackFiles,
    Orthophoto,
    OrthophotoLocked,
    OrthophotoNotFound,
    OrthophotoRequired,
)
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.domain.track_repository import TrackRepository
from OTAnalytics.domain.video import VideoRepository

ORTHOPHOTO_REQUIRED = (
    "These track files place road users only by geo coordinates, so they need an"
    " orthophoto to be shown and counted. Nothing was loaded."
)
ORTHOPHOTO_LOCKED = (
    "An orthophoto can only be chosen for a project without sections, tracks or"
    " videos, because sections are drawn on it. Start a new project to use this"
    " orthophoto. Nothing was loaded."
)
MIXED_TRACK_FILES = (
    "This project shows an orthophoto, so it can only hold track files that place"
    " road users by geo coordinates. Track files with their own video belong in a"
    " separate project. Nothing was loaded."
)
VIDEOS_BESIDE_ORTHOPHOTO = (
    "This project shows an orthophoto, so it cannot hold videos. Videos and the"
    " track files made from them belong in a separate project. Nothing was loaded."
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
        """Refuse, as there is never an Orthophoto here.

        Args:
            crs (str): the CRS of the tracks' geo coordinates.

        Raises:
            OrthophotoRequired: always.
        """
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
        """The pixel-geo mapping of the current Orthophoto.

        Args:
            crs (str): the CRS of the tracks' geo coordinates.

        Returns:
            GeoreferenceMetadata: bounds in `crs` and the image size.

        Raises:
            OrthophotoRequired: if the project has no Orthophoto.
        """
        if (orthophoto := self._current_orthophoto.get()) is None:
            raise OrthophotoRequired(ORTHOPHOTO_REQUIRED)
        key = (orthophoto.file, crs)
        if key not in self._cache:
            self._cache[key] = self._read_georeference(orthophoto.file, crs)
        return self._cache[key]


ReadOrthophotoImage = Callable[[Path], TrackImage]


class CurrentOrthophotoImage:
    """The current Orthophoto's pixels, read once per file.

    Args:
        current_orthophoto (CurrentOrthophoto): the project's Orthophoto.
        read_image (ReadOrthophotoImage): reads a file's pixels.
    """

    def __init__(
        self, current_orthophoto: CurrentOrthophoto, read_image: ReadOrthophotoImage
    ) -> None:
        self._current_orthophoto = current_orthophoto
        self._read_image = read_image
        self._cached: tuple[Path, TrackImage] | None = None

    def get(self) -> TrackImage | None:
        """The Orthophoto's image.

        Returns:
            TrackImage | None: the pixels, or None without an Orthophoto.
        """
        if (orthophoto := self._current_orthophoto.get()) is None:
            return None
        if self._cached is None or self._cached[0] != orthophoto.file:
            self._cached = (orthophoto.file, self._read_image(orthophoto.file))
        return self._cached[1]


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
    or tracks were placed on it, a different image would silently move them. A
    project with videos places its tracks on those instead.
    """

    def __init__(
        self,
        current_orthophoto: CurrentOrthophoto,
        section_repository: SectionRepository,
        track_repository: TrackRepository,
        video_repository: VideoRepository,
    ) -> None:
        self._current_orthophoto = current_orthophoto
        self._section_repository = section_repository
        self._track_repository = track_repository
        self._video_repository = video_repository

    def choose(self, file: Path) -> None:
        """Show `file` behind the project's tracks.

        Args:
            file (Path): the GeoTIFF.

        Raises:
            OrthophotoLocked: if the project has sections, tracks or videos.
        """
        if self._has_sections_tracks_or_videos():
            raise OrthophotoLocked(ORTHOPHOTO_LOCKED)
        self._current_orthophoto.set(Orthophoto(file=file))

    def _has_sections_tracks_or_videos(self) -> bool:
        return (
            not self._section_repository.is_empty()
            or not self._track_repository.is_empty()
            or not self._video_repository.is_empty()
        )


LoadVideoFiles = Callable[[list[Path]], None]


class AddVideoFiles:
    """Adds videos to a project, unless it shows an Orthophoto (ADR 0005).

    Args:
        load_video_files (LoadVideoFiles): loads the videos into the project.
        current_orthophoto (CurrentOrthophoto): the project's Orthophoto.
    """

    def __init__(
        self, load_video_files: LoadVideoFiles, current_orthophoto: CurrentOrthophoto
    ) -> None:
        self._load_video_files = load_video_files
        self._current_orthophoto = current_orthophoto

    def add(self, files: list[Path]) -> None:
        """Load `files` as the project's videos.

        Args:
            files (list[Path]): the video files.

        Raises:
            MixedTrackFiles: if the project shows an Orthophoto.
        """
        if self._current_orthophoto.get() is not None:
            raise MixedTrackFiles(VIDEOS_BESIDE_ORTHOPHOTO)
        self._load_video_files(files)


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

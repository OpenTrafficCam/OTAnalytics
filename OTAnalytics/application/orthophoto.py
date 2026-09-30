"""Everything a project needs to place Geo-only Track Files on its Orthophoto."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

from OTAnalytics.application.state import CurrentOrthophoto
from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.orthophoto import OrthophotoRequired

# The CRS OTFusion's default geo offset shifts local world coordinates into.
# Files written before OTFusion declared its CRS (OTCloud OP#10404) are assumed
# to be in it.
FALLBACK_GEO_CRS = "EPSG:25833"
ORTHOPHOTO_REQUIRED = (
    "These track files place road users only by geo coordinates, so they need an"
    " orthophoto to be shown and counted. Nothing was loaded."
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

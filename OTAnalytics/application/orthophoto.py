"""Everything a project needs to place Geo-only Track Files on its Orthophoto."""

from abc import ABC, abstractmethod

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

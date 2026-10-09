"""The Orthophoto a project shows behind its Geo-only Track Files."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Orthophoto:
    """A georeferenced aerial image of a site.

    Attributes:
        file (Path): the local file to read.
        reference (Path | None): the path as the otconfig declares it, relative
            to the otconfig. None when the user picked the file and no otconfig
            has named it yet.
    """

    file: Path
    reference: Path | None = None


class OrthophotoError(Exception):
    """Base for every reason Geo-only Track Files cannot be placed."""


class OrthophotoRequired(OrthophotoError):
    """Geo-only Track Files were loaded, but the project has no Orthophoto."""


class OrthophotoLocked(OrthophotoError):
    """An Orthophoto was chosen for a project that already has Sections or Tracks."""


class MixedTrackFiles(OrthophotoError):
    """Camera Track Files were loaded into a project that shows an Orthophoto."""


class MissingGeoCoordinatesCrs(OrthophotoError):
    """A Geo-only Track File does not say which CRS its geo coordinates are in."""


class OrthophotoNotFound(OrthophotoError):
    """The Orthophoto the project declares cannot be obtained."""


class UnsupportedOrthophoto(OrthophotoError):
    """The Orthophoto file cannot be used as a georeferenced background."""

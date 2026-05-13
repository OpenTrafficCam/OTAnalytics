"""Domain model for georeference BEV coordinate metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeoreferenceMetadata:
    """Geo-referencing metadata from a georeferenced ottrk file.

    Describes the affine mapping between BEV pixel coordinates and UTM
    geo coordinates for a single ottrk output file.

    Attributes:
        geo_min_x: West boundary in UTM easting (metres).
        geo_min_y: South boundary in UTM northing (metres).
        geo_max_x: East boundary in UTM easting (metres).
        geo_max_y: North boundary in UTM northing (metres).
        birds_eye_view_width: Width of the BEV image in pixels.
        birds_eye_view_height: Height of the BEV image in pixels.
        padding: Pixel padding applied to all edges of the BEV image.
        crs: Coordinate reference system as a WKT or authority string.
    """

    geo_min_x: float
    geo_min_y: float
    geo_max_x: float
    geo_max_y: float
    birds_eye_view_width: int
    birds_eye_view_height: int
    padding: int
    crs: str


def pixel_to_geo(
    x: float, y: float, metadata: GeoreferenceMetadata
) -> tuple[float, float]:
    """Convert a BEV pixel coordinate to UTM geo coordinate.

    Args:
        x: Pixel x coordinate (column, increases rightward).
        y: Pixel y coordinate (row, increases downward).
        metadata: Georeference metadata containing geo bounds and image size.

    Returns:
        Tuple (geo_x, geo_y) in the same UTM coordinate system as the
        per-detection geo_x/geo_y fields.
    """
    scale_x = (metadata.geo_max_x - metadata.geo_min_x) / (
        metadata.birds_eye_view_width - 2 * metadata.padding
    )
    scale_y = (metadata.geo_max_y - metadata.geo_min_y) / (
        metadata.birds_eye_view_height - 2 * metadata.padding
    )
    geo_x = metadata.geo_min_x + (x - metadata.padding) * scale_x
    geo_y = metadata.geo_max_y - (y - metadata.padding) * scale_y
    return geo_x, geo_y

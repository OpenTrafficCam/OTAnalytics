"""Domain model for georeference Birds-Eye-View coordinate metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeoreferenceMetadata:
    """Geo-referencing metadata from a georeferenced ottrk file.

    Describes the affine mapping between Birds-Eye-View pixel coordinates and UTM
    geo coordinates for a single ottrk output file.

    Attributes:
        geo_min_x (float): West boundary in UTM easting (metres).
        geo_min_y (float): South boundary in UTM northing (metres).
        geo_max_x (float): East boundary in UTM easting (metres).
        geo_max_y (float): North boundary in UTM northing (metres).
        birds_eye_view_width (int): Width of the BEV image in pixels.
        birds_eye_view_height (int): Height of the BEV image in pixels.
        padding (int): Pixel padding applied to all edges of the BEV image.
        crs (str): Coordinate reference system as a WKT or authority string.
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
    """Convert a Birds-Eye-View pixel coordinate to UTM geo coordinate.

    Args:
        x (float): Pixel x coordinate (column, increases rightward).
        y (float): Pixel y coordinate (row, increases downward).
        metadata (GeoreferenceMetadata): Metadata containing geo bounds and image size.

    Returns:
        Tuple[float, float] in the same UTM coordinate system as the per-detection
        geo_x/geo_y fields.
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

"""Domain model for OTFusion BEV coordinate metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OtfusionMetadata:
    """Geo-referencing metadata from an OTFusion ottrk file.

    Describes the affine mapping between BEV pixel coordinates and UTM
    geo coordinates for a single OTFusion output file.

    Attributes:
        geo_min_x: West boundary in UTM easting (metres).
        geo_min_y: South boundary in UTM northing (metres).
        geo_max_x: East boundary in UTM easting (metres).
        geo_max_y: North boundary in UTM northing (metres).
        bev_width: Width of the BEV image in pixels.
        bev_height: Height of the BEV image in pixels.
        padding: Pixel padding applied to all edges of the BEV image.
    """

    geo_min_x: float
    geo_min_y: float
    geo_max_x: float
    geo_max_y: float
    bev_width: int
    bev_height: int
    padding: int


def pixel_to_geo(x: float, y: float, metadata: OtfusionMetadata) -> tuple[float, float]:
    """Convert a BEV pixel coordinate to UTM geo coordinate.

    Args:
        x: Pixel x coordinate (column, increases rightward).
        y: Pixel y coordinate (row, increases downward).
        metadata: OTFusion metadata containing geo bounds and image size.

    Returns:
        Tuple (geo_x, geo_y) in the same UTM coordinate system as the
        per-detection geo_x/geo_y fields.
    """
    scale_x = (metadata.geo_max_x - metadata.geo_min_x) / (
        metadata.bev_width - 2 * metadata.padding
    )
    scale_y = (metadata.geo_max_y - metadata.geo_min_y) / (
        metadata.bev_height - 2 * metadata.padding
    )
    geo_x = metadata.geo_min_x + (x - metadata.padding) * scale_x
    geo_y = metadata.geo_max_y - (y - metadata.padding) * scale_y
    return geo_x, geo_y

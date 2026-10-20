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

    @property
    def units_per_pixel_x(self) -> float:
        """Geo units covered by one pixel horizontally."""
        return (self.geo_max_x - self.geo_min_x) / (
            self.birds_eye_view_width - 2 * self.padding
        )

    @property
    def units_per_pixel_y(self) -> float:
        """Geo units covered by one pixel vertically."""
        return (self.geo_max_y - self.geo_min_y) / (
            self.birds_eye_view_height - 2 * self.padding
        )


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
    geo_x = metadata.geo_min_x + (x - metadata.padding) * metadata.units_per_pixel_x
    geo_y = metadata.geo_max_y - (y - metadata.padding) * metadata.units_per_pixel_y
    return geo_x, geo_y


@dataclass(frozen=True)
class PixelTransform:
    """Axis-aligned affine map from geo to pixel coordinates.

    `pixel_x = scale_x * geo_x + offset_x`, likewise for y. Exposed so that
    vectorised callers apply the same mapping as `geo_to_pixel` without
    re-deriving it.
    """

    scale_x: float
    offset_x: float
    scale_y: float
    offset_y: float


def geo_to_pixel_transform(metadata: GeoreferenceMetadata) -> PixelTransform:
    """Invert `pixel_to_geo` into an affine transform.

    Args:
        metadata (GeoreferenceMetadata): geo bounds and image size.

    Returns:
        PixelTransform: maps geo coordinates onto the image's pixels.
    """
    scale_x = 1 / metadata.units_per_pixel_x
    scale_y = -1 / metadata.units_per_pixel_y
    return PixelTransform(
        scale_x=scale_x,
        offset_x=metadata.padding - metadata.geo_min_x * scale_x,
        scale_y=scale_y,
        offset_y=metadata.padding - metadata.geo_max_y * scale_y,
    )


def geo_to_pixel(
    geo_x: float, geo_y: float, metadata: GeoreferenceMetadata
) -> tuple[float, float]:
    """Convert a geo coordinate to a pixel coordinate of the georeferenced image.

    Args:
        geo_x (float): easting in the metadata's CRS.
        geo_y (float): northing in the metadata's CRS.
        metadata (GeoreferenceMetadata): geo bounds and image size.

    Returns:
        tuple[float, float]: pixel column and row; may lie outside the image.
    """
    transform = geo_to_pixel_transform(metadata)
    return (
        transform.scale_x * geo_x + transform.offset_x,
        transform.scale_y * geo_y + transform.offset_y,
    )

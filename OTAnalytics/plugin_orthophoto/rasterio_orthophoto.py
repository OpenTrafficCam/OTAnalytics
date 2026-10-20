"""Reading an Orthophoto's georeference and pixels with rasterio."""

from pathlib import Path

import numpy
import rasterio
from PIL import Image
from rasterio.coords import BoundingBox
from rasterio.errors import RasterioIOError
from rasterio.warp import transform

from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.domain.orthophoto import OrthophotoNotFound, UnsupportedOrthophoto
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_prototypes.track_visualization.pil_image import PilImage

NO_PADDING = 0
NO_ROTATION = 0.0
BAND_AXIS = 0
LAST_AXIS = -1
SUPPORTED_DTYPE = "uint8"
GREYSCALE = "L"
MODE_BY_BAND_COUNT = {1: GREYSCALE, 3: "RGB", 4: "RGBA"}
# How far a reprojected corner may stray from an upright rectangle, in pixels.
MAX_CORNER_DEVIATION_IN_PIXELS = 0.5
HALF = 0.5


def read_orthophoto_georeference(file: Path, crs: str) -> GeoreferenceMetadata:
    """Describe where the Orthophoto lies, in the CRS of the tracks.

    Tracks and Orthophoto may use different CRSs. The image's corners and centre
    are reprojected into the tracks' CRS. Only if they still form an upright
    rectangle, within half a pixel, can bounds describe the image there; this
    holds for a shifted CRS, but not for one turned against the tracks' CRS such
    as a neighbouring UTM zone.

    Args:
        file (Path): the GeoTIFF.
        crs (str): the CRS of the tracks' geo coordinates.

    Returns:
        GeoreferenceMetadata: bounds in `crs`, raster size, no padding.

    Raises:
        OrthophotoNotFound: if the file cannot be opened.
        UnsupportedOrthophoto: if it has no CRS, is rotated, or its CRS is too
            different from `crs`.
    """
    with _open(file) as dataset:
        if dataset.crs is None:
            raise UnsupportedOrthophoto(
                f"The orthophoto '{file.name}' is not georeferenced."
            )
        affine = dataset.transform
        if affine.b != NO_ROTATION or affine.d != NO_ROTATION:
            raise UnsupportedOrthophoto(
                f"The orthophoto '{file.name}' is rotated, which is not supported."
            )
        bounds = _reproject_upright_bounds(dataset, crs)
        if bounds is None:
            raise UnsupportedOrthophoto(
                f"The CRS of the orthophoto '{file.name}' is too different from"
                f" the tracks' CRS. Reproject the orthophoto into {crs}."
            )
        return GeoreferenceMetadata(
            geo_min_x=bounds.left,
            geo_min_y=bounds.bottom,
            geo_max_x=bounds.right,
            geo_max_y=bounds.top,
            birds_eye_view_width=dataset.width,
            birds_eye_view_height=dataset.height,
            padding=NO_PADDING,
            crs=crs,
        )


def _reproject_upright_bounds(
    dataset: rasterio.DatasetReader, crs: str
) -> BoundingBox | None:
    """Bounds of the image in `crs`, or None if it is no upright rectangle there."""
    xs, ys = transform(dataset.crs, crs, *zip(*_corners_and_centre(dataset.bounds)))
    bounds = BoundingBox(left=min(xs), bottom=min(ys), right=max(xs), top=max(ys))
    tolerance_x = MAX_CORNER_DEVIATION_IN_PIXELS * (
        (bounds.right - bounds.left) / dataset.width
    )
    tolerance_y = MAX_CORNER_DEVIATION_IN_PIXELS * (
        (bounds.top - bounds.bottom) / dataset.height
    )
    is_upright = all(
        abs(actual_x - expected_x) <= tolerance_x
        and abs(actual_y - expected_y) <= tolerance_y
        for actual_x, actual_y, (expected_x, expected_y) in zip(
            xs, ys, _corners_and_centre(bounds)
        )
    )
    return bounds if is_upright else None


def _corners_and_centre(bounds: BoundingBox) -> list[tuple[float, float]]:
    return [
        (bounds.left, bounds.top),
        (bounds.right, bounds.top),
        (bounds.left, bounds.bottom),
        (bounds.right, bounds.bottom),
        ((bounds.left + bounds.right) * HALF, (bounds.bottom + bounds.top) * HALF),
    ]


def read_orthophoto_image(file: Path) -> TrackImage:
    """Read the Orthophoto's pixels as a background image.

    Args:
        file (Path): the GeoTIFF.

    Returns:
        TrackImage: the image, one pixel per raster cell.

    Raises:
        OrthophotoNotFound: if the file cannot be opened.
        UnsupportedOrthophoto: if it is not 8-bit greyscale, RGB or RGBA.
    """
    with _open(file) as dataset:
        mode = MODE_BY_BAND_COUNT.get(dataset.count)
        if mode is None or any(dtype != SUPPORTED_DTYPE for dtype in dataset.dtypes):
            raise UnsupportedOrthophoto(
                f"The orthophoto '{file.name}' must be 8-bit greyscale, RGB or RGBA."
            )
        pixels = numpy.moveaxis(dataset.read(), BAND_AXIS, LAST_AXIS)
    if mode == GREYSCALE:
        pixels = pixels.squeeze(axis=LAST_AXIS)
    return PilImage(Image.fromarray(pixels, mode=mode))


def _open(file: Path) -> rasterio.DatasetReader:
    try:
        return rasterio.open(file)
    except RasterioIOError as cause:
        raise OrthophotoNotFound(
            f"The orthophoto '{file}' cannot be opened: {cause}"
        ) from cause

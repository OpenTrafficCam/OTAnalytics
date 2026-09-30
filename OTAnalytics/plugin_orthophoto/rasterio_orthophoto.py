"""Reading an Orthophoto's georeference and pixels with rasterio."""

from pathlib import Path

import numpy
import rasterio
from PIL import Image
from rasterio.errors import RasterioIOError
from rasterio.warp import transform_bounds

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


def read_orthophoto_georeference(file: Path, crs: str) -> GeoreferenceMetadata:
    """Describe where the Orthophoto lies, in the CRS of the tracks.

    Tracks and Orthophoto may use different CRSs. The image's bounds are
    reprojected into the tracks' CRS; over a site of a few hundred metres the
    result is exact for a shifted CRS and accurate far below a pixel otherwise.

    Args:
        file (Path): the GeoTIFF.
        crs (str): the CRS of the tracks' geo coordinates.

    Returns:
        GeoreferenceMetadata: bounds in `crs`, raster size, no padding.

    Raises:
        OrthophotoNotFound: if the file cannot be opened.
        UnsupportedOrthophoto: if it has no CRS or is rotated.
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
        min_x, min_y, max_x, max_y = transform_bounds(dataset.crs, crs, *dataset.bounds)
        return GeoreferenceMetadata(
            geo_min_x=min_x,
            geo_min_y=min_y,
            geo_max_x=max_x,
            geo_max_y=max_y,
            birds_eye_view_width=dataset.width,
            birds_eye_view_height=dataset.height,
            padding=NO_PADDING,
            crs=crs,
        )


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

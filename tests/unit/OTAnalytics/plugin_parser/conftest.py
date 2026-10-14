from OTAnalytics.domain.georeference import GeoreferenceMetadata
from OTAnalytics.plugin_parser import ottrk_dataformat

GEOREF_METADATA = GeoreferenceMetadata(
    geo_min_x=449199.096512522,
    geo_min_y=5699274.275524861,
    geo_max_x=449294.8688478645,
    geo_max_y=5699370.047860203,
    birds_eye_view_width=983,
    birds_eye_view_height=983,
    padding=20,
    crs="EPSG:25833",
)

SAMPLE_GEOREFERENCE_METADATA_DICT = {
    ottrk_dataformat.GEOREFERENCE: {
        ottrk_dataformat.GEO_BOUNDS: {
            ottrk_dataformat.GEO_BOUNDS_MIN_X: GEOREF_METADATA.geo_min_x,
            ottrk_dataformat.GEO_BOUNDS_MIN_Y: GEOREF_METADATA.geo_min_y,
            ottrk_dataformat.GEO_BOUNDS_MAX_X: GEOREF_METADATA.geo_max_x,
            ottrk_dataformat.GEO_BOUNDS_MAX_Y: GEOREF_METADATA.geo_max_y,
        },
        ottrk_dataformat.BIRDS_EYE_VIEW_SIZE: {
            ottrk_dataformat.BIRDS_EYE_VIEW_WIDTH: GEOREF_METADATA.birds_eye_view_width,
            ottrk_dataformat.BIRDS_EYE_VIEW_HEIGHT: (
                GEOREF_METADATA.birds_eye_view_height
            ),
        },
        ottrk_dataformat.BEV_PADDING: GEOREF_METADATA.padding,
        ottrk_dataformat.CRS: GEOREF_METADATA.crs,
    }
}

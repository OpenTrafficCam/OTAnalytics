import OTAnalytics.plugin_parser.ottrk_dataformat as ottrk_format
from OTAnalytics.domain.georeference import GeoreferenceMetadata


class GeoreferenceMetadataParsingMixin:
    @classmethod
    def parse_georeference_metadata(cls, metadata: dict) -> GeoreferenceMetadata | None:
        """Parse the georeference block from ottrk metadata.

        Args:
            metadata: The full metadata dict from an ottrk file.

        Returns:
            GeoreferenceMetadata if the georeference block is present, otherwise None.
        """
        georeference = metadata.get(ottrk_format.GEOREFERENCE)
        if georeference is None:
            return None
        bounds = georeference[ottrk_format.GEO_BOUNDS]
        bev_size = georeference[ottrk_format.BIRDS_EYE_VIEW_SIZE]
        return GeoreferenceMetadata(
            geo_min_x=bounds[ottrk_format.GEO_BOUNDS_MIN_X],
            geo_min_y=bounds[ottrk_format.GEO_BOUNDS_MIN_Y],
            geo_max_x=bounds[ottrk_format.GEO_BOUNDS_MAX_X],
            geo_max_y=bounds[ottrk_format.GEO_BOUNDS_MAX_Y],
            birds_eye_view_width=bev_size[ottrk_format.BIRDS_EYE_VIEW_WIDTH],
            birds_eye_view_height=bev_size[ottrk_format.BIRDS_EYE_VIEW_HEIGHT],
            padding=georeference[ottrk_format.BEV_PADDING],
            crs=georeference[ottrk_format.CRS],
        )

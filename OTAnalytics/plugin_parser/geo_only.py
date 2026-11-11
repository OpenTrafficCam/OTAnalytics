"""The one rule for recognising a Geo-only Track File."""


def is_geo_only(
    has_georeference: bool,
    carries_geo_coordinates: bool,
    declares_geo_coordinates: bool,
) -> bool:
    """Whether a track file places road users by geo coordinates alone.

    The declaration counts on its own because a file without detections, such as
    one written during a quiet period, carries no geo coordinates to look at.

    Args:
        has_georeference (bool): the file maps its pixels to geo coordinates.
        carries_geo_coordinates (bool): its detections have geo_x / geo_y.
        declares_geo_coordinates (bool): its metadata has a geo_coordinates block.

    Returns:
        bool: True for files such as OTFusion's since it stopped writing videos.
    """
    return (carries_geo_coordinates or declares_geo_coordinates) and (
        not has_georeference
    )

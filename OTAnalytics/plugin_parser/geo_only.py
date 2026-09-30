"""The one rule for recognising a Geo-only Track File."""


def is_geo_only(has_georeference: bool, carries_geo_coordinates: bool) -> bool:
    """Whether a track file places road users by geo coordinates alone.

    Args:
        has_georeference (bool): the file maps its pixels to geo coordinates.
        carries_geo_coordinates (bool): its detections have geo_x / geo_y.

    Returns:
        bool: True for files such as OTFusion's since it stopped writing videos.
    """
    return carries_geo_coordinates and not has_georeference

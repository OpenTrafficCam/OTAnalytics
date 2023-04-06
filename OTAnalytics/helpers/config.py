"""
Factor for ...
E.g. (0,0) for top-left corner, (1,0) for top-right corner,
(0,1) for bottom-left corner, (1,1) for bottom-right corner
"""



ENCODING = "UTF-8"
COMPRESSED_FILETYPE = ".bz2"

TRANSFORMED_COORDS = False

bbox_factor_reference = {
    "car": (1, 0.5),
    "bicycle": (0.5, 0.5),
    "truck": (0.5, 0.5),
    "motorcycle": (0.5, 0.5),
    "person": (0.5, 1),
    "bus": (0.5, 0.5),
    "unclear": (0.5,0.5)
}



maincanvas = None
sliderobject = None

from base64 import b64encode

import cv2
from numpy import ndarray

DEFAULT_FORMAT = ".jpg"
DEFAULT_JPEG_QUALITY = 80


def serialize_image(image: ndarray) -> str:
    if image is None:
        return ""
    _, buffer = cv2.imencode(
        DEFAULT_FORMAT,
        image,
        [cv2.IMWRITE_JPEG_QUALITY, DEFAULT_JPEG_QUALITY],
    )
    return b64encode(buffer).decode()

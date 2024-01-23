import bz2
from pathlib import Path

import ujson

ENCODING: str = "UTF-8"


def parse_json_bz2(path: Path) -> dict:
    """Parse JSON bz2.

    Args:
        path (Path): Path to bz2 JSON.

    Returns:
        dict: The content of the JSON file.
    """

    with bz2.open(path, "rt", encoding=ENCODING) as file:
        return ujson.load(file)


def write_json_bz2(data: dict, path: Path) -> None:
    """Serialize JSON bz2.

    Args:
        data (dict): The content of the JSON file.
        path (Path): Path to bz2 JSON.
    """
    with bz2.open(path, "wt", encoding=ENCODING) as file:
        ujson.dump(data, file)


def _parse_json(path: Path) -> dict:
    """Parse JSON.

    Args:
        path (Path): Path to JSON.

    Returns:
        dict: The content of the JSON file.
    """
    with open(path, "rt", encoding=ENCODING) as file:
        return ujson.load(file)


def parse_json(path: Path) -> dict:
    """Parse file as JSON or bzip2 compressed JSON.

    Args:
        path (Path): Path to file

    Returns:
        dict: The content of the JSON file.
    """
    try:
        return _parse_json(path)
    except UnicodeDecodeError:
        return parse_json_bz2(path)


def write_json(data: dict, path: Path) -> None:
    """Serialize JSON.

    Args:
        data (dict): The content of the JSON file.
        path (Path): Path to JSON.
    """
    with open(path, "wt", encoding=ENCODING) as file:
        ujson.dump(data, file, indent=4)

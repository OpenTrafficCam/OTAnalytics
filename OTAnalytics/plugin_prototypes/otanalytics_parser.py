from pathlib import Path

import ujson
from pandas import DataFrame, read_json

ENCODING = "UTF-8"


class JsonParser:
    @staticmethod
    def from_dict(f: Path) -> dict:
        with open(f, "r", encoding=ENCODING) as out:
            eventlist_dict = ujson.load(out)
            return eventlist_dict


class PandasDataFrameParser:
    @staticmethod
    def from_json(f: Path) -> DataFrame:
        return read_json(f)

    @staticmethod
    def from_dict(d: dict, transpose: bool = False) -> DataFrame:
        df = DataFrame(d)
        if transpose:
            return df.transpose()
        return df

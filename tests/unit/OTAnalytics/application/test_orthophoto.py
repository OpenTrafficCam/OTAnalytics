from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.orthophoto import CurrentOrthophotoGeoreference
from OTAnalytics.application.state import CurrentOrthophoto
from OTAnalytics.domain.orthophoto import Orthophoto, OrthophotoRequired

ORTHOPHOTO_FILE = Path("site/map.tiff")
CRS = "EPSG:25833"


@dataclass
class Given:
    current_orthophoto: CurrentOrthophoto
    read_georeference: Mock


def create_given() -> Given:
    return Given(current_orthophoto=CurrentOrthophoto(), read_georeference=Mock())


def setup_default(given: Given) -> Given:
    given.current_orthophoto.set(Orthophoto(file=ORTHOPHOTO_FILE))
    return given


def create_target(given: Given) -> CurrentOrthophotoGeoreference:
    return CurrentOrthophotoGeoreference(
        given.current_orthophoto, given.read_georeference
    )


class TestCurrentOrthophotoGeoreference:
    def test_reads_the_current_orthophoto_in_the_requested_crs(self) -> None:
        given = setup_default(create_given())
        target = create_target(given)

        actual = target.for_crs(CRS)

        given.read_georeference.assert_called_once_with(ORTHOPHOTO_FILE, CRS)
        assert actual == given.read_georeference.return_value

    def test_reads_each_orthophoto_only_once(self) -> None:
        given = setup_default(create_given())
        target = create_target(given)

        target.for_crs(CRS)
        target.for_crs(CRS)

        given.read_georeference.assert_called_once()

    def test_refuses_without_an_orthophoto(self) -> None:
        given = create_given()
        target = create_target(given)

        with pytest.raises(OrthophotoRequired):
            target.for_crs(CRS)


class TestCurrentOrthophoto:
    def test_reset_forgets_the_orthophoto(self) -> None:
        given = setup_default(create_given())

        given.current_orthophoto.reset()

        assert given.current_orthophoto.get() is None

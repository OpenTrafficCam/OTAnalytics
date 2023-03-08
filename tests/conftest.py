import shutil
from pathlib import Path
from typing import Generator, TypeVar

import pytest

T = TypeVar("T")
YieldFixture = Generator[T, None, None]


@pytest.fixture(scope="module")
def test_data_tmp_dir() -> YieldFixture[Path]:
    test_data_tmp_dir = Path(__file__).parent / "data_tmp"
    test_data_tmp_dir.mkdir(exist_ok=True)
    yield test_data_tmp_dir
    shutil.rmtree(test_data_tmp_dir)


@pytest.fixture(scope="module")
def test_data_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="module")
def ottrk_path(test_data_dir: Path) -> Path:
    name = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.ottrk"
    return test_data_dir / name


@pytest.fixture
def cyclist_video(test_data_dir: Path) -> Path:
    name = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
    return test_data_dir / name

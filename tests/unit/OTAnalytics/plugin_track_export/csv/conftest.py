from pathlib import Path

import pytest


@pytest.fixture
def output_file_csv(tmp_path: Path) -> Path:
    return tmp_path / "output.csv"

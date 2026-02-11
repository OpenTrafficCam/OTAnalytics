import bz2
from pathlib import Path

import pytest
import ujson

from OTAnalytics.plugin_parser.json_parser import (
    parse_json,
    parse_json_bz2,
    write_json,
    write_json_bz2,
)


@pytest.fixture
def example_json_bz2(test_data_tmp_dir: Path) -> tuple[Path, dict]:
    bz2_json_file = test_data_tmp_dir / "bz2_file.json"
    bz2_json_file.touch()
    content = {"first_name": "John", "last_name": "Doe"}
    with bz2.open(bz2_json_file, "wt", encoding="UTF-8") as out:
        ujson.dump(content, out)
    return bz2_json_file, content


@pytest.fixture
def example_json(test_data_tmp_dir: Path) -> tuple[Path, dict]:
    json_file = test_data_tmp_dir / "file.json"
    json_file.touch()
    content = {"first_name": "John", "last_name": "Doe"}
    with bz2.open(json_file, "wt", encoding="UTF-8") as out:
        ujson.dump(content, out)
    return json_file, content


def test_parse_compressed_and_uncompressed_section(test_data_tmp_dir: Path) -> None:
    content = {"some": "value", "other": "values"}
    json_file = test_data_tmp_dir / "section.json"
    bzip2_file = test_data_tmp_dir / "section.json.bz2"
    json_file.touch()
    bzip2_file.touch()
    write_json(content, json_file)
    write_json_bz2(content, bzip2_file)
    json_content = parse_json(json_file)
    bzip2_content = parse_json(bzip2_file)

    assert json_content == content
    assert bzip2_content == content


def test_parse_bz2(example_json_bz2: tuple[Path, dict]) -> None:
    example_json_bz2_path, expected_content = example_json_bz2
    result_content = parse_json_bz2(example_json_bz2_path)
    assert result_content == expected_content


def test_parse_bz2_uncompressed_file(example_json: tuple[Path, dict]) -> None:
    example_path, expected_content = example_json
    result_content = parse_json_bz2(example_path)
    assert result_content == expected_content

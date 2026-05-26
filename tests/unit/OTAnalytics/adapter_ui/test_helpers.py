import pytest

from OTAnalytics.adapter_ui.helpers import (
    ensure_file_extension_is_present,
    strip_extension,
)


@pytest.mark.parametrize(
    "input,allowed_extensions,default_extension,expected_result",
    [
        (
            "some-file.file-extension",
            [".file-extension"],
            ".file-extension",
            "some-file.file-extension",
        ),
        (
            "some-file",
            [".file-extension"],
            ".file-extension",
            "some-file.file-extension",
        ),
        (
            "some-file",
            [".file-extension"],
            "file-extension",
            "some-file.file-extension",
        ),
        (
            "path/to/some-file",
            [".file-extension"],
            "file-extension",
            "path/to/some-file.file-extension",
        ),
        (
            "path/to/some-file",
            [".file-extension"],
            "*.file-extension",
            "path/to/some-file.file-extension",
        ),
        (
            "path/to/some-file.file-extension2",
            [".file-extension", ".file-extension2"],
            "*.file-extension",
            "path/to/some-file.file-extension2",
        ),
        (
            "path/to/some-file",
            [".file-extension", ".file-extension2"],
            "*.file-extension",
            "path/to/some-file.file-extension",
        ),
        (
            "path/to/some-file.file-extension",
            [],
            "*.file-extension",
            "path/to/some-file.file-extension",
        ),
        (
            "path/to/some-file",
            [],
            "*.file-extension",
            "path/to/some-file.file-extension",
        ),
        (
            "",
            [],
            "*.file-extension",
            "",
        ),
    ],
)
def test_ensure_file_extension_is_appended(
    input: str,
    allowed_extensions: list[str],
    default_extension: str,
    expected_result: str,
) -> None:
    actual_result = ensure_file_extension_is_present(
        input, allowed_extensions, default_extension
    )

    assert actual_result == expected_result


@pytest.mark.parametrize(
    "file_name,extension,expected",
    [
        ("mydata.events.csv", ".events.csv", "mydata"),
        (
            "my_data.track_statistics.csv",
            ".track_statistics.csv",
            "my_data",
        ),
        (
            "trip_summary.road_user_assignments.csv",
            ".road_user_assignments.csv",
            "trip_summary",
        ),
        ("unrelated.csv", ".events.csv", "unrelated.csv"),
        ("aaa", "a", "aa"),
        ("", ".events.csv", ""),
        ("mydata.events.csv", "", "mydata.events.csv"),
    ],
)
def test_strip_extension_removes_literal_suffix(
    file_name: str, extension: str, expected: str
) -> None:
    assert strip_extension(file_name, extension) == expected

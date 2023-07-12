from pathlib import Path

import pytest

from OTAnalytics.adapter_ui.helpers import ensure_file_extension_is_present


@pytest.mark.parametrize(
    "input,extension,expected_result",
    [
        (
            "some-file.file-extension",
            ".file-extension",
            Path("some-file.file-extension"),
        ),
        (
            "some-file",
            ".file-extension",
            Path("some-file.file-extension"),
        ),
        (
            "some-file",
            "file-extension",
            Path("some-file.file-extension"),
        ),
        (
            "path/to/some-file",
            "file-extension",
            Path("path/to/some-file.file-extension"),
        ),
    ],
)
def test_ensure_file_extension_is_appended(
    input: str, extension: str, expected_result: Path
) -> None:
    actual_result = ensure_file_extension_is_present(input, extension)

    assert actual_result == expected_result

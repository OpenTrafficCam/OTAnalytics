from pathlib import Path

import pytest

from OTAnalytics.application.export_path_builder import build_export_path


class TestBuildExportPath:
    def test_simple_stem(self) -> None:
        result = build_export_path(Path("/output"), "video", ".csv")

        assert result == Path("/output/video.csv")

    def test_stem_with_multiple_dots_is_preserved(self) -> None:
        """Regression test for OP#9548.

        Path.with_suffix() would truncate this stem; build_export_path must not.
        """
        stem = "video.00000_2025-08-28_15-00-00"

        result = build_export_path(Path("/output"), stem, ".tracks.csv")

        assert result == Path("/output/video.00000_2025-08-28_15-00-00.tracks.csv")

    def test_compound_suffix(self) -> None:
        result = build_export_path(Path("/output"), "video", ".tracks_metadata.json")

        assert result == Path("/output/video.tracks_metadata.json")

    def test_relative_directory(self) -> None:
        result = build_export_path(Path("data"), "video", ".csv")

        assert result == Path("data/video.csv")

    def test_nested_directory(self) -> None:
        result = build_export_path(Path("/output/sub/dir"), "video", ".csv")

        assert result == Path("/output/sub/dir/video.csv")

    def test_empty_stem_raises(self) -> None:
        with pytest.raises(ValueError):
            build_export_path(Path("/output"), "", ".csv")

    def test_suffix_without_leading_dot_raises(self) -> None:
        with pytest.raises(ValueError):
            build_export_path(Path("/output"), "video", "csv")

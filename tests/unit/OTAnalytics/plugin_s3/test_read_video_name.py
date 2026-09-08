"""Tests for reading which video a track file belongs to.

The companion is named by the ottrk's own metadata, never guessed by swapping
the suffix, because a companion may be any supported video type.
"""

import bz2
import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from OTAnalytics.plugin_s3.s3_file_providers import UnreadableTrackFile, read_video_name


@dataclass
class Given:
    ottrk: Path


def create_given(tmp_path: Path, metadata: dict | None, name: str = "a.ottrk") -> Given:
    ottrk = tmp_path / name
    content = b"not json" if metadata is None else json.dumps(metadata).encode()
    ottrk.write_bytes(bz2.compress(content))
    return Given(ottrk=ottrk)


def metadata_naming(filename: str, filetype: str) -> dict:
    return {"metadata": {"video": {"filename": filename, "filetype": filetype}}}


class TestReadVideoName:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    def test_reads_the_name_from_a_real_track_file(self, ottrk_path: Path) -> None:
        """The crafted files below cannot catch drift in the real ottrk format."""
        assert read_video_name(ottrk_path) == (
            "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        )

    @pytest.mark.parametrize("filetype", [".mp4", ".mkv", ".avi", ".mov"])
    def test_resolves_any_supported_companion_type(
        self, tmp_path: Path, filetype: str
    ) -> None:
        """Swapping in '.mp4' would silently look for the wrong object."""
        given = create_given(
            tmp_path, metadata_naming("OTCamera19_2023-05-24_06-00-00", filetype)
        )

        assert read_video_name(given.ottrk) == (
            f"OTCamera19_2023-05-24_06-00-00{filetype}"
        )

    def test_the_video_name_need_not_match_the_track_file_name(
        self, tmp_path: Path
    ) -> None:
        given = create_given(
            tmp_path, metadata_naming("something_else", ".mkv"), name="a.ottrk"
        )

        assert read_video_name(given.ottrk) == "something_else.mkv"

    def test_a_track_file_without_video_metadata_is_reported(
        self, tmp_path: Path
    ) -> None:
        given = create_given(tmp_path, {"metadata": {}})

        with pytest.raises(UnreadableTrackFile):
            read_video_name(given.ottrk)

    def test_an_unreadable_track_file_is_reported(self, tmp_path: Path) -> None:
        given = create_given(tmp_path, None)

        with pytest.raises(UnreadableTrackFile):
            read_video_name(given.ottrk)

    def test_a_missing_track_file_is_reported(self, tmp_path: Path) -> None:
        with pytest.raises(UnreadableTrackFile):
            read_video_name(tmp_path / "absent.ottrk")

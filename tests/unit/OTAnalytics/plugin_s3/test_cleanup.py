"""Tests for wiping the local user source."""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, Mock

from OTAnalytics.plugin_s3.cleanup import WipeUserSource, WipeUserSourceOnReset


@dataclass
class Given:
    user_source: Path


def create_given(tmp_path: Path, populated: bool = True) -> Given:
    user_source = tmp_path / "user-source"
    if populated:
        nested = user_source / "cam19" / "2023-05-24"
        nested.mkdir(parents=True)
        (nested / "a.ottrk").write_bytes(b"tracks")
        (nested / "a.mp4").write_bytes(b"video")
        (user_source / "loose.txt").write_text("loose")
    return Given(user_source=user_source)


def create_target(given: Given) -> WipeUserSource:
    return WipeUserSource(given.user_source)


class TestWipeUserSource:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    def test_removes_everything_staged(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)
        target = create_target(given)

        target.wipe()

        assert list(given.user_source.iterdir()) == []

    def test_keeps_the_user_source_itself(self, tmp_path: Path) -> None:
        """Downloads write into it, so it must survive as an empty directory."""
        given = create_given(tmp_path)
        target = create_target(given)

        target.wipe()

        assert given.user_source.is_dir()

    def test_creates_the_user_source_when_it_does_not_exist(
        self, tmp_path: Path
    ) -> None:
        given = create_given(tmp_path, populated=False)
        target = create_target(given)

        target.wipe()

        assert given.user_source.is_dir()

    def test_wiping_twice_is_harmless(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)
        target = create_target(given)

        target.wipe()
        target.wipe()

        assert list(given.user_source.iterdir()) == []


class TestWipeUserSourceOnReset:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    def test_clears_repositories_before_removing_their_files(
        self, tmp_path: Path
    ) -> None:
        """A Video still pointing at a removed file would break get_frame."""
        order = MagicMock()
        order.clear_repositories = Mock()
        order.reset_state = Mock()
        wipe = Mock(spec=WipeUserSource)
        order.wipe = wipe
        target = WipeUserSourceOnReset(
            order.clear_repositories, order.reset_state, wipe
        )

        target.reset()

        assert [name for name, _, _ in order.mock_calls] == [
            "clear_repositories",
            "reset_state.reset",
            "wipe.wipe",
        ]

    def test_removes_the_staged_downloads(self, tmp_path: Path) -> None:
        given = create_given(tmp_path)
        target = WipeUserSourceOnReset(
            Mock(), Mock(), WipeUserSource(given.user_source)
        )

        target.reset()

        assert list(given.user_source.iterdir()) == []

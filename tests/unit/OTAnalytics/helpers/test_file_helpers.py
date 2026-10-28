import os
from pathlib import Path

import pytest

from OTAnalytics.helpers.file_helpers import atomic_write


class TestAtomicWrite:
    def test_writes_content_and_leaves_no_temp_file(self, tmp_path: Path) -> None:
        path = tmp_path / "sub" / "out.bin"

        with atomic_write(path) as file:
            file.write(b"new")

        assert path.read_bytes() == b"new"
        assert list(path.parent.iterdir()) == [path]

    @pytest.mark.parametrize("umask, expected", [(0o022, 0o644), (0o077, 0o600)])
    def test_file_gets_default_permissions(
        self, tmp_path: Path, umask: int, expected: int
    ) -> None:
        path = tmp_path / "out.bin"
        old_umask = os.umask(umask)
        try:
            with atomic_write(path) as file:
                file.write(b"new")
        finally:
            os.umask(old_umask)

        assert path.stat().st_mode & 0o777 == expected

    def test_failing_block_keeps_old_file(self, tmp_path: Path) -> None:
        path = tmp_path / "out.bin"
        path.write_bytes(b"old")

        with pytest.raises(RuntimeError):
            with atomic_write(path) as file:
                file.write(b"new")
                raise RuntimeError("boom")

        assert path.read_bytes() == b"old"
        assert list(tmp_path.iterdir()) == [path]

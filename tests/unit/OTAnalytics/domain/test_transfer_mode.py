import pytest

from OTAnalytics.domain.transfer_mode import TransferMode


class TestTransferMode:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("local-filesystem", TransferMode.LOCAL_FILESYSTEM),
            ("s3", TransferMode.S3),
        ],
    )
    def test_parse_supported_value(self, value: str, expected: TransferMode) -> None:
        assert TransferMode(value) == expected

    @pytest.mark.parametrize("value", ["ftp", "local-file", "S3", ""])
    def test_reject_unsupported_value(self, value: str) -> None:
        """Unknown modes are rejected by the enum itself.

        FTP exists in OTCloud's TransferMode but is not supported here.

        # Requirement OP#10256
        """
        with pytest.raises(ValueError):
            TransferMode(value)

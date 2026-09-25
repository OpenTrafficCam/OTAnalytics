from pathlib import Path

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.upload_otconfig import UploadOtconfig
from OTAnalytics.plugin_s3.upload import S3Upload


class S3OtconfigUpload(UploadOtconfig):
    """Uploads a saved otconfig beside the project's other objects in s3."""

    def __init__(self, upload: S3Upload) -> None:
        self._upload = upload

    async def upload(self, file: Path, key_prefix: S3KeyPrefix) -> None:
        await self._upload.upload(src=file, key=f"{key_prefix}/{file.name}")

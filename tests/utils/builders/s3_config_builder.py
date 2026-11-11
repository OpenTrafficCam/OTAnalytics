"""Shared S3Config builder for plugin_s3 unit tests."""

from datetime import timedelta

from OTAnalytics.plugin_s3.config.s3 import S3Config

ENDPOINT_URL = "http://localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"  # gitleaks:allow
BUCKET = "otcloud"
REGION = "us-east-1"
USER_SOURCE = "/data/otanalytics-source"


def create_s3_config(
    endpoint_url: str = ENDPOINT_URL,
    access_key: str = ACCESS_KEY,
    secret_key: str = SECRET_KEY,
    bucket: str = BUCKET,
    region: str | None = REGION,
    user_source: str = USER_SOURCE,
    max_load_duration: timedelta = timedelta(hours=10),
    download_concurrency: int = 8,
) -> S3Config:
    return S3Config(
        endpoint_url=endpoint_url,
        access_key=access_key,
        secret_key=secret_key,
        bucket=bucket,
        region=region,
        user_source=user_source,
        max_load_duration=max_load_duration,
        download_concurrency=download_concurrency,
    )

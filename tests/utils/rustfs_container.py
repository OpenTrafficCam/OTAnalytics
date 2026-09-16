"""A testcontainers wrapper for RustFS, an S3-compatible object store.

testcontainers-python ships a dedicated module for MinIO but not for RustFS (that
only exists in the Rust bindings), so this wraps the official `rustfs/rustfs` image
as a generic container the same way `testcontainers.minio.MinioContainer` wraps
MinIO's. MinIO stopped publishing free images to Docker Hub in 2025 and later
pulled the `minio/minio` repository entirely, which is why acceptance and
integration tests were switched to RustFS.
"""

from minio import Minio
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy


class RustFsContainer(DockerContainer):
    """Runs RustFS and exposes it through the `minio` Python client.

    RustFS speaks the S3 API, so the same client used against MinIO works here
    unchanged; only how the container itself is started and its endpoint is
    obtained differs.
    """

    def __init__(
        self,
        image: str,
        port: int = 9000,
        access_key: str = "rustfsadmin",
        secret_key: str = "rustfsadmin",
        **kwargs: object,
    ) -> None:
        super().__init__(image, **kwargs)
        self.port = port
        self.access_key = access_key
        self.secret_key = secret_key

        self.with_exposed_ports(self.port)
        self.with_env("RUSTFS_ACCESS_KEY", self.access_key)
        self.with_env("RUSTFS_SECRET_KEY", self.secret_key)
        self.with_env("RUSTFS_ADDRESS", f"0.0.0.0:{self.port}")
        self.waiting_for(
            HttpWaitStrategy(self.port, "/health/ready").for_status_code(200)
        )

    def get_client(self) -> Minio:
        """Returns a `minio` Python client connected to this container."""
        return Minio(
            self.get_config()["endpoint"],
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )

    def get_config(self) -> dict:
        """Returns the container's endpoint, access key, and secret key."""
        host_ip = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(self.port)
        return {
            "endpoint": f"{host_ip}:{exposed_port}",
            "access_key": self.access_key,
            "secret_key": self.secret_key,
        }

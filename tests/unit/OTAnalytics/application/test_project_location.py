"""Tests the refusal of a project this installation cannot read.

ADR 0004 gives four cases. Two of them belong to the default implementation,
which is wired whenever s3 is not configured:

| Transfer mode      | s3_key_prefix | Behaviour       |
|--------------------|---------------|-----------------|
| `local-filesystem` | absent        | unchanged       |
| `local-filesystem` | present       | refuse the load |

No code here asks what the transfer mode is. The wiring answers that by
choosing an implementation, so local mode refuses a prefix-carrying file
without a mode check anywhere.
"""

from dataclasses import dataclass

import pytest

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.project_location import (
    RefuseAnyProjectLocation,
    UnsupportedProjectLocation,
)

A_PREFIX = S3KeyPrefix("project-1/site-2/otcamera19/")


@dataclass
class Given:
    key_prefix: S3KeyPrefix | None


def create_given(key_prefix: S3KeyPrefix | None = A_PREFIX) -> Given:
    return Given(key_prefix=key_prefix)


def create_target(given: Given) -> RefuseAnyProjectLocation:
    return RefuseAnyProjectLocation()


class TestRefuseAnyProjectLocation:
    def test_accepts_a_project_that_names_no_location(self) -> None:
        given = create_given(key_prefix=None)

        create_target(given)(given.key_prefix)

    def test_refuses_a_project_stored_in_s3(self) -> None:
        given = create_given()

        with pytest.raises(UnsupportedProjectLocation) as error:
            create_target(given)(given.key_prefix)

        assert "local filesystem" in str(error.value)

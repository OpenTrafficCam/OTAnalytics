"""Tests the two s3-mode rows of ADR 0004's table.

| Transfer mode | s3_key_prefix | Behaviour       |
|---------------|---------------|-----------------|
| `s3`          | present       | use it          |
| `s3`          | absent        | refuse the load |

Plus containment. The bucket is environment-only, so a submitted otconfig can
never read across buckets, but it can name any prefix within the configured
one. An absolute or `..`-bearing prefix is refused because it reads as an
attempt to leave that bucket rather than as a location inside it.
"""

from dataclasses import dataclass

import pytest

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.project_location import UnsupportedProjectLocation
from OTAnalytics.plugin_s3.project_location import RequireWellFormedKeyPrefix

A_PREFIX = S3KeyPrefix("project-1/site-2/otcamera19/")


@dataclass
class Given:
    key_prefix: S3KeyPrefix | None


def create_given(key_prefix: S3KeyPrefix | None = A_PREFIX) -> Given:
    return Given(key_prefix=key_prefix)


def create_target(given: Given) -> RequireWellFormedKeyPrefix:
    return RequireWellFormedKeyPrefix()


class TestRequireWellFormedKeyPrefix:
    def test_accepts_a_prefix_inside_the_bucket(self) -> None:
        given = create_given()

        create_target(given)(given.key_prefix)

    def test_refuses_a_project_that_does_not_say_where_its_data_lives(self) -> None:
        given = create_given(key_prefix=None)

        with pytest.raises(UnsupportedProjectLocation) as error:
            create_target(given)(given.key_prefix)

        assert "does not say where its data lives" in str(error.value)

    @pytest.mark.parametrize(
        "malformed",
        [
            "/project-1/site-2/",
            "../project-1/site-2/",
            "project-1/../../site-2/",
            "project-1/..",
        ],
    )
    def test_refuses_a_prefix_that_leaves_the_bucket(self, malformed: str) -> None:
        given = create_given(key_prefix=S3KeyPrefix(malformed))

        with pytest.raises(UnsupportedProjectLocation):
            create_target(given)(given.key_prefix)

    def test_accepts_a_name_that_merely_contains_dots(self) -> None:
        given = create_given(key_prefix=S3KeyPrefix("project-1/v1.2..3/site/"))

        create_target(given)(given.key_prefix)

"""Tests the holder for the loaded project's key prefix.

The prefix arrives with the project rather than with the process (ADR 0004), so
something has to hold it between loading a project and saving or listing under
it. Until a project is loaded there is no prefix, which is why the seed is None
and why reset returns to the seed rather than to some last-known value.
"""

from dataclasses import dataclass

from OTAnalytics.application.key_prefix import S3KeyPrefix
from OTAnalytics.application.state import CurrentKeyPrefix

A_PREFIX = S3KeyPrefix("project-1/site-2/otcamera19/")
ANOTHER_PREFIX = S3KeyPrefix("project-1/site-2/otcamera20/")


@dataclass
class Given:
    key_prefix: S3KeyPrefix


def create_given(key_prefix: S3KeyPrefix = A_PREFIX) -> Given:
    return Given(key_prefix=key_prefix)


def create_target(given: Given) -> CurrentKeyPrefix:
    return CurrentKeyPrefix()


class TestCurrentKeyPrefix:
    def test_holds_no_prefix_until_a_project_is_loaded(self) -> None:
        assert create_target(create_given()).get() is None

    def test_holds_the_prefix_it_was_given(self) -> None:
        given = create_given()
        target = create_target(given)

        target.set(given.key_prefix)

        assert target.get() == given.key_prefix

    def test_opening_another_project_moves_where_this_instance_reads(self) -> None:
        target = create_target(create_given())

        target.set(A_PREFIX)
        target.set(ANOTHER_PREFIX)

        assert target.get() == ANOTHER_PREFIX

    def test_reset_returns_to_having_no_prefix(self) -> None:
        given = create_given()
        target = create_target(given)
        target.set(given.key_prefix)

        target.reset()

        assert target.get() is None

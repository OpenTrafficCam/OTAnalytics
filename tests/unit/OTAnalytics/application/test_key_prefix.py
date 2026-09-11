"""Tests for the key prefix an otconfig declares.

The prefix says where in the bucket a project's tracks and videos live. It is
declared by the file rather than the environment (ADR 0004) so that one
deployment can open projects stored under different prefixes.

Whether a prefix may be honoured *here* -- local mode refuses any, s3 mode
requires a well-formed one -- is a separate question answered on load by
ValidateProjectLocation. These tests cover only what the type itself promises.
"""

from dataclasses import dataclass

import pytest

from OTAnalytics.application.key_prefix import InvalidS3KeyPrefix, S3KeyPrefix

A_PREFIX = "project-1/site-2/otcamera19/"


@dataclass
class Given:
    value: str


def create_given(value: str = A_PREFIX) -> Given:
    return Given(value=value)


def create_target(given: Given) -> S3KeyPrefix:
    return S3KeyPrefix(given.value)


class TestS3KeyPrefix:
    def test_carries_the_declared_prefix(self) -> None:
        given = create_given()

        target = create_target(given)

        assert target.value == A_PREFIX
        assert str(target) == A_PREFIX

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_refuses_a_prefix_that_names_nothing(self, blank: str) -> None:
        given = create_given(value=blank)

        with pytest.raises(InvalidS3KeyPrefix):
            create_target(given)

    def test_two_prefixes_with_the_same_value_are_equal(self) -> None:
        assert create_target(create_given()) == create_target(create_given())

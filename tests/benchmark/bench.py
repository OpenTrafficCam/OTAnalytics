import pytest
from fib import fib


def test_fib_10(benchmark: pytest) -> None:
    benchmark(fib, 10)


def test_fib_20(benchmark: pytest) -> None:
    benchmark(fib, 20)

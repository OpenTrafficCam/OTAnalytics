"""Plugin for parallelizing parser file conversion operations."""

from OTAnalytics.plugin_parser_parallelization.multiprocessing import (
    MultiprocessingParseParallelization,
)
from OTAnalytics.plugin_parser_parallelization.parse_parallelization import (
    ParseParallelization,
)
from OTAnalytics.plugin_parser_parallelization.sequential import (
    SequentialParseParallelization,
)

__all__ = [
    "ParseParallelization",
    "SequentialParseParallelization",
    "MultiprocessingParseParallelization",
]

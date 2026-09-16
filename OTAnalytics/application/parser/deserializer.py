from collections.abc import Callable
from pathlib import Path

Deserializer = Callable[[Path], dict]

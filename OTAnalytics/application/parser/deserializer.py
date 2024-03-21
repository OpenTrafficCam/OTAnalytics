from pathlib import Path
from typing import Callable

Deserializer = Callable[[Path], dict]

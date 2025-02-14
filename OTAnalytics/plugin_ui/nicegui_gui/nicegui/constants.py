from typing import Literal


class NotifyLevels:
    """
    Helper class providing constants to set type of NiceGUI's `ui.notify` function.
    """

    positive: Literal["positive"] = "positive"
    negative: Literal["negative"] = "negative"
    warning: Literal["warning"] = "warning"
    info: Literal["info"] = "info"
    ongoing: Literal["ongoing"] = "ongoing"


class Alignment:
    """
    Helper class providing constants to set alignment of NiceGUI UI elements.
    """

    start: Literal["start"] = "start"
    end: Literal["end"] = "end"
    center: Literal["center"] = "center"
    baseline: Literal["baseline"] = "baseline"
    stretch: Literal["stretch"] = "stretch"

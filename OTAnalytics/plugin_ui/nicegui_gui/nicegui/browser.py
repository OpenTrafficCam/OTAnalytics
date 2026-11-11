from nicegui import app
from nicegui.slot import Slot


def has_browser_to_show_in() -> bool:
    """Whether the current task renders into a page a browser is looking at.

    Two callers have none: preloading input files given on the command line at
    startup, which runs before the app is started and any page is served, and
    a load requested over HTTP rather than from a page, such as OTCloud handing
    its UI Worker an otconfig, whose task has no NiceGUI slot at all.

    Creating ui elements without a browser is pointless. Before the app is
    started, NiceGUI even discards them with a warning when it is started.

    The slot stack is read directly: `context.slot_stack` would create a script
    mode client as a side effect when called before the app is started.
    """
    return app.is_started and bool(Slot.get_stack())

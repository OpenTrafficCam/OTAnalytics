import warnings

from OTAnalytics.plugin_ui.application_starter import ApplicationStarter

warnings.simplefilter(action="ignore", category=FutureWarning)


def main() -> None:
    ApplicationStarter().start()


if __name__ in {"__main__"}:
    main()

import warnings

from OTAnalytics.plugin_ui.main_application import ApplicationStarter

warnings.simplefilter(action="ignore", category=FutureWarning)


def main() -> None:
    ApplicationStarter().start()


if __name__ == "__main__":
    main()

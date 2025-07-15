from pathlib import Path

from OTAnalytics.application.use_cases.load_otconfig import LoadOtconfig

OTCONFIG_PATH: str = "otconfig_path"


class HandleLoadOtConfig:
    def __init__(self, load_otconfig: LoadOtconfig) -> None:
        self.load_otconfig = load_otconfig

    def load(self, payload: dict) -> None:
        otconfig_path = payload.get(OTCONFIG_PATH)
        if otconfig_path is not None:
            self.load_otconfig.load(Path(otconfig_path))

from abc import abstractmethod

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate


class AbstractSectionFrame(AbstractFrame):

    @abstractmethod
    def configure_section(
            self,
            title: str,
            section_offset: RelativeOffsetCoordinate,
            initial_position: tuple[int, int],
            input_values: dict | None,
            show_offset: bool,
    ) -> dict:
        raise NotImplementedError
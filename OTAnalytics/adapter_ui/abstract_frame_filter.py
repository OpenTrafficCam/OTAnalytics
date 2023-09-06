from abc import ABC, abstractmethod

from OTAnalytics.adapter_ui.dto import DateRangeDto


class AbstractFrameFilter(ABC):
    @abstractmethod
    def _introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def set_active_color_on_filter_by_date_button(self) -> None:
        pass

    @abstractmethod
    def set_inactive_color_on_filter_by_date_button(self) -> None:
        pass

    @abstractmethod
    def set_active_color_on_filter_by_class_button(self) -> None:
        pass

    @abstractmethod
    def set_inactive_color_on_filter_by_class_button(self) -> None:
        pass

    @abstractmethod
    def enable_filter_by_date_button(self) -> None:
        pass

    @abstractmethod
    def disable_filter_by_date_button(self) -> None:
        pass

    @abstractmethod
    def enable_filter_by_class_button(self) -> None:
        pass

    @abstractmethod
    def disable_filter_by_class_button(self) -> None:
        pass

    @abstractmethod
    def update_date_range(self, date_range: DateRangeDto) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset all filters."""
        raise NotImplementedError

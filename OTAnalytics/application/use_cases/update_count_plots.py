from application.state import TrackViewState
from domain.event import EventRepository
from plugin_ui.visualization.counts.counts_plotter import (
    CountsPlotter,
    MultipleCountsPlotters,
)


class CountPlotsUpdater:

    def __init__(self, state: TrackViewState, *plotters: CountsPlotter) -> None:
        self._state = state

        state.view_width.register(lambda _: self.update())

        if len(plotters) > 1:
            self._plotter = MultipleCountsPlotters(list(plotters))
        elif len(plotters) == 1:
            self._plotter = plotters[0]
        else:
            raise ValueError("No CountsPlotter given in var arg: plotters")

    def __call__(self) -> None:
        self.update()

    def register_at(self, event_repository: EventRepository) -> None:
        event_repository.register_observer(lambda _: self.update())

    def update(self) -> None:
        width = self._state.view_width.get()
        height = self._state.view_width.get()
        plots = self._plotter.plot(width, height)

        self._state.count_plots.set(plots)

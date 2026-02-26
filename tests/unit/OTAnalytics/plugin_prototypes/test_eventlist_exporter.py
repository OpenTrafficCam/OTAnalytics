from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    EventListDataFrameBuilder,
)


class TestEventListDataFrameBuilder:
    def test_build_no_events(self) -> None:
        """
        Supporting test case for bug OP#9023
        """
        builder = EventListDataFrameBuilder([], [])

        actual = builder.build()

        assert actual.empty

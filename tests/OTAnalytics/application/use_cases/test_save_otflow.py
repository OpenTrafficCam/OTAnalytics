from unittest.mock import Mock

from OTAnalytics.application.use_cases.save_otflow import SaveOTFlow


class TestSaveOTFlow:
    def test_save(self) -> None:
        sections = Mock()
        flows = Mock()

        get_sections = Mock()
        get_sections.return_value = sections
        get_flows = Mock()
        get_flows.get.return_value = flows

        flow_parser = Mock()
        some_file = Mock()

        save_otflow = SaveOTFlow(flow_parser, get_sections, get_flows)
        save_otflow.save(some_file)

        flow_parser.serialize.assert_called_once_with(
            sections=sections, flows=flows, file=some_file
        )

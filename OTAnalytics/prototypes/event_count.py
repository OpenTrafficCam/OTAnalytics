from pathlib import Path

from prototypes.otanalytics_parser import JsonParser, PandasDataFrameParser

eventlist_json_path = Path("data/eventlist.json")
eventlist_dict = JsonParser.from_dict(eventlist_json_path)
EVENT_LIST = "event_list"
SECTIONS = "sections"
metadata = eventlist_dict[SECTIONS]
eventlist = eventlist_dict[EVENT_LIST]
eventlist_df = PandasDataFrameParser.from_dict(eventlist)
metadata_df = PandasDataFrameParser.from_dict(metadata)

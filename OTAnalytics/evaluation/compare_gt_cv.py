#function to calculate numbers
import logging
from pathlib import Path

import pandas as pd

movement_dic = {"Nord-Sued": ["Nord", "Sued"] ,"Sued-Nord": ["Sued", "Nord"]}

INPUT_EVENTS_DIR =(r"\\vs-grp08.zih.tu-dresden.de\otc_live\recordings\stationary\Dresden\Augustusbruecke_2022-09\videos\TUDCam02\Auswertung\automated_events")

# list with files of the eventbased dictionary
eventlist = Path(INPUT_EVENTS_DIR).glob("*.csv")

def assign_movement(row):
    #get track id of row
    id = row["TrackID"]

    dataframe_new = dataframe.loc[dataframe["TrackID"] == id]
    if len(dataframe_new.index) >= 2:
        # sort the dataframe by frames
        dataframe_new = dataframe_new.sort_values(by=['Frame'])

        # create a list of crossed section in framewise dependent order
        list_of_crossed_sections = dataframe_new['SectionID'].tolist()

        #compare the list with movement dictionary
        return [k for k, v in movement_dic.items() if v == list_of_crossed_sections ][0]


#%%

logging.basicConfig(filename="log.txt", level=logging.INFO,
                    format="%(asctime)s %(message)s",  filemode="w")


#create logfile
for event_csv in eventlist:
    dataframe = pd.read_csv(event_csv, index_col=0)
    dataframe['Movement'] = dataframe.apply(lambda row: assign_movement(row), axis=1)
    logging.info(f"\n Working on File: {event_csv}")
    dataframe.to_csv(event_csv)





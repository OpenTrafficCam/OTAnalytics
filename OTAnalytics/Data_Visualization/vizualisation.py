from tkinter import Button, Entry, Label, Toplevel, filedialog

# import helpers.file_helper as file_helper
import pandas as pd
import plotly.graph_objects as go

# from view.helpers.gui_helper import info_message


# Load data
def load_track_dataframe():

    return pd.read_pickle(
        r"C:\Users\Goerner\Desktop\code\OpenTrafficCam\OTAnalytics\OTAnalytics\Data_Visualization\dataframe1.pkl"
    )


def groupby_timeintervall(tracks_df, intervall: int):
    selection = "Sued-Ost"

    if selection == "all":

        tracks_df_all = (
            tracks_df.groupby(
                by=[
                    pd.Grouper(freq=f"{intervall}T"),
                    "Class",
                    # "Movement",
                    "Movement_name",
                ],
                as_index=True,
                dropna=False,
            )
            .size()
            .reset_index(name="Count")
        )
        return tracks_df_all

    else:
        tracks_df_selected_by_movement = (
            tracks_df.groupby(
                by=[
                    pd.Grouper(freq=f"{intervall}T"),
                    "Class",
                    "Movement_name",
                ],
                as_index=True,
                dropna=False,
            )
            .size()
            .reset_index(name="Count")
        )

        tracks_df_selected_by_movement = tracks_df_selected_by_movement.loc[
            tracks_df_selected_by_movement["Movement_name"] == selection
        ]
        print("test")
        print(tracks_df_selected_by_movement)

        return tracks_df_selected_by_movement


def prepare_dataframe(intervall):
    # groupy by time
    df = groupby_timeintervall(load_track_dataframe(), intervall)

    # exclude person when summed up trafficcount
    df_summed_up_class = df.loc[df["Class"] != "person"].groupby("Datetime").sum()

    # creates group object to create bars per class
    df_group_by_class = df.groupby("Class")

    return df_group_by_class, df_summed_up_class


def create_plot(intervall):

    # uncomment when using gui
    # intervall = intervall.get()
    df_group_by_class, df_summed_up_class = prepare_dataframe(intervall)

    fig = go.Figure()

    # loop over groups
    for Class, group in df_group_by_class:
        fig.add_trace(go.Bar(x=group["Datetime"], y=group["Count"], name=Class))

    fig.add_trace(
        go.Scatter(x=list(df_summed_up_class.index), y=list(df_summed_up_class.Count))
    )

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(step="all"),
                    dict(count=int(intervall), label=str(intervall), step="minute"),
                ]
            ),
            rangeslider=dict(visible=True),
            type="category",
        )
    )
    # Sort in right order by creating array as xaxis
    fig.update_xaxes(
        categoryorder="array", categoryarray=list(df_summed_up_class.index)
    )

    fig.show()


def create_graphic_setting_window():
    """Creates window with button to resample dataframe and two
    inputfields to enter starting time and timeinterval.

    Args:
        fps (int): Frames per second.
        flowdictionary (dictionary): Dictionary with sections and movements.
        tracks (dictionary): Dictionary with tracks.
    """

    # if not file_helper.tracks:
    #     info_message("Warning", "Please import tracks first!")

    #     return

    # creates window to insert autocount time and groupby time
    toplevelwindow = Toplevel()

    toplevelwindow.title("Settings for graphics")

    intervall_entry_header = Label(toplevelwindow, text="Graphic-Settings")
    intervall_entry_header.grid(row=0, column=0, columnspan=5, sticky="w")

    intervall_entry = Entry(toplevelwindow, width=8)

    intervall_entry.grid(row=1, column=0, sticky="w", pady=5, padx=5)
    intervall_entry.focus()
    intervall_entry.insert(0, "5")

    toplevelwindow_button = Button(
        toplevelwindow,
        text="Create Graphic",
        command=lambda: create_plot(intervall_entry),
    )
    toplevelwindow_button.grid(
        row=4, columnspan=5, column=0, sticky="w", pady=5, padx=5
    )

    toplevelwindow.protocol("WM_DELETE_WINDOW")
    # makes the background window unavailable
    toplevelwindow.grab_set()


if __name__ == "__main__":

    intervall = input("Enter your value: ")
    create_plot(intervall)

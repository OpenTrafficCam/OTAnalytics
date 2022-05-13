from tkinter import Button, Entry, Label, Toplevel, OptionMenu, StringVar

# import helpers.file_helper as file_helper
import pandas as pd
import plotly.graph_objects as go

import helpers.file_helper as file_helper

# from view.helpers.gui_helper import info_message


# Load data
def load_track_dataframe():

    return pd.read_pickle(
        r"C:\Users\Goerner\Desktop\code\OpenTrafficCam\OTAnalytics\OTAnalytics\Data_Visualization\dataframe1.pkl"
    )


def groupby_timeintervall(tracks_df, intervall, movement):
    """_summary_

    Args:
        tracks_df (dataframe): Dateframe computed by autocounting module
        intervall (int): Timeintervall to represent traffic count
        movement (str): Movementname chosen in toplevel window.

    Returns:
        _type_: _description_
    """

    if movement == "All":

        tracks_df_all = (
            tracks_df.groupby(
                by=[
                    pd.Grouper(freq=f"{intervall}T"),
                    "Class",
                    # "Movement",
                    # "Movement_name",
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
            tracks_df_selected_by_movement["Movement_name"] == movement
        ]

        return tracks_df_selected_by_movement


def prepare_dataframe(intervall, movement):
    # groupy by time
    df = groupby_timeintervall(load_track_dataframe(), intervall, movement)

    # exclude person when summed up trafficcount
    df_summed_up_class = df.loc[df["Class"] != "person"].groupby("Datetime").sum()

    # creates group object to create bars per class
    df_group_by_class = df.groupby("Class")

    return df_group_by_class, df_summed_up_class


def create_plot(intervall_entry, movement_var):
    """Creates a figure with bar and line chart.

    Args:
        intervall_entry (entry_widget): entry widget to recieve data from
        movement_var (variable): variable from dropdown menu
    """

    # uncomment when using gui
    intervall = intervall_entry.get()
    movement = movement_var.get()

    df_group_by_class, df_summed_up_class = prepare_dataframe(intervall, movement)

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
    inputfields to enter timeinterval.

    """

    # if not file_helper.tracks:
    #     info_message("Warning", "Please import tracks first!")

    #     return

    # creates window to insert autocount time and groupby time

    toplevelwindow = Toplevel()

    toplevelwindow.title("Settings for graphics")

    intervall_entry_header = Label(toplevelwindow, text="Graphic-Settings")
    intervall_entry_header.grid(row=0, column=0, sticky="w")

    intervall_entry_label = Label(toplevelwindow, text="Timeintervall")
    intervall_entry_label.grid(row=1, column=0, sticky="w")

    intervall_entry = Entry(toplevelwindow, width=4)

    intervall_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
    intervall_entry.focus()
    intervall_entry.insert(0, "5")

    movement_list = list(file_helper.flow_dict["Movements"].keys())

    movement_list.append("All")

    variable = StringVar(toplevelwindow)
    variable.set(movement_list[-1])

    movement_entry = OptionMenu(toplevelwindow, variable, *movement_list)
    movement_entry.config(width=8, font=("Helvetica", 8))
    movement_entry.grid(row=1, column=2, sticky="ew", pady=5, padx=5)

    toplevelwindow_button = Button(
        toplevelwindow,
        text="Create Graphic",
        command=lambda: create_plot(intervall_entry, variable),
    )
    toplevelwindow_button.grid(
        row=2, column=0, columnspan=3, sticky="ew", pady=5, padx=5
    )

    toplevelwindow.protocol("WM_DELETE_WINDOW")
    # makes the background window unavailable
    toplevelwindow.grab_set()


if __name__ == "__main__":

    intervall = input("Enter your value: ")
    create_plot(intervall, "All")

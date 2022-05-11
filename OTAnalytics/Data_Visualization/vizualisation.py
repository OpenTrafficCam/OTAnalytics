import plotly.graph_objects as go
import pandas as pd


# Load data
def load_track_dataframe():

    return pd.read_pickle(
        r"C:\Users\Goerner\Desktop\code\OpenTrafficCam\OTAnalytics\OTAnalytics\Data_Visualization\dataframe1.pkl"
    )


def groupby_timeintervall(tracks_df, intervall: int):
    tracks_df = (
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
    return tracks_df


def create_plot(intervall):

    df = groupby_timeintervall(load_track_dataframe(), intervall)

    df = df.groupby("Class")

    fig = go.Figure()

    for Class, group in df:
        print((group["Count"]))
        print((group["Datetime"]))
        fig.add_trace(go.Bar(x=group["Datetime"], y=group["Count"], name=Class))

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(buttons=[dict(step="all")]),
            rangeslider=dict(visible=True),
            type="date",
        )
    )

    fig.show()

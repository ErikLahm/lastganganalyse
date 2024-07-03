import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_yearly(raw_df: pd.DataFrame):
    fig = px.line(raw_df, x=raw_df.columns[0], y=raw_df.columns[1])
    return fig


def plot_monthly_bar(stats_df: pd.DataFrame):
    stats_df["Month_Name"] = stats_df["Month"].dt.strftime("%B")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=stats_df.iloc[:, 7].tolist(),
            y=stats_df.iloc[:, 2].tolist(),
            name="Monatliche Maxima [kW]",
            yaxis="y2",
        )
    )
    fig.add_trace(
        go.Bar(
            x=stats_df.iloc[:, 7].tolist(),
            y=stats_df.iloc[:, 1].tolist(),
            name="Summierter monatlicher Verbrauch [kW]",
        )
    )
    return fig

from dash import html
import plotly.express as px
import plotly.graph_objects as go
import dash_leaflet as dl
import pandas as pd
import sqlite3 as sql

GRADIENT_PALETTE = ["#0377A8", "#1FA6B8", "#3EC4D6", "#63D4CC", "#A0F1DA", "#B4FADC"]


def acumulatedBar(df):
    fig = go.Figure(
        [
            go.Bar(
                x=df["data"],
                y=df["obitosAcumulado"],
                name="Defunctions",
                marker_color=GRADIENT_PALETTE[0],
            ),
            go.Bar(
                x=df["data"],
                y=df["casosAcumulado"],
                name="Positive cases",
                marker_color=GRADIENT_PALETTE[1],
            ),
        ]
    )
    fig.update_layout(
        title="Acumulated Cases and Defunctions until Today",
        barmode="stack",
        template="plotly_dark",
        legend=dict(y=0.95, x=0.01),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_yaxes(title_text="Acumulated")
    return fig


def brazilMap(geojson, info):
    return dl.Map(
        children=[
            dl.TileLayer(
                url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png"
            ),
            geojson,
            info,
        ],
        style={"width": "50%", "height": "500px"},
    )

def stateMap(geojson, info):
    return dl.Map(
        id="stateMap",
        children=[
            dl.TileLayer(
                url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png"
            ),
            geojson,
            info,
        ],
        style={"width": "100%", "height": "500px"},
    )

def choroplethMap(geojson, df):
    choromap = px.choropleth(
        df,
        geojson=geojson,
        locations="codmun",
        color="casosAcumulado",
        scope="south america",
        locationmode='geojson-id',
        basemap_visible=True,
    )
    choromap.update_geos(
        fitbounds="locations", 
        visible=False,
        projection_type="natural earth",
        showland=True,
        )
    choromap.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        template="plotly_dark"
    )
    choromap.update_traces(colorbar_title="Acumulated Cases", marker_line_width=1, marker_line_color="rgba(255, 255, 255, 0.439)")
    return choromap

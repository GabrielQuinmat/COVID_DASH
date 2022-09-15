# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, html, dcc, page_registry, page_container
from dash.dependencies import Input, Output
import dash_leaflet as dl
from dash_extensions.javascript import arrow_function, assign, Namespace
from dash import Dash, html, dcc, page_registry, page_container
from dash.dependencies import Input, Output
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from datetime import date
import geojson as gj
import plotly.express as px
import pandas as pd
from components import *
from apputils import *
from visualutils import *

ns = Namespace("leafletNamespace", "mapNamespace")

external_stylesheets = [
    "https://cdn-uicons.flaticon.com/uicons-solid-rounded/css/uicons-solid-rounded.css"
]

app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)

current_tab = ""

def globalTabServer(ns):
    totalDF = queryDB("SELECT * FROM global")
    acuPlot = acumulatedBar(totalDF)

    today = date.today()
    year = today.year
    lastMonth = f"{today.month-1}".rjust(2, "0")
    dateFilter = f"{year}-{lastMonth}-01"

    stateDF = queryDB(f"SELECT * FROM state")
    stateDF.data = pd.to_datetime(stateDF.data)
    stateDF = stateDF[stateDF.data >= dateFilter]
    currentStateDF = stateDF[stateDF.data == stateDF.data.max()][
        [
            "data",
            "estado",
            "casosAcumulado",
            "obitosAcumulado",
            "casosNovos",
            "obitosNovos",
        ]
    ]
    lastStateDF = stateDF[stateDF.data == stateDF.data.max() - pd.DateOffset(days=7)][
        ["estado", "casosAcumulado", "obitosAcumulado", "casosNovos", "obitosNovos"]
    ]
    mergedDF = pd.merge(
        currentStateDF, lastStateDF, on=["estado"], suffixes=("_current", "_last")
    )
    mergedDF["cases_DIFF"] = mergedDF.casosNovos_current / mergedDF.casosNovos_last - 1
    mergedDF["defunc_DIFF"] = (
        mergedDF.obitosNovos_current / mergedDF.obitosNovos_last - 1
    )
    mergedDF["growing"] = mergedDF.cases_DIFF > 0
    mergedDF.sort_values(by=["cases_DIFF"], inplace=True, ascending=False)

    style = dict(weight=2, opacity=1, color="white", dashArray="3", fillOpacity=0.7)
    style_handle = ns("styleHandler")
    colorscale = GRADIENT_PALETTE
    classes = mergedDF.casosAcumulado_current.quantile([0.2, 0.4, 0.6, 0.8, 1]).values
    geo = gj.load(open("COVID/assets/brasil_uf.json"))
    geo = assignGeoData(geo, mergedDF)
    with open("COVID/assets/brasil_ufdata.json", "w") as f:
        gj.dump(geo, f)

    geojson = dl.GeoJSON(
        url="assets/brasil_ufdata.json",
        options=dict(style=style_handle),
        # when true, zooms to bounds when data changes (e.g. on load)
        zoomToBounds=True,
        # when true, zooms to bounds of feature (e.g. polygon) on click
        zoomToBoundsOnClick=True,
        # style applied on hover
        hoverStyle=arrow_function(dict(weight=5, color="#FFF", dashArray="3")),
        hideout=dict(
            colorscale=colorscale, classes=classes, style=style, colorProp="cases"
        ),
        id="geojson-obj",
    )

    info = html.Div(
        children=get_info(),
        id="info-div",
        className="info",
        style={
            "position": "absolute",
            "top": "10px",
            "right": "10px",
            "z-index": "1000",
        },
    )

    mapGlobal = brazilMap(geojson, info)

    mergedDF["data"] = mergedDF.data.dt.strftime("%Y-%m-%d")

    mergedDF["casosAcumulado_current"] = mergedDF.apply(casesFormat, axis=1)
    mergedDF["obitosAcumulado_current"] = mergedDF.apply(defuncFormat, axis=1)
    mergedDF["estado"] = mergedDF.apply(estadoFormat, axis=1)

    data = mergedDF[["estado", "casosAcumulado_current", "obitosAcumulado_current"]][
        0:8
    ].to_dict(orient="records")

    tableC = DataTable(
        data,
        [
            {"name": "State", "id": "estado", "presentation": "markdown"},
            {
                "name": "Acumulated Cases",
                "id": "casosAcumulado_current",
                "presentation": "markdown",
            },
            {
                "name": "Acumulated Defunctions",
                "id": "obitosAcumulado_current",
                "presentation": "markdown",
            },
        ],
        style_data={"backgroundColor": "#2a292c", "color": "white"},
        style_header={
            "backgroundColor": "#2a292c",
            "color": "white",
            "textAlign": "center",
            "fontWeight": "bold",
            "fontSize": "1.2rem",
        },
        style_table={"padding": "5px 8px"},
        style_as_list_view=True,
        page_size=10,
        markdown_options={"link_target": "_blank", "html": True},
    )

    # return {'acuPlot': acuPlot, 'mapGlobal': mapGlobal, 'tableC': tableC,
    #         'min_date': totalDF.data.min(), 'max_date': totalDF.data.max()}
    return (acuPlot, mapGlobal, tableC, totalDF.data.min(), totalDF.data.max())


def get_info(feature=None):
    header = [html.H4("COVID Acumulated Cases by State")]
    if not feature:
        return header + [html.P("Hoover over a state")]
    return header + [
        html.B(feature["properties"]["UF_05"]),
        html.Br(),
        "{:,} Positive Cases".format(feature["properties"]["cases"]),
    ]


acuPlot, mapGlobal, tableC, min_date, max_date = globalTabServer(ns)


# | State Tab
munDF = queryDB(
    """SELECT 
                estado, municipio, coduf, codmun,
                casosAcumulado, obitosAcumulado, data fecha
                FROM granular
                where data = (
                    select max(data) from granular
                    )"""
)
munDF["codmun"] = munDF.codmun.astype(int)
munDF["codmun"] = munDF.codmun.astype(str)
geo = gj.load(open("COVID/assets/brasil_mun.geojson"))
geo = assignMunGeoData(geo, munDF)
ufgeo = filterUF(geo, "SP")
with open("COVID/assets/brasil_mundata.json", "w") as f:
    gj.dump(ufgeo, f)
current_state = "SP"
style_handle = ns("styleHandler")
style = dict(weight=1, opacity=1, color="white", dashArray="3", fillOpacity=0.7)
colorscale = GRADIENT_PALETTE
classes = (
    munDF[munDF.estado == "SP"].casosAcumulado.quantile([0.2, 0.4, 0.6, 0.8, 1]).values
)
geojson = dl.GeoJSON(
    url="assets/brasil_mundata.json",
    options=dict(style=style_handle),
    # when true, zooms to bounds when data changes (e.g. on load)
    zoomToBounds=True,
    # when true, zooms to bounds of feature (e.g. polygon) on click
    zoomToBoundsOnClick=True,
    # style applied on hover
    hoverStyle=arrow_function(dict(weight=5, color="#FFF", dashArray="3")),
    hideout=dict(
        colorscale=colorscale, classes=classes, style=style, colorProp="cases"
    ),
    id="geojson-mun-obj",
)

info = html.Div(
    children=get_info(),
    id="info-mun-div",
    className="info",
    style={
        "position": "absolute",
        "top": "10px",
        "right": "10px",
        "z-index": "1000",
    },
)
choromap = stateMap(geojson, info)


# choromap = choroplethMap(ufgeo, munDF)
# | Global Tab Callbacks


@app.callback(
    Output("global-content", "children"),
    Input("tabs", "value"),
)
def renderTab(tab):
    global current_tab
    if current_tab == tab:
        raise PreventUpdate
    if tab == "tab-1":
        current_tab = "tab-1"
        return GlobalTab(
            acuPlot, mapGlobal, tableC, min_date=min_date, max_date=max_date
        )
    elif tab == "tab-2":
        current_tab = "tab-2"
        return StateTab(choromap)


@app.callback(
    Output("info-div", "children"), 
    [Input("geojson-obj", "hover_feature")])
def info_hover(feature):
    return get_info(feature)


# | State Tab Callbacks
@app.callback(
    Output("stateMap", "children"), 
    Input("state-dropdown", "value"))
def filterState(state):
    global current_state
    if current_state != state:
        current_state = state
        ufgeo = filterUF(geo, state)
        with open("COVID/assets/brasil_mundata.json", "w") as f:
            gj.dump(ufgeo, f)

        style_handle = ns("styleHandler")
        style = dict(weight=1, opacity=1, color="white", dashArray="3", fillOpacity=0.7)
        colorscale = GRADIENT_PALETTE
        classes = (
            munDF[munDF.estado == "SP"]
            .casosAcumulado.quantile([0.2, 0.4, 0.6, 0.8, 1])
            .values
        )
        geojson = dl.GeoJSON(
            url="assets/brasil_mundata.json",
            options=dict(style=style_handle),
            # when true, zooms to bounds when data changes (e.g. on load)
            zoomToBounds=True,
            # when true, zooms to bounds of feature (e.g. polygon) on click
            zoomToBoundsOnClick=True,
            # style applied on hover
            hoverStyle=arrow_function(dict(weight=5, color="#FFF", dashArray="3")),
            hideout=dict(
                colorscale=colorscale, classes=classes, style=style, colorProp="cases"
            ),
            id="geojson-mun-obj",
        )
        return stateMap(geojson, info)
    else:
        raise PreventUpdate


app.layout = html.Div(
    children=[
        Navbar(app, logo="logo.png"),
        Container(
            [
                AppContainer(
                    [
                        Sidebar(),
                        TabContent(id="global-content"),
                    ]
                )
            ]
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)

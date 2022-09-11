from dash import Dash, html, dcc, page_registry, page_container
from dash.dash_table import DataTable
from dash.dependencies import Input, Output
from dash.dash_table.Format import Format
import dash_leaflet as dl
from dash_extensions.javascript import  arrow_function, assign, Namespace
import geojson as gj


app = Dash(__name__)

style = dict(weight=2, opacity=1, color='white',
             dashArray='3', fillOpacity=0.7)
colorscale = ['#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
classes = [0, 10, 20, 50, 100, 200, 500, 1000]
ctg = ["{}+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}+".format(classes[-1])]

geojson = dl.GeoJSON(
    url='/assets/brasil_uf.json',
    id="geojson"
)

mapL = dl.Map(
        children=[
            dl.TileLayer(
                url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png'),
            geojson
        ],
        style={'width': '600px', 'height': '600px'})

app.layout = html.Div(children=[
    mapL
])

if __name__ == '__main__':
    app.run_server(debug=True)
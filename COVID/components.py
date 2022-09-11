from datetime import date
from dash import Dash, html, dcc


def generate_table(dataframe, max_rows=10):
    """Generate a table from a Pandas dataframe"""
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


def Navbar(app, title=None, logo='dash-logo.png'):
    if title:
        title_comp = html.Div(
            html.H4(title),
            className="navbar-brand--title"
        )
    else:
        title_comp = None
    return html.Div(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url(logo),
                            className='navbar-brand--logo'
                        ),
                        title_comp,
                    ],
                    className="navbar-brand--div",
                ),
                className="navbar-brand",
                href="https://plotly.com/dash/",
            ),
            html.Div(
                [
                    html.A(
                        "Learn More",
                        href="/about",
                        className="navbar-link",
                    ),
                ],
                className="navbar-links"
            )
        ],
        className="navbar",	)


def Container(children):
    return html.Div(children, className='container')


def AppContainer(children):
    return html.Div(children, className='container-inner')

# def Sidebar():
#     return html.Div([
#         SidebarTab('Home', 'fi fi-sr-home'),
#         SidebarTab('State', 'fi fi-sr-map'),
#     ],
#         className='sidebar')


def Sidebar():
    return dcc.Tabs(
        id="tabs", value='tab-1',
        parent_className='sidebar',
        className='sidebar-tabs',
        children=[
            dcc.Tab(label='Global', value='tab-1', className='sidebar-tab global',
                    selected_className='sidebar-tab--selected'),
            dcc.Tab(label='State', value='tab-2', className='sidebar-tab state',
                    selected_className='sidebar-tab--selected'),
        ]
    )


def SidebarTab(name, icon):
    return html.Div([
        html.Div([
            html.Span(name, className='sidebar-tab--name'),
            html.I(className=f'sidebar-tab--icon {icon}'),
        ], className='sidebar-tab__content')
    ], className='sidebar-tab')


def TabContent(id, children=[]):
    return html.Div(children, id=id,  className='tab-content')


def GlobalTab(acuPlot, mapGlobal, table, min_date, max_date):
    return [
        html.H2(children='Country Level'),
        # GlobalToolbar([dcc.DatePickerRange(id='datepick',
        #                     min_date_allowed=min_date,
        #                     max_date_allowed=max_date,
        #                     end_date=max_date
        #                     )]),
        Row([dcc.Graph(figure=acuPlot, style={'width': '100%'})]),
        Row([
            mapGlobal,
            html.Div([
                table
            ], style={'width': '50%'})
        ])
    ]


def GlobalToolbar(children):
    return html.Div([html.I(), *children], className='global-toolbar')

def StateTab():
    return []


def Row(children):
    return html.Div(children, className='row')

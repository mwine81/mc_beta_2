from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from fig import KPIS
from datetime import date


app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

HEADER = dbc.Col(
    html.H2('MCCPDC Dashboard'),
    className='bg-primary text-white border rounded p-3',
)

def group_select(name,**kwargs):
    return dbc.Card([
        dbc.CardHeader(name),
        dbc.CardBody(
            dcc.Dropdown(**kwargs)
        ),
    ],)

date_selector = dbc.Card([
        dbc.CardHeader('Date Range'),
        dbc.CardBody(
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(2022, 1, 1),
                max_date_allowed=date(2024, 12, 31),
                #initial_visible_month=date(2017, 8, 5),
                end_date=date(2024, 12, 31),
                start_date=date(2022, 1, 1),
            ),
        ),
    ],)

CONTROL_CARD = dbc.Card([
    group_select('Drug Group',options=['group1','group2']),
    group_select('Product',options=['drug1','drug2']),
    group_select('Affilated Dispensing',options=['All','Affilated','Non-Affilated']),
    group_select('Specialty',options=['All','Specialty','Non-Specialty']),
    group_select('FTC Generic',options=['All','FTC','Non-FTC']),
    date_selector
    ],
    className="gap-4 mt-4 py-4 px-2",
)


TABS = dcc.Tabs([
    dcc.Tab(CONTROL_CARD,label='Controls', value='tab-1'),
    dcc.Tab(label='Methods', value='tab-2'),
],className='mt-2')


app.layout = dbc.Container([
    dbc.Row([HEADER],className='pt-4'),
    dbc.Row(
        KPIS
        ,justify="between"
    ),
    dbc.Row([
        dbc.Col(TABS,width=12,lg=4,className='bg-light mt-4 border'),
        dbc.Col([
            dcc.Graph(id='graph1'),
            dcc.Graph(id='graph2'),
            html.Hr(),
            dcc.Graph(id="summary_table"),
            html.H6('datasource_text', className="my-2"),
                 ],width=12,lg=8,className='pt-4'),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
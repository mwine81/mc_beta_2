from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def kpi_card(name,value):
    return (
        dbc.Col(dbc.Card([
        dbc.CardHeader(name,className="text-center"),
        dbc.CardBody( html.H4(value, className="card-title text-center"))
        ]),className="pt-2"
    )
    )

KPIS = [
    kpi_card('Total',f'{1000000}'),
    kpi_card('MCCPDC',f'{1000000}'),
    kpi_card('DIFF',f'{1000000}'),
    kpi_card('Rx Ct',f'{1000000}'),
    kpi_card('Diff Per Rx',f'{1000000}')
]
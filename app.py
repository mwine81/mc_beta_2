from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from fig import kpi_card, top_saving_drugs,FIG1,FIG2, fig_drug_group_fig, HEADER, FIG3, fig_monthly_spend, average_charge_per_rx_fig, FIG4
from datetime import date
from calc import *
from polars import col as c


app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])



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
                id='date-picker',
                min_date_allowed=date(2023, 1, 1),
                max_date_allowed=date(2024, 12, 31),
                #initial_visible_month=date(2017, 8, 5),
                end_date=date(2024, 12, 31),
                start_date=date(2023, 1, 1),
            ),
        ),
    ],)

# CONTROLS CARD
CONTROL_CARD = dbc.Card([
    date_selector,
    group_select('Date Sets', options=get_files(), multi=True, id='data-set'),
    group_select('Drug Class', id='drug-class-group', multi=True),
    group_select('Product', id='product-group', multi=True),
    group_select('Affiliated Dispensing', options={'All': 'All', True: 'Affiliated', False: 'Non-Affiliated'},
                 value='All', id='affiliated-group', clearable=False),
    group_select('Specialty', options={'All': 'All', True: 'Specialty', False: 'Non-Specialty'}, value='All',
                 id='specialty-group', clearable=False),
    group_select('FTC Generic', options={'All': 'All', True: 'FTC', False: 'Non-FTC'}, id='ftc-group', value='All',
                 clearable=False),

],
    className="gap-4 mt-4 p-2",
)

FIG_TAB_1 = html.Div([
html.Div(FIG1),
html.Div(FIG2,className='pt-4')
])

FIG_TAB_2 = html.Div([
html.Div(FIG3),
html.Div(FIG4,className='pt-4')
]
)

FIG_TABS = dcc.Tabs([
    dcc.Tab(FIG_TAB_1,label='Figures 1'),
    dcc.Tab(FIG_TAB_2,label='Figures 2'),
     ]
)

TABS = dcc.Tabs([
    dcc.Tab(CONTROL_CARD,label='Controls', value='tab-1'),
    dcc.Tab(label='Methods', value='tab-2'),
],className='mt-2')


#LAYOUT
app.layout = dbc.Container([
    dbc.Row([HEADER],className='pt-4'),
    dbc.Row(id='kpi-row'
        ,justify="between"
    ),
    dbc.Row([
        dbc.Col(TABS,width=12,lg=4,className='bg-light my-4 border pb-2 border rounded'),
        dbc.Col([
            FIG_TABS
            ,
            # html.Hr(),
            # dcc.Graph(id="summary_table"),
            # html.H6('datasource_text', className="my-2"),
                 ],width=12,lg=8,className='p-4'),
    ])
],className='mb-4')

# @app.callback(
# Output('dataframe-store', 'data'),
#     Input('data-set', 'value'),
# )
# def update_dataframe(data_set):
#     return load_files(data_set).collect().to_dict(as_series=False)

ALL_VALUE = 'All'  # Introduced constant for reused string

def filter_data(data_set_list, affiliated_group, specialty_group,ftc_group, product_list=None, date_start=None, date_end=None,
                drug_class_list=None):
    data = load_files(data_set_list)
    if date_start and date_end:
        start, end = [int(x) for x in date_start.split('-')], [int(x) for x in date_end.split('-')]
        data = data.filter(c.dos.is_between(pl.date(start[0], start[1], start[2]), pl.date(end[0], end[1], end[2])))
    if affiliated_group != ALL_VALUE:
        data = data.filter(c.affiliated == affiliated_group)
    if specialty_group != ALL_VALUE:
        data = data.filter(c.is_special == specialty_group)
    if product_list:
        data = data.filter(c.product.is_in(product_list))
    if drug_class_list:
        data = data.filter(c.drug_class.is_in(drug_class_list))
    if ftc_group != ALL_VALUE:
        data = data.filter(c.is_ftc == ftc_group)
    return data


@app.callback(
    Output('drug-class-group', 'options'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('product-group', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_control_group_options(data_set_list, affiliated_group, specialty_group,ftc_group, product_list, date_start, date_end):
    data = filter_data(data_set_list = data_set_list,affiliated_group= affiliated_group,specialty_group= specialty_group,ftc_group=ftc_group, product_list=product_list, date_start=date_start, date_end=date_end)
    drug_group_options = data.select(c.drug_class).unique().sort(c.drug_class).collect().to_series().to_list()
    return drug_group_options


@app.callback(
    Output('product-group', 'options'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_product_group_options(data_set_list, affiliated_group, specialty_group,ftc_group,drug_class_list,date_start, date_end):
    data = filter_data(data_set_list = data_set_list,affiliated_group= affiliated_group,specialty_group= specialty_group,ftc_group=ftc_group,drug_class_list=drug_class_list, date_start=date_start, date_end=date_end)
    drug_product_options = data.select(c.product).unique().sort(c.product).collect().to_series().to_list()
    return drug_product_options

#GRAPH1 CALLBACK
@app.callback(
    Output('graph1','children'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),
    Input('product-group', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('fig-drug-class-how','value'),
)
def update_graph1(data_set_list,affiliated_group,specialty_group,ftc_group,drug_class_list,product_list,date_start,date_end,how):
    data = filter_data(data_set_list=data_set_list, affiliated_group=affiliated_group, specialty_group=specialty_group,ftc_group=ftc_group,
                       drug_class_list=drug_class_list,product_list=product_list, date_start=date_start, date_end=date_end)

    fig = dcc.Graph(figure=fig_drug_group_fig(data,how))
    return fig

#GRAPH2 CALLBACK
@app.callback(
    Output('graph2','children'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),
    Input('product-group', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('fig-per-drug-n','value'),
    Input('fig-per-drug-how','value'),
)
def update_graph2(data_set_list,affiliated_group,specialty_group,ftc_group, drug_class_list,product_list,date_start,date_end,n_drugs,how):
    data = filter_data(data_set_list=data_set_list, affiliated_group=affiliated_group, specialty_group=specialty_group,ftc_group=ftc_group,
                       drug_class_list=drug_class_list,product_list=product_list, date_start=date_start, date_end=date_end)

    fig = dcc.Graph(figure=top_saving_drugs(data, n_drugs,how))

    return fig

#FIG3 CALLBACK
@app.callback(
    Output('graph3','children'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),
    Input('product-group', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('fig-over-time-fee','value')
)
def update_graph3(data_set_list,affiliated_group,specialty_group,ftc_group, drug_class_list,product_list,date_start,date_end,fee):
    data = filter_data(data_set_list=data_set_list, affiliated_group=affiliated_group, specialty_group=specialty_group,ftc_group=ftc_group,
                       drug_class_list=drug_class_list,product_list=product_list, date_start=date_start, date_end=date_end)

    fig = dcc.Graph(figure=fig_monthly_spend(data,fee))

    return fig

#FIG4 CALLBACK
@app.callback(
    Output('graph4','children'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),
    Input('product-group', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_graph4(data_set_list,affiliated_group,specialty_group,ftc_group, drug_class_list,product_list,date_start,date_end):
    data = filter_data(data_set_list=data_set_list, affiliated_group=affiliated_group, specialty_group=specialty_group,ftc_group=ftc_group,
                       drug_class_list=drug_class_list,product_list=product_list, date_start=date_start, date_end=date_end)

    fig = dcc.Graph(figure=average_charge_per_rx_fig(data))

    return fig

@app.callback(
    Output('kpi-row','children'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),
    Input('product-group', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)

def update_kpis(data_set_list,affiliated_group,specialty_group,ftc_group, drug_class_list,product_list,date_start,date_end):
    data = filter_data(data_set_list=data_set_list, affiliated_group=affiliated_group, specialty_group=specialty_group,ftc_group=ftc_group,
                       drug_class_list=drug_class_list,product_list=product_list, date_start=date_start, date_end=date_end)
    data_dict = dict_for_kpis(data)
    KPIS = [
        kpi_card('Total', f'{"${:,.0f}".format(data_dict["total"][0])}'),
        kpi_card('MCCPDC', f'{"${:,.0f}".format(data_dict.get("mc_total")[0])}'),
        kpi_card('DIFF', f'{"${:,.0f}".format(data_dict.get("mc_diff")[0])}'),
        kpi_card('Rx Ct', f'{"{:,}".format(data_dict.get("rx_ct")[0])}'),
        kpi_card('Diff Per Rx', f'{"${:,.2f}".format(data_dict.get("per_rx")[0])}')
    ]
    return KPIS




if __name__ == '__main__':
    app.run_server(debug=True)
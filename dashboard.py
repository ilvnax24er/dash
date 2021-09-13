import dash
from dash import html as html
from dash import dcc as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
from dash import dash_table
import plotly.express as px
import time
import yfinance as yf
import dash_auth



cols = ['Ticker', 'Number']
valid_username_password_pairs = {
    'ilvnax24er' : '123456'
}


def get_stock_price_fig(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(mode='lines', x=df['Date'], y=df['Close']))
    return fig

def get_donuts(df, label):
    non_main = 1 - df.values[0]
    labels = ["main", label]
    values = [non_main, df.values[0]]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.499)])
    return fig

def data_to_frame(y):
    df = pd.DataFrame(y)
    tickers = df['ticker-data']
    numbers = df['number-data']
    return df, tickers, numbers

def get_data_from_yf(tickers):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        close = stock.info['previousClose']
        sector = stock.info['sector']
        industries = stock.info['industry']
        datum = [ticker, close, sector, industries]
        data.append(datum)

    return pd.DataFrame(data)

def cal_volume(final_data):
    cols = ['Ticker', 'Close', 'Sector', 'Industry', 'Number']
    final_data.columns = cols
    final_data['Volume'] = final_data['Close'] * final_data['Number']

    return final_data

def make_final_df(y):
    df, tickers, numbers = data_to_frame(y)
    data = get_data_from_yf(tickers)
    final_data = pd.concat([data, df['number-data'].astype('int64')], axis=1)
    final = cal_volume(final_data)
    final['Ticker'] = final[['Ticker']].applymap(str.upper)

    return final

### ETF ###
def get_data_from_yf_etf(tickers):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        close = stock.info['previousClose']
        cat = stock.info['category']
        datum = [ticker, close, cat]
        data.append(datum)
        
    return pd.DataFrame(data)


def cal_volume_etf(df):
    cols = ['Ticker','Close','Industry','Number','Sector']
    df.columns = cols
    df['Volume'] = df['Close'] * df['Number']

    return df


def make_final_df_etf(etf):
    df, tickers, numbers = data_to_frame(etf)
    data = get_data_from_yf_etf(tickers)
    final_data = pd.concat([data, df['number-data'].astype('int64')], axis=1)
    final_data['Sector'] = 'ETF'
    final = cal_volume_etf(final_data)
    final['Ticker'] = final[['Ticker']].applymap(str.upper)

    return final

def cal_percentage(a, b):
    df = pd.concat([a, b], axis=0)
    df['Percentage'] = round(df['Volume'] / df['Volume'].sum() * 100, 3)
    df.fillna('No Data', inplace=True)
    return df


def make_pie_chart(df):
    fig = px.sunburst(data_frame=df,
                     path = ['Sector','Industry','Ticker'],
                     values = 'Volume',
                     template = 'ggplot2',
                     height = 700)
    return fig

app = dash.Dash(__name__, external_stylesheets=['https://fonts.googleapis.com/css2?family=Montserrat&display=swap'])
server = app.server

# tab layout
tabs_styles = {
    'height' : '44px'
}
tab_style = {
    'borderBotton' : '1px solid #d6d6d6',
    'padding' : '6px',
    'fontWeight' : 'bold'
}
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}


auth = dash_auth.BasicAuth(
    app, valid_username_password_pairs
)


app.layout = html.Div([
        # html.Div([
        #     html.H1('Ticker는 소문자로, Number에는 보유한 주식수를 입력'),
        #     html.H2('반드시 모두 완성한 후 Submit 버튼을 눌러주세요')],
        #     className='Header'),


        html.Div([
            html.H1('Stock'),
            dash_table.DataTable(
                id='adding-rows-table',
                columns=[
                    {'name' : 'Ticker', 'id' : 'ticker-data'},
                    {'name' : 'Number', 'id' : 'number-data'}
                ],
                data=[{}],
                editable=True,
                row_deletable=True
            ),

            html.Button('Add Row', id='editing-rows-button', n_clicks=0)

        ], className='Table'),
#####################

        html.Div([
            html.H1('ETF'),
            dash_table.DataTable(
                id='adding-rows-table-etf',
                columns=[
                    {'name' : 'Ticker', 'id' : 'ticker-data'},
                    {'name' : 'Number', 'id' : 'number-data'}
                ],
                data=[{}],
                editable=True,
                row_deletable=True
            ),

            html.Button('Add Row', id='editing-rows-button-etf', n_clicks=0),
            html.Button('Submit', id='submit-button', n_clicks=0)

        ], className='Table-etf'),
#############################
        html.Div([
            html.Div([], id='graphs-contents')]),


        # # tab 설정
        # html.Div([
        #     dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        #         dcc.Tab(label='Information', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        #         dcc.Tab(label='Total', value='tab-2', style=tab_style, selected_style=tab_selected_style),
        #         dcc.Tab(label='by Sector', value='tab-3', style=tab_style, selected_style=tab_selected_style),
        #         dcc.Tab(label='by Industry', value='tab-4', style=tab_style, selected_style=tab_selected_style),
        #     ], style=tabs_styles),
        #     html.Div(id='tabs-content-inline')
        # ]),


        # table 나오게
        # html.Div([
        #     dash_table.DataTable(
        #         id='table',
        #         columns=[],
        #         data=[]
        #     ),
        #     html.Div(id='submitted-table')
        #
        # ]),


        # html.Div([
        #     html.P('Choose a Ticker to start', className='start'),
        #     dcc.Dropdown('dropdown_tickers', options=[
        #         {'label':'Apple','value':'AAPL'},
        #         {'label':'Stem','value':'STEM'},
        #         {'label':'Microsoft','value':'MSFT'},
        #     ]),
        #     html.Div([
        #         html.Button('Stock Price', className='stock-btn', id='stock'),
        #         html.Button('Indicator', className='indicator-btn', id='indicators'),
        #     ], className='buttons')
        # ], className='navigation'),
        #
        # html.Div([
        #     html.Div([
        #         html.P(id='ticker'),
        #         html.Img(id='logo')
        #     ], className='header'),
        #     html.Div(id='description', className='description_ticker'),
        #     html.Div([
        #         html.Div([], id='graphs-contents')
        #     ], id='main-content'),
        #
        #
        # ], className='content')
        #
], className='container')


# @app.callback(
#     [Output('description', 'children'),Output('logo', 'src'),Output('ticker', 'children')],
#     [Input('dropdown_tickers', 'value')]
# )
# def update_data(v):
#     if v == None:
#         raise PreventUpdate
#     ticker = yf.Ticker(v)
#     inf = ticker.info
#
#     df = pd.DataFrame().from_dict(inf, orient='index').T
#     df = df[['logo_url', 'shortName','longBusinessSummary']]
#
#     return df['longBusinessSummary'].values[0], df['logo_url'].values[0], df['shortName'].values[0]
#
# @app.callback(
#     [Output('graphs-contents', 'children')],
#     [Input('stock', 'n_clicks'), Input('dropdown_tickers','value')]
# )
# def stock_price(v, v2):
#     if v == None:
#         raise PreventUpdate
#
#     df = yf.download(v2)
#     df.reset_index(inplace=True)
#
#     fig = get_stock_price_fig(df)
#     return [dcc.Graph(figure=fig)]
#
# @app.callback(
#     [Output('main-content', 'children'), Output('stock', 'n_clicks')],
#     [Input('indicators', 'n_clicks'), Input('dropdown_tickers','value')]
# )
# def indicators(v, v2):
#     if v == None:
#         raise PreventUpdate
#
#     ticker = yf.Ticker(v2)
#     df_info = pd.DataFrame.from_dict(ticker.info, orient='index').T
#     df_info = df_info[['priceToBook', 'profitMargins', 'bookValue',
#                       'enterpriseToEbitda', 'shortRatio', 'beta', 'payoutRatio', 'trailingEps']]
#
#     kpi_data = \
#         html.Div([
#         html.Div([
#         html.Div([
#             html.H4('Price to Book'),
#             html.P(df_info['priceToBook'])
#         ]),
#         html.Div([
#             html.H4('Enterprise to Ebitda'),
#             html.P(df_info['enterpriseToEbitda'])
#         ]),
#         html.Div([
#             html.H4('Beta'),
#             html.P(df_info['beta'])
#         ])
#     ], className='kpi'),
#     html.Div([
#         dcc.Graph(figure=get_donuts(df_info["profitMargins"], "Margin")),
#         dcc.Graph(figure=get_donuts(df_info["payoutRatio"], "Payout"))
#     ], className='donuts')
#     ])
#
#
#     return [html.Div([kpi_data], id='graphs-contents')], None
#

@app.callback(
    Output('adding-rows-table', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('adding-rows-table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

#######################
@app.callback(
    Output('adding-rows-table-etf', 'data'),
    Input('editing-rows-button-etf', 'n_clicks'),
    State('adding-rows-table-etf', 'data'),
    State('adding-rows-table-etf', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


# @app.callback([Output('tabs-content-inline', 'children')],
#               [Input('tabs-styled-with-inline', 'value'), Input('adding-rows-table', 'data')])
# def render_content(tab, y):
#
#     df = make_final_df(y)
#
#     if tab == 'tab-1':
#         return html.Div([
#             html.H3('Tab content 1')
#         ])
#     elif tab == 'tab-2':
#         return html.Div([
#             html.H3('Total Pie Chart')
#         ])
#     elif tab == 'tab-3':
#         return html.Div([
#             html.H3('by Sector')
#         ])
#     elif tab == 'tab-4':
#         return html.Div([
#             html.H3('by Industry')
#         ])



@app.callback(
    [Output('graphs-contents', 'children')],
    [Input('submit-button', 'n_clicks'), Input('adding-rows-table', 'data'), Input('adding-rows-table-etf', 'data')]
)
def check(n_clicks, y, e):
    if n_clicks == 0:
        raise PreventUpdate

    a = make_final_df(y)
    b = make_final_df_etf(e)
    df = cal_percentage(a, b)
    fig = make_pie_chart(df)
    return [dcc.Graph(figure=fig)]



app.run_server(debug=True)

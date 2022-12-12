
import requests as http
import streamlit as st
import plotly.graph_objects as go

AV_URL = 'https://alphavantage.co/query'

def get_api_key():
    with open('api-key.txt') as file:
        return file.read()

#@st.cache
def fetch_data(url: str) -> str:
    req = http.get(url)
    if req.status_code != 200:
        raise Exception(f'Request error: {req.status_code} - {req.content}')
    return str(req.content, 'utf-8')

def store_data(data: str, file_path: str):
    with open(file_path, 'w') as file:
        file.write(data)

def load_data(file_path: str) -> str:
    with open(file_path, 'w') as file:
        return file.read()

def intraday_query(api_key, symbol, interval_mins, output_size='compact', data_type='csv'):
    params = f'function=TIME_SERIES_INTRADAY&apikey={api_key}&symbol={symbol}'

    if \
        interval_mins == 1 or interval_mins == '1' or \
        interval_mins == 5 or interval_mins == '5' or \
        interval_mins == 30 or interval_mins == '30' or \
        interval_mins == 60 or interval_mins == '60' \
    :
        params += f'&interval={interval_mins}min'
    else:
        raise Exception(f'Invalid interval: {interval_mins}')

    if output_size == 'compact' or output_size == 'full':
        params += f'&outputsize={output_size}'
    else:
        raise Exception(f'Invalid output size: {output_size}')

    if data_type == 'csv' or data_type == 'json':
        params += f'&datatype={data_type}'
    else:
        raise Exception(f'Invalid data type: {data_type}')
    
    return f'{AV_URL}?{params}'

def daily_adjusted_query(api_key, symbol, output_size='compact', data_type='csv'):
    
    params = f'function=TIME_SERIES_DAILY_ADJUSTED&apikey={api_key}&symbol={symbol}'

    if output_size == 'compact' or output_size == 'full':
        params += f'&outputsize={output_size}'
    else:
        raise Exception(f'Invalid output size: {output_size}')

    if data_type == 'csv' or data_type == 'json':
        params += f'&datatype={data_type}'
    else:
        raise Exception(f'Invalid data type: {data_type}')
    
    return f'{AV_URL}?{params}'

def symbol_search(api_key, keywords, data_type = 'csv'):

    params = params = f'function=SYMBOL_SEARCH&apikey={api_key}&keywords={keywords}'

    if data_type == 'csv' or data_type == 'json':
        params += f'&datatype={data_type}'
    else:
        raise Exception(f'Invalid data type: {data_type}')
    
    return f'{AV_URL}?{params}'

def make_candlestick(symbol, data, title, x='timestamp', open='open', high='high', low='low', close='close'):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x = data[x],
                open = data[open],
                high = data[high],
                low = data[low],
                close = data[close],
                name = symbol.tick()
            )
        ],
        layout_title = title
    )

    fig.update_layout(
        autosize=True,
        height = 700,
        margin = {
            'l': 50,
            'r': 50,
            'b': 50,
            't': 100,
            'pad': 4 
        }
    )

    return fig


class Symbol:
    def __init__(self, tick: str, name: str, region: str) -> None:
        self._tick = tick
        self._name = name
        self._region = region

    def __str__(self) -> str:
        return f'{self._tick} | {self._name} | {self._region}'

    @classmethod
    def from_dict(cls, dict):
        return Symbol(dict['1. symbol'], dict['2. name'], dict['4. region'])

    def tick(self) -> str:
        return self._tick

    def name(self) -> str:
        return self._name
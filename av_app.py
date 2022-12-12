from av_lib import *
import streamlit as st

import requests as http
from io import StringIO
import json

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px

def main():

    api_key = get_api_key()

    st.set_page_config(
        page_title='Stock market analisys',
        initial_sidebar_state = 'expanded',
        layout = 'wide'
    )

    st.write('# Stock market analisys')
    st.markdown('---')

    keywords = st.sidebar.text_input('Search symbols:')
    selected_symbols = []
    if len(keywords) > 0:
        search_url = symbol_search(api_key, keywords, data_type='json')
        symbols = fetch_data(search_url)
        symbols = json.loads(symbols)['bestMatches']
        symbols = list(map( lambda x: Symbol.from_dict(x), symbols))
        selected_symbols.append(st.sidebar.selectbox('Select symbol:', symbols))

    for symbol in selected_symbols:

        st.markdown(f'## {symbol.tick()} - {symbol.name()}')

        url = daily_adjusted_query(api_key, symbol.tick(), 'full')
        data = None
        try:
            data = fetch_data(url)
            data = StringIO(data)
            data = pd.read_csv(data)
        except Exception as e:
            st.error(e)
        #st.write(data)

        try:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        except:
            st.error(f'Query error - symbol: {symbol}')

        candlestick = make_candlestick(symbol, data, title=f'Daily Stock Price - {symbol.tick()}')
        st.write(candlestick)

        log_y = st.sidebar.checkbox('Log scale')

        adj_close = px.line(
            data_frame=data, 
            x='timestamp', 
            y='adjusted_close', 
            title=f'Adjusted Stock Price - {symbol.tick()}',
            labels={
                'timestamp': 'Date',
                'adjusted_close': 'Price'
            },
            log_y=log_y
        )
        st.write(adj_close)


if __name__ == '__main__':
    main()
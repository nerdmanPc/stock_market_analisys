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
        selected_symbols = st.sidebar.multiselect('Select symbols:', symbols)

    for symbol in selected_symbols:
        url = daily_adjusted_query(api_key, symbol.tick())
        data = fetch_data(url)
        data = StringIO(data)
        data = pd.read_csv(data)
        st.write(data)
        data['timestamp'] = pd.to_datetime(data['timestamp'])


        fig = go.Figure(
            data=[
                go.Candlestick(
                    x = data['timestamp'],
                    open = data['open'],
                    high = data['high'],
                    low = data['low'],
                    close = data['close'],
                    name = 'IBM'
                )
            ],
            layout_title = symbol.name()
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

        st.write(fig)


if __name__ == '__main__':
    main()
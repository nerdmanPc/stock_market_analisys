from av_lib import *
from av_load import load_data
from os.path import exists
import pandas as pd
import json
from io import StringIO

DATA_FOLDER = './data/alpha_vantage'

def store_data(data: str, file_path: str):
    with open(file_path, 'w') as file:
        file.write(data)

def init_price_data(api_key, tick):
    price_path = f'{DATA_FOLDER}/price_data/{tick}.csv'
    if not exists(price_path):
        query = daily_adjusted_query(api_key, tick, data_type='csv', output_size='full')
        data = fetch_data(query)
        store_data(data, price_path)

def init_overview_data(api_key, tick):
    overview_path = f'{DATA_FOLDER}/company_data/{tick}.json'
    if not exists(overview_path):
        query = company_overview_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, overview_path)

def init_income_statement(api_key, tick):
    income_path = f'{DATA_FOLDER}/income_statements/{tick}.json'
    if not exists(income_path):
        query = income_statement_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, income_path)

def init_balance_sheet(api_key, tick):
    balance_path = f'{DATA_FOLDER}/balance_sheets/{tick}.json'
    if not exists(balance_path):
        query = balance_sheet_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, balance_path)

def init_cashflow_data(api_key, tick): 
    cashflow_path = f'{DATA_FOLDER}/cashflow_data/{tick}.json'
    if not exists(cashflow_path):
        query = cash_flow_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, cashflow_path)

def init_earnings_data(api_key, tick): 
    earnings_path = f'{DATA_FOLDER}/earnings_data/{tick}.json'
    if not exists(earnings_path):
        query = earnings_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, earnings_path)

#UPDATE

def update_price_data(api_key, tick):
    price_path = f'{DATA_FOLDER}/price_data/{tick}.csv'
    if exists(price_path):
        current_data = load_data(price_path)
        current_data = decode_price_data(current_data)
        current_data.set_index('timestamp', inplace=True)

        query = daily_adjusted_query(api_key, tick, data_type='csv', output_size='full')
        print(f'Query: {query}')
        new_data = fetch_data(query)
        new_data = decode_price_data(new_data)
        new_data.set_index('timestamp', inplace=True)

        final_data = pd.concat([current_data, new_data], axis='index')
        final_data.drop_duplicates(inplace=True)
        final_data.sort_index(ascending=False, inplace=True)
        
        final_data.to_csv(price_path)

def update_overview_data(api_key, tick):
    overview_path = f'{DATA_FOLDER}/company_data/{tick}.json'
    if exists(overview_path):
        query = company_overview_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, overview_path)

def update_income_statement(api_key, tick):
    income_path = f'{DATA_FOLDER}/income_statements/{tick}.json'
    if exists(income_path):
        query = income_statement_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, income_path)

def update_balance_sheet(api_key, tick):
    balance_path = f'{DATA_FOLDER}/balance_sheets/{tick}.json'
    if exists(balance_path):
        query = balance_sheet_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, balance_path)

def update_cashflow_data(api_key, tick): 
    cashflow_path = f'{DATA_FOLDER}/cashflow_data/{tick}.json'
    if exists(cashflow_path):
        query = cash_flow_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, cashflow_path)

def update_earnings_data(api_key, tick): 
    earnings_path = f'{DATA_FOLDER}/earnings_data/{tick}.json'
    if exists(earnings_path):
        query = earnings_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, earnings_path)

if __name__ == '__main__':
    api_key = get_api_key()
    ticks = get_tick_list(f'{DATA_FOLDER}/tick_list.txt')

    for tick in ticks:
        init_price_data(api_key, tick)
        init_overview_data(api_key, tick)
        init_income_statement(api_key, tick)
        init_balance_sheet(api_key, tick)
        init_cashflow_data(api_key, tick)
        init_earnings_data(api_key, tick)

        #update_overview_data(api_key, tick)
        #update_income_statement(api_key, tick)
        #update_balance_sheet(api_key, tick)
        #update_cashflow_data(api_key, tick)
        #update_earnings_data(api_key, tick)
        update_price_data(api_key, tick)
    
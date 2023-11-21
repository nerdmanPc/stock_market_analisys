from av_api import *
from av_load import load_data
from os.path import exists
import pandas as pd
import json
from io import StringIO

DATA_FOLDER = './data/alpha_vantage'

#def store_bytes(data: str, file_path: str):
#    with open(file_path, 'w') as file:
#        file.write(data)

def store_data(data: pd.DataFrame, table: str, tick: str):
    path = f'{DATA_FOLDER}/{table}/{tick}.ftr'
    return data.to_feather(path)

def table_exists(table: str, tick: str) -> bool: 
    path = f'{DATA_FOLDER}/{table}/{tick}.ftr'
    return exists(path)

def init_price_data(api_key, tick):
    table = 'price_data'
    if not table_exists(table, tick):
        query = daily_adjusted_query(api_key, tick, data_type='csv', output_size='full')
        data = fetch_data(query)
        data = decode_price_data(data)
        store_data(data, table, tick)

def init_overview_data(api_key, tick):
    table = 'company_data'
    if not table_exists(table, tick):
        query = company_overview_query(api_key, tick)
        data = fetch_data(query)
        data = decode_company_data(data)
        store_data(data, table, tick)

def init_income_statement(api_key, tick):
    table = 'income_statements'
    if not table_exists(table, tick):
        query = income_statement_query(api_key, tick)
        data = fetch_data(query)
        data = decode_fundamentals(data)
        store_data(data, table, tick)

def init_balance_sheet(api_key, tick):
    table = 'balance_sheets'
    if not table_exists(table, tick):
        query = balance_sheet_query(api_key, tick)
        data = fetch_data(query)
        data = decode_fundamentals(data)
        store_data(data, table, tick)

def init_cashflow_data(api_key, tick): 
    table = 'cashflow_data'
    if not table_exists(table, tick):
        query = cash_flow_query(api_key, tick)
        data = fetch_data(query)
        data = decode_fundamentals(data)
        store_data(data, table, tick)

def init_earnings_data(api_key, tick): 
    table = 'earnings_data'
    if not table_exists(table, tick):
        query = earnings_query(api_key, tick)
        data = fetch_data(query)
        data = decode_earnings_data(data)
        store_data(data, table, tick)

#UPDATE

def update_price_data(api_key, tick):
    table = 'price_data'
    #price_path = f'{DATA_FOLDER}/{table}/{tick}.csv'
    if table_exists(table, tick):
        current_data = load_data(table, tick)
        current_data.set_index('timestamp', inplace=True)

        query = daily_adjusted_query(api_key, tick, data_type='csv', output_size='full')
        #print(f'Query: {query}')
        new_data = fetch_data(query)
        new_data = decode_price_data(new_data)
        new_data.set_index('timestamp', inplace=True)

        final_data = pd.concat([current_data, new_data], axis='index')
        final_data.drop_duplicates(inplace=True)
        final_data.sort_index(ascending=False, inplace=True)

        store_data(final_data.reset_index(), table, tick)

def update_overview_data(api_key, tick):
    table = 'company_data'
    #overview_path = f'{DATA_FOLDER}/company_data/{tick}.json'
    if table_exists(table, tick):
        query = company_overview_query(api_key, tick)
        data = fetch_data(query)
        store_bytes(data, overview_path)

def update_income_statement(api_key, tick):
    table = 'income_statements'
    #income_path = f'{DATA_FOLDER}/income_statements/{tick}.json'
    if table_exists(table, tick):
        query = income_statement_query(api_key, tick)
        data = fetch_data(query)
        store_bytes(data, income_path)

def update_balance_sheet(api_key, tick):
    table = 'balance_sheets'
    #balance_path = f'{DATA_FOLDER}/balance_sheets/{tick}.json'
    if table_exists(table, tick):
        query = balance_sheet_query(api_key, tick)
        data = fetch_data(query)
        store_bytes(data, balance_path)

def update_cashflow_data(api_key, tick):
    table = 'cashflow_data'
    #cashflow_path = f'{DATA_FOLDER}/cashflow_data/{tick}.json'
    if table_exists(table, tick):
        query = cash_flow_query(api_key, tick)
        data = fetch_data(query)
        store_bytes(data, cashflow_path)

def update_earnings_data(api_key, tick): 
    table = 'earnings_data'
    #earnings_path = f'{DATA_FOLDER}/earnings_data/{tick}.json'
    if table_exists(table, tick):
        current_data = load_data(table, tick)
        current_data.set_index('timestamp', inplace=True)

        query = earnings_query(api_key, tick)
        data = fetch_data(query)
        store_data(data, table, tick)

        new_data = fetch_data(query)
        new_data = decode_earnings_data(new_data)
        new_data.set_index('timestamp', inplace=True)

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
    
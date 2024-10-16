
import requests as http
from time import sleep
import json
from datetime import date

AV_ENDPOINT = 'https://alphavantage.co/query'

class AlphaVantage:

    def __init__(self, api_key=None, request_callback=None) -> None:
        self._api_key = api_key or get_api_key()
        self._fetch_data = request_callback or fetch_data

    def search_symbol(self, keywords, data_type='json') -> str:
        query = self.symbol_search_query(keywords, data_type)
        return self._fetch_data(query)

    def symbol_search_query(self, keywords, data_type='json') -> str:
        arguments = {
            'function': 'SYMBOL_SEARCH',
            'apikey': self._api_key,
            'keywords': keywords,
            'datatype': data_type
        }
        validate_arguments(**arguments)
        arguments = assemble_arguments(**arguments)
        return f'{AV_ENDPOINT}?{arguments}'
    
    def get_intraday(self, symbol, interval_mins, output_size='full', data_type='json') -> str:
        query = self.intraday_query(symbol, interval_mins, output_size, data_type)
        return self._fetch_data(query)

    def intraday_query(self, symbol, interval_mins, output_size='full', data_type='json') -> str:
        arguments = {
            'function': 'TIME_SERIES_INTRADAY',
            'apikey': self._api_key,
            'symbol': symbol,
            'interval': interval_mins,
            'outputsize': output_size,
            'datatype': data_type
        }
        validate_arguments(**arguments)
        arguments = assemble_arguments(**arguments)
        return f'{AV_ENDPOINT}?{arguments}'
    
    def get_daily_adjusted(self, symbol, output_size='full', data_type='json') -> str:
        query = self.daily_adjusted_query(symbol, output_size, data_type)
        return self._fetch_data(query)

    def daily_adjusted_query(self, symbol, output_size='full', data_type='json') -> str:
        arguments = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'apikey': self._api_key,
            'symbol': symbol,
            'outputsize': output_size,
            'datatype': data_type
        }
        validate_arguments(**arguments)
        arguments = assemble_arguments(**arguments)
        return f'{AV_ENDPOINT}?{arguments}'
    
    def get_weekly_adjusted(self, symbol, data_type='json') -> str:
        query = self.weekly_adjusted_query(symbol, data_type)
        return self._fetch_data(query)

    def weekly_adjusted_query(self, symbol, data_type='json') -> str:
        arguments = {
            'function': 'TIME_SERIES_WEEKLY_ADJUSTED',
            'apikey': self._api_key,
            'symbol': symbol,
            'datatype': data_type
        }
        validate_arguments(**arguments)
        arguments = assemble_arguments(**arguments)
        return f'{AV_ENDPOINT}?{arguments}'
    
    def get_company_overview(self, symbol) -> str:
        query = self.company_overview_query(symbol)
        return self._fetch_data(query)

    def company_overview_query(self, symbol) -> str:
        params = f'function=OVERVIEW&apikey={self._api_key}&symbol={symbol}'
        return f'{AV_ENDPOINT}?{params}'
    
    def get_income_statement(self, symbol) -> str:
        query = self.income_statement_query(symbol)
        return self._fetch_data(query)

    def income_statement_query(self, symbol) -> str:
        params = f'function=INCOME_STATEMENT&apikey={self._api_key}&symbol={symbol}'
        return f'{AV_ENDPOINT}?{params}'

    def get_balance_sheet(self, symbol) -> str:
        query = self.balance_sheet_query(symbol)
        return self._fetch_data(query)

    def balance_sheet_query(self, symbol) -> str:
        params = f'function=BALANCE_SHEET&apikey={self._api_key}&symbol={symbol}'
        return f'{AV_ENDPOINT}?{params}'
    
    def get_cash_flow(self, symbol) -> str:
        query = self.cash_flow_query(symbol)
        return self._fetch_data(query)

    def cash_flow_query(self, symbol) -> str:
        params = f'function=CASH_FLOW&apikey={self._api_key}&symbol={symbol}'
        return f'{AV_ENDPOINT}?{params}'
    
    def get_earnings(self, symbol) -> str:
        query = self.earnings_query(symbol)
        return self._fetch_data(query)

    def earnings_query(self, symbol) -> str:
        params = f'function=EARNINGS&apikey={self._api_key}&symbol={symbol}'
        return f'{AV_ENDPOINT}?{params}'
    
def validate_arguments(**kw_args):
    match kw_args['function']:
        case 'SYMBOL_SEARCH':
            data_type = kw_args['datatype']
            if not(data_type == 'csv' or data_type == 'json'):
                raise Exception(f'Invalid data type: {data_type}')
        case 'TIME_SERIES_INTRADAY':
            interval_mins = kw_args['interval']
            if not(interval_mins in [1, 5, 30, 60, '1', '5', '30', '60']):
                raise Exception(f'Invalid interval: {interval_mins}')
            output_size = kw_args['outputsize']
            if not(output_size == 'full' or output_size == 'full'):
                raise Exception(f'Invalid output size: {output_size}')
            data_type = kw_args['datatype']
            if not(data_type == 'csv' or data_type == 'json'):
                raise Exception(f'Invalid data type: {data_type}')
        case ('TIME_SERIES_DAILY_ADJUSTED'):
            output_size = kw_args['outputsize']
            if not(output_size == 'full' or output_size == 'full'):
                raise Exception(f'Invalid output size: {output_size}')
            data_type = kw_args['datatype']
            if not(data_type == 'csv' or data_type == 'json'):
                raise Exception(f'Invalid data type: {data_type}')
        case ('TIME_SERIES_WEEKLY_ADJUSTED'):
            data_type = kw_args['datatype']
            if not(data_type == 'csv' or data_type == 'json'):
                raise Exception(f'Invalid data type: {data_type}')
        case ('OVERVIEW'|'INCOME_STATEMENT'|'BALANCE_SHEET'|'CASH_FLOW'|'EARNINGS'): pass
        case invalid_function : raise Exception(f'Invalid function: {invalid_function}')

def assemble_arguments(**kw_args) -> str:
    pairs = [f'{name}={value}' for name, value in kw_args.items()]
    return '&'.join(pairs)

def extract_arguments(url: str) -> dict[str, str]:
    [endpoint, args] = url.split('?')
    args = { arg.split('=')[0]: arg.split('=')[1] for arg in args.split('&') }
    args['ENDPOINT'] = endpoint
    return args


def get_api_key():
    with open('api-key.txt') as file:
        return file.read()

def fetch_data(url: str) -> str:
    print(f'Fetching data from: {url}')
    req = http.get(url)
    if req.status_code != 200:
        raise Exception(f'Request error {req.status_code}:\n{req.content}')
    data = str(req.content, 'utf-8')
    check_api_error(data, url)
    print('Fetching successful!')
    return data

def check_api_error(data: str, url: str):
    err_msg = None
    try: # Happy path is when there is no 'Error Message'
        err_msg = json.loads(data)['Error Message']
    except: pass
    try:
        err_msg = json.loads(data)['Information']
    except: pass
    if err_msg: 
        raise Exception(f'API error!\nMessage: {err_msg}\nURL: {url}')


def decode_price_data(data: str, tick: str) -> list[tuple]:
    data = json.loads(data)["Weekly Adjusted Time Series"]
    return [decode_row((tick, timestamp, *row.values())) for timestamp, row in data.items()]

def decode_earnings_data(data: str, tick: str):
    data = json.loads(data)
    if 'quarterlyEarnings' in data:
        data = data['quarterlyEarnings']
    elif 'annualEarnings' in data:
        data = data['annualEarnings']
    else:
        raise Exception(f'Malformed earnings data:\n{data}')
    return [decode_row((tick, *row.values())) for row in data]

def decode_fundamentals(data: str, tick: str) -> list[tuple]:
    data = json.loads(data)
    if 'quarterlyReports' in data:
        data = data['quarterlyReports']
    elif 'annualReports' in data:
        data = data['annualReports']
    else:
        raise Exception(f'Malformed fundamental data:\n{data}')
    return [decode_row((tick, *row.values())) for row in data]

def decode_company_data(data: str) -> list[tuple]:
    data = json.loads(data)
    return [decode_row(data.values())]

def decode_row(row: list[str]) -> tuple:
    if not row:
        return ()
    head, *tail = row
    if head == 'None':
        return (None, *decode_row(tail))
    try: 
        return (int(head), *decode_row(tail))
    except: pass
    try: 
        return (float(head), *decode_row(tail))
    except: pass
    try: 
        return (date.fromisoformat(head), *decode_row(tail))
    except: pass
    return (head, *decode_row(tail))
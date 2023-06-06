import json
import pandas as pd

def load_data(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

def load_json(table_name: str, tick: str) -> dict:
    return json.loads(load_data(f'./data/alpha_vantage/{table_name}/{tick}.json'))

def convert_type(column: pd.Series) -> pd.Series:
    if column.name in ['tick', 'reportedCurrency']:
        return column
    elif column.name in ['reportedDate', 'fiscalDateEnding', 'timestamp']:
        return pd.to_datetime(column)
    else:
        return pd.to_numeric(column, errors='coerce')
    
def get_quarterly_reports(data: dict) -> list:
    if 'quarterlyReports' in data:
        return data['quarterlyReports']
    else:
        return data['quarterlyEarnings']

def rename_timestamp(data: pd.DataFrame, use_reported_date: bool) -> None:
    if ('reportedDate' in data.columns) and use_reported_date:
        data.rename(columns={'reportedDate': 'timestamp'}, inplace=True)
    else:
        data.rename(columns={'fiscalDateEnding': 'timestamp'}, inplace=True)
    
def load_fundamentals(table_name: str, tick: str, use_reported_date: bool=False) -> pd.DataFrame:
    data = load_json(table_name, tick)
    data = get_quarterly_reports(data)
    data = pd.DataFrame(data)
    data = data.apply(convert_type)
    rename_timestamp(data, use_reported_date)
    data['tick'] = tick
    data.set_index(['tick', 'timestamp'], inplace=True)
    return data
    
# REFACTOR TO USE decode_price_data()
def load_price_data(tick_list: list[str], format='csv') -> pd.DataFrame:
    price_data = []
    for tick in tick_list:
        tick_data = None
        if format == 'json':
            tick_data = load_json('price_data', tick)['Time Series (Daily)']
            tick_data = current_data = [
                {
                    'timestamp': key,
                    'open': value['1. open'],
                    'high': value['2. high'],
                    'low': value['3. low'],
                    'close': value['4. close'],
                    'adjusted_close': value['5. adjusted close'],
                    'volume': value['6. volume'],
                    'dividend_amount': value['7. dividend amount'],
                    'split_coefficient': value['8. split coefficient'],
                } 
                for key, value in current_data.items()
            ]
            tick_data = pd.DataFrame(tick_data)
        else:
            tick_data = pd.read_csv(f'./data/alpha_vantage/price_data/{tick}.csv')
        tick_data['timestamp'] = pd.to_datetime(tick_data['timestamp'])
        tick_data['tick'] = tick
        tick_data.set_index(['tick', 'timestamp'], inplace=True)
        price_data.append(tick_data)
    return pd.concat(price_data)
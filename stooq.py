import pandas as pd
import numpy as np
from random import random
from pathlib import Path

def load_table(path: Path) -> pd.DataFrame | None:
    try: 
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return None
    
def build_prices_table(directory: str, period: str, market: str) -> pd.DataFrame:
    pathes = Path(f'{directory}/{period}/{market}').glob(f'* stocks/*/*.{market}.txt')
    tables = [load_table(path) for path in pathes if path]
    tables = pd.concat(tables)
    tables.drop(columns=['<PER>', '<OPENINT>'], inplace=True, errors='ignore')
    tables['<DATE>'] = pd.to_datetime(tables['<DATE>'].astype(str))
    tables.reset_index(drop=True, inplace=True)
    tables.sort_values(['<TICKER>', '<DATE>'], inplace=True)
    return tables

def add_one_cent_noise(table: pd.DataFrame) -> pd.DataFrame:
    table['<CLOSE>'] = table['<CLOSE>'].apply(lambda x: x + (random())*0.01 )
    return table

def add_columns_prices(table: pd.DataFrame) -> pd.DataFrame:
    table['<RETURN>'] = table['<CLOSE>'] / table.groupby('<TICKER>')['<CLOSE>'].shift()
    table['<LOG_CLOSE>'] = np.log(table['<CLOSE>'])
    table['<LOG_RETURN>'] = np.log(table['<RETURN>'])
    return table
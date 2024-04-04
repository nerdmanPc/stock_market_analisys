import pandas as pd
import json
from datetime import timedelta

def load_company(cik: int) -> dict:
    return json.load(open(f'data/sec/companyfacts/CIK{str(cik).zfill(10)}.json'))

def get_time_series(sec_data: dict, col_name: str, currency: str='USD') -> pd.DataFrame:
    time_series = sec_data['facts']['us-gaap'][col_name]['units'][currency]
    time_series = pd.DataFrame(time_series)
    return time_series

def convert_datetimes(time_series: pd.DataFrame):
    time_series['start'] = pd.to_datetime(time_series['start'])
    time_series['end'] = pd.to_datetime(time_series['end'])
    time_series['filed'] = pd.to_datetime(time_series['filed'])

def add_time_offsets(time_series: pd.DataFrame):
    time_series['delay'] = time_series['filed'] - time_series['end']
    time_series['period'] = time_series['end'] - time_series['start']

def drop_unused_columns(time_series: pd.DataFrame):
    time_series.drop(columns=['frame', 'accn', 'start', 'form'], inplace=True)

def get_current_quarters_years(time_series: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    is_current = (time_series['delay'] < timedelta(days=45))
    is_quarter = (time_series['period'] < timedelta(days=135))
    is_fiscal_year = (time_series['period'] > timedelta(days=315))
    quarters = time_series[ is_current & is_quarter ] 
    years = time_series[ is_current & is_fiscal_year ]
    return (quarters, years)

def add_q4(fiscal_year: pd.DataFrame, fy_quarters: pd.DataFrame) -> pd.DataFrame: 
    if (fy_quarters.fp == 'FY').any() or fiscal_year.empty: 
        return fy_quarters
    year_row = fiscal_year.iloc[0]
    q1_row, q2_row, q3_row = fy_quarters[fy_quarters.fp == 'Q1'].iloc[0], fy_quarters[fy_quarters.fp == 'Q2'].iloc[0], fy_quarters[fy_quarters.fp == 'Q3'].iloc[0]
    q4 = {
        'end': [year_row.end],
        'val': [year_row.val - q3_row.val - q2_row.val - q1_row.val],
        'fy': [year_row.fy],
        'fp': ['FY'],
        'filed': [year_row.filed],
        'delay': [year_row.delay],
        'period': [year_row.end - (q3_row.end + timedelta(days=1))],
    }
    fy_quarters = pd.concat([fy_quarters, pd.DataFrame(q4)], axis='index')
    return fy_quarters

'''
# Gets Q4 value from time series as FY - Q3 - Q2 - Q1
fiscal_years = []
for year, fy_data in quarters.groupby('fy'):
    if (fy_data.fp == 'FY').any() or not (years.fy == year).any(): 
        fiscal_years.append(fy_data)
        continue
    year_row = years[years.fy == year].iloc[0]
    q1_row, q2_row, q3_row = fy_data[fy_data.fp == 'Q1'].iloc[0], fy_data[fy_data.fp == 'Q2'].iloc[0], fy_data[fy_data.fp == 'Q3'].iloc[0]
    q4 = {
        'end': [year_row.end],
        'val': [year_row.val - q3_row.val - q2_row.val - q1_row.val],
        'fy': [year],
        'fp': ['FY'],
        'form': ['10-K'],
        'filed': [year_row.filed],
        'delay': [year_row.delay],
        'period': [year_row.end - (q3_row.end + timedelta(days=1))],
    }
    fy_data = pd.concat([fy_data, pd.DataFrame(q4)], axis='index')
    fiscal_years.append(fy_data)

final_df: pd.DataFrame = pd.concat(fiscal_years)
final_df['fp'] = final_df.fp.map({'Q1': 'Q1', 'Q2': 'Q2', 'Q3': 'Q3', 'FY': 'Q4'})
final_df.set_index(['fy', 'fp']).sort_index()
'''
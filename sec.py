import pandas as pd
import json
from tqdm.notebook import tqdm
from datetime import timedelta

def load_company(cik: int, directory) -> dict | None:
    try: 
        return json.load(open(f'{directory}/CIK{str(cik).zfill(10)}.json'))
    except FileNotFoundError:
        return None

def get_time_series(sec_data: dict, col_name: str, currency: str='USD') -> pd.DataFrame:
    time_series = sec_data['facts']['us-gaap'][col_name]['units'][currency]
    time_series = pd.DataFrame(time_series)
    return time_series

def convert_datetimes(time_series: pd.DataFrame):
    time_series['filed'] = pd.to_datetime(time_series['filed'])
    time_series['end'] = pd.to_datetime(time_series['end'])
    try: time_series['start'] = pd.to_datetime(time_series['start']) 
    except KeyError: time_series['start'] = time_series['end'] - timedelta(days=90)

def add_time_offsets(time_series: pd.DataFrame):
    time_series['delay'] = time_series['filed'] - time_series['end']
    time_series['period'] = time_series['end'] - time_series['start']

def drop_unused_columns(time_series: pd.DataFrame):
    time_series.drop(columns=['frame', 'accn', 'start', 'form'], inplace=True)

def get_current_quarters_years(time_series: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    is_current = (time_series['delay'] < timedelta(days=60))
    is_quarter = (time_series['period'] < timedelta(days=135))
    is_fiscal_year = (time_series['period'] > timedelta(days=315))
    quarters = pd.DataFrame(time_series[ is_current & is_quarter ] )
    years = pd.DataFrame(time_series[ is_current & is_fiscal_year ])
    return (quarters, years)

def add_q4(fy_quarters: pd.DataFrame, fiscal_year: pd.DataFrame) -> pd.DataFrame: 
    if (
        (fy_quarters.fp == 'FY').any() or
        (fy_quarters.fp == 'Q1').sum() != 1 or
        (fy_quarters.fp == 'Q2').sum() != 1 or
        (fy_quarters.fp == 'Q3').sum() != 1 or 
        fiscal_year.empty
    ): 
        return fy_quarters
    year_row = fiscal_year.sort_values('delay', ascending=False).iloc[0]
    q1_row = fy_quarters[fy_quarters.fp == 'Q1'].sort_values('delay', ascending=False).iloc[0] 
    q2_row = fy_quarters[fy_quarters.fp == 'Q2'].sort_values('delay', ascending=False).iloc[0]
    q3_row = fy_quarters[fy_quarters.fp == 'Q3'].sort_values('delay', ascending=False).iloc[0]
    q4 = {
        'end': [year_row.end],
        'val': [year_row.val - q3_row.val - q2_row.val - q1_row.val],
        'fy': [year_row.fy],
        'fp': ['FY'],
        'filed': [year_row.filed],
        'delay': [year_row.delay],
        'period': [year_row.end - (q3_row.end + timedelta(days=1))],
    }
    if q4['period'][0] < timedelta(days=135): 
        fy_quarters = pd.concat([fy_quarters, pd.DataFrame(q4)], axis='index', ignore_index=True)
    return fy_quarters

def build_fundamental_col(directory: str, column_name: str, unit: str, column_alias: str, companies) -> pd.DataFrame:
    time_series = []
    for company_cik in tqdm(companies):
        try:
            company_data = load_company(company_cik, directory)
            if company_data is None: continue
            company_data = get_time_series(company_data, column_name, unit)
            convert_datetimes(company_data)
            add_time_offsets(company_data)
            drop_unused_columns(company_data)
            quarters, years = get_current_quarters_years(company_data)
            company_data = [add_q4(quarters, years[years.fy == fy]) for fy, fy_quarters in quarters.groupby('fy')]
            company_data = pd.concat(company_data, ignore_index=True)
            company_data['cik'] = company_cik

            company_data.drop(columns=['end', 'fy', 'fp', 'period', 'delay'], inplace=True)
            company_data.set_index(['cik', 'filed'], inplace=True)
            company_data.drop_duplicates(inplace=True)
            time_series.append(company_data)
        except KeyError as ke:
            #display(ke)
            continue
        except ValueError as ve:
            #display(ve)
            continue
    time_series = pd.concat(time_series).rename({'val': column_alias}, axis='columns')
    #display(time_series.columns)
    return time_series

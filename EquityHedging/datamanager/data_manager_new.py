# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi
"""
import copy
from datetime import datetime as dt

import pandas as pd
from math import isnan

NEW_DATA_COL_LIST = ['SPTR', 'SX5T', 'M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                     'Vortex', 'VOLA I', 'VOLA II', 'Dynamic VOLA', 'Dynamic Put Spread',
                     'GW Dispersion', 'Corr Hedge', 'Def Var (Mon)', 'Def Var (Fri)', 'Def Var (Wed)',
                     'Commodity Basket']

LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A', 'Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital'],
                     'Trend Following': ['1907 ARP TF', '1907 Campbell TF', '1907 Systematica TF',
                                         'One River Trend'],
                     'Absolute Return': ['1907 ARP EM', '1907 III CV', '1907 III Class A',
                                         'ABC Reversion', 'Acadian Commodity AR',
                                         'Blueshift', 'Duality', 'Elliott'],
                     }


def merge_dicts_list(dict_list, drop_na=True, fillzeros=False, how='outer'):
    """
    merge main dictionary with a dictionary list

    Parameters
    ----------
    dict_list : list
    drop_na: bool
    fillzeros: bool
    how: basestring
    Returns
    -------
    main_dict : dictionary
        new dictionary created upon being merged with a list

    """
    main_dict = dict_list[0]
    dict_list.remove(main_dict)
    # iterate through dictionary
    for new_dict in dict_list:
        # merge each dictionary in the list of dictionaries to the main
        main_dict = merge_dicts(main_dict=main_dict, new_dict=new_dict, drop_na=drop_na, fillzeros=fillzeros, how=how)
    return main_dict


def merge_dicts(main_dict, new_dict, drop_na=True, fillzeros=False, how='outer'):
    """
    Merge new_dict to main_dict

    Parameters:
    main_dict -- dictionary
    new_dict -- dictionary
    drop_na -- bool
    fillzeros -- bool

    Returns:
    dictionary
    """

    merged_dict = {}
    for key in main_dict:
        try:
            main_df = main_dict[key].copy()
            new_df = new_dict[key]
            merged_dict[key] = merge_dfs(main_df, new_df, drop_na=drop_na, fillzeros=fillzeros, how=how)
        except (ValueError, KeyError) as error:
            print(error)
            pass
    return merged_dict


def merge_df_lists(df_list, drop_na=True, fillzeros=False, how='outer'):
    main_df = df_list[0]
    df_list.remove(main_df)
    # iterate through dictionary
    for new_df in df_list:
        # merge each dictionary in the list of dictionaries to the main
        main_df = merge_dfs(main_df=main_df, new_df=new_df, drop_na=drop_na, fillzeros=fillzeros, how=how)
    return main_df


def merge_dfs(main_df, new_df, drop_na=True, fillzeros=False, how='outer'):
    """
    Merge df_new to df_main and drop na values

    Parameters:
    df_main -- dataframe
    df_new -- dataframe
    drop_na -- bool
    fillzeros -- bool
    how -- string

    Returns:
    dataframe
    """

    df = pd.merge(main_df, new_df, left_index=True, right_index=True, how=how)
    if drop_na:
        # Find first valid index for each column in df
        first_valid_index_list = [get_first_valid_index(df[col]) for col in df]
        first_valid_index_list.sort(reverse=True)
        # Find last valid index for each column in df
        last_valid_index_list = [get_last_valid_index(df[col]) for col in df]
        last_valid_index_list.sort(reverse=True)
        no_rows_from_last = len(df) - last_valid_index_list[0]
        # drop invalid indices from top and bottom of df
        if no_rows_from_last > 1:
            df = df[:-no_rows_from_last]
        if first_valid_index_list[0] > 0:
            df = df.iloc[first_valid_index_list[0]:, ]
        # fill rest of nans with 0
        # TODO: might want to fill with last relevant index if df is price data, 0 only works for returns data
        df = df.fillna(0)
        df.dropna(inplace=True)
    if fillzeros:
        df = df.fillna(0)
    return df


def get_columns_data(data):
    if isinstance(data, dict):
        col_data = {}
        for key in data:
            col_data[key] = list(data[key].columns)
    else:
        return list(data.columns)


def get_min_max_dates(returns_df):
    """
    Return a dict with the min and max dates of a dataframe.

    Parameters:
    df_returns -- dataframe with index dates

    Returns:
    dict(key (string), value(dates))
    """
    # get list of date index
    dates_list = list(returns_df.index.values)
    try:
        dates = {'start': dt.utcfromtimestamp(dates_list[0].astype('O') / 1e9),
                 'end': dt.utcfromtimestamp(dates_list[len(dates_list) - 1].astype('O') / 1e9)}
        return dates
    except TypeError:
        print(TypeError)


def remove_na_from_dates_index(data_df):
    data_df.index.names = ['Dates']
    data_df.reset_index(inplace=True)
    data_df = data_df.dropna(subset=['Dates'])
    data_df.set_index('Dates', inplace=True)
    return data_df


def compute_no_of_years(df_returns):
    """
    Returns number of years in a dataframe based off the min and max dates

    Parameters:
    df_returns -- dataframe with returns

    Returns:
    double
    """

    min_max_dates = get_min_max_dates(df_returns)
    no_of_years = (min_max_dates['end'] - min_max_dates['start']).days / 365
    return no_of_years


def switch_freq_int(arg):
    """
    Return an integer equivalent to frequency in years

    Parameters:
    arg -- string ('D', 'W', 'M')

    Returns:
    int of frequency in years
    """
    switcher = {
        "D": 252,
        "B": 252,
        "W": 52,
        "M": 12,
        "Q": 4,
        "Y": 1,
        "A": 1,
        "1D": 252,
        "1W": 52,
        "1M": 12,
        "1Q": 4,
        "1Y": 1,
        "1A": 1,
    }
    return switcher.get(arg, 252)


def switch_freq_list(arg):
    """
    Return an integer equivalent to frequency in years

    Parameters:
    arg -- string ('D', 'W', 'M')

    Returns:
    int of frequency in years
    """
    switcher = {
        "D": ['D', 'W', 'M', 'Q', 'Y'],
        "W": ['W', 'M', 'Q', 'Y'],
        "M": ['M', 'Q', 'Y'],
        "Q": ['Q', 'Y'],
        "Y": ['Y'],
    }
    return switcher.get(arg, ['D', 'W', 'M', 'Q', 'Y'])


def switch_freq_string(arg):
    """
    Return an string equivalent to frequency
    eg: swith_freq_string('D') returns 'Daily'

    Parameters:
    arg -- string ('D', 'W', 'M')

    Returns:
    string
    """
    switcher = {
        "D": "Daily",
        "B": "Daily",
        "W": "Weekly",
        "M": "Monthly",
        "Q": "Quarterly",
        "Y": "Yearly",
        "A": "Yearly",
        "1D": "Daily",
        "1W": "Weekly",
        "1M": "Monthly",
        "1Q": "Quarterly",
        "1Y": "Yearly",
        "1A": "Yearly",
    }
    return switcher.get(arg, 'Daily')


def format_date_index(data_df, freq='M'):
    try:
        if 'Y' in freq or 'A' in freq:
            data_df.index = data_df.index.year
        if 'Q' in freq:
            data_df.index = 'Q' + data_df.index.quarter.astype(str) + ' ' + data_df.index.year.astype(str)
        if 'M' in freq:
            data_df.index = data_df.index.month_name().str[:3].astype(str) + ' ' + data_df.index.year.astype(str)
    except AttributeError:
        pass
    return data_df


def switch_string_freq(arg):
    """
    Return an string equivalent to freq
    eg: swith_freq_string('Daily') returns 'D'

    Parameters:
    arg -- string ('D', 'W', 'M')

    Returns:
    string
    """
    switcher = {
        "Daily": "D",
        "Weekly": "W",
        "Monthly": "M",
        "Quarterly": "Q",
        "Yearly": "Y",
    }
    return switcher.get(arg, 'D')


def get_freq(returns_df):
    dates = returns_df.index
    date_rng = pd.to_datetime(dates)  # DatetimeIndex
    freq = pd.infer_freq(date_rng)
    if freq is not None:
        if freq[0] == 'B':
            return 'D'
        else:
            return freq[0]
    else:
        return 'D'


def get_freq_string(returns_df):
    return switch_freq_string(get_freq(returns_df))


def get_freq_data(returns_df):
    freq = get_freq(returns_df)
    return {'freq': freq, 'freq_string': switch_freq_string(freq), 'freq_int': switch_freq_int(freq)}


def remove_na(df, col_name):
    """
    Remove na values from column

    Parameters:
    df -- dataframe
    col_name -- string (column name in dataframe)

    Returns:
    dataframe
    """
    clean_df = pd.DataFrame(df[col_name].copy())
    clean_df.dropna(inplace=True)
    return clean_df


def get_freq_ratio(freq1, freq2):
    """
    Returns ratio of 2 frequencies

    Parameters:
    freq1 -- string
    freq2 -- string

    Returns:
    int
    """

    return round(switch_freq_int(freq1) / switch_freq_int(freq2))


def convert_to_freq2(arg, freq1, freq2):
    """
    Converts number from freq1 to freq2

    Parameters:
    arg -- int
    freq1 -- string
    freq2 -- string

    Returns:
    int
    """

    return round(arg / get_freq_ratio(freq1, freq2))


def drop_nas(data, axis=0):
    if isinstance(data, dict):
        for key in data:
            data[key].dropna(inplace=True, axis=axis)
    else:
        data.dropna(inplace=True, axis=axis)
    return data


def check_col_len(df, col_list):
    if len(col_list) != len(df.columns):
        return list(df.columns)
    else:
        return col_list


def rename_columns(data, col_dict):
    if isinstance(data, dict):
        for key in data:
            data[key].rename(columns=col_dict, inplace=True)
    else:
        data.rename(columns=col_dict, inplace=True)
    return data


def get_notional_weights(returns_df):
    """
    Returns list of notional values for stratgies

    Parameters:
    df_returns -- dataframe

    Returns:
    list
    """
    weights = [float(input('notional value (Billions) for ' + col + ': ')) for col in returns_df.columns]
    # df_returns = create_vrr_portfolio(df_returns, weights)
    # weights.append(weights[4]+weights[5])
    # del weights[4:6]
    return weights


# TODO: Move to DataImporter


# TODO: Move to analytics


# TODO: Move to analytics


# TODO: read the whole work book as a dicitonary then format by key


def check_notional(returns_df, notional_weights=[]):
    """
    Get notional weights if some weights are missing

    Parameters
    ----------
    returns_df : dataframe
        dataframe of returns
    notional_weights : list, optional
        notional weights of strategies. The default is [].

    Returns
    -------
    notional_weights : list

    """
    # create list of df_returns column names
    col_list = list(returns_df.columns)

    # get notional weights for weighted strategy returns if not accurate
    if len(col_list) != len(notional_weights):
        notional_weights = get_notional_weights(returns_df)

    return notional_weights


def get_weights(mvs_df: pd.DataFrame, total_col: bool = False, add_total_wgt: bool = False) -> pd.DataFrame:
    if total_col:
        col_len = mvs_df.shape[1] - 1
        weights_df = mvs_df.iloc[:, :col_len].divide(mvs_df.iloc[:, :col_len].sum(axis=1), axis='rows')
    else:
        weights_df = mvs_df.divide(mvs_df.sum(axis=1), axis='rows')

    if add_total_wgt:
        total_name = mvs_df.columns[col_len] if total_col else 'Total'
        weights_df[total_name] = weights_df.sum(axis=1)
    return weights_df


def get_agg_data(returns_df, mvs_df, agg_col='Total-Composite', merge_agg=False):
    agg_ret = returns_df.copy()
    agg_mv = mvs_df.copy()
    weights = get_weights(agg_mv)
    agg_ret[agg_col] = (agg_ret * weights).sum(axis=1)
    agg_mv[agg_col] = agg_mv.sum(axis=1)
    weights[agg_col] = weights.sum(axis=1)
    if merge_agg:
        return {'returns': agg_ret, 'market_values': agg_mv, 'weights': weights}
    else:
        return {'returns': agg_ret[[agg_col]], 'market_values': agg_mv[[agg_col]],
                'weights': weights[[agg_col]]
                }


def get_period_dict(returns_df):
    obs = len(returns_df)
    freq = get_freq(returns_df)
    m = switch_freq_int(freq)
    full_dict = {'Full': returns_df}
    if obs <= m:
        return full_dict
    else:
        if obs <= 3 * m:
            period_dict = {'1 Year': returns_df.iloc[obs - m:, ]}
        elif obs <= 5 * m:
            period_dict = {'3 Year': returns_df.iloc[obs - 3 * m:, ],
                           '1 Year': returns_df.iloc[obs - m:, ]}
        elif obs <= 10 * m:
            period_dict = {'5 Year': returns_df.iloc[obs - 5 * m:, ],
                           '3 Year': returns_df.iloc[obs - 3 * m:, ],
                           '1 Year': returns_df.iloc[obs - m:, ]}
        else:
            period_dict = {'10 Year': returns_df.iloc[obs - 10 * m:, ],
                           '5 Year': returns_df.iloc[obs - 5 * m:, ],
                           '3 Year': returns_df.iloc[obs - 3 * m:, ],
                           '1 Year': returns_df.iloc[obs - m:, ]}
        period_dict = {key: drop_nas(value, axis=1) for key, value in period_dict.items()}
        returns_dict = full_dict | period_dict
        return returns_dict


def get_last_n_values(dict, n=1):
    """Returns the last n values of a dictionary.

    Args:
      dict: The dictionary to get the values from.
      n: The number of values to get.

    Returns:
      A list of the last n values of the dictionary.
    """

    # Get the keys of the dictionary in reverse order.
    keys = list(dict.keys())[::-1]

    # Get the last n values of the dictionary.
    values = [dict[key] for key in keys[:n]]

    return values


def compare_freq(main_df, new_df):
    return get_freq(main_df) == get_freq(new_df)


def drop_data(data_df, drop_list, drop_col=True, drop_row=False):
    if drop_col:
        data_df.drop(drop_list, axis=1, inplace=True)
    if drop_row:
        data_df.drop(drop_list, axis=0, inplace=True)
    return data_df


def filter_data_dict(data_dict, filter_list):
    return {key: data_dict[key] for key in filter_list}


def is_nan(value):
    return isnan(float(value))


def check_freq(data_df, freq='M'):
    data_freq = get_freq(data_df)
    return data_freq.__eq__(freq)


def copy_data(data):
    return copy.deepcopy(data) if isinstance(data, dict) else data.copy()


def get_date_offset(freq):
    switcher = {
        "D": pd.DateOffset(days=1),
        "W": pd.DateOffset(weeks=1),
        "M": pd.DateOffset(months=1),
        "Q": pd.DateOffset(months=3),
        "Y": pd.DateOffset(years=1)
    }
    return switcher.get(freq, 'D')


def replace_value_with_nan(data_df, value=0):
    data_df = remove_na_from_dates_index(data_df)
    nan_filter = data_df.ne(value).groupby(data_df.index).cummax()

    return data_df.where(nan_filter)


def get_first_valid_index(data_series):
    return data_series.index.get_loc(data_series.first_valid_index())


def get_last_valid_index(data_series):
    return data_series.index.get_loc(data_series.last_valid_index())

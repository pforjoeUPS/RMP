# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 23:37:21 2024

@author: Maddie Choi, Powis Forjoe
"""
import pandas as pd

from ..datamanager import data_manager_new as dm

QUANTILE_STATS_LIST = ['Quartile', 'Quintile', 'Decile']

# TODO: rethink this module, might have to start from return_series

def get_quantile_df(returns_df, strat, quantile='Quintile'):
    """
    Computes Quantile. 
    
    Parameters
    ----------
    returns_df : data frame
        returns data for given frequency
    strat: string
    quantile : string
        Quartile, Quintile or Decile

    Returns
    -------
    quantiles : TYPE
        DESCRIPTION.

    """
    data = returns_df.copy()
    # freq_data = dm.get_freq_data(data)

    bucket_data = get_bucket_data(quantile)

    data['percentile'] = data[strat].rank(pct=True).mul(bucket_data['size'])
    data[quantile] = data['percentile'].apply(bucket_data['function'])
    quantiles = data.groupby(quantile).mean()
    quantiles = quantiles.sort_values(by=[strat], ascending=True)
    quantiles.drop(['percentile'], axis=1, inplace=True)
    quantiles.index.names = [f'{quantile} Rankings']
    return quantiles


def get_quantile_dict(returns_df, quantile='Quintile'):
    """
    Returns a dictionary dataframe containing average returns of each strategy grouped
    into quintiles based on the equity returns ranking.
    
    Parameters
    ----------
    returns_df : dataframe
    quantile: basestring

    Returns
    -------
    quintile: dataframe
        quinitle analysis data

    """

    quantile_dict = {}

    for strat in returns_df:
        quantile_dict[strat] = get_quantile_df(returns_df, strat, quantile=quantile)

    return quantile_dict


def get_mkt_quantile_dict(returns_df, mkt_df, quantile='Quintile'):
    mkt_quantile_dict = {}
    for mkt in mkt_df:
        data = dm.merge_dfs(mkt_df[[mkt]], returns_df)
        mkt_quantile_dict[mkt] = get_quantile_df(data, mkt, quantile)
    return mkt_quantile_dict


def get_quantile_data(returns_df):
    ret_quantile_data = {}
    for quantile in QUANTILE_STATS_LIST:
        ret_quantile_data[quantile] = get_quantile_dict(returns_df, quantile)
    return ret_quantile_data


def get_mkt_quantile_data(returns_df, mkt_df):
    mkt_quantile_data = {}
    for quantile in QUANTILE_STATS_LIST:
        mkt_quantile_data[quantile] = get_mkt_quantile_dict(returns_df, mkt_df, quantile)
    return mkt_quantile_data


def get_all_quantile_data(returns_df, mkt_df=pd.DataFrame()):
    ret_quantile_data = get_quantile_data(returns_df)
    if mkt_df.empty:
        return {'returns_data': ret_quantile_data}
    else:
        mkt_quantile_data = get_mkt_quantile_data(returns_df, mkt_df)
        return {'returns_data': ret_quantile_data, 'mkt_data': mkt_quantile_data}


def get_bucket_data(quantile='Quintile'):
    bucket_dict = {'Quartile': {'size': 4, 'function': quartile_bucket},
                   'Quintile': {'size': 5, 'function': quintile_bucket},
                   'Decile': {'size': 10, 'function': decile_bucket}
                   }

    return bucket_dict[quantile]


def quartile_bucket(x):
    if x < 1.0:
        return 'Bottom Quartile'

    if x < 2.0:
        return '2nd Quartile'

    if x < 3.0:
        return '3rd Quartile'

    return 'Top Quartile'


def quintile_bucket(x):
    """
    Assigns a quintile label based on the input value x.
    """
    if x < 1.0:
        return 'Bottom Quintile'
    elif x < 2.0:
        return '2nd Quintile'
    elif x < 3.0:
        return '3rd Quintile'
    elif x < 4.0:
        return '4th Quintile'
    else:
        return 'Top Quintile'


def decile_bucket(x):
    if x < 1.0:
        return 'Bottom Decile'
    elif x < 2.0:
        return '2nd Decile'
    elif x < 3.0:
        return '3rd Decile'
    elif x < 4.0:
        return '4th Decile'
    elif x < 5.0:
        return '5th Decile'
    elif x < 6.0:
        return '6th Decile'
    elif x < 7.0:
        return '7th Decile'
    elif x < 8.0:
        return '8th Decile'
    elif x < 9.0:
        return '9th Decile'
    else:
        return 'Top Decile'

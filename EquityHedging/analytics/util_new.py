# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 00:02:00 2021

@author: Powis Forjoe and Maddie Choi
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def get_pos_neg_df(return_series, pos=True, target=0):
    """
    Return dataframe with positive/negative returns of col_name as a condition
    
    Parameters
    ----------
    return_series : series
        returns series.
    pos : boolean, optional
        get positive returns. The default is True.

    Returns
    -------
    dataframe

    """

    # make copy of series
    data_series = return_series.copy()

    # filter index for positive/negative returns
    return_index = data_series.index[data_series >= target] if pos else data_series.index[data_series < target]

    # create new series
    return data_series.loc[return_index]


# TODO: Move to rolling_stats
def get_rolling_cum(returns_df, interval):
    """
    Get rolling cum returns dataframe

    Parameters
    ----------
    returns_df : dataframe
        returns dataframe.
    interval : int

    Returns
    -------
    rolling_cum_ret : dataframe

    """

    rolling_cum_ret = returns_df.copy()
    for col in returns_df.columns:
        rolling_cum_ret[col] = (1 + rolling_cum_ret[col]).rolling(window=interval).apply(np.prod, raw=True) - 1
    rolling_cum_ret.dropna(inplace=True)
    return rolling_cum_ret


def get_normalized_data(data_df):
    """

    Parameters
    ----------
    data_df : data frame
        data frame of returns data for a given frequency

    Returns
    -------
    df_normal : data frame
        normalizes data to be within the range 0 to 1

    """
    scaler = MinMaxScaler()

    # creates data frame with normalized data
    normal_df = pd.DataFrame(scaler.fit_transform(data_df), columns=data_df.columns, index=data_df.index)

    return normal_df


def convert_dict_to_df(data_dict, index=[]):
    """

    Parameters
    ----------
    data_dict : dictionary
        Input a dictionary that will be turned into a data frame.
    index : list
        Index (aka row) names. The default is [].

    ** Note the data frame column names will be the keys in the dictionary **

    Returns
    -------
    Data Frame

    """

    data_df = pd.DataFrame(data_dict, index=index)

    return data_df


# TODO: change mult cols
def reverse_signs_in_col(data_df, column):
    """


    Parameters
    ----------
    data_df : data frame
    column: string
    Returns
    -------
    reverse_df : data frame
        same data frame as in the input, but with downside reliability terms as positive.

    """
    reverse_df = data_df.copy()
    if column in data_df:
        for x in reverse_df.index:
            reverse_df[column][x] = -(reverse_df[column][x])

    return reverse_df


def change_to_neg(data_df):
    """


    Parameters
    ----------
    data_df : data frame

    Returns
    -------
    reverse_df : data frame
        same data frame as in the input, but with downside reliability terms as positive.

    """
    reverse_df = data_df.copy()
    for column in data_df:
        for x in reverse_df.index:
            if reverse_df[column][x] > 0:
                reverse_df[column][x] = -(reverse_df[column][x])

    return reverse_df


def append_dict_dfs(dictionary):
    """


    Parameters
    ----------
    dictionary : dictionary

    Returns
    -------
    Dataframe that appends all dataframes within dictionary into one.

    """
    df = pd.DataFrame()
    for i in list(dictionary.keys()):
        temp_df = dictionary[i]
        df = df.append(temp_df)

    return df

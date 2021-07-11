# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe
"""

import numpy as np

def get_rolling_cum(df_returns, interval):
    """
    Get rolling cum returns dataframe

    Parameters
    ----------
    df_returns : dataframe
        returns dataframe.
    interval : int

    Returns
    -------
    rolling_cum_ret : dataframe

    """
    
    rolling_cum_ret = df_returns.copy()
    for col in df_returns.columns:
        rolling_cum_ret[col] = (1+rolling_cum_ret[col]).rolling(window=interval).apply(np.prod, raw=True)-1
    rolling_cum_ret.dropna(inplace=True)
    return rolling_cum_ret
   
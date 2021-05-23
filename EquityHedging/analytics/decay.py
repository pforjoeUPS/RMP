# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 21:54:16 2021

@author: Powis Forjoe
"""

import numpy as np
from ..datamanager import data_manager as dm
from .returns_stats import get_ann_vol

#hedge_metrics-decay
def get_peak_return(df_prices, col, look_back_days, day):
    """
    Returns peak return for a specific day during look back period

    Parameters:
    df_prices -- price index dataframe
    col -- string (column name in dataframe)
    look_back_days -- double 
    day --

    Returns:
    peak_return -- double
    """

    # get index level for specific day
    day_index_level = df_prices[col][day]

    # get minimum index level within the look back days period
    min_index_level = df_prices.loc[df_prices.index[day-look_back_days]:df_prices.index[day-1], col].min()

    #compute peak return
    return day_index_level/min_index_level

#hedge_metrics-decay
def get_retrace_index_info(peak_return, day_index_level, index_series, retrace_pct):
    """
    Returns return and date when index retraces by retrace pct
    
    Parameters:
    peak_return -- double
    day_index_level --
    index_series --
    retrace_pct -- double
    
    Returns:
    retrace_info -- dict(index(double), date(date))
    """
    
    retrace_index = ((peak_return - 1)*(1-retrace_pct) + 1)*(day_index_level/peak_return)
    retrace_date = index_series.index[index_series < retrace_index][0]
    return {'index': retrace_index, 'date': retrace_date}

#hedge_metrics-decay
def get_retrace_index(peak_return, day_index_level, retrace_pct):
    """
    Returns index level for when index retraces by retrace pct
    
    Parameters:
    peak_return -- double
    day_index_level --
    retrace_pct -- double
    
    Returns:
    retrace_figure -- double
    """
    
    return ((peak_return - 1)*(1-retrace_pct) + 1)*(day_index_level/peak_return)

#hedge_metrics-decay
def get_retrace_date(peak_return, day_index_level, index_series, retrace_pct):
    """
    Returns date when index retraces by retrace pct
    
    Parameters:
    peak_return -- return dataframe
    day_index_level -- 
    index_series -- series
    retrace_pct -- double
    
    Returns:
    retrace_figure -- double
    """
    
    retrace_index = ((peak_return - 1)*(1-retrace_pct) + 1)*(day_index_level/peak_return)
    retrace_date = index_series.index[index_series < retrace_index][0]
    return retrace_date

#hedge_metrics-decay
def get_max_index_level_from_range(df_prices, col, look_back_days, look_fwd_days, day):
    """
    Return the max index level from a range in a dataframe

    Parameters:
    df_prices -- price dataframe
    col -- string (column name in dataframe)
    look_back_days -- int
    look_back_days -- int
    day --
    
    Returns:
    index_level -- double
    """
    start = day - look_back_days
    end = day + look_fwd_days
    
    if start < 0:
        start = day
        
    if end > len(df_prices):
        end = len(df_prices)
    index_list = []
    for i in range(start, end):
        index_list.append(df_prices[col][i])
    
    return np.array(index_list).max()

#hedge_metrics-decay
def get_decay_days(df_returns, col, freq="1M", retrace_pct=.50, sd =1.28, look_back_days=60, look_fwd_days=60):
    """
    Returns avg number of days it takes for strategy to retrace by retrace_level
    
    Parameters:
    df_returns -- returns dataframe
    col -- string (column name in dataframe)
    freq -- string ('1M', '1W', '1D')
    retrace_pct -- double
    sd -- double
    look_back_days -- int
    look_back_days -- int
    
    Returns:
    decay_value -- double
    """
    
    #compute threshold based off sd figure
    threshold = sd*get_ann_vol(df_returns[col], freq)
    
    #convert return dataframe to index dataframe
    df_prices = dm.get_prices_df(df_returns)
    
    #convert look back and look fwd days to frequency type
    if freq != "1D":
        look_back_days = dm.convert_to_freq2(look_back_days,"1D",freq)
        look_fwd_days = dm.convert_to_freq2(look_fwd_days,"1D",freq)
    
    decay_freq = 0
    decay_sum = 0
    
    #one year equivalent in fro freq period
    one_year = dm.switch_freq_int(freq)
    
    day = look_back_days

    while day < len(df_prices):
        jump = 1
        # get index level for specific day
        # day_index_level = df_prices[col][day]
        
        #get peak_return over look_back_days
        peak_return = get_peak_return(df_prices, col, look_back_days, day)
        
        #check if peak_return is greater than threshold return
        if  peak_return > (1 + threshold):
            # try:
            #     max_index_level = df_prices.loc[df_prices.index[day-look_back_days]:df_prices.index[day + look_fwd_days - 1],col].max()
            #     print('Day {}, level: {}'.format(day, max_index_level))
            # except IndexError:
            #  	#compute max index level from look_back & look_fwd range
            #     max_index_level = get_max_index_level_from_range(df_prices, col, look_back_days, look_fwd_days, day)
            #     print('\tError: Day {}, level: {}'.format(day, max_index_level))
            #     pass
            
            #compute max index level from look_back & look_fwd range
            max_index_level = get_max_index_level_from_range(df_prices, col, look_back_days, look_fwd_days, day)
            max_day = np.where(df_prices[col]==max_index_level)[0][0]
            if max_day - day > one_year:
                max_index_level = df_prices.loc[df_prices.index[day-look_back_days]:df_prices.index[day + look_fwd_days - 1],col].max()
                max_day = np.where(df_prices[col]==max_index_level)[0][0]
            
            # print('Day {}, level: {}'.format(day, max_index_level))
            if max_day >= day:    
                #make default retrace date the last date
                retrace_date = df_prices.index[len(df_prices)-1]
                temp_day = max_day
                try:
                    #find retrace date
                    temp_series = df_prices[col][max_day:len(df_prices)]
                    max_return = get_peak_return(df_prices, col, look_back_days, max_day)
                    # retrace_info = get_retrace_index_info(peak_return, day_index_level, temp_series,retrace_pct)
                    retrace_info = get_retrace_index_info(max_return, max_index_level, temp_series,retrace_pct)
                    retrace_date = retrace_info['date']
                    # print('retrace_date: {}'.format(retrace_date))
                except IndexError:
                	#if error make jump go to last date
                    jump = len(df_prices) - 1
                	# print('\tError: retrace_date: {}'.format(retrace_date))
                #find decay day number and add to decay_sum and increment decay_freq
                max_index_date = df_prices.index[max_day]
                decay_days = (retrace_date - max_index_date).days
                #check if decay days > 365
                if decay_days > 365:
                    decay_days=365
                    jump = one_year
                    temp_day = day
                
                decay_freq +=1
                decay_sum += decay_days
                day = temp_day
        day += jump
    # print('{}: {}'.format(col, round(decay_sum/decay_freq)))
    if (decay_sum == 0 and decay_freq ==0):
        return 0
    else:
        return round(decay_sum/decay_freq)

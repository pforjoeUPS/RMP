# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 21:54:16 2021

@author: Powis Forjoe
"""

import numpy as np
from ..datamanager import data_manager as dm
from .returns_stats import get_ann_vol

def get_index_list(price_series, start, end):
    """
    

    Parameters
    ----------
    price_series : series
        DESCRIPTION.
    start : int
        DESCRIPTION.
    end : int
        DESCRIPTION.

    Returns
    -------
    list
        DESCRIPTION.

    """
    index_list = []
    for i in range(start, end):
        index_list.append(price_series[i])
    
    return np.array(index_list)

def get_max_index(price_series, start, end, look_fwd_days):
    """
    

    Parameters
    ----------
    price_series : series
        DESCRIPTION.
    start : int
        DESCRIPTION.
    end : int
        DESCRIPTION.
    look_fwd_days : int
        DESCRIPTION.

    Returns
    -------
    max_index : int
        DESCRIPTION.

    """
    max_index=start
    peak = price_series[max_index]
                
    for i in range(start, end):
        temp_max = price_series[i]
        if temp_max > peak:
            peak = temp_max
            try:
                if peak == get_index_list(price_series, i, i+look_fwd_days).max():
                    max_index=i
                    break
            except IndexError:
                    max_index=end-1    
                    break
    return max_index

def get_min_index(price_series, start, end, look_fwd_days):
    """
    

    Parameters
    ----------
    price_series : series
        DESCRIPTION.
    start : int
        DESCRIPTION.
    end : int
        DESCRIPTION.
    look_fwd_days : int
        DESCRIPTION.

    Returns
    -------
    min_index : int
        DESCRIPTION.

    """
    min_index = start
    
    trough = price_series[min_index]
    
    for i in range(start, end):
        temp_min = price_series[i]
        if temp_min < trough:
            trough = temp_min
            try:
                if trough == get_index_list(price_series, i, i+look_fwd_days).min():
                    min_index = i        
                    break
            except IndexError:
                    min_index=end-1
                    break
    return min_index

def get_dd_list(price_series, freq='1W', look_fwd_days=60, look_fwd_days_2=120):
    """
    get start and end dates for draw downs in price series

    Parameters
    ----------
    price_series : series
        Index data.
    freq : string, optional
        Frequency. The default is '1W'.
    look_fwd_days : int, optional
        DESCRIPTION. The default is 60.
    look_fwd_days_2 : int, optional
        DESCRIPTION. The default is 120.

    Returns
    -------
    dd_list : list
        list of dictionaries with start and end index numbers.

    """
    
    #convert look fwd days to frequency type
    if freq != '1D':
        look_fwd_days = dm.convert_to_freq2(look_fwd_days,"1D",freq)
        look_fwd_days_2 = dm.convert_to_freq2(look_fwd_days_2,"1D",freq)
    
    #set start and end points
    start = look_fwd_days
    end = len(price_series)

    max_index = start
    dd_list=[]
    
    #get start and end dates for each drawdown
    while start < end:
        #find max_index which represents start of drawdown
        max_index = get_max_index(price_series, start, end, look_fwd_days_2)
                    
        #find min_index which represents end of drawdown
        min_index = get_min_index(price_series, max_index, end, look_fwd_days_2)
        
        #create drawdown dict and add to dd_list
        if min_index < end-1:
            temp_dd = {'start':max_index, 'end':min_index}
            dd_list.append(temp_dd)
        
        #increase start to get next drawdown dict                
        start = min_index + look_fwd_days 
    return dd_list

def get_du_list(df_returns, col, freq='1W', look_fwd_days=60, look_fwd_days_2=120):
    """
    get start and end dates for draw ups in price series

    Parameters
    ----------
    price_series : series
        Index data.
    freq : string, optional
        Frequency. The default is '1W'.
    look_fwd_days : int, optional
        DESCRIPTION. The default is 60.
    look_fwd_days_2 : int, optional
        DESCRIPTION. The default is 120.

    Returns
    -------
    dd_list : list
        list of dictionaries with start and end index numbers.

    """
    
    #convert look fwd days to frequency type
    if freq != '1D':
        look_fwd_days = dm.convert_to_freq2(look_fwd_days,"1D",freq)
        look_fwd_days_2 = dm.convert_to_freq2(look_fwd_days_2,"1D",freq)
    
    threshold = 1.28*get_ann_vol(df_returns[col], freq)
    
    df_prices = dm.get_prices_df(df_returns)
    price_series = df_prices[col]
    #set start and end points
    start = look_fwd_days
    end = len(price_series)

    min_index = start
    du_list=[]
    
    #get start and end dates for each drawdown
    while start < end:
        #find max_index which represents start of drawdown
        min_index = get_min_index(price_series, start, end, look_fwd_days_2)
                    
        #find min_index which represents end of drawdown
        max_index = get_max_index(price_series, min_index, end, look_fwd_days_2)
        
        #create drawdown dict and add to dd_list
        if max_index < end-1:
            if (price_series[max_index]/price_series[min_index]-1) > threshold:
                temp_du = {'start':min_index, 'end':max_index}
                du_list.append(temp_du)
        
        #increase start to get next drawdown dict                
        start = max_index + look_fwd_days 
    return du_list

def check_dd_du_list(dd_du_list,price_series,dd_du_range):
    if dd_du_list: 
        dd_du = dd_du_list[len(dd_du_list)-1]
        start = dd_du['end']
        end = dd_du_range + start
        if end >= len(price_series):
            del dd_du_list[-1]
    return dd_du_list

def compute_retrace(peak, trough, min_index_list, days):
    """
    compute retrace pct for a given period

    Parameters
    ----------
    peak : double
        DESCRIPTION.
    trough : double
        DESCRIPTION.
    min_index_list : list
        DESCRIPTION.
    days : int
        DESCRIPTION.

    Returns
    -------
    double
        DESCRIPTION.

    """
    return (min_index_list[days]/peak-1)/(trough/peak-1)

def get_recovery_retrace_list(dd,dd_range,price_series, days):
    #set start and end points
    start = dd['end']
    end = dd_range + start
    
    max_index_list=[]
    max_index = price_series[start]
    for i in range(start, end):
        temp_max = price_series[i]
        if temp_max > max_index:
            max_index = temp_max
        max_index_list.append(max_index)
    
    min_index_list = []
    trough = price_series[dd['end']]
    peak = price_series[dd['start']]
    
    for index in max_index_list:
        temp_min = max(trough,index)
        if temp_min < peak:
            min_index_list.append(temp_min)
        else:
            min_index_list.append(peak)
    #compute retrace pct for each day in days list
    retrace_list = []
    for day in days:
        day = dm.convert_to_freq2(day, '1D', freq)
        retrace_list.append(compute_retrace(peak, trough, min_index_list, day))
    return retrace_list

def get_decay_retrace_list(du,du_range,price_series, days):
    #set start and end points
    start = du['end']
    end = du_range + start
    
    min_index_list=[]
    min_index = price_series[start]
    for i in range(start, end):
        temp_min = price_series[i]
        if temp_min < min_index:
            min_index = temp_min
        min_index_list.append(min_index)
    # index_list = get_index_list(price_series, start, end)
    peak = price_series[du['end']]
    retrace_list=[]
    for day in days:
        day = dm.convert_to_freq2(day, '1D', freq)
        retrace_list.append((1-(min_index_list[day]/peak)))
    return retrace_list

def get_decay_retrace_list2(du,du_range,price_series, days):
    #set start and end points
    start = du['end']
    end = du_range + start
    
    trough = price_series[start]
    for i in range(start, end):
        temp_min = price_series[i]
        if temp_min < trough:
            trough = temp_min
    
    index_list = get_index_list(price_series, start, end)
    peak = price_series[du['end']]
    retrace_list=[]
    for day in days:
        day = dm.convert_to_freq2(day, '1D', freq)
        retrace_list.append((index_list[day]/trough-1)/(peak/trough-1))
    return retrace_list

    
def compute_recovery_pct(price_series, freq='1W', look_fwd_days=60, look_fwd_days_2=120, dd_range = 260,days=[20,60,120,180,240]):
    """
    Compute recovery percent given a price series

    Parameters
    ----------
    price_series : series
        DESCRIPTION.
    freq : string, optional
        Frequency. The default is '1W'.
    look_fwd_days : TYPE, optional
        DESCRIPTION. The default is 60.
    look_fwd_days_2 : TYPE, optional
        DESCRIPTION. The default is 60.

    Returns
    -------
    double
        DESCRIPTION.

    """
    #convert dd_range to frequency type
    if freq != '1D':
        dd_range = dm.convert_to_freq2(dd_range,"1D",freq)
    
    #get drawdown list
    dd_list = get_dd_list(price_series,freq,look_fwd_days, look_fwd_days_2)
    dd_list = check_dd_du_list(dd_list, price_series, dd_range)
    
    
    if not dd_list:
        return 1
    else:
        recovery_list=[]
        for dd in dd_list:
            #get retrace list per dd
            retrace_list = get_recovery_retrace_list(dd, dd_range, price_series,days)
            
            #add average retrace to recovery list
            recovery_list.append(np.mean(retrace_list))
        #compute mean of recovery list
        return 1-np.mean(recovery_list)

def compute_decay_pct(df_returns,col, freq='1W', look_fwd_days=60, look_fwd_days_2=120, du_range = 260,days=[20,40,60,80,100,120]):
    """
    Compute decay percent given a price series

    Parameters
    ----------
    price_series : series
        DESCRIPTION.
    freq : string, optional
        Frequency. The default is '1W'.
    look_fwd_days : TYPE, optional
        DESCRIPTION. The default is 60.
    look_fwd_days_2 : TYPE, optional
        DESCRIPTION. The default is 60.

    Returns
    -------
    double
        DESCRIPTION.

    """
    #convert du_range to frequency type
    if freq != '1D':
        du_range = dm.convert_to_freq2(du_range,"1D",freq)
    
    #get drawup list
    du_list = get_du_list(df_returns, col,freq,look_fwd_days, look_fwd_days_2)
    
    df_prices = dm.get_prices_df(df_returns)
    du_list = check_dd_du_list(du_list, df_prices[col], du_range)
    
    if not dd_list:
        return 0
    else:
        
        decay_list=[]
        for du in du_list:
            #get retrace list per du
            retrace_list = get_decay_retrace_list2(du, du_range, df_prices[col],days)
            
            #add average retrace to decay list
            decay_list.append(np.mean(retrace_list))
        #compute mean of decay list
        return np.mean(decay_list)
    
sptr_dict = dm.get_equity_hedge_returns(only_equity=True)
sptr_w = dm.get_prices_df(sptr_dict['Weekly'])
price_series = sptr_w['SPTR']
look_fwd_days = 60
freq='1W'
look_fwd_days_2 = 120
dd_range = 260

look_fwd_days = dm.convert_to_freq2(look_fwd_days,"1D",freq)
look_fwd_days_2 = dm.convert_to_freq2(look_fwd_days_2,"1D",freq)

dd_list=[]
start = look_fwd_days
end = len(price_series)



max_index = start
# i=start

while start < end:
    max_index = get_max_index(price_series, start, end, look_fwd_days_2)
                
    start = max_index
    
    min_index = get_min_index(price_series, start, end, look_fwd_days_2)
    
    if min_index < end:
        temp_dd = {'start':max_index, 'end':min_index}
        dd_list.append(temp_dd)
                
    start = min_index + look_fwd_days 





while start < end:
    peak = price_series[start]
                
    for i in range(start, end):
        temp_max = price_series[i]
        if temp_max > peak:
            peak = temp_max
            # max_index=i
            try:
                if peak == get_index_list(price_series, i, i+look_fwd_days_2).max():
                    max_index=i
                    break
            except IndexError:
                    max_index=i    
                    break
        
    min_index = max_index
    
    trough = price_series[min_index]
    
    for i in range(max_index, end):
        temp_min = price_series[i]
        if temp_min < trough:
            trough = temp_min
            try:
                if trough == get_index_list(price_series, i, i+look_fwd_days_2).min():
                    min_index = i        
                    temp_dd = {'start':max_index, 'end':min_index}
                    dd_list.append(temp_dd)
                    break
            except IndexError:
                    min_index=end
                    break
                
    # print(price_series.index[max_index])
    # print(price_series.index[min_index])
    # temp_dd = {'start':max_index, 'end':min_index}
    # dd_list.append(temp_dd)
    
    start = min_index + look_fwd_days 

dd_range = 260

dd_range = dm.convert_to_freq2(dd_range,"1D",freq)


start = dd_list[5]['end']
end = dd_range + dd_list[5]['end']

max_index_list=[]
max_index = price_series[start]
for i in range(start, end):
    temp_max = price_series[i]
    if temp_max > max_index:
        max_index = temp_max
    max_index_list.append(max_index)

min_index_list = []
trough=price_series[dd_list[5]['end']]
peak=price_series[dd_list[5]['start']]

for index in max_index_list:
    temp_min = max(trough,index)
    if temp_min < peak:
        min_index_list.append(temp_min)
    else:
        min_index_list.append(peak)

days = [20,60,120,240]

retrace_list = []
for day in days:
    day = dm.convert_to_freq2(day, '1D', freq)
    retrace_list.append(compute_retrace(peak, trough, min_index_list, day))
np.mean(retrace_list)



    
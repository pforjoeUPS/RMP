# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 21:54:16 2021

@author: Powis Forjoe
"""

import numpy as np

from .returns_stats_new import get_ann_vol
from ..datamanager import data_manager_new as dm
from ..datamanager import data_xformer_new as dxf


def get_peak_return(price_series, look_back_days, day):
    """
    Returns peak return for a specific day during look back period

    Parameters
    ----------
    price_series : series
    look_back_days : double
    day : TYPE
        DESCRIPTION.

    Returns
    -------
    double
        peak return.

    """

    # get index level for specific day
    day_index_level = price_series[day]

    # get minimum index level within the look back days period
    min_index_level = price_series.loc[price_series.index[day - look_back_days]:price_series.index[day - 1]].min()

    # compute peak return
    return day_index_level / min_index_level


def get_retrace_index_info(peak_return, day_index_level, index_series, retrace_pct):
    """
    Returns return and date when index retraces by retrace pct

    Parameters
    ----------
    peak_return : double
    day_index_level : TYPE
        DESCRIPTION.
    index_series : TYPE
        DESCRIPTION.
    retrace_pct : double

    Returns
    -------
    dictionary
        retrace_info (index(double), date(date)).

    """

    # compute retrace return
    retrace_index = ((peak_return - 1) * (1 - retrace_pct) + 1) * (day_index_level / peak_return)

    # compute retrace date
    retrace_date = index_series.index[index_series < retrace_index][0]

    # return a dictionary
    return {'index': retrace_index, 'date': retrace_date}


# def get_retrace_index(peak_return, day_index_level, retrace_pct):
#     """
#     Returns index level for when index retraces by retrace pct    

#     Parameters
#     ----------
#     peak_return : double
#     day_index_level : TYPE
#     retrace_pct : double

#     Returns
#     -------
#     double
#         retrace figure.

#     """

#     return ((peak_return - 1)*(1-retrace_pct) + 1)*(day_index_level/peak_return)

# def get_retrace_date(peak_return, day_index_level, index_series, retrace_pct):
#     """
#     Returns date when index retraces by retrace pct

#     Parameters
#     ----------
#     peak_return : dataframe
#     day_index_level : TYPE
#         DESCRIPTION.
#     index_series : series
#     retrace_pct : double

#     Returns
#     -------
#     retrace_date : date

#     """

#     retrace_index = ((peak_return - 1)*(1-retrace_pct) + 1)*(day_index_level/peak_return)
#     retrace_date = index_series.index[index_series < retrace_index][0]
#     return retrace_date

def get_max_index_level_from_range(price_series, look_back_days, look_fwd_days, day):
    """
    Return the max index level from a range in a dataframe

    Parameters
    ----------
    price_series : series
    look_back_days : int
        DESCRIPTION.
    look_fwd_days : int
        DESCRIPTION.
    day : TYPE
        DESCRIPTION.

    Returns
    -------
    double
        Index level.

    """

    start = day - look_back_days
    end = day + look_fwd_days

    if start < 0:
        start = day

    if end > len(price_series):
        end = len(price_series)
    index_list = []
    for i in range(start, end):
        index_list.append(price_series[i])

    return np.array(index_list).max()


def get_decay_days(return_series, freq="M", retrace_pct=.50, sd=1.28, look_back_days=60, look_fwd_days=60):
    """
    Returns avg number of days it takes for strategy to retrace by retrace_level
    
    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        The default is "M".
    retrace_pct : double, optional
        The default is .50.
    sd : double, optional
        The default is 1.28.
    look_back_days : int, optional
        The default is 60.
    look_fwd_days : int, optional
        The default is 60.

    Returns
    -------
    double
        decay value.

    """

    # compute threshold based off sd figure
    threshold = sd * get_ann_vol(return_series, freq)

    # convert return dataframe to index dataframe
    price_series = dxf.get_price_data(return_series, 1)

    # convert look back and look fwd days to frequency type
    if freq != "D":
        look_back_days = dm.convert_to_freq2(look_back_days, "D", freq)
        look_fwd_days = dm.convert_to_freq2(look_fwd_days, "D", freq)

    decay_freq = 0
    decay_sum = 0

    # one year equivalent in fro freq period
    one_year = dm.switch_freq_int(freq)

    day = look_back_days

    while day < len(price_series):
        jump = 1

        # get peak_return over look_back_days
        peak_return = get_peak_return(price_series, look_back_days, day)

        # check if peak_return is greater than threshold return
        if peak_return > (1 + threshold):

            # compute max index level from look_back & look_fwd range
            max_index_level = get_max_index_level_from_range(price_series, look_back_days, look_fwd_days, day)
            max_day = np.where(price_series == max_index_level)[0][0]
            if max_day - day > one_year:
                max_index_level = price_series.loc[price_series.index[day - look_back_days]:price_series.index[
                    day + look_fwd_days - 1]].max()
                max_day = np.where(price_series == max_index_level)[0][0]

            if max_day >= day:
                # make default retrace date the last date
                retrace_date = price_series.index[len(price_series) - 1]
                temp_day = max_day
                try:
                    # find retrace date
                    temp_series = price_series[max_day:len(price_series)]
                    max_return = get_peak_return(price_series, look_back_days, max_day)
                    retrace_info = get_retrace_index_info(max_return, max_index_level, temp_series, retrace_pct)
                    retrace_date = retrace_info['date']

                except IndexError:
                    # if error make jump go to last date
                    jump = len(price_series) - 1

                # find decay day number and add to decay_sum and increment decay_freq
                max_index_date = price_series.index[max_day]
                decay_days = (retrace_date - max_index_date).days

                # check if decay days > 365
                if decay_days > 365:
                    decay_days = 365
                    jump = one_year
                    temp_day = day

                decay_freq += 1
                decay_sum += decay_days
                day = temp_day
        day += jump
    if decay_sum == 0 and decay_freq == 0:
        return 0
    else:
        return round(decay_sum / decay_freq)

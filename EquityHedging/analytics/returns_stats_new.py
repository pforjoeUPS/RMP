# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""

import numpy as np
from scipy.interpolate import interp1d

from . import util_new
from ..datamanager import data_manager_new as dm


def get_comp_returns(return_series):
    return return_series.add(1).prod() - 1


def get_ann_return(return_series, freq='M'):
    """
    Return annualized return for a return series.

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is 'M'.

    Returns
    -------
    double
        Annualized return.

    """
    # compute the annualized return
    d = len(return_series)
    return return_series.add(1).prod() ** (dm.switch_freq_int(freq) / d) - 1


def get_ann_vol(return_series, freq='M'):
    """
    Return annualized volatility for a return series.

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is 'M'.

    Returns
    -------
    double
        Annualized volatility.

    """
    # compute the annualized volatility
    return np.std(return_series, ddof=1) * np.sqrt(dm.switch_freq_int(freq))


def get_beta(return_series, mkt_series):
    return return_series.cov(mkt_series) / mkt_series.var()


def get_alpha(return_series, mkt_series, freq='M', rfr=0.0):
    beta = get_beta(return_series, mkt_series)
    mkt_ret = get_ann_return(mkt_series, freq)
    port_ret = get_ann_return(return_series, freq)
    return port_ret - (rfr + beta * (mkt_ret - rfr))


def get_up_down_capture_ratio(return_series, mkt_series, upside=True):
    mkt_cap = util.get_pos_neg_df(mkt_series, pos=upside)
    ret_cap = dm.merge_data_frames(mkt_cap, return_series, True)[return_series.name]
    return get_comp_returns(ret_cap) / get_comp_returns(mkt_cap)


def get_max_dd(return_series):
    """
    Return maximum draw down (Max DD) for a price series.

    Parameters
    ----------
    price_series : series
        price series.

    Returns
    -------
    double
        Max DD.

    """

    # we are going to use the length of the series as the window
    price_series = dm.get_price_series(return_series)
    window = len(price_series)

    # calculate the max drawdown in the past window periods for each period in the series.
    roll_max = price_series.rolling(window, min_periods=1).max()
    drawdown = price_series / roll_max - 1.0

    return drawdown.min()


def get_max_dd_freq(return_series, freq='M', max_3m_dd=False):
    """
    Return dictionary (value and date) of either Max 1M DD or Max 3M DD

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is 'M'.
    max_3m_dd : boolean, optional
        Compute Max 3M DD. The default is False.

    Returns
    -------
    dictionary
    """

    # convert returns series into price
    price_series = dm.get_price_series(return_series)

    # get int frequency
    int_freq = dm.switch_freq_int(freq)

    # compute 3M or 1M returns
    if max_3m_dd:
        periods = round((3 / 12) * int_freq)
        dd_return_series = price_series.pct_change(periods)
    else:
        periods = round((1 / 12) * int_freq)
        dd_return_series = price_series.pct_change(periods)
    dd_return_series.dropna(inplace=True)

    # compute Max 1M/3M DD
    max_dd_freq = dd_return_series.min()

    # get Max 1M/3M DD date
    index_list = dd_return_series.index[dd_return_series == max_dd_freq].tolist()

    # return dictionary
    return {'max_dd': max_dd_freq, 'index': index_list[0].strftime('%m/%d/%Y')}


def get_avg_pos_neg(return_series, pos=True):
    """
    Average positve returns/ Average negative returns
    of a strategy

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
    
    """

    # filter positive and negative returns
    pos_neg_series = util.get_pos_neg_df(return_series, pos)

    return pos_neg_series.mean()


def get_avg_pos_neg_ratio(return_series):
    """
    Return Average positve returns/ Average negative returns
    of a strategy

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
    
    """
    # compute means
    avg_pos = get_avg_pos_neg(return_series)
    avg_neg = get_avg_pos_neg(return_series, False)

    try:
        return avg_pos / abs(avg_neg)
    except ZeroDivisionError:
        return float('inf')


def get_pct_pos_neg_periods(return_series, pos=True):
    pos_neg_series = util.get_pos_neg_df(return_series, pos)
    return len(pos_neg_series) / len(return_series)


def get_updown_dev(return_series, freq='M', target=0, up=False):
    """
    Compute annualized upside/downside dev

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is 'M'.
    target : int, optional
        The default is 0.

    Returns
    -------
    double
        upside / downside std deviation.

    """
    # create a upside/downside return column with the positive/negative returns only
    up_down_series = return_series >= target if up else return_series < target

    up_down_side_returns = return_series.loc[up_down_series]

    # return annualized std dev of downside
    return get_ann_vol(up_down_side_returns, freq)


def get_up_dev(return_series, freq='M', target=0):
    """
    Compute annualized upside/downside dev

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is 'M'.
    target : int, optional
        The default is 0.

    Returns
    -------
    double
        upside / downside std deviation.

    """
    # create a upside/downside return column with the positive/negative returns only
    up_series = return_series >= target

    up_side_returns = return_series.loc[up_series]

    # return annualized std dev of downside
    return get_ann_vol(up_side_returns, freq)


def get_down_dev(return_series, freq='M', target=0):
    """
    Compute annualized upside/downside dev

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is 'M'.
    target : int, optional
        The default is 0.

    Returns
    -------
    double
        upside / downside std deviation.

    """
    # create a upside/downside return column with the positive/negative returns only
    down_series = return_series < target

    down_side_returns = return_series.loc[down_series]

    # return annualized std dev of downside
    return get_ann_vol(down_side_returns, freq)


def get_up_down_dev_ratio(return_series, freq='M', target=0):
    return get_updown_dev(return_series, freq, target, True) / get_updown_dev(return_series, freq, target)


def get_sortino_ratio(return_series, freq='M', target=0, rfr=0):
    """
    Compute Sortino ratio

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is 'M'.
    rfr : int, optional
        The default is 0.
    target : int, optional
        The default is 0.
    
    Returns
    -------
    double
        sortino ratio
    """
    # calculate annulaized return and std dev of downside
    ann_ret = get_ann_return(return_series, freq)
    down_stddev = get_updown_dev(return_series, freq, target)

    # calculate the sortino ratio
    return (ann_ret - rfr) / down_stddev


def get_sharpe_ratio(return_series, freq='M', rfr=0.0):
    """
    Compute Return/Vol ratio

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is 'M'.

    Returns
    -------
    double
        Return/vol ratio

    """

    # calculate annulaized return and vol
    ann_ret = get_ann_return(return_series, freq)
    ann_vol = get_ann_vol(return_series, freq)

    # calculate ratio
    return (ann_ret - rfr) / ann_vol


def get_ret_max_dd_ratio(return_series, freq='M'):
    """
    Compute Return/Max DD ratio

    Parameters
    ----------
    return_series : series
        returns series.
    price_series : series
        price series.
    freq : string, optional
        frequency. The default is 'M'.

    Returns
    -------
    double
        Return/Max DD ratio

    """
    # compute annual returns and Max DD
    ann_ret = get_ann_return(return_series, freq)
    max_dd = get_max_dd(return_series)

    # calculate ratio
    return ann_ret / abs(max_dd)


def get_skew(return_series):
    """
    Compute skew of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        skew.

    """
    return return_series.skew()


def get_kurtosis(return_series):
    """
    Compute kurtosis of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        kurtosis.

    """
    return return_series.kurtosis()


def get_median(return_series):
    """
    Compute median of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        skew.

    """
    return return_series.median()


def get_mean(return_series):
    """
    Compute mean of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        kurtosis.

    """
    return return_series.mean()


def get_max(return_series):
    """
    Compute skew of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        skew.

    """
    return return_series.max()


def get_min(return_series):
    """
    Compute kurtosis of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        kurtosis.

    """
    return return_series.min()


def get_ret_max_dd_freq_ratio(return_series, freq, max_3m_dd=False):
    """
    Compute Return/Max 1M/3M DD ratio

    Parameters
    ----------
    return_series : series
        returns series.
    price_series : series
        price series.
    freq : string, optional
        frequency. The default is 'M'.
    max_3m_dd : boolean, optional
        Compute Max 3M DD. The default is False.

    Returns
    -------
    double
        Return/Max 1M/3M DD ratio

    """
    # calculate annual return
    ann_ret = get_ann_return(return_series, freq)
    max_freq_dd = get_max_dd_freq(return_series, freq, max_3m_dd)['max_dd']

    # compute ratio
    return ann_ret / abs(max_freq_dd)


def get_var(return_series, p=0.05):
    count = len(return_series)
    location = p * count

    # sort returns
    ranked_returns = list(return_series.sort_values())

    rank = list(range(1, count + 1))

    # interp = scipy.interpolate.interp1d(rank, ranked_returns, fill_value='extrapolate')
    interp = interp1d(rank, ranked_returns, fill_value='extrapolate')

    return float(interp(location))


def get_cvar(return_series, p=0.05):
    var = get_var(return_series, p)

    cvar_series = return_series.loc[return_series < var]

    return cvar_series.mean()


# move to dd
def get_drawdown_series(price_series):
    """
    Calculate drawdown series (from calculation of MaxDD)

    Parameters
    ----------
    price_series : series
        price series.

    Returns
    -------
    Drawdown series

    """
    window = len(price_series)
    roll_max = price_series.rolling(window, min_periods=1).max()
    drawdown = price_series / roll_max - 1.0
    return drawdown


# move to dd
def find_dd_date(price_series):
    """
    Finds the date where Max DD occurs

    Parameters
    ----------
    price_series : series
        price series.

    Returns
    -------
    Date of MaxDD in dataframe

    """
    max_dd = get_max_dd(price_series)
    drawdown = get_drawdown_series(price_series)
    dd_date = drawdown.index[drawdown == float(max_dd)]

    return dd_date


# move to dd
def find_zero_dd_date(price_series):
    """
    Finds the date where drawdown was at zero before Max DD

    Parameters
    ----------
    price_series : series
        price series.

    Returns
    -------
    Date of where drawdown was at zero before MaxDD in dataframe

    """
    drawdown = get_drawdown_series(price_series)
    drawdown_reverse = drawdown[::-1]
    x = (find_dd_date(price_series)[0])
    strat_drawdown = drawdown_reverse.loc[x:]

    for dd_index, dd_value in enumerate(strat_drawdown):
        if dd_value == 0:
            zero_dd_date = strat_drawdown.index[dd_index]
            break
    return zero_dd_date


# move to dd
def get_recovery(price_series):
    """
    Finds the recovery timeline from where MaxDD occured and when strategy recoverd

    Parameters
    ----------
    price_series : series
        price series.

    Returns
    -------
    The number of "days" it took for strategy to return back to 'recovery'

    """
    zero_dd_date = find_zero_dd_date(price_series)
    zero_dd_date_price = price_series.loc[zero_dd_date]
    dd_date = find_dd_date(price_series)
    count_price_series = price_series.loc[dd_date[0]:]
    recovery_days = 0

    for price in count_price_series:
        if price < zero_dd_date_price:
            recovery_days += 1
        else:
            break
    return recovery_days


def get_cum_ret(return_series):
    return return_series.add(1).prod(axis=0) - 1


def get_port_analytics(return_series, freq='M', rfr=0.0, target=0.0, p=0.05):
    ann_ret = get_ann_return(return_series, freq)
    med_ret = get_median(return_series)
    avg_ret = get_mean(return_series)
    avg_up_ret = get_avg_pos_neg(return_series)
    avg_down_ret = get_avg_pos_neg(return_series, False)
    avg_pos_neg = get_avg_pos_neg_ratio(return_series)
    best_period = get_max(return_series)
    worst_period = get_min(return_series)
    pct_pos_periods = get_pct_pos_neg_periods(return_series)
    pct_neg_periods = get_pct_pos_neg_periods(return_series, False)
    ann_vol = get_ann_vol(return_series, freq)
    up_dev = get_updown_dev(return_series, freq, up=True)
    down_dev = get_updown_dev(return_series, freq)
    up_down_dev_ratio = get_up_down_dev_ratio(return_series, freq)
    skew = get_skew(return_series)
    kurt = get_kurtosis(return_series)
    max_dd = get_max_dd(return_series)
    max_1m_dd_dict = get_max_dd_freq(return_series, freq)
    max_3m_dd_dict = get_max_dd_freq(return_series, freq, True)
    ret_vol = get_sharpe_ratio(return_series, freq)
    sortino = get_sortino_ratio(return_series, freq)
    ret_dd = get_ret_max_dd_ratio(return_series, freq)
    ret_1m_dd = get_ret_max_dd_freq_ratio(return_series, freq, False)
    ret_3m_dd = get_ret_max_dd_freq_ratio(return_series, freq, True)
    var = get_var(return_series, p)
    cvar = get_cvar(return_series, p)
    return {'ann_ret': ann_ret, 'median_ret': med_ret, 'avg_ret': avg_ret,
            'avg_pos_ret': avg_up_ret, 'avg_neg_ret': avg_down_ret,
            'avg_pos_neg_ret': avg_pos_neg, 'best_period': best_period,
            'worst_period': worst_period, 'pct_pos_periods': pct_pos_periods,
            'pct_neg_periods': pct_neg_periods, 'ann_vol': ann_vol,
            'up_dev': up_dev, 'down_dev': down_dev, 'up_down_dev': up_down_dev_ratio,
            'vol_down_dev': ann_vol / down_dev, 'skew': skew, 'kurt': kurt, 'max_dd': max_dd,
            'max_1m_dd': max_1m_dd_dict['max_dd'], 'max_1m_dd_date': max_1m_dd_dict['index'],
            'max_3m_dd': max_3m_dd_dict['max_dd'], 'max_3m_dd_date': max_3m_dd_dict['index'],
            'ret_vol': ret_vol, 'sortino': sortino, 'ret_dd': ret_dd, 'ret_1m_dd': ret_1m_dd,
            'ret_3m_dd': ret_3m_dd, f'VaR {(1 - p):.0%}': var, f'CVaR {(1 - p):.0%}': cvar
            }


def get_active_analytics(return_series, bmk_series=dm.pd.Series(dtype='float64'), freq='M', empty=False):
    empty_analytics = {'bmk_name': None, 'bmk_beta': None, 'excess_ret': None,
                       'te': None, 'dwnside_te': None, 'te_dwnside_te': None, 'ir': None, 'ir_asym': None}
    if empty:
        return empty_analytics
    else:
        try:
            bmk_name = bmk_series.name
            df_port_bmk = dm.merge_data_frames(return_series, bmk_series)
            df_port_bmk.columns = ['port', 'bmk']
            df_port_bmk['active'] = df_port_bmk['port'] - df_port_bmk['bmk']
            beta_bmk = get_beta(df_port_bmk['port'], df_port_bmk['bmk'])
            excess_ret = get_ann_return(df_port_bmk['port'], freq) - get_ann_return(df_port_bmk['bmk'], freq)
            te = get_ann_vol(df_port_bmk['active'], freq)
            dwnside_te = get_updown_dev(df_port_bmk['active'], freq)
            ir = None if te == 0.0 else excess_ret / te
            ir_asym = None if dwnside_te == 0.0 else excess_ret / dwnside_te
            return {'bmk_name': bmk_name, 'bmk_beta': beta_bmk, 'excess_ret': excess_ret,
                    'te': te, 'dwnside_te': dwnside_te, 'te_dwnside_te': te / dwnside_te, 'ir': ir, 'ir_asym': ir_asym}
        except KeyError:
            print('Skipping active stats for {}.'.format(return_series.name))
            return empty_analytics


def get_mkt_analytics(mkt_ret_df, mkt, strat, freq='M', rfr=0.0, empty=False):
    empty_analytics = {'alpha': None, 'beta': None, 'up_beta': None, 'dwn_beta': None,
                       'corr': None, 'up_corr': None, 'dwn_corr': None}
    if empty:
        return empty_analytics
    else:
        try:
            mkt_series = mkt_ret_df[mkt]
            return_series = mkt_ret_df[strat]
            mkt_up_df = (mkt_ret_df[mkt_series > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_series <= 0])

            mkt_alpha = 0 if strat == mkt else get_alpha(return_series, mkt_series, freq, rfr)
            mkt_beta = 1 if strat == mkt else get_beta(return_series, mkt_series)
            mkt_up_beta = 1 if strat == mkt else get_beta(mkt_up_df[strat], mkt_up_df[mkt])
            mkt_dwn_beta = 1 if strat == mkt else get_beta(mkt_dwn_df[strat], mkt_dwn_df[mkt])
            mkt_corr = 1 if strat == mkt else mkt_series.corr(return_series)
            mkt_up_corr = 1 if strat == mkt else mkt_up_df[mkt].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt else mkt_dwn_df[mkt].corr(mkt_dwn_df[strat])
            return {'alpha': mkt_alpha, 'beta': mkt_beta, 'up_beta': mkt_up_beta, 'dwn_beta': mkt_dwn_beta,
                    'corr': mkt_corr, 'up_corr': mkt_up_corr, 'dwn_corr': mkt_dwn_corr}
        except KeyError:
            return empty_analytics


def get_mkt_analytics_list(mkt_analytics):
    mkt_list = []
    for asset_class in mkt_analytics:
        mkt_list = mkt_list + list(mkt_analytics[asset_class].values())
    return mkt_list

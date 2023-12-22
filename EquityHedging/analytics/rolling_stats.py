# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 15:10:56 2023

@author: Powis Forjoe
"""
import pandas as pd
from ..datamanager import data_manager as dm
from .import returns_stats as rs

RET_STATS_DICT = {'ann_ret': 'rs.get_ann_return(return_series, freq)', 'median_ret': 'rs.get_median(return_series)',
                 'avg_ret': 'rs.get_mean(return_series)', 'avg_pos_ret': 'rs.get_avg_pos_neg(return_series)',
                 'avg_neg_ret': 'rs.get_avg_pos_neg(return_series,False)', 
                 'avg_pos_neg_ret': 'rs.get_avg_pos_neg_ratio(return_series)', 'best_period': 'rs.get_max(return_series)',
                 'worst_period': 'rs.get_min(return_series)', 'pct_pos_periods': 'rs.get_pct_pos_neg_periods(return_series)',
                 'pct_neg_periods': 'rs.get_pct_pos_neg_periods(return_series, False)', 
                 'ann_vol': 'rs.get_ann_vol(return_series, freq)','up_dev': 'rs.get_updown_dev(return_series, freq,up=True)',
                 'down_dev': 'rs.get_updown_dev(return_series, freq)','up_down_dev': 'rs.get_up_down_dev_ratio(return_series,freq)',
                 'skew': 'rs.get_skew(return_series)', 'kurt':'rs.get_kurtosis(return_series)','max_dd': 'rs.get_max_dd(return_series)',
                 'ret_vol': 'rs.get_sharpe_ratio(return_series,freq)', 'sortino':'rs.get_sortino_ratio(return_series, freq)',
                 'ret_dd':'rs.get_ret_max_dd_ratio(return_series,freq)'
                 }

ACTIVE_STATS_DICT = {'bmk_beta': 'get_rolling_bmk_beta(return_series, bmk_series, years, freq)',
                     'excess_ret': 'get_rolling_excess_ret(return_series, bmk_series, years, freq)',
                     'te': 'get_rolling_te(return_series, bmk_series, years, freq)',
                     'downside_te': 'get_rolling_te(return_series, bmk_series, years, freq, True)',
                     'ir': 'get_rolling_ir(return_series, bmk_series, years, freq)',
                     'asym_ir': 'get_rolling_ir(return_series, bmk_series, years, freq, True)'
                     }

def get_window_len(years,freq):
    return int(years*dm.switch_freq_int(freq))

def get_rolling_data(returns_df, years=3, freq='1M',rfr = 0.0,include_bmk = False, 
                     bmk_df = pd.DataFrame(), bmk_dict={},include_mkt=False, mkt_df=pd.DataFrame()):
    rolling_dict = {'ret_stats': get_rolling_stat_data(returns_df, years, freq),
                    'corr_stats': get_rolling_corr_data(returns_df, years, freq)
                    }
    if include_bmk:
        if not bmk_df.empty and bool(bmk_dict):
            rolling_dict['active_stats'] = get_rolling_active_data(returns_df, bmk_df, bmk_dict, years, freq)
        else:
            print('Missing bmk data...check bmk_df or bmk_dict')
    
    if include_mkt:
        if not mkt_df.empty:
            rolling_dict['mkt_stats'] = get_rolling_mkt_data(returns_df, mkt_df, years, freq, rfr)
        else:
            print('Missing mkt data...check mkt_df')
    return rolling_dict

def get_rolling_stat_data(return_df,years=3, freq='1M'):
    print('Computing rolling return stats')
    rolling_dict = {}
    for key in RET_STATS_DICT:
        rolling_dict[key] = get_rolling_stat_df(return_df,key,years,freq)
    return rolling_dict

def get_rolling_corr_data(return_df,years=3, freq='1M'):
    """
    Get a dictionary contaiing rolling correlations of each strategy in df_returns vs the other strategies

    Parameters
    ----------
    df_returns : TYPE
        DESCRIPTION.
    window : int
        rolling window.

    Returns
    -------
    rolling_corr_dict : Dictionary
        DESCRIPTION.

    """
    print('Computing rolling correlation stats')
    rolling_corr_dict = {}
    for strat in return_df:
        rolling_corr_dict[strat] = get_rolling_corr_df(return_df, return_df[strat], years, freq)
    return rolling_corr_dict

def get_rolling_active_data(return_df, bmk_df, bmk_dict, years=3, freq='1M'):
    print('Computing rolling active stats')
    rolling_dict = {}
    for key in ACTIVE_STATS_DICT:
        rolling_dict[key] = get_rolling_active_df(return_df, bmk_df, bmk_dict, key, years, freq)
    return rolling_dict
    
def get_rolling_mkt_data(return_df, mkt_df, years=3, freq='1M',rfr=0.0):
    print('Computing rolling mkt stats (alpha, beta)')
    return {'alpha': get_rolling_alpha_beta_data(return_df, mkt_df, years,freq, True, rfr),
            'beta': get_rolling_alpha_beta_data(return_df, mkt_df, years,freq)
            }

def get_rolling_alpha_beta_data(return_df, mkt_df, years=3, freq='1M', alpha=False, rfr=0.0):
    #make a dict to collect the data
    rolling_dict = {}
    #iterate through items
    for strat in return_df:
        try:
            rolling_dict[strat] = get_rolling_mkt_df(return_df[strat],mkt_df,years, freq, alpha, rfr)
        except KeyError:
            print(f'Missing mkt data for {strat}...check mkt_df')
            pass
    return rolling_dict
    
def get_rolling_stat_df(return_df, stat='ann_ret', years=3, freq='1M'):
    rolling_df = pd.DataFrame()
    for strat in return_df:
        rolling_df = pd.concat([rolling_df, get_rolling_stat(return_df[strat], stat,years,freq)],axis=1)
    return rolling_df

def get_rolling_corr_df(return_df, return_series, years=3, freq='1M'):
    rolling_df = pd.DataFrame()
    for strat in return_df:
        rolling_corr = get_rolling_corr(return_series, return_df[strat], years, freq)
        #do not include correlation of same return_series
        if(len(rolling_corr) == round(rolling_corr.sum())):
            pass
        else:
            rolling_df = pd.concat([rolling_df, rolling_corr], axis=1)
    return rolling_df

def get_rolling_active_df(return_df, bmk_df,bmk_dict, stat='bmk_beta', years=3, freq='1M'):
    #make a df to collect the data
    rolling_df = pd.DataFrame()
    #iterate through items
    for strat in return_df:
        try:
            bmk_name = bmk_dict[strat]
            rolling_df = pd.concat([rolling_df, get_rolling_active_stat(return_df[strat],bmk_df[bmk_name],stat,years,freq)], axis=1)
        except KeyError:
            print(f'Missing bmk data for {strat}...check bmk_df or bmk_dict')
            pass
    return rolling_df

def get_rolling_mkt_df(return_series, mkt_df, years=3, freq='1M', alpha=False, rfr=0.0):
    rolling_df = pd.DataFrame()
    for mkt in mkt_df:
        if alpha:
            rolling_mkt = get_rolling_alpha(return_series, mkt_df[mkt],years,freq,rfr)
        else:
            rolling_mkt = get_rolling_beta(return_series, mkt_df[mkt],years,freq)
        rolling_df = pd.concat([rolling_df, rolling_mkt], axis=1)
    return rolling_df

def get_clean_series(data_series, name):
    data_series.dropna(inplace=True)
    data_series.name = name
    return data_series

def get_rolling_stat(return_series,stat='ann_ret', years=3, freq='1M'):
    window = get_window_len(years, freq)
    rolling_stat = return_series.rolling(window).apply(lambda return_series: eval(RET_STATS_DICT[stat],{'rs':rs},{'return_series':return_series,'freq':freq}))
    return get_clean_series(rolling_stat, return_series.name)  

def get_rolling_corr(ret_series_1, ret_series_2, years=3, freq='1M'):
    """
    Get rolling correlation between 2 return series

    Parameters
    ----------
    ret_series_1 : Series
        returns.
    ret_series_2 : Series
        returns.
    window : int
        rolling window.

    Returns
    -------
    rolling_corr : series
        correlation series.

    """
    window = get_window_len(years, freq)
    rolling_corr = ret_series_1.rolling(window).corr(ret_series_2)
    return get_clean_series(rolling_corr, ret_series_2.name)

def get_rolling_active_stat(return_series,bmk_series,stat='bmk_beta', years=3, freq='1M'):
    return eval(ACTIVE_STATS_DICT[stat])
                
def get_active_data(return_series, bmk_series):
    df_port_bmk = dm.merge_data_frames(return_series,bmk_series)
    name_key = {'port':return_series.name, 'bmk':bmk_series.name}
    active_series = df_port_bmk[name_key['port']] - df_port_bmk[name_key['bmk']]
    active_series.name = name_key['port']
    return {'port': df_port_bmk[name_key['port']], 'bmk':df_port_bmk[name_key['bmk']], 'active':active_series}

def get_rolling_bmk_beta(return_series, bmk_series, years=3, freq='1M'):
    active_dict = get_active_data(return_series, bmk_series)
    rolling_beta = get_rolling_beta(active_dict['port'], active_dict['bmk'], years,freq)
    return get_clean_series(rolling_beta, return_series.name)

def get_rolling_excess_ret(return_series, bmk_series, years=3, freq='1M'):
    active_dict = get_active_data(return_series, bmk_series)
    rolling_excess_ret = get_rolling_stat(active_dict['port'], 'ann_ret',years, freq) - get_rolling_stat(active_dict['bmk'], 'ann_ret',years, freq)
    return get_clean_series(rolling_excess_ret, return_series.name)

def get_rolling_te(return_series, bmk_series, years=3, freq='1M', downside=False):
    active_dict = get_active_data(return_series, bmk_series)
    if downside:
        return get_rolling_stat(active_dict['active'],'down_dev',years, freq)
    else:
        return get_rolling_stat(active_dict['active'],'ann_vol',years, freq)

def get_rolling_ir(return_series, bmk_series, years=3, freq='1M', asym=False):
    rolling_excess_ret = get_rolling_excess_ret(return_series, bmk_series, years,freq)
    rolling_te = get_rolling_te(return_series, bmk_series, years, freq, downside=asym)
    return get_clean_series(rolling_excess_ret/rolling_te, return_series.name)

def get_rolling_alpha(return_series, mkt_series, years=3, freq='1M', rfr = 0.0):
    rolling_beta = get_rolling_beta(return_series, mkt_series, years, freq)
    rolling_mkt_ret = get_rolling_stat(mkt_series,'ann_ret',years, freq)
    rolling_ret = get_rolling_stat(return_series,'ann_ret',years, freq)
    rolling_alpha = rolling_ret - (rfr +  rolling_beta*(rolling_mkt_ret - rfr))
    return get_clean_series(rolling_alpha, mkt_series.name)
    
def get_rolling_beta(return_series, mkt_series, years=3, freq='1M'):
    window = get_window_len(years, freq)
    rolling_beta = return_series.rolling(window).cov(mkt_series)/mkt_series.rolling(window).var()
    return get_clean_series(rolling_beta, mkt_series.name)

# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""

#TODO: Clean this and merge
from ..datamanager import data_manager as dm
from .decay import get_decay_days
from .util import get_pos_neg_df
from .recovery import compute_decay_pct

HEDGE_METRICS_INDEX = ['Benefit Count','Benefit Median','Benefit Mean','Benefit Cum', 
                       'Downside Reliability','Upside Reliability',
                       'Convexity Count','Convexity Median','Convexity Mean','Convexity Cum',
                       'Cost Count','Cost Median','Cost Mean','Cost Cum',
                       'Decay Days (50% retrace)','Decay Days (25% retrace)','Decay Days (10% retrace)']

def get_hm_index_list(full_list=True):
    if full_list:
        return HEDGE_METRICS_INDEX
    else:
        return ['Benefit','Downside Reliability','Upside Reliability', 'Tail Reliability', 
                'Non Tail Reliability','Convexity','Cost', 'Decay','Average Return']

def get_pct_index(return_series, pct, less_than = True):
    #compute the pct percentile
    percentile = return_series.quantile(pct)
    
    if less_than:
        #get the all data that is less than/equal to the pct percentile
        return return_series.index[return_series <= percentile]
    else:
        #get the all data that is greater than the pct percentile
        return return_series.index[return_series > percentile]
    # return return_series.loc[pct_index]

def get_hm_stats(return_series, pct=.98, less_than=True, pos = True):
    if pos:
        pos_ret = return_series.loc[get_pct_index(return_series, pct, less_than)]
        hm_ret = get_pos_neg_df(pos_ret,pos)
    else:
        hm_ret = get_pos_neg_df(return_series,pos)
    
    return {'count': hm_ret.count(), 'mean': hm_ret.mean(),
            'med': hm_ret.median(),'cumulative': hm_ret.sum()
            }
    
#TODO: switch to return_series
def get_benefit_stats(return_series, pct=.98):
    """
    Return count, mean, mode and cumulative of all positive returns
    less than the 98th percentile rank

    Parameters
    ----------
    return_series : series
        returns series.
    
    col_name : string
        strategy name in df_returns.

    Returns
    -------
    benefit : dictionary
        {count: double, mean: double, median: double, cumulative: double}

    """
    
    #create a dataframe containing only the col_name strategy
    # df_strat = dm.remove_na(df_returns, col_name)
    
    #compute the 98th percentile
    # percentile = return_series.quantile(.98)
    
    #get the all data that is less than the 98th percentile
    # benefit_index = return_series.index[return_series < percentile]
    benefit_ret = return_series.loc[get_pct_index(return_series, pct, True)]
    
    #filter out negative returns
    pos_ret = get_pos_neg_df(benefit_ret,True)
    
    #calculate hedge metrics
    benefit_count = pos_ret.count()
    benefit_mean = pos_ret.mean()
    benefit_med = pos_ret.median()
    benefit_cum = benefit_count*benefit_mean
    
    #create dictionary
    return {'count': benefit_count, 'mean': benefit_mean, 
            'median': benefit_med,'cumulative': benefit_cum
            }

#TODO: switch to return_series
def get_convexity_stats(return_series, pct=.98):
    """
    Return count, mean, mode and cumulative of all positive returns
    greater than the 98th percentile rank

    Parameters
    ----------
    return_series : series
        returns series.
    
    Returns
    -------
    convexity : dictionary
        {count: double, mean: double, median: double, cumulative: double}
    """
    
    #create a dataframe containing only the col_name strategy
    # df_strat = dm.remove_na(df_returns, col_name)
    
    #compute the 98th percentile
    # percentile = return_series.quantile(.98)
    
    # #get the all data that is greater than the 98th percentile
    # convexity_index = return_series.index[return_series > percentile]
    convexity_ret = return_series.loc[get_pct_index(return_series, pct, False)]
    
    #may not need this line since all the data may be positive already
    pos_ret = get_pos_neg_df(convexity_ret,True)
    
    #calculate hedge metrics
    convexity_count = pos_ret.count()
    convexity_mean = pos_ret.mean()
    convexity_med = pos_ret.median()
    convexity_cum = convexity_count*convexity_mean
    
    #create convexity dictionary
    return {'count': convexity_count, 
                 'mean': convexity_mean , 
                 'median': convexity_med,
                 'cumulative': convexity_cum
                 }

    # return convexity

#TODO: switch to return_series
#TODO: revisit decay
def get_decay_stats(return_series, freq):
    """
    Return decay stats of returns

    Parameters
    ----------
    return_series : series
        returns series.
    
    col_name : string
        strategy name in df_returns.
    freq : string
        frequency.

    Returns
    -------
    decay_dict : dictionary
        {key: decay_percent, value: int)

    """
    
    #Compute decay values only if data is daily or weekly
    if dm.switch_freq_int(freq) >= 12:
        decay_half = get_decay_days(return_series, freq)
        decay_quarter = get_decay_days(return_series, freq, .25)
        decay_tenth = get_decay_days(return_series, freq, .10)
    else:
        decay_half = 0
        decay_quarter = 0
        decay_tenth = 0
        
    #create decay dictionary
    decay_dict = {'half': decay_half, 
                  'quarter': decay_quarter, 
                  'tenth':decay_tenth
                  }
    
    return decay_dict

def get_decay_stats_2(df_returns, col_name, freq):
    """
    Return decay stats of returns

    Parameters
    ----------
    return_series : series
        returns series.
    
    col_name : string
        strategy name in df_returns.
    freq : string
        frequency.

    Returns
    -------
    decay_dict : dictionary
        {key: decay_percent, value: int)

    """
    
    #Compute decay values only if data is daily or weekly
    if dm.switch_freq_int(freq) >= 12:
        return compute_decay_pct(df_returns, col_name,freq)
    else:
        return 0
    
#TODO: switch to return_series
def get_cost_stats(return_series):
    """
    Return count, mean, mode and cumulative of all negative returns

    Parameters
    ----------
    return_series : series
        returns series.
    
    Returns
    -------
    cost : dictionary
        {count: double, mean: double, median: double, cumulative: double}

    """
    
    #filter out positive returns
    neg_ret = get_pos_neg_df(return_series ,False)
    
    #calculate hedge metrics
    cost_count = neg_ret.count()
    cost_mean = neg_ret.mean()
    cost_med = neg_ret.median()
    cost_cum = cost_count*cost_mean
    
    #create cost dictionary
    cost = {'count': cost_count , 
            'mean': cost_mean , 
            'median': cost_med,
            'cumulative': cost_cum
            }
    
    return cost

#TODO: switch to return_series
def get_reliability_stats(return_series, mkt_series, tail=False):
    """
    Return correlation of strategy to equity bencmark downside returns and upside returns
    
    Parameters
    ----------
    return_series : series
        returns series.
    mkt_series : series
        mkt series.
    tail: Boolean, optional
        get tail correlation, Default is False
    Returns
    -------
    reliability : dictionary
        dict{down:(double), up:(double),
             tail:(double), non_tail:(double)}.

    """
    #merge return and mkt series
    mkt_ret_df = dm.merge_data_frames(mkt_series, return_series)
    mkt_id = mkt_series.name
    strat_id = return_series.name
    
    #create dataframes containing only data when mkt is <= 0 and > 0
    mkt_up_df = mkt_ret_df[mkt_ret_df[mkt_id] > 0]
    mkt_dwn_df = mkt_ret_df[mkt_ret_df[mkt_id] <= 0]
    
    #create reliability dictionary
    if tail:
        tail = mkt_dwn_df.loc[get_pct_index(mkt_dwn_df[mkt_id], 0.1)]
        non_tail = mkt_dwn_df.loc[get_pct_index(mkt_dwn_df[mkt_id],0.1,False)]
        return {'down': mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat_id]),
                'up':mkt_up_df[mkt_id].corr(mkt_up_df[strat_id]),
                'tail':tail[mkt_id].corr(tail[strat_id]),
                'non_tail':non_tail[mkt_id].corr(non_tail[strat_id])
                }
    else:
        return {'down': mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat_id]),
                'up':mkt_up_df[mkt_id].corr(mkt_up_df[strat_id])
                }
    
def get_reliability_stats1(df_returns, col_name, tail=False):
    """
    Return correlation of strategy to equity bencmark downside returns and upside returns
    
    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.
        
    Returns
    -------
    reliability : dictionary
        dict{down(double), up(double)}.

    """
    
    #get the equity_id
    col_list = list(df_returns.columns)
    equity_id = col_list[0]
    
    #create dataframe containing only data when equity_id < 0
    equity_down = (df_returns[df_returns[equity_id] < 0])
    
    #comupte the correlation and get the reliability stat for the col_name strategy
    corr_d = equity_down.corr()
    reliability_d= corr_d[col_name].iloc[0]
    
    #create dataframe containing only data when equity_id > 0
    equity_up = (df_returns[df_returns[equity_id] > 0])
    
    #comupte the correlation and get the reliability stat for the col_name strategy
    corr_u = equity_up.corr()
    reliability_u = corr_u[col_name].iloc[0]
    
    #create reliability dictionary
    reliability={'down': reliability_d,
                 'up':reliability_u}
    
    #compute tail & non tail reliability
    if tail:
        percentile = equity_down[equity_id].quantile(.1)
        tail_index = equity_down.index[equity_down[equity_id]<percentile]
        tail_df = equity_down.loc[tail_index]
        non_tail_index = equity_down.index[equity_down[equity_id]>percentile]
        non_tail_df = equity_down.loc[non_tail_index]
        corr_tail = tail_df.corr()
        reliability['tail'] = corr_tail[col_name].iloc[0]
        corr_non_tail = non_tail_df.corr()
        reliability['non_tail'] = corr_non_tail[col_name].iloc[0]
    
    return reliability


def get_hm_analytics(return_series, mkt_series, freq='1M', full_list=True):
    benefit = get_hm_stats(return_series)
    convexity = get_hm_stats(return_series, less_than=False)
    cost = get_hm_stats(return_series,pos=False)
    decay = get_decay_stats(return_series, freq)
    
    if full_list:
        reliability = get_reliability_stats(return_series, mkt_series)
        hm_list = [*list(benefit.values()), *list(reliability.values()), *list(convexity.values()),
                   *list(cost.values()), *list(decay.values())]
    else:
        reliability = get_reliability_stats(return_series, mkt_series, True)
        avg_ret = benefit['cumulative']+ convexity['cumulative'] + cost['cumulative']
        hm_list = [*[benefit['cumulative']], *list(reliability.values()), 
                   *[convexity['cumulative'],cost['cumulative'], decay['half'], avg_ret]]
            
    return dict(zip(get_hm_index_list(full_list), hm_list))
    
# def get_hm_df(df_returns, mkt_series,freq="1M", full_list=True):
#     hm_dict = {}
#     period = get_time_frame(df_returns)
#     for col in df_returns:
#         return_series = dm.remove_na(df_returns, col)[col]
#         hm_dict[col] = [period[col], len(return_series)] +list(get_hm_analytics(return_series, mkt_series, freq, full_list).values())
#     hm_df = util.convert_dict_to_df(hm_dict, get_hm_index_list(full_list))
#     return hm_df
    
def get_hedge_metrics(df_returns, freq="1M", full_list=True):
    """
    Return a dataframe of hedge metrics

    Parameters
    ----------
    return_series : series
        returns series.
    
    freq : string, optional
        Frequency. The default is "1M".
    full_list: boolean, optional

    Returns
    -------
    df_hedge_metrics : dataframe
        
    """
    
    #create empty dictionary
    hedge_dict = {}
    if full_list:
        #loop through columns in df_returns to compute and store the hedge 
        #metrics for each strategy
        for col in df_returns.columns:
            benefit = get_benefit_stats(df_returns[col])
            reliability = get_reliability_stats1(df_returns,col)
            convexity = get_convexity_stats(df_returns[col])
            cost = get_cost_stats(df_returns[col])
            decay = get_decay_stats(df_returns[col], freq)
            
            hedge_dict[col] = [*list(benefit.values()),*list(reliability.values()),*list(convexity.values()),
                               *list(cost.values()),*list(decay.values())]
    else:
        for col in df_returns.columns:
            benefit = get_benefit_stats(df_returns[col])
            reliability = get_reliability_stats1(df_returns,col,True)
            convexity = get_convexity_stats(df_returns[col])
            cost = get_cost_stats(df_returns[col])
            decay = get_decay_days(df_returns[col], freq)
            avg_ret = benefit['cumulative']+ convexity['cumulative'] + cost['cumulative']
            
            hedge_dict[col] = [*[benefit['cumulative']], *list(reliability.values()), 
                               *[convexity['cumulative'],cost['cumulative'], decay['half'], avg_ret]]
    
    #Converts hedge_dict to a data grame
    df_hedge_metrics = util.convert_dict_to_df(hedge_dict, get_hm_index_list(full_list))
    return df_hedge_metrics

def get_hedge_metrics_2(df_returns, freq="1M", full_list=True):
    """
    Return a dataframe of hedge metrics

    Parameters
    ----------
    df_returns : dataframe
    freq : string, optional
        Frequency. The default is "1M".
    full_list: boolean, optional

    Returns
    -------
    df_hedge_metrics : dataframe
        
    """
    
    #create empty dictionary
    hedge_dict = {}
    
    if full_list:
        #loop through columns in df_returns to compute and store the hedge 
        #metrics for each strategy
        for col in df_returns.columns:
            benefit = get_benefit_stats(df_returns, col)
            reliability = get_reliability_stats(df_returns, col)
            convexity = get_convexity_stats(df_returns, col)
            cost = get_cost_stats(df_returns, col)
            decay = get_decay_stats_2(df_returns, col, freq)
            
            hedge_dict[col] = [benefit['count'],benefit['median'],benefit['mean'],
                               benefit['cumulative'],reliability['down'],reliability['up'],
                               convexity['count'],convexity['median'],convexity['mean'],
                               convexity['cumulative'],cost['count'],cost['median'],cost['mean'], 
                               cost['cumulative'],decay]
    else:
        for col in df_returns.columns:
            benefit = get_benefit_stats(df_returns, col)
            reliability = get_reliability_stats(df_returns, col,True)
            convexity = get_convexity_stats(df_returns, col)
            cost = get_cost_stats(df_returns, col)
            decay = get_decay_stats_2(df_returns, col, freq)
            avg_ret = benefit['cumulative']+ convexity['cumulative'] + cost['cumulative']
            
            hedge_dict[col] = [benefit['cumulative'],
                              reliability['down'],reliability['up'],
                              convexity['cumulative'], cost['cumulative'], decay,
                              avg_ret, reliability['tail'],reliability['non_tail']]
    
    #Converts hedge_dict to a data grame
    df_hedge_metrics = util.convert_dict_to_df(hedge_dict, get_hm_index_list(full_list))
    return df_hedge_metrics
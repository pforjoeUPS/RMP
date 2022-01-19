# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 12:30:00 2021

@author: Powis Forjoe
"""

import pandas as pd
from ..datamanager.data_manager import switch_freq_int

def format_return_stats(anayltics_df):
    """
    Formats the return stats analytics

    Parameters
    ----------
    anayltics_df : dataframe
        dataframe containing returns stats

    Returns
    -------
    formatters : formatter

    """
    
    formatters = {"Annualized Ret":lambda x: f"{x:.2%}"
                  ,"Annualized Vol":lambda x: f"{x:.2%}"
                  ,"Ret/Vol":lambda x: f"{x:.2f}"
                  ,"Max DD":lambda x: f"{x:.2%}"
                  ,"Ret/Max DD":lambda x: f"{x:.2f}"
                  ,"Max 1M DD":lambda x: f"{x:.2%}"
                  ,"Max 1M DD Date":lambda x: x.to_pydatetime().strftime("%Y-%m-%d")
                  ,"Ret/Max 1M DD":lambda x: f"{x:.2f}"
                  ,"Max 3M DD":lambda x: f"{x:.2%}"
                  ,"Max 3M DD Date":lambda x: x.to_pydatetime().strftime("%Y-%m-%d")
                  ,"Ret/Max 3M DD":lambda x: f"{x:.2f}"
                  ,"Skew":lambda x: f"{x:.2f}"
                  ,"Avg Pos Ret/Avg Neg Ret":lambda x: f"{x:.2f}"
                  ,"Downside Deviation":lambda x: f"{x:.2%}"
                  ,"Sortino Ratio":lambda x: f"{x:.2f}"
                  }
    return formatters 

def format_hedge_metrics(anayltics_df, freq='1M'):
    """
    Formats the hedge metrics analytics

    Parameters
    ----------
    anayltics_df : dataframe
        dataframe containing hedge metrics
    freq : string, optional
        frequency of hedge metrics computed. The default is '1M'.

    Returns
    -------
    formatters : formatter

    """
    
    if switch_freq_int(freq) <= 12:
        formatters = {"Benefit Count":lambda x: f"{x:.0f}"
                      ,"Benefit Median":lambda x: f"{x:.2%}"
                      ,"Benefit Mean":lambda x: f"{x:.2%}"
                      ,"Benefit Cum":lambda x: f"{x:.2%}"
                      ,"Downside Reliability":lambda x: f"{x:.2f}"
                      ,"Upside Reliability":lambda x: f"{x:.2f}"
                      ,"Convexity Count":lambda x: f"{x:.0f}"
                      ,"Convexity Median":lambda x: f"{x:.2%}"
                      ,"Convexity Mean":lambda x: f"{x:.2%}"
                      ,"Convexity Cum":lambda x: f"{x:.2%}"
                      ,"Cost Count":lambda x: f"{x:.0f}"
                      ,"Cost Median":lambda x: f"{x:.2%}"
                      ,"Cost Mean":lambda x: f"{x:.2%}" 
                      ,"Cost Cum":lambda x: f"{x:.2%}"
                 }
    else:
        formatters = {"Benefit Count":lambda x: f"{x:.0f}"
                      ,"Benefit Median":lambda x: f"{x:.2%}"
                      ,"Benefit Mean":lambda x: f"{x:.2%}"
                      ,"Benefit Cum":lambda x: f"{x:.2%}"
                      ,"Downside Reliability":lambda x: f"{x:.2f}"
                      ,"Upside Reliability":lambda x: f"{x:.2f}"
                      ,"Convexity Count":lambda x: f"{x:.0f}"
                      ,"Convexity Median":lambda x: f"{x:.2%}"
                      ,"Convexity Mean":lambda x: f"{x:.2%}"
                      ,"Convexity Cum":lambda x: f"{x:.2%}"
                      ,"Cost Count":lambda x: f"{x:.0f}"
                      ,"Cost Median":lambda x: f"{x:.2%}"
                      ,"Cost Mean":lambda x: f"{x:.2%}" 
                      ,"Cost Cum":lambda x: f"{x:.2%}"
                      ,"Decay Days (50% retrace)":lambda x: f"{x:.0f}"
                      ,"Decay Days (25% retrace)":lambda x: f"{x:.0f}"
                      ,"Decay Days (10% retrace)":lambda x: f"{x:.0f}"
             }
    return formatters
    
def format_premia_metrics(anayltics_df):
    """
    Formats the hedge metrics analytics

    Parameters
    ----------
    anayltics_df : dataframe
        dataframe containing hedge metrics
    freq : string, optional
        frequency of hedge metrics computed. The default is '1M'.

    Returns
    -------
    formatters : formatter

    """
    
   
    formatters = {"Benefit Count":lambda x: f"{x:.0f}"
                  ,"Benefit Median":lambda x: f"{x:.2%}"
                  ,"Benefit Mean":lambda x: f"{x:.2%}"
                  ,"Benefit Cum":lambda x: f"{x:.2%}"
                  ,"Correlation to Equity":lambda x: f"{x:.4f}"
                  ,"Correlation to Rates":lambda x: f"{x:.4f}"
                  ,"Convexity Count":lambda x: f"{x:.0f}"
                  ,"Convexity Median":lambda x: f"{x:.2%}"
                  ,"Convexity Mean":lambda x: f"{x:.2%}"
                  ,"Convexity Cum":lambda x: f"{x:.2%}"
                  ,"Cost Count":lambda x: f"{x:.0f}"
                  ,"Cost Median":lambda x: f"{x:.2%}"
                  ,"Cost Mean":lambda x: f"{x:.2%}" 
                  ,"Cost Cum":lambda x: f"{x:.2%}"
                  ,"Recovery":lambda x: f"{x:.2%}"
         }
    return formatters    

def format_hm_to_normalize(hm_df, more_metrics=False):
    '''
    

    Parameters
    ----------
    df : data frame
        data from hm.get_hedge_metrics_to_normalize

    Returns
    -------
    styler

    '''

    if more_metrics:
        formatters = {"Benefit":lambda x: f"{x:.2%}"
                  ,"Downside Reliability":lambda x: f"{x:.4f}"
                  ,"Upside Reliability":lambda x: f"{x:.4f}"                      
                  ,"Convexity":lambda x: f"{x:.2%}"
                  ,"Cost":lambda x: f"{x:.2%}"
                  ,"Decay":lambda x: f"{x:.0f}"
                  ,"Average Return":lambda x: f"{x:.2%}"
                  ,"Tail Reliability":lambda x: f"{x:.4f}"
                  ,"Non Tail Reliability":lambda x: f"{x:.4f}"                      
                  }
    else:
        formatters = {"Benefit":lambda x: f"{x:.2%}"
                  ,"Downside Reliability":lambda x: f"{x:.4f}"
                  ,"Upside Reliability":lambda x: f"{x:.4f}"                      
                  ,"Convexity":lambda x: f"{x:.2%}"
                  ,"Cost":lambda x: f"{x:.2%}"
                  ,"Decay":lambda x: f"{x:.0f}"
                  }
        
    return hm_df.style.\
            format(formatters)
            
def format_pm_to_normalize(pm_df):
    '''
    

    Parameters
    ----------
    df : data frame
        data from hm.get_hedge_metrics_to_normalize

    Returns
    -------
    styler

    '''

    formatters = {"Benefit":lambda x: f"{x:.2%}"
                  ,"Correlation to Equity":lambda x: f"{x:.4f}"
                  ,"Correlation to Rates":lambda x: f"{x:.4f}"                  
                  ,"Convexity":lambda x: f"{x:.2%}"
                  ,"Cost":lambda x: f"{x:.2%}"
                  ,"Recovery":lambda x: f"{x:.2%}"
                  }
        
    return pm_df.style.\
            format(formatters)

def format_normalized_data(df_normal):
    '''
    

    Parameters
    ----------
    df_normal : data frame

    Returns
    -------
    df_normal : data frame
        rounds data to 2 decimal points

    '''
    
    formatter = {}
    col_list = list(df_normal.columns)
    
    for strat in col_list:
        formatter[strat] = "{:.4f}"
        
    return df_normal.style.\
            apply(highlight_min, subset = pd.IndexSlice[:,col_list[0:]]).\
            apply(highlight_max, subset = pd.IndexSlice[:,col_list[0:]]).\
            format(formatter)

def format_notional_weights(df_weights):
    """
    Formats the portfolio weightings

    Parameters
    ----------
    df_weights : dataframe
        dataframe containing portfolio weightings

    Returns
    -------
    formatters : formatter

    """
    
    formatters = {"Notional Weights (Billions)":lambda x: f"${x:.2f}"
                  ,"Percentage Weights":lambda x: f"{x:.2%}"
                  ,"Strategy Weights":lambda x: f"{x:.2%}"
                  }
    return formatters 

def format_row_wise(styler, formatter):
    """
    Returns a styler that applies a formatter to a dataframe by row

    Parameters
    ----------
    styler : styler
    formatter : formatter

    Returns
    -------
    styler : styler

    """
    
    for row, row_formatter in formatter.items():
        row_num = styler.index.get_loc(row)
        for col_num in range(len(styler.columns)):
            styler._display_funcs[(row_num, col_num)] = row_formatter
    return styler

def get_analytics_styler(analytics_dict, stats='return_stats', freq='1M'):
    """
    Returns styler for analytics dataframe

    Parameters
    ----------
    analytics_dict : dictionary
        Dictionary containing return stats and hedge metrics
    stats : string, optional
        'return_stats', 'hedge_metrics'. The default is 'return_stats'.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    analytics_styler : styler

    """
    
    #make copy of dataframe being styled
    stats_df = analytics_dict[stats].copy()
    
    #apply appropirate styler based on stats freq choice
    if stats == 'return_stats':
        return_formatter = format_return_stats(stats_df)
        analytics_styler = format_row_wise(stats_df.style, return_formatter)
    elif stats == 'hedge_metrics':
        hedge_formatter = format_hedge_metrics(stats_df, freq)
        analytics_styler = format_row_wise(stats_df.style, hedge_formatter)
    elif stats == 'premia_metrics':
        premia_formatter = format_premia_metrics(stats_df)
        analytics_styler = format_row_wise(stats_df.style, premia_formatter)
    
    return analytics_styler

def get_notional_styler(df_weights):
    """
    Returns styler for portfolio weightings dataframe

    Parameters
    ----------
    df_weights : dataframe

    Returns
    -------
    styler

    """
    return format_row_wise(df_weights.style,
                           format_notional_weights(df_weights))

def color_neg_pos(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, green for positive, black otherwise.

    Parameters
    ----------
    val : float

    Returns
    -------
    string

    """

    if val < 0:
        color = 'red'
    elif val > 0:
        color = 'green'
    else:
        color = 'black'
    return 'color: %s' % color

def color_neg_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.

    Parameters
    ----------
    val : float

    Returns
    -------
    string

    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

#TODO:fix bug with daily data
def get_returns_styler(df_returns):
    """
    Returns styler for returns dataframe

    Parameters
    ----------
    df_returns : dataframe

    Returns
    -------
    styler

    """
    
    #make copy of dataframe
    data = df_returns.copy()
    
    #format dates
    data.index = pd.to_datetime(data.index, format = '%m/%d/%Y').strftime('%Y-%m-%d')
    
    #define formatter
    col_list = data.columns.tolist()
    formatter = {}
    for strat in col_list:
        formatter[strat] = "{:.2%}"
    
    #return styler
    return data.style.\
        applymap(color_neg_red, subset = pd.IndexSlice[:,col_list]).\
        format(formatter)

def get_hist_styler(df_hist):
    """
    Returns styler for historical selloffs dataframe

    Parameters
    ----------
    df_hist : dataframe
    Returns
    -------
    styler

    """
    
    #define formatter
    col_list = list(df_hist.columns)[2:]
    formatter = {}
    for strat in col_list:
        formatter[strat] = "{:.2%}"
    
    #return styler
    return df_hist.style.\
        applymap(color_neg_pos, subset = pd.IndexSlice[:,col_list]).\
        format(formatter)

def highlight_max(s):
    """
    Highlight the maximum in a Series yellow

    Parameters
    ----------
    s : series

    Returns
    -------
    list

    """
    
    is_max = s == s.max()
    return ['background-color: green' if v else '' for v in is_max]
    
def highlight_max_ret(s):
    """
    Highlight the maximum in a Series yellow

    Parameters
    ----------
    s : series

    Returns
    -------
    list

    """
    
    is_max = s == s.max()
    return ['background-color: yellow' if v else '' for v in is_max]
  
def highlight_min(s):
    """
    Highlight the minimum in a Series red

    Parameters
    ----------
    s : series

    Returns
    -------
    list

    """
    
    is_min = s == s.min()
    return ['background-color: red' if v else '' for v in is_min]
    
def get_dollar_ret_styler(dollar_returns):
    """
    Returns styler for returns dataframe

    Parameters
    ----------
    dollar_returns : dataframe

    Returns
    -------
    styler

    """
    
    #make copy of dataframe
    data = dollar_returns.copy()
    
    #format dates
    data.index = pd.to_datetime(data.index, format = '%m/%d/%Y').strftime('%Y')
    
    #define formatter
    formatter = {}
    col_list = list(data.columns)
    for strat in col_list:
        formatter[strat] = "${:,.0f}"
    
    #return styler
    return data.style.\
            applymap(color_neg_pos).\
            apply(highlight_max_ret, subset = pd.IndexSlice[:,col_list[1:]]).\
            format(formatter)
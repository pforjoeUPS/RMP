# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 12:30:00 2021

@author: Powis Forjoe
"""

import pandas as pd
from ..datamanager.data_manager import switch_freq_int

#TODO: separate code into dataframe stylers vs formats
def format_return_stats(anayltics_df):
    """
    """
    
    formatters = {"Annualized Ret":lambda x: f"{x:.2%}"
                  ,"Annualized Vol":lambda x: f"{x:.2%}"
                  ,"Ret/Vol":lambda x: f"{x:.2f}"
                  ,"Max DD":lambda x: f"{x:.2%}"
                  ,"Ret/Max DD":lambda x: f"{x:.2f}"
                  ,"Max 1M DD":lambda x: f"{x:.2%}"
                  ,"Max 1M DD Date":lambda x: x.to_pydatetime().strftime("%Y-%m-%d")
                  ,"Max 3M DD":lambda x: f"{x:.2%}"
                  ,"Max 3M DD Date":lambda x: x.to_pydatetime().strftime("%Y-%m-%d")
                  ,"Skew":lambda x: f"{x:.2f}"
                  ,"Avg Pos Ret/Avg Neg Ret":lambda x: f"{x:.2f}"
                  ,"Downside Deviation":lambda x: f"{x:.2%}"
                  ,"Sortino Ratio":lambda x: f"{x:.2f}"
                  }
    return formatters 

def format_hedge_metrics(anayltics_df, freq='1M'):
    """
    """
    
    if switch_freq_int(freq) <= 12:
        formatters = {"Benefit Count":lambda x: f"{x:.0f}"
                      ,"Benefit Median":lambda x: f"{x:.2%}"
                      ,"Benefit Mean":lambda x: f"{x:.2%}"
                      ,"Reliabitlity":lambda x: f"{x:.2f}"
                      ,"Convexity Count":lambda x: f"{x:.0f}"
                      ,"Convexity Median":lambda x: f"{x:.2%}"
                      ,"Convexity Mean":lambda x: f"{x:.2%}"
                      ,"Cost Count":lambda x: f"{x:.0f}"
                      ,"Cost Median":lambda x: f"{x:.2%}"
                      ,"Cost Mean":lambda x: f"{x:.2%}"
                 }
    else:
        formatters = {"Benefit Count":lambda x: f"{x:.0f}"
                      ,"Benefit Median":lambda x: f"{x:.2%}"
                      ,"Benefit Mean":lambda x: f"{x:.2%}"
                      ,"Reliabitlity":lambda x: f"{x:.2f}"
                      ,"Convexity Count":lambda x: f"{x:.0f}"
                      ,"Convexity Median":lambda x: f"{x:.2%}"
                      ,"Convexity Mean":lambda x: f"{x:.2%}"
                      ,"Cost Count":lambda x: f"{x:.0f}"
                      ,"Cost Median":lambda x: f"{x:.2%}"
                      ,"Cost Mean":lambda x: f"{x:.2%}" 
                      ,"Decay Days (50% retrace)":lambda x: f"{x:.0f}"
                      ,"Decay Days (25% retrace)":lambda x: f"{x:.0f}"
                      ,"Decay Days (10% retrace)":lambda x: f"{x:.0f}"
             }
    return formatters    

def format_notional_weights(df_weights):
    """
    """
    
    formatters = {"Notional Weights (Billions)":lambda x: f"${x:.2f}"
                  ,"Percentage Weights":lambda x: f"{x:.2%}"
                  ,"Strategy Weights":lambda x: f"{x:.2%}"
                  }
    return formatters 

def format_row_wise(styler, formatter):
    """
    """
    for row, row_formatter in formatter.items():
        row_num = styler.index.get_loc(row)
        for col_num in range(len(styler.columns)):
            styler._display_funcs[(row_num, col_num)] = row_formatter
    return styler

def get_analytics_styler(analytics_dict, stats='return_stats', freq='1M'):
    """
    """
    stats_df = analytics_dict[stats].copy()
    if stats == 'return_stats':
        return_formatter = format_return_stats(stats_df)
        analytics_styler = format_row_wise(stats_df.style, return_formatter)
    elif stats == 'hedge_metrics':
        hedge_formatter = format_hedge_metrics(stats_df, freq)
        analytics_styler = format_row_wise(stats_df.style, hedge_formatter)
    return analytics_styler

def get_notional_styler(df_weights):
    """
    """
    return format_row_wise(df_weights.style,
                           format_notional_weights(df_weights))

def color_neg_pos(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, green for positive, black otherwise.
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
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

def get_returns_styler(df_returns):
    """
    """
    data = df_returns.copy()
    data.index = pd.to_datetime(data.index, format = '%m/%d/%Y').strftime('%Y-%m-%d')
    col_list = data.columns.tolist()
    formatter = {}
    for strat in col_list:
        formatter[strat] = "{:.2%}"
    return data.style.\
        applymap(color_neg_red, subset = pd.IndexSlice[:,col_list]).\
        format(formatter)

def get_hist_styler(df_hist):
    """
    """
    col_list = list(df_hist.columns)[2:]
    formatter = {}
    for strat in col_list:
        formatter[strat] = "{:.2%}"
    return df_hist.style.\
        applymap(color_neg_pos, subset = pd.IndexSlice[:,col_list]).\
        format(formatter)

def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    is_max = s == s.max()
    return ['background-color: yellow' if v else '' for v in is_max]

def get_dollar_ret_styler(dollar_returns):
    """
    """
    data = dollar_returns.copy()
    # data.index = pd.to_datetime(data.index, format = '%m/%d/%Y').strftime('%Y-%m-%d')
    data.index = pd.to_datetime(data.index, format = '%m/%d/%Y').strftime('%Y')
    formatter = {}
    col_list = list(data.columns)
    for strat in col_list:
        formatter[strat] = "${:,.0f}"
    return data.style.\
            applymap(color_neg_pos).\
            apply(highlight_max, subset = pd.IndexSlice[:,col_list[1:]]).\
            format(formatter)
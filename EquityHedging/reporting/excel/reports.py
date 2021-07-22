# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe
"""

import pandas as pd
from ...analytics import summary
from ...analytics import util
from ...analytics.corr_stats import get_corr_rank_data
from ...analytics.historical_selloffs import get_hist_sim_table
from ...datamanager import data_manager as dm
from .import sheets
import os


def get_report_path(report_name):
    """
    Gets the file path where the report will be stored

    Parameters
    ----------
    report_name : String
        Name of report

    Returns
    -------
    string
        File path

    """
    
    cwd = os.getcwd()
    reports_fp = '\\EquityHedging\\reports\\'
    file_name = report_name +'.xlsx'
    return cwd + reports_fp + file_name
    
def get_equity_hedge_report(report_name, returns_dict, equity_bmk, notional_weights=[],include_fi=False, new_strat=False, weighted=False, selloffs=False):
    """
    Generate equity hedge analysis report
    
    Parameters
    ----------
    report_name : string
        Name of report.
    returns_dict : dict
        dictionary of returns containing different frequencies.
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    include_fi : boolean, optional
        Include Fixed Income benchmark. The default is False.
    new_strat : boolean, optional
        Does analysis involve a new strategy. The default is False.
    weighted : boolean, optional
        Include weighgted hedges and weighgted strats. The default is False.
    selloffs : boolean, optional
        Include historical selloffs. The default is False.

    Returns
    -------
    None. An excel report called [report_name].xlsx is created 

    """
    
    #get file path and create excel writer
    file_path = get_report_path(report_name)
    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
    
    #create list of frequencies we want to create the report for
    freq_list = ['Monthly', 'Weekly']
    
    #check length of notional weights is accurate
    notional_weights = util.check_notional(returns_dict['Monthly'], notional_weights)
    
    #loop through frequencies
    for freq in freq_list:
        print("Computing {} Analytics...".format(freq))
        
        #get analytics
        analysis_data = summary.get_analysis_sheet_data(returns_dict[freq], notional_weights,
                                                          include_fi,new_strat,
                                                          dm.switch_string_freq(freq), weighted)
        df_weighted_returns = summary.get_weighted_data(returns_dict[freq],notional_weights,
                                                          include_fi,new_strat)
        
        corr_sheet =  freq + ' Analysis'
        return_sheet = freq + ' Historical Returns'
        spaces = 3
        
        #create sheets
        sheets.set_analysis_sheet(writer,analysis_data, corr_sheet, spaces)
        sheets.set_hist_return_sheet(writer,df_weighted_returns, return_sheet)
    
    #get historical selloffs data if selloffs == True
    if selloffs:
        print("Computing Historical SellOffs...")
        
        #get daily returns
        daily_returns = returns_dict['Daily'].copy()
        
        #compute historical selloffs
        hist_df = summary.get_hist_sim_table(daily_returns, notional_weights, weighted)
        
        #create sheets
        sheets.set_hist_sheet(writer, hist_df)
        sheets.set_hist_return_sheet(writer, daily_returns, 'Daily Historical Returns')

    #Get Normalized Hedge Metrics 
    print("Normalizing Hedge Metrics...")
    
    #get weekly returns
    weekly_returns = returns_dict['Weekly'].copy()
    
    #Compute hedge metrics and normalize them
    normal_data = summary.get_normal_sheet_data(weekly_returns, equity_bmk, notional_weights, weighted, weighted_hedge=True)
   
    #Create Sheet
    sheets.set_normal_sheet(writer, normal_data, 'Hedge Metric Framework', spaces)

    print_report_info(report_name, file_path)
    writer.save()

def get_corr_rank_report(report_name, df_returns, buckets, notional_weights=[],include_fi=False):
    """
    """
    
    file_path = get_report_path(report_name)
    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
    
    corr_pack = get_corr_rank_data(df_returns, buckets, notional_weights,include_fi)
    dates = dm.get_min_max_dates(df_returns)
    
    #create excel report
    sheets.set_corr_rank_sheet(writer,corr_pack,dates)
    sheets.set_hist_return_sheet(writer,df_returns, 'Returns')
    
    print_report_info(report_name, file_path)
    writer.save()

def get_rolling_cum_ret_report(report_name, df_returns, freq, notional_weights):
    """
    """
    
    file_path = get_report_path(report_name)
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    
    rolling_cum_dict = summary.get_rolling_cum_data(df_returns, freq,notional_weights)
    
    sheets.set_hist_return_sheet(writer, rolling_cum_dict['3M'], 'Rolling Cum Returns_3 Months')
    sheets.set_hist_return_sheet(writer, rolling_cum_dict['6M'], 'Rolling Cum Returns_6 Months')
    sheets.set_hist_return_sheet(writer, rolling_cum_dict['1Y'], 'Rolling Cum Returns_1 Year')
    
    print_report_info(report_name, file_path)
    writer.save()

def generate_strat_report(report_name, returns_dict, selloffs=False):
    """
    Generate strat analysis report
    
    Parameters
    ----------
    report_name : string
        Name of report.
    returns_dict : dict
        dictionary of returns containing different frequencies.
    selloffs : boolean, optional
        Include historical selloffs. The default is False.

    Returns
    -------
    None. An excel report called [report_name].xlsx is created 

    """
    
    #get file path and create excel writer
    file_path = get_report_path(report_name)
    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
    
    #create list of frequencies we want to create the report for
    freq_list = ['Monthly', 'Weekly']
    
    #loop through frequencies
    for freq in freq_list:
        print("Computing {} Analytics...".format(freq))
        
        #get analytics
        analysis_data = summary.get_analysis_sheet_data(returns_dict[freq], 
                                                        freq=dm.switch_string_freq(freq))

        corr_sheet =  freq + ' Analysis'
        return_sheet = freq + ' Historical Returns'
        spaces = 3
        
        #create sheets
        sheets.set_analysis_sheet(writer,analysis_data, corr_sheet, spaces)
        sheets.set_hist_return_sheet(writer,returns_dict[freq], return_sheet)

    if selloffs:
        print("Computing Historical SellOffs...")
        
        #get daily returns
        daily_returns = returns_dict['Daily'].copy()
        
        #compute historical selloffs
        hist_df = get_hist_sim_table(daily_returns)
        
        #create sheets
        sheets.set_hist_sheet(writer, hist_df)
        sheets.set_hist_return_sheet(writer, daily_returns, 'Daily Historical Returns')
    #TODO: add normalized data sheet    
    print_report_info(report_name, file_path)
    writer.save()

def generate_hs_report(report_name, returns_dict, notional_weights=[], weighted=False):
    """
    Generate historical selloffs report
    
    Parameters
    ----------
    report_name : string
        Name of report.
    returns_dict : dict
        dictionary of returns containing different frequencies.
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    weighted : boolean, optional
        Include weighgted hedges and weighgted strats. The default is False.
    
    Returns
    -------
    None. An excel report called [report_name].xlsx is created 

    """
    
    #get file path and create excel writer
    file_path = get_report_path(report_name)
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

    print("Computing Historical SellOffs...")
    
    #get daily returns
    daily_returns = returns_dict['Daily'].copy()
    
    #compute historical selloffs
    hist_df = get_hist_sim_table(daily_returns, notional_weights, weighted)
    
    #create sheets
    sheets.set_hist_sheet(writer, hist_df)
    sheets.set_hist_return_sheet(writer, daily_returns, 'Daily Historical Returns')
        
    writer.save()
def get_returns_report(report_name, returns_dict):
    """
    Generates historical returns spreadsheet containing returns for different frequencies

    Parameters
    ----------
    report_name : string
        Name of report.
    returns_dict : dict
        dictionary of returns containing different frequencies.
    
    Returns
    -------
    None. An excel report called [report_name].xlsx is created 

    """
    #get file path and create excel writer
    file_path = get_report_path(report_name)
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    
    #loop through dictionary to create returns spreadsheet
    for key in returns_dict:
        print("Writing {} Historical Returns sheet...".format(key))
        sheets.set_hist_return_sheet(writer, returns_dict[key], key)
    
    #save file
    print_report_info(report_name, file_path)
    writer.save()

def print_report_info(report_name, file_path):
    """
    Print name of report and location

    Parameters
    ----------
    report_name : string
        Name of report.
    file_path : string
        flie location.

    Returns
    -------
    None.

    """
    folder_location = file_path.replace(report_name+'.xlsx', '')
    print('"{}.xlsx" report generated in "{}" folder'.format(report_name,folder_location))
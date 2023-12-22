# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe
"""

import pandas as pd
from ...analytics import summary
from ...analytics import util
from ...analytics import drawdowns as dd
from ...analytics.corr_stats import get_corr_rank_data
# from ...analytics.historical_selloffs import get_hist_sim_table
from ...datamanager import data_manager as dm
from .import sheets
from .import new_sheets
import os


def get_filepath_path(report_name, data_file=False):
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

    fp = '\\EquityHedging\\data\\returns_data\\' if data_file else '\\EquityHedging\\reports\\'
    file_name = report_name +'.xlsx'
    return cwd + fp + file_name
    
def get_equity_hedge_report(report_name, returns_dict, notional_weights=[],
                            include_fi=False, new_strat=False, weighted=False, selloffs=False, freq_list=['Monthly', 'Weekly']):
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
    file_path = get_filepath_path(report_name)
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
        
        #create sheets
        
        sheets.set_analysis_sheet(writer,analysis_data, corr_sheet)
        #new_sheets.AnalysisSheet(writer,analysis_data, corr_sheet)
        sheets.set_hist_return_sheet(writer,df_weighted_returns, return_sheet)
        #new_sheets.setHistReturnSheet(writer,df_weighted_returns, return_sheet)
        
    #get historical selloffs data if selloffs == True
    if selloffs:
        print("Computing Historical SellOffs...")
        
        #get daily returns
        try:
            daily_returns = returns_dict['Daily'].copy()
            hs_notional_weights = notional_weights.copy()
            
            if include_fi:
                col_list = list(daily_returns.columns)
                
                #remove fi weight
                if len(col_list) != len(hs_notional_weights):
                    hs_notional_weights.pop(1)
                    
            #compute historical selloffs
            hist_df = summary.get_hist_sim_table(daily_returns, hs_notional_weights, weighted)
            
            #create sheets
            sheets.set_hist_sheet(writer, hist_df)
            sheets.set_hist_return_sheet(writer, daily_returns)
            #new_sheets.setHistSheet(writer,hist_df)
            #new_sheets.setHistReturnSheet(writer, daily_returns)
        except KeyError:
            print('Skipping Historical SellOffs, no daily data in returns dictionary')
            pass
    
    #Get Normalized Hedge Metrics 
    # if 'Weekly' in returns_dict.keys():
    #     print("Computing Normalized Hedge Metrics...")
        
    #     #get weekly returns
    #     weekly_returns = returns_dict['Weekly'].copy()
        
    #     #Compute hedge metrics and normalize them
    #     normal_data = summary.get_normal_sheet_data(weekly_returns, notional_weights, drop_bmk=True, weighted=False)
       
    #     #Create Sheet
    #     sheets.set_normal_sheet(writer, normal_data)
        
    grouped_data_dict = summary.get_grouped_data(returns_dict, notional_weights, weighted = True)
    # quintile_df = summary.get_grouped_data(returns_dict, notional_weights, weighted = True, group = 'Quintile')
    # decile_df = summary.get_grouped_data(returns_dict, notional_weights, weighted = True, group = 'Decile')

    sheets.set_grouped_data_sheet(writer, grouped_data_dict)
    #new_sheets.setGroupedDataSheet(writer, grouped_data_dict)
    print_report_info(report_name, file_path)
    writer.save()

def get_alts_report(report_name,returns_dict,mv_dict={},include_fi=True,freq='1M',include_bmk=False,
                     df_bmk = dm.pd.DataFrame(), bmk_dict={}):
    """
    Generate alts report
    
    Parameters
    ----------
    report_name : string
        Name of report.
    returns_dict : dict
        dictionary of returns containing different frequencies.
    include_fi : boolean, optional
        Include Fixed Income benchmark. The default is False.
    
    Returns
    -------
    None. An excel report called [report_name].xlsx is created 

    """
    
    #get file path and create excel writer
    file_path = get_filepath_path(report_name)
    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
    
    
    #loop through frequencies
    for key in returns_dict:
        print("Computing {} Analytics...".format(key))
        #get analytics
        returns_df = returns_dict[key].copy()
        try:
            df_mv = mv_dict[key].copy()
        except KeyError:
            df_mv = pd.DataFrame()
        returns_df.dropna(axis=1, inplace=True)
        df_mv.dropna(axis=1, inplace=True)
        analysis_data = summary.get_alts_data(returns_df,df_mv,include_fi=include_fi,freq=freq,
                                              include_bmk=include_bmk,df_bmk = df_bmk, bmk_dict=bmk_dict)
        
        #create sheets
        sheets.set_corr_sheet(writer,analysis_data['corr'],sheet_name='Correlation Analysis ({})'.format(key), include_fi=include_fi)
        sheets.set_ret_stat_sheet(writer,analysis_data['ret_stat_df'],sheet_name='Returns Statistics ({})'.format(key), include_fi=include_fi, include_bmk=include_bmk)
        
    return_sheet = dm.switch_freq_string(freq) + ' Historical Returns'
    sheets.set_hist_return_sheet(writer,returns_dict['Full'], return_sheet)
    sheets.set_mtd_ytd_sheet_1(writer, summary.all_strat_month_ret_table(returns_dict['Full'], include_fi=include_fi))
    print_report_info(report_name, file_path)
    writer.save()

def get_fi_report(report_name, returns_dict, freq='1M'):
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
    file_path = get_filepath_path(report_name)
    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
    
    #loop through frequencies
    for key in returns_dict:
        print("Computing {} Analytics...".format(key))
        #get analytics
        returns_df = returns_dict[key].copy()
        analysis_df = summary.get_fi_data(returns_df,freq=freq)
        
        #create sheets
        sheets.set_ret_stat_sheet_fi(writer,analysis_df,sheet_name='Returns Statistics ({})'.format(key))
        
        
    
    #MTD-YTD sheet 
    strat_sheet = 'MTD-YTD-ITD'
    df_list = []
    for col in returns_dict['Full'].columns:
        df_list.append(dm.month_ret_table(returns_dict['Full'], col))
        
    sheets.set_mtd_ytd_sheet_1(writer, {'df_list': df_list,'title_list': list(returns_dict['Full'].columns)}, strat_sheet)
    
    #historical return sheet
    return_sheet = dm.switch_freq_string(freq) + ' Historical Returns'
    sheets.set_hist_return_sheet(writer,returns_dict['Full'], return_sheet)
    
    print_report_info(report_name, file_path)
    writer.save()

def get_strat_fi_report(report_name, returns_dict,freq='1M'):
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
    file_path = get_filepath_path(report_name)
    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
    
    analysis_df = pd.DataFrame()
    col_list_1 = list(returns_dict.keys())
    col_list_1[0] = 'Since Inception'
    col_list_2 = list(returns_dict['Full'].columns)
    header = pd.MultiIndex.from_product([col_list_1,col_list_2])
    
    #loop through frequencies
    for key in returns_dict:
        print("Computing {} Analytics...".format(key))
        #get analytics
        analysis_data = summary.get_fi_data(returns_dict[key],freq)
        analysis_data.columns = ['bench_{}'.format(key), 'port_{}'.format(key)]
        analysis_df = dm.merge_data_frames(analysis_df, analysis_data,False)
        
    analysis_df.columns = header
    
    #returns stat sheet
    sheets.set_ret_stat_sheet_fi_1(writer,analysis_df)
    
    #MTD-YTD sheet 
    strat_sheet = 'MTD-YTD-ITD'
    df_list = []
    for col in returns_dict['Full'].columns:
        df_list.append(dm.month_ret_table(returns_dict['Full'], col))
        
    sheets.set_mtd_ytd_sheet_1(writer, {'df_list': df_list,'title_list': list(returns_dict['Full'].columns)}, strat_sheet)
   
   
    #historical return sheet
    return_sheet = dm.switch_freq_string(freq) + ' Historical Returns'
    sheets.set_hist_return_sheet(writer,returns_dict['Full'], return_sheet, freeze=False)
    
    print_report_info(report_name, file_path)
    writer.save()


def get_strat_alts_report(report_name, returns_dict, include_fi=True, freq='1M'):
    """
    Generate strats_alt_report
    
    Parameters
    ----------
    report_name : string
        Name of report.
    returns_dict : dict
        dictionary of returns containing different frequencies.
    include_fi : boolean, optional
        Include Fixed Income benchmark. The default is False.
    
    Returns
    -------
    None. An excel report called [report_name].xlsx is created 

    """
    
    #get file path and create excel writer
    file_path = get_filepath_path(report_name)
    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
    
    analysis_df = pd.DataFrame()
    col_list_1 = list(returns_dict.keys())
    col_list_1[0] = 'Since Inception'
    skip = 2 if include_fi else 1
    col_list_2 = returns_dict['Full'].columns[skip:].tolist()
    header = pd.MultiIndex.from_product([col_list_1,col_list_2])
    
    #loop through frequencies
    for key in returns_dict:
        print("Computing {} Analytics...".format(key))
        #get analytics
        analysis_data = summary.get_alts_strat_data(returns_dict[key],include_fi=include_fi,freq=freq)
        analysis_data.columns = ['port_{}'.format(key), 'bench_{}'.format(key)]
        analysis_df = dm.merge_data_frames(analysis_df, analysis_data,drop_na=False, how='right')
        
    analysis_df.columns = header
    
    #returns stat sheet
    sheets.set_ret_stat_sheet_1(writer,analysis_df,sheet_name='Returns Statistics', include_fi=include_fi)
    
    #worst_dd sheet
    sheets.set_dd_stat_sheet(writer, dd.get_worst_drawdowns(returns_dict['Full'][[col_list_2[0]]], recovery=True), 'Drawdown Statistics')
    #index sheet
    sheets.set_ratio_sheet(writer, dm.get_prices_df(returns_dict['Full'][col_list_2]), 'Index')
    
    #MTD-YTD sheet 
    # strat_sheet = 'MTD-YTD'
    # sheets.set_mtd_ytd_sheet(writer, dm.month_ret_table(returns_dict['Full'], col_list_2[0]))
    sheets.set_mtd_ytd_sheet_1(writer, summary.all_strat_month_ret_table(returns_dict['Full'], include_fi=include_fi))
    
    #historical return sheet
    return_sheet = dm.switch_freq_string(freq) + ' Historical Returns'
    sheets.set_hist_return_sheet(writer,returns_dict['Full'][col_list_2], return_sheet)
    
    print_report_info(report_name, file_path)
    writer.save()

def get_corr_rank_report(report_name, df_returns, buckets, notional_weights=[],include_fi=False):
    """
    """
    
    file_path = get_filepath_path(report_name)
    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
    
    corr_pack = get_corr_rank_data(df_returns, buckets, notional_weights,include_fi)
    dates = dm.get_min_max_dates(df_returns)
    corr_data_dict = {'df_list':[], 'title_list':[]}
    
    #unpack corr_pack
    for i in corr_pack:
        corr_data_dict['df_list'].append(corr_pack[str(i)][0])
        corr_data_dict['title_list'].append(corr_pack[str(i)][1])
        
    
    #create excel report
    sheets.set_corr_rank_sheet(writer,corr_data_dict,dates)
    sheets.set_hist_return_sheet(writer,df_returns, 'Returns')
    
    print_report_info(report_name, file_path)
    writer.save()

def get_rolling_cum_ret_report(report_name, df_returns, freq, notional_weights):
    """
    """
    
    file_path = get_filepath_path(report_name)
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    
    rolling_cum_dict = summary.get_rolling_cum_data(df_returns, freq,notional_weights)
    
    sheets.set_hist_return_sheet(writer, rolling_cum_dict['3M'], 'Rolling Cum Returns_3 Months')
    sheets.set_hist_return_sheet(writer, rolling_cum_dict['6M'], 'Rolling Cum Returns_6 Months')
    sheets.set_hist_return_sheet(writer, rolling_cum_dict['1Y'], 'Rolling Cum Returns_1 Year')
    
    print_report_info(report_name, file_path)
    writer.save()

def generate_strat_report(report_name, returns_dict, selloffs=False, freq_list=['Monthly', 'Weekly'], include_fi=False):
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
    file_path = get_filepath_path(report_name)
    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
    
    #loop through frequencies
    for freq in freq_list:
        print("Computing {} Analytics...".format(freq))
        
        #get analytics
        analysis_data = summary.get_analysis_sheet_data(returns_dict[freq], 
                                                        freq=dm.switch_string_freq(freq),include_fi=include_fi)

        corr_sheet =  freq + ' Analysis'
        return_sheet = freq + ' Historical Returns'
        spaces = 3
        
        #create sheets
        sheets.set_analysis_sheet(writer,analysis_data, corr_sheet, spaces, include_fi)
        sheets.set_hist_return_sheet(writer,returns_dict[freq], return_sheet)

    if selloffs:
        print("Computing Historical SellOffs...")
        
        #get daily returns
        try:
            daily_returns = returns_dict['Daily'].copy()
        
            #compute historical selloffs
            hist_df = summary.get_hist_sim_table(daily_returns)
            
            #create sheets
            sheets.set_hist_sheet(writer, hist_df)
            sheets.set_hist_return_sheet(writer, daily_returns)
        except KeyError():
            print('Skipping Historical SellOffs, no daily data in returns dictionary')
            pass
    
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
    file_path = get_filepath_path(report_name)
    try:
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    
    
        print("Computing Historical SellOffs...")
        
        #get daily returns
        try:
            daily_returns = returns_dict['Daily'].copy()
        
            #TODO: change to get_hist_data    
            #compute historical selloffs
            hist_df = summary.get_hist_sim_table(daily_returns, notional_weights, weighted)
            
            #create sheets
            sheets.set_hist_sheet(writer, hist_df)
            sheets.set_hist_return_sheet(writer, daily_returns)
                
            writer.save()
        except KeyError:
            print('Skipping Historical SellOffs, no daily data in returns dictionary')
            pass
    except PermissionError:
        print('Permission denied: {}\nMake sure {} file is not opened'.format(file_path, report_name))
        pass

def get_returns_report(report_name, returns_dict, data_file = False):
    """
    Generates excel file containing historical returns for different frequencies

    Parameters
    ----------
    report_name : string
        Name of report.
    data_dict : dict
        Dictionary containing returns of different frequencies.
    data_file : boolean, optional
        Boolean to determine if excel file belongs in data folder or reports folder. The default is True.

    Returns
    -------
    None. An excel report called [report_name].xlsx is created
    """
    #get file path and create excel writer
    file_path = get_filepath_path(report_name, data_file)
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    
    #loop through dictionary to create returns spreadsheet
    for key in returns_dict:
        print("Writing {} Historical Returns sheet...".format(key))
        if len(key) > 31:
            diff = len(key) - 31
            sheets.set_hist_return_sheet(writer, returns_dict[key], key[:-diff])
        else:
            sheets.set_hist_return_sheet(writer, returns_dict[key], key)
    
    #save file
    print_report_info(report_name, file_path)
    writer.save()

def get_returns_report_1(report_name, returns_dict, data_file = False):
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
    file_path = get_filepath_path(report_name, data_file)
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    
    #loop through dictionary to create returns spreadsheet
    for key in returns_dict:
        print("Writing {} Historical Returns sheet...".format(key))
        if len(key) > 31:
            diff = len(key) - 31
            new_sheets.setHistReturnSheet(writer, returns_dict[key],key[:-diff])
            
        else:
            new_sheets.setHistReturnSheet(writer, returns_dict[key],key)
            
    #save file
    print_report_info(report_name, file_path)
    writer.save()

def get_ret_mv_report(report_name, nexen_dict, data_file = True):
    file_path = get_filepath_path(report_name, data_file)
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    print("Writing Monthly Returns sheet...")
    sheets.set_hist_return_sheet(writer, nexen_dict['returns'], 'returns')
    print("Writing Monthly Market Values sheet...")
    sheets.set_mv_sheet(writer, nexen_dict['market_values'], 'market_values')

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
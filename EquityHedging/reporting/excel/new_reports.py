# -*- coding: utf-8 -*-
"""
Created on Fri July  7 2023

@author: Powis Forjoe, Maddie Choi, Devang Ajmera
"""

import pandas as pd
from ...analytics import summary
from ...analytics import util
from ...analytics.corr_stats import get_corr_rank_data
from ...analytics.historical_selloffs import get_hist_sim_table
from ...datamanager import data_manager as dm
from .import new_sheets
import os

def get_filepath_path(report_name, data_file=False):
    """
    Gets the file path where the report will be stored

    Parameters
    ----------
    report_name : String
        Name of report
    data_file : boolean, optional
        Boolean to determine if excel file belongs in data folder or not. The default is False.
    Returns
    -------
    string
        File path

    """
    
    cwd = os.getcwd()
    
    fp = '\\EquityHedging\\data\\returns_data\\' if data_file else '\\EquityHedging\\reports\\'
    file_name = report_name +'.xlsx'
    return cwd + fp + file_name

def print_report_info(report_name, file_path):
    """
    Print name of report and location

    Parameters
    ----------
    report_name : string
        Name of report.
    file_path : string
        File location.

    Returns
    -------
    None.

    """
    folder_location = file_path.replace(report_name+'.xlsx', '')
    print('"{}.xlsx" report generated in "{}" folder'.format(report_name,folder_location))

class setReport():
    def __init__(self, report_name, data_file=False):
        """
        Setup excel report

        Parameters
        ----------
        report_name : string
            Name of excel report.
        data_file : boolean, optional
            Boolean to determine if excel file belongs in data folder or not. The default is False.

        Returns
        -------
        None.

        """
        self.report_name = report_name
        self.data_file = data_file
        self.file_path = get_filepath_path(self.report_name, self.data_file)
        self.writer = pd.ExcelWriter(self.file_path, engine='xlsxwriter')

class getReturnsReport(setReport):
    def __init__(self, report_name, data_dict, data_file=True):
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
        super().__init__(report_name, data_file)
        self.data_dict = data_dict
        self.generate_report()
        print_report_info(self.report_name, self.file_path)
        self.writer.close()
        
    def generate_report(self):
        #loop through dictionary to create returns spreadsheets
        for key in self.data_dict:
            print("Writing {} Historical Returns sheet...".format(key))
            if len(key) > 31:
                diff = len(key) - 31
                new_sheets.setHistReturnSheet(self.writer, self.data_dict[key],key[:-diff])
                
            else:
                new_sheets.setHistReturnSheet(self.writer, self.data_dict[key],key)

class getRetMVReport(getReturnsReport):
    def __init__(self, report_name, data_dict, data_file=True):
        """
        Generates an excel file containing monthly returns and market values

        Parameters
        ----------
        report_name : string
            Name of report.
        data_dict : dict
            Dictionary containing returns and market_values.
        data_file : boolean, optional
            Boolean to determine if excel file belongs in data folder or reports folder. The default is True.

        Returns
        -------
        None. An excel report called [report_name].xlsx is created
        """
        super().__init__(report_name, data_dict, data_file)
                
    def generate_report(self):
        print("Writing Monthly Returns sheet...")
        new_sheets.setHistReturnSheet(self.writer, self.data_dict['returns'], 'returns')
        print("Writing Monthly Market Values sheet...")
        new_sheets.setMVSheet(self.writer, self.data_dict['market_values'])        
        
class generateHSReport(getReturnsReport):
    def __init__(self, report_name, returns_dict, notional_weights=[], weighted=False):
        """
        Generate historical selloffs report

        Parameters
        ----------
        report_name : string
            Name of report.
        returns_dict : dict
            Dictionary of returns containing different frequencies.
        notional_weights : list, optional
            Notional weights of strategies. The default is [].
        weighted : boolean, optional
            Include weighted hedges and weighted strats. The default is False.

        Returns
        -------
        None. An excel report called [report_name].xlsx is created
        """
        self.data_dict = returns_dict
        self.notional_weights = notional_weights
        self.weighted = weighted
        self.data_file = False 
        super().__init__(report_name, returns_dict, self.data_file)
        
    def generate_report(self):
        self.generate_selloffs_sheets()
        
    def generate_selloffs_sheets(self):
        print("Computing Historical SellOffs...")

        # Get daily returns
        try:
            daily_returns = self.data_dict['Daily'].copy()

            # Compute historical selloffs
            self.hist_df = get_hist_sim_table(daily_returns, self.notional_weights, self.weighted)

            # Create sheets
            new_sheets.setHistSheet(self.writer, self.hist_df)
            new_sheets.setHistReturnSheet(self.writer, daily_returns, 'Daily')
            
        except KeyError:
            print('Skipping Historical SellOffs, no daily data in returns dictionary')
            pass
        
class generateEquityHedgeReport(generateHSReport):
    def __init__(self, report_name, returns_dict, notional_weights=[], include_fi=False,
                 new_strat=False, weighted=False, selloffs=False):
        """
        Generate equity hedge analysis report

        Parameters
        ----------
        report_name : string
            Name of report.
        returns_dict : dict
            Dictionary of returns containing different frequencies.
        notional_weights : list, optional
            Notional weights of strategies. The default is [].
        include_fi : boolean, optional
            Include Fixed Income benchmark. The default is False.
        new_strat : boolean, optional
            Does analysis involve a new strategy. The default is False.
        weighted : boolean, optional
            Include weighted hedges and weighted strats. The default is False.
        selloffs : boolean, optional
            Include historical selloffs. The default is False.

        Returns
        -------
        None. An excel report called [report_name].xlsx is created
        """
        self.data_dict = returns_dict
        self.notional_weights = notional_weights
        self.include_fi = include_fi
        self.new_strat = new_strat
        self.weighted = weighted
        self.selloffs = selloffs
        super().__init__(report_name, returns_dict)

    def generate_report(self):
        self.generate_analysis_sheets()
       
        if self.selloffs:
            self.generate_selloffs_sheets()
            
        # Generate Grouped Data Sheet
        self.grouped_data_dict = summary.get_grouped_data(self.data_dict, self.notional_weights, weighted=True)
        new_sheets.setGroupedDataSheet(self.writer, self.grouped_data_dict)
        
    def generate_analysis_sheets(self):
        # Create list of frequencies we want to create the report for
        self.freq_list = ['Monthly', 'Weekly']

        # Check length of notional weights is accurate
        self.notional_weights = util.check_notional(self.data_dict['Monthly'], self.notional_weights)

        # Loop through frequencies
        for freq in self.freq_list:
            try:
                print("Computing {} Analytics...".format(freq))
    
                # Get analytics
                self.analysis_data = summary.get_analysis_sheet_data(self.data_dict[freq], self.notional_weights,
                                                                self.include_fi, self.new_strat,
                                                                dm.switch_string_freq(freq), self.weighted)
                self.df_weighted_returns = summary.get_weighted_data(self.data_dict[freq], self.notional_weights,
                                                                self.include_fi, self.new_strat)
    
                self.corr_sheet = freq + ' Analysis'
                self.return_sheet = freq + ' Historical Returns'
    
                # Create sheets
                new_sheets.AnalysisSheet(self.writer, self.analysis_data, self.corr_sheet)
                new_sheets.setHistReturnSheet(self.writer, self.df_weighted_returns, self.return_sheet)
            except KeyError:
               print(f"Skipping {freq} , no {freq} data in returns dictionary")
               pass

class generateStratReport(generateEquityHedgeReport):
    def __init__(self, report_name, returns_dict, selloffs=False):
        """
        Generate strat analysis report

        Parameters
        ----------
        report_name : string
            Name of report.
        returns_dict : dict
            Dictionary of returns containing different frequencies.
        selloffs : boolean, optional
            Include historical selloffs. The default is False.

        Returns
        -------
        None. An excel report called [report_name].xlsx is created
        """
        
        super().__init__(report_name, returns_dict,selloffs=selloffs)

    def generate_report(self):
        self.generate_analysis_sheets()

        if self.selloffs:
           self.generate_selloffs_sheet()
           
class generateCorrRankReport(getReturnsReport):
    def __init__(self, report_name, df_returns, buckets, notional_weights=[], include_fi=False):
        """
        Generate correlation rank analysis report

        Parameters
        ----------
        report_name : string
            Name of report.
        df_returns : DataFrame
            DataFrame containing returns data.
        buckets : int
            Number of buckets for the correlation rank analysis.
        notional_weights : list, optional
            Notional weights of strategies. The default is [].
        include_fi : boolean, optional
            Include Fixed Income benchmark. The default is False.

        Returns
        -------
        None. An excel report called [report_name].xlsx is created
        """
        self.buckets = buckets
        self.notional_weights = notional_weights
        self.include_fi = include_fi
        self.data_file = False
        super().__init__(report_name, {'Returns': df_returns}, self.data_file)
        
    def generate_report(self):
        
        # Get correlation rank data
        self.corr_pack = get_corr_rank_data(self.data_dict['Returns'], self.buckets, self.notional_weights, self.include_fi)
        self.dates = dm.get_min_max_dates(self.data_dict['Returns'])
        self.corr_data_dict = {'df_list': [], 'title_list': []}

        # Unpack corr_pack
        for i in self.corr_pack:
            self.corr_data_dict['df_list'].append(self.corr_pack[str(i)][0])
            self.corr_data_dict['title_list'].append(self.corr_pack[str(i)][1])

        # Create Excel report
        new_sheets.setCorrRankSheet(self.writer, self.corr_data_dict, self.dates)
        new_sheets.setHistReturnSheet(self.writer, self.data_dict['Returns'], 'Returns')
      
class generateRollingCumRetReport(getReturnsReport):
    def __init__(self, report_name, df_returns, freq, notional_weights):
        """
        Generate rolling cumulative return analysis report

        Parameters
        ----------
        report_name : string
            Name of report.
        df_returns : DataFrame
            DataFrame containing returns data.
        freq : string
            Frequency for rolling cumulative returns (e.g., '3M', '6M', '1Y').
        notional_weights : list
            Notional weights of strategies.

        Returns
        -------
        None. An excel report called [report_name].xlsx is created
        """
        self.freq = freq
        self.notional_weights = notional_weights
        self.generate_report()
        self.data_file = False
        super().__init__(report_name, {'Returns': df_returns},self.data_file)

    def generate_report(self):
        # Get rolling cumulative return data
        self.rolling_cum_dict = summary.get_rolling_cum_data(self.data_dict['Returns'], self.freq, self.notional_weights)

        # Create Excel reports
        new_sheets.setHistReturnSheet(self.writer, self.rolling_cum_dict['3M'], 'Rolling Cum Returns_3 Months')
        new_sheets.setHistReturnSheet(self.writer, self.rolling_cum_dict['6M'], 'Rolling Cum Returns_6 Months')
        new_sheets.setHistReturnSheet(self.writer, self.rolling_cum_dict['1Y'], 'Rolling Cum Returns_1 Year')
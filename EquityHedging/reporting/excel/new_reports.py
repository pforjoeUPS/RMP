# -*- coding: utf-8 -*-
"""
Created on Fri July  7 2023

@author: Powis Forjoe, Maddie Choi, Devang Ajmera
"""

import os

import pandas as pd

from . import new_sheets
from ...analytics import drawdowns as dd
from ...analytics import returns_analytics as rsa
from ...analytics import summary
from ...analytics import summary_new
from ...analytics import util_new
from ...analytics.corr_stats_new import get_corr_rank_data
from ...analytics.historical_selloffs_new import get_hist_sim_table
from ...datamanager import data_manager_new as dm


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

class setReport:
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
        self.report_name = None
        self.data_file = data_file
        self.file_path = None
        self.rename_report(report_name)

    def rename_report(self, report_name):
        self.report_name = report_name
        self.file_path = get_filepath_path(self.report_name, self.data_file)

class returnsReport(setReport):
    def __init__(self, report_name, data, data_file=True):
        """
        Generates excel file containing historical returns for different frequencies

        Parameters
        ----------
        report_name : string
            Name of report.
        data : dict/dataframe
            Dictionary containing returns of different frequencies.
        data_file : boolean, optional
            Boolean to determine if excel file belongs in data folder or reports folder. The default is True.

        Returns
        -------
        None. An excel report called [report_name].xlsx is created
        """
        super().__init__(report_name, data_file)
        self.writer = None
        self.data = data
        # self.generate_report()
        # print_report_info(self.report_name, self.file_path)
        # self.writer.save()

    def run_report(self, report_name):
        if report_name != self.report_name:
            self.rename_report(report_name)
        self.writer = pd.ExcelWriter(self.file_path, engine='xlsxwriter')
        self.generate_report()
        print_report_info(self.report_name, self.file_path)
        self.writer.save()

    def generate_report(self):
        #loop through dictionary to create returns spreadsheets
        for data_key in self.data:
            print("Writing {} Historical Returns sheet...".format(data_key))
            diff = -(len(data_key) - 31) if len(data_key) > 31 else None
            new_sheets.histReturnSheet(writer=self.writer, returns_df=self.data[data_key], sheet_name=data_key[:diff]).create_sheet()
                
class returnMktValueReport(returnsReport):
    def __init__(self, report_name, data, data_file=True):
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
        super().__init__(report_name, data, data_file)
                
    def generate_report(self):
        print("Writing Monthly Returns sheet...")
        new_sheets.histReturnSheet(writer=self.writer, returns_df=self.data['returns'], sheet_name='returns').create_sheet()
        print("Writing Monthly Market Values sheet...")
        new_sheets.mktValueSheet(self.writer, self.data['market_values']).create_sheet()
        

class histSelloffReport(returnsReport):
    def __init__(self, report_name, data_handler, weighted=False, new_strat=False):
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
        self.weighted = weighted
        self.new_strat = new_strat
        self.report_analytic = self.get_report_analytic(data_handler)
        self.data = self.get_report_data(data_handler)

        super().__init__(report_name=report_name, data=self.data, data_file=False)

    def get_report_data(self, data_handler):
        self.report_analytic.get_reporting_data()
        return self.report_analytic.reporting_data

    def get_report_analytic(self, data_handler):
        return summary_new.histSellOffReportAnalytic(data_handler, self.new_strat, self.weighted)

    def generate_report(self):
        self.generate_selloffs_sheets()

    def generate_selloffs_sheets(self):
        # Create sheets
        new_sheets.histSelloffSheet(self.writer, self.data['selloffs']).create_sheet()
        new_sheets.histReturnSheet(self.writer, self.data['returns']['Daily'], sheet_name='Daily Historical Returns').create_sheet()

class equityHedgeReport(histSelloffReport):
    def __init__(self, report_name, data_handler, new_strat=False, weighted=False, selloffs=False):


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
        self.selloffs = selloffs
        super().__init__(report_name, data_handler, weighted, new_strat)

    def get_report_analytic(self, data_handler):
        return summary_new.eqHedgeReportAnalytic(data_handler, new_strat=self.new_strat, weighted=self.weighted,
                                                 selloffs=self.selloffs)

    def generate_report(self):
        self.generate_analysis_sheets()
        self.generate_quantile_sheet()
        if self.selloffs:
            if 'selloffs' in self.data:
                self.generate_selloffs_sheets()
            else:
                self.data['selloffs'] = self.compute_selloffs()
                self.generate_selloffs_sheets()

    def compute_selloffs(self):
        self.report_analytic.get_hist_selloff()
        self.data['returns']['Daily'] = self.report_analytic.returns_dict['Daily'].copy()
        return self.report_analytic.historical_selloff_data

    def generate_quantile_sheet(self):
        for mkt in self.data['quantiles']:
            new_sheets.quantileDataSheet(self.writer, self.data['quantiles'][mkt], sheet_name=f'{mkt} Quantile Data').create_sheet()

    def generate_analysis_sheets(self):
        for freq in self.data['analytics']:
            new_sheets.analysisSheet(self.writer, self.data['analytics'][freq], sheet_name=f'{freq} Analysis').create_sheet()
            new_sheets.histReturnSheet(self.writer, self.data['returns'][freq], sheet_name=f'{freq} Historical Returns').create_sheet()


class stratReport(equityHedgeReport):
    def __init__(self, report_name, data_handler, selloffs=False):
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

        super().__init__(report_name, data_handler, new_strat=False, weighted=False, selloffs=selloffs)

    def generate_report(self):
        self.generate_analysis_sheets()

        if self.selloffs:
            self.generate_selloffs_sheet()


class corrRankReport(returnsReport):
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
        new_sheets.setCorrRankSheet(self.writer, self.corr_data_dict, self.dates).create_sheets()
        new_sheets.setHistReturnSheet(self.writer, self.data_dict['Returns'], 'Returns').create_sheets()
      
class rollingCumRetReport(returnsReport):
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
        super().__init__(report_name, {'Returns': df_returns},data_file=False)

    def generate_report(self):
        # Get rolling cumulative return data
        self.rolling_cum_dict = summary.get_rolling_cum_data(self.data_dict['Returns'], self.freq, self.notional_weights)

        # Create Excel reports
        new_sheets.histReturnSheet(self.writer, self.rolling_cum_dict['3M'], 'Rolling Cum Returns_3 Months').create_sheets()
        new_sheets.histReturnSheet(self.writer, self.rolling_cum_dict['6M'], 'Rolling Cum Returns_6 Months').create_sheets()
        new_sheets.histReturnSheet(self.writer, self.rolling_cum_dict['1Y'], 'Rolling Cum Returns_1 Year').create_sheets()
        
class altsReport(returnsReport):
    def __init__(self, report_name, returns_data, mv_data={}, include_fi=True,
                 freq='1M', include_bmk=False, bmk_df=dm.pd.DataFrame(), bmk_dict={}):
        
        self.returns_data = returns_data
        self.mv_data = mv_data
        self.include_fi = include_fi
        self.freq = freq
        self.include_bmk = include_bmk
        self.bmk_df = bmk_df
        self.bmk_dict = bmk_dict
        
        super().__init__(report_name, self.returns_data, data_file=False)
        
        
    def check_data_type(self,):
        if type(self.data) is not dict:
            self.data = {'Full': self.returns_data.copy()}
            try:
                if type(self.mv_data) is not dict:
                    self.mv_data = {'Full': self.mv_data.copy()}
            except KeyError:
                self.mv_data = {'Full': pd.DataFrame()}
    
    
    def generate_report(self):
        self.check_data_type()
        for key in self.data:
            print(f'Computing {key} Analytics...')
            #get analytics
            returns_df = self.data[key].copy()
            try:
                mv_df = self.mv_data[key].copy()
                returns_df.dropna(axis=1, inplace=True)
                mv_df.dropna(axis=1, inplace=True)
            except KeyError:
                mv_df = pd.DataFrame()
            analysis_data = summary.get_alts_data(returns_df, mv_df, include_fi=self.include_fi, freq= self.freq,
                                                  include_bmk= self.include_bmk, bmk_df= self.bmk_df, bmk_dict= self.bmk_dict)
            
            #create sheets
            new_sheets.corrStatsSheet(self.writer, analysis_data['corr'], sheet_name=f'Correlation Analysis ({key})', include_fi=self.include_fi).create_sheets()
            new_sheets.altsReturnStatsSheet(self.writer, analysis_data['ret_stat_df'], sheet_name=f'Returns Statistics ({key})', include_fi=self.include_fi, include_bmk=self.include_bmk).create_sheets()
        # returns_df = returns_data['Full'].copy()
        return_sheet_name = dm.switch_freq_string(self.freq) + ' Historical Returns'
        new_sheets.histReturnSheet(self.writer, self.data['Full'], return_sheet_name).create_sheets()
        new_sheets.histReturnMTDYTDSheet(self.writer, summary.all_strat_month_ret_table(self.data['Full'], include_fi=self.include_fi)).create_sheets()

class stratAltsReport(altsReport):
    def __init__(self, report_name, returns_data, include_fi=True, freq='1M'):
        
        super().__init__(report_name, returns_data, include_fi=include_fi, freq=freq)
        
    def generate_report(self):
        print('in generate report')
        analysis_df = pd.DataFrame()
        col_list_1 = list(self.data.keys())
        col_list_1[0] = 'Since Inception'
        skip = 2 if self.include_fi else 1
        col_list_2 = self.data['Full'].columns[skip:].tolist()
        header = pd.MultiIndex.from_product([col_list_1,col_list_2])
        
        #loop through frequencies
        for key in self.data:
            print(f'Computing {key} Analytics...')
            #get analytics
            analysis_data = summary.get_alts_strat_data(self.data[key], include_fi=self.include_fi, freq=self.freq)
            analysis_data.columns = ['port_{}'.format(key), 'bench_{}'.format(key)]
            analysis_df = dm.merge_data_frames(analysis_df, analysis_data, drop_na=False, how='right')
            
        analysis_df.columns = header
        
        #returns stat sheet
        new_sheets.stratAltsReturnStatsSheet(self.writer, analysis_df, sheet_name='Returns Statistics', include_fi=self.include_fi).create_sheets()
        
        #worst_dd sheet
        new_sheets.drawdownSheet(self.writer, dd.get_worst_drawdowns(self.data['Full'][col_list_2[0]], recovery=True), 'Drawdown Statistics').create_sheets()
        #index sheet
        new_sheets.ratioSheet(self.writer, dm.get_prices_df(self.data['Full'][col_list_2]), sheet_name='Index').create_sheets()
        
        #MTD-YTD sheet 
        new_sheets.histReturnMTDYTDSheet(self.writer, summary.all_strat_month_ret_table(self.data['Full'], include_fi=self.include_fi)).create_sheets()
        
        #historical return sheet
        return_sheet = dm.switch_freq_string(self.freq) + ' Historical Returns'
        new_sheets.histReturnSheet(self.writer, self.data['Full'][col_list_2], return_sheet).create_sheets()
           

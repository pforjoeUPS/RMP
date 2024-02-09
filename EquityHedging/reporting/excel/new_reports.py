# -*- coding: utf-8 -*-
"""
Created on Fri July 7, 2023

@author: Powis Forjoe, Maddie Choi, Devang Ajmera
"""

import os

import pandas as pd

from . import new_sheets
# from ...analytics import drawdowns as dd
from ...datamanager import data_manager_new as dm
from ...analytics import summary_new


class SetReport:
    def __init__(self, report_name, data_file=False):
        """
        Setup Excel report

        Parameters
        ----------
        report_name : string
            Name of Excel report.
        data_file : boolean, optional
            Boolean to determine if Excel file belongs in data folder or not. The default is False.

        Returns
        -------
        None.

        """
        self.report_name = report_name
        self.data_file = data_file
        self.file_path = self.get_filepath_path()

    def get_filepath_path(self):
        """
        Gets the file path where the report will be stored

        Returns
        -------
        string
            File path

        """

        cwd = os.getcwd()

        file_path = '\\EquityHedging\\data\\returns_data\\' if self.data_file else '\\EquityHedging\\reports\\'
        file_name = self.report_name + '.xlsx'
        return cwd + file_path + file_name


class DataReport(SetReport):
    def __init__(self, report_name, data, data_file=False):
        """
        Generates Excel file containing historical returns for different frequencies

        Parameters
        ----------
        report_name : string
            Name of report.
        data : dict/dataframe
            Dictionary containing returns of different frequencies.
        data_file : boolean, optional
            Boolean to determine if Excel file belongs in data folder or reports folder. The default is True.

        Returns
        -------
        None. An Excel report called [report_name].xlsx is created
        """
        super().__init__(report_name, data_file)
        self.writer = None
        self.data = data
        # self.info_dict = None

    def run_report(self):
        self.writer = self.get_writer()
        # self.generate_info_dict()
        # self.generate_info_sheet()
        self.generate_report()
        self.print_report_info()
        self.writer.close()

    def get_writer(self):
        return pd.ExcelWriter(self.file_path, engine='xlsxwriter')

    def generate_info_dict(self):
        # self.info_dict = {'Report Name': self.report_name}
        pass

    def generate_info_sheet(self):
        new_sheets.InfoSheet(self.writer, self)

    def generate_report(self, *kwargs):
        pass

    def print_report_info(self):
        """
        Print name of report and location

        Returns
        -------
        None.

        """
        folder_location = self.file_path.replace(self.report_name + '.xlsx', '')
        print(f'"{self.report_name}.xlsx" report generated in "{folder_location}" folder')


class ReturnsReport(DataReport):
    def __init__(self, report_name, data, data_file=True):
        """
        Generates Excel file containing historical returns for different frequencies

        Parameters
        ----------
        report_name : string
            Name of report.
        data : dict/dataframe
            Dictionary containing returns of different frequencies.
        data_file : boolean, optional
            Boolean to determine if Excel file belongs in data folder or reports folder. The default is True.

        Returns
        -------
        None. An Excel report called [report_name].xlsx is created
        """
        super().__init__(report_name=report_name, data=data, data_file=data_file)

    def generate_report(self, *kwargs):
        # loop through dictionary to create returns spreadsheets
        if isinstance(self.data, dict) is False:
            freq_string = dm.switch_freq_string(dm.get_freq(self.data))
            self.data = {freq_string: self.data}
        for data_key, returns_df in self.data.items():
            print(f'Writing {data_key} Historical Returns sheet...')
            diff = -(len(data_key) - 31) if len(data_key) > 31 else None
            new_sheets.HistReturnSheet(writer=self.writer, data=returns_df, sheet_name=data_key[:diff]).create_sheet()


class ReturnMktValueReport(DataReport):
    def __init__(self, report_name, data, data_file=True):
        """
        Generates an Excel file containing monthly returns and market values

        Parameters
        ----------
        report_name : string
            Name of report.
        data : dict
            Dictionary containing returns and market_values.
        data_file : boolean, optional
            Boolean to determine if Excel file belongs in data folder or reports folder. The default is True.

        Returns
        -------
        None. An Excel report called [report_name].xlsx is created
        """
        super().__init__(report_name, data, data_file)

    def generate_report(self):
        print("Writing Monthly Returns sheet...")
        new_sheets.HistReturnSheet(writer=self.writer, data=self.data['returns'],
                                   sheet_name='returns').create_sheet()
        print("Writing Monthly Market Values sheet...")
        new_sheets.MktValueSheet(self.writer, self.data['market_values']).create_sheet()


class AnalyticReport(DataReport):
    def __init__(self, report_name, data_handler, include_bmk=False, include_eq=True, include_fi=False):
        self.data_handler = data_handler
        self.include_bmk = include_bmk
        self.include_eq = include_eq
        self.include_fi = include_fi
        self.analytic_summary = self.get_analytic_summary()
        self.data = self.get_analytic_summary_data()

        super().__init__(report_name=report_name, data=self.data, data_file=False)

    def get_analytic_summary_data(self):
        self.analytic_summary.get_reporting_data()
        return self.analytic_summary.reporting_data

    def get_analytic_summary(self):
        return summary_new.AnalyticsSummary(self.data_handler, include_bmk=self.include_bmk, include_eq=self.include_eq,
                                            include_fi=self.include_fi)


# TODO: add include_fi
class HistSelloffReport(AnalyticReport):

    def __init__(self, report_name, data_handler, include_fi=False, weighted=False, new_strat=False):
        """
        Generate historical selloffs report

        Parameters
        ----------
        report_name : string
            Name of report.
        data_handler : DataHandler object
        weighted : boolean, optional
            Include weighted hedges and weighted strats. The default is False.
        new_strat : boolean, optional
            Does analysis involve a new strategy. The default is False.
        Returns
        -------
        None. An Excel report called [report_name].xlsx is created
        """
        self.weighted = weighted
        self.new_strat = new_strat

        super().__init__(report_name=report_name, data_handler=data_handler, include_fi=include_fi)

    def get_analytic_summary(self):
        return summary_new.HistSellOffAnalyticSummary(data_handler=self.data_handler, new_strat=self.new_strat,
                                                      weighted=self.weighted)

    def generate_report(self):
        self.generate_selloffs_sheets()

    def generate_selloffs_sheets(self):
        # Create sheets
        new_sheets.HistSelloffSheet(self.writer, self.data['selloffs']).create_sheet()
        new_sheets.HistReturnSheet(self.writer, self.data['returns']['Daily'],
                                   sheet_name='Daily Historical Returns').create_sheet()

class EquityHedgeReport(HistSelloffReport):
    def __init__(self, report_name, data_handler, include_fi=False, new_strat=False, weighted=True, selloffs=True,
                 include_quantile=True):

        """
        Generate equity hedge analysis report

        Parameters
        ----------
        report_name : string
            Name of report.
        data_handler : DataHandler object
        new_strat : boolean, optional
            Does analysis involve a new strategy. The default is False.
        weighted : boolean, optional
            Include weighted hedges and weighted strats. The default is True.
        selloffs : boolean, optional
            Include historical selloffs. The default is True.
        include_quantile : boolean, optional
            Include Quantile Analysis.

        Returns
        -------
        None. An Excel report called [report_name].xlsx is created
        """
        self.selloffs = selloffs
        self.include_quantile = include_quantile
        super().__init__(report_name=report_name, data_handler=data_handler, include_fi=include_fi, weighted=weighted,
                         new_strat=new_strat)

    def get_analytic_summary(self):
        return summary_new.EqHedgeAnalyticSummary(data_handler=self.data_handler, include_fi=self.include_fi,
                                                  new_strat=self.new_strat, weighted=self.weighted,
                                                  selloffs=self.selloffs, include_quantile=self.include_quantile)

    def generate_report(self):
        self.generate_analysis_sheets()
        if self.include_quantile:
            self.generate_quantile_sheets()
        if self.selloffs:
            self.generate_selloffs_sheets()

    def generate_quantile_sheets(self):
        for mkt, mkt_quantile_dict in self.data['quantiles'].items():
            new_sheets.QuantileDataSheet(writer=self.writer, data=mkt_quantile_dict,
                                         sheet_name=f'{mkt} Quantile Analysis').create_sheet()

    def generate_analysis_sheets(self):
        for freq in self.data['analytics']:
            new_sheets.AnalysisSheet(self.writer, self.data['analytics'][freq],
                                     sheet_name=f'{freq} Analysis').create_sheet()
            new_sheets.HistReturnSheet(self.writer, self.data['returns'][freq],
                                       sheet_name=f'{freq} Historical Returns').create_sheet()


class StratReport(EquityHedgeReport):
    def __init__(self, report_name, data_handler, include_fi=False, selloffs=True):
        """
        Generate strat analysis report

        Parameters
        ----------
        report_name : string
            Name of report.
        data_handler : DataHandler object
        selloffs : boolean, optional
            Include historical selloffs. The default is True.

        Returns
        -------
        None. An Excel report called [report_name].xlsx is created
        """

        super().__init__(report_name=report_name, data_handler=data_handler, include_fi=include_fi, new_strat=False,
                         weighted=False, selloffs=selloffs, include_quantile=False)


class CorrRankReport(DataReport):
    def __init__(self, report_name, df_returns, buckets, notional_weights=None, include_fi=False):
        """
        Generate correlation rank analysis report

        Parameters
        ----------
        report_name : string
            Name of report.
        df_returns : DataFrame containing returns data.
        buckets : int
            Number of buckets for the correlation rank analysis.
        notional_weights : list, optional
            Notional weights of strategies. The default is [].
        include_fi : boolean, optional
            Include Fixed Income benchmark. The default is False.

        Returns
        -------
        None. An Excel report called [report_name].xlsx is created
        """
        self.corr_data_dict = None
        self.dates = None
        self.corr_pack = None
        if notional_weights is None:
            notional_weights = []
        self.buckets = buckets
        self.notional_weights = notional_weights
        self.include_fi = include_fi
        self.data_file = False
        super().__init__(report_name, {'Returns': df_returns}, self.data_file)

    # def generate_report(self):
    # # Get correlation rank data
    # self.corr_pack = get_corr_rank_data(self.data['Returns'], self.buckets, self.notional_weights)
    # self.dates = dm.get_min_max_dates(self.data['Returns'])
    # self.corr_data_dict = {'df_list': [], 'title_list': []}
    #
    # # Unpack corr_pack
    # for i in self.corr_pack:
    #     self.corr_data_dict['df_list'].append(self.corr_pack[str(i)][0])
    #     self.corr_data_dict['title_list'].append(self.corr_pack[str(i)][1])

    # Create Excel report
    # new_sheets.CorrRankSheet(self.writer, self.corr_data_dict, self.dates).create_sheets()
    # new_sheets.HistReturnSheet(self.writer, self.data['Returns'], 'Returns').create_sheets()


class RollingCumRetReport(DataReport):
    def __init__(self, report_name, df_returns, freq, notional_weights):
        """
        Generate rolling cumulative return analysis report

        Parameters
        ----------
        report_name : string
            Name of report.
        df_returns : DataFrame
            returns data.
        freq : string
            Frequency for rolling cumulative returns (e.g., '3M', '6M', '1Y').
        notional_weights : list
            Notional weights of strategies.

        Returns
        -------
        None. An Excel report called [report_name].xlsx is created
        """
        self.freq = freq
        self.notional_weights = notional_weights
        super().__init__(report_name, {'Returns': df_returns}, data_file=False)


class AltsReport(AnalyticReport):
    def __init__(self, report_name, data_handler, full_port=False, sub_port='Global Macro', add_composite_data=True,
                 include_bmk=True, include_fi=True, include_cm=True, include_fx=True,
                 include_dd=False, include_quantile=False, include_best_worst_pd=False, include_roll_stats=True):

        self.full_port = full_port
        self.sub_port = sub_port
        self.add_composite_data = add_composite_data
        self.include_cm = include_cm
        self.include_fx = include_fx
        self.include_dd = include_dd
        self.include_best_worst_pd = include_best_worst_pd
        self.include_quantile = include_quantile
        self.include_roll_stats = include_roll_stats

        super().__init__(report_name=report_name, data_handler=data_handler, include_bmk=include_bmk,
                         include_eq=True, include_fi=include_fi)

    def get_analytic_summary(self):
        return summary_new.LiquidAltsAnalyticSummary(data_handler=self.data_handler, full_port=self.full_port,
                                                     sub_port=self.sub_port, add_composite_data=self.add_composite_data,
                                                     include_bmk=self.include_bmk, include_fi=self.include_fi,
                                                     include_cm=self.include_cm, include_fx=self.include_fx,
                                                     include_best_worst_pd=self.include_best_worst_pd,
                                                     include_roll_stats=self.include_roll_stats)

    def run_report(self, period_list):
        self.writer = self.get_writer()
        self.generate_report(period_list)
        self.print_report_info()
        self.writer.close()

    def generate_report(self, period_list):
        self.generate_period_sheets(period_list)
        if self.include_quantile:
            self.generate_quantile_sheets()
        if self.include_dd:
            self.generate_drawdowns_sheets()
        if self.include_roll_stats:
            self.generate_roll_sheets()
        if self.include_best_worst_pd:
            self.generate_best_worst_sheets()
        self.generate_mtd_ytd_itd_sheets()
        self.generate_returns_sheets()

    def generate_period_sheets(self, period_list=[]):
        if any(period_list) is False:
            period_list = period_list.copy()
        for period in period_list:
            try:
                self.generate_correlation_sheets(period)
                self.generate_analytics_sheets(period)
            except KeyError:
                pass

    def generate_correlation_sheets(self, period):
        corr_dict = self.data['correlations'][period]
        new_sheets.CorrStatsSheet(writer=self.writer, data=corr_dict,
                                  sheet_name=f'Correlation Analysis ({period})').create_sheet()

    def generate_return_stats_sheets(self, period):
        analytics_dict = self.data['analytics'][period]
        new_sheets.LiquidAltsReturnsStatsSheet(writer=self.writer, data=analytics_dict['return_stats'],
                                               sheet_name=f'Return Statistics ({period})',
                                               include_bmk=self.include_bmk).create_sheet()

    def generate_mkt_stats_sheets(self, period):
        analytics_dict = self.data['analytics'][period]
        new_sheets.MarketStatsDataSheet(writer=self.writer, data=analytics_dict['market_stats'],
                                        sheet_name=f'Market Statistics ({period})').create_sheet()

    def generate_roll_sheets(self):
        for key, roll_dict in self.data['rolling_stats']['ret_stats'].items():
            new_sheets.RatioSheet(writer=self.writer, data=roll_dict[key],
                                  sheet_name=f'Rolling 36M {key}').create_sheet()
        for key, roll_dict in self.data['rolling_stats']['mkt_stats']['beta'].items():
            # diff = -(len(key) - 31) if len(key) > 31 else None
            new_sheets.RatioSheet(writer=self.writer, data=roll_dict[key],
                                  sheet_name=f'36M Beta to {key}').create_sheet()
        for key, roll_dict in self.data['rolling_stats']['mkt_stats']['corr'].items():
            new_sheets.RatioSheet(writer=self.writer, data=roll_dict[key],
                                  sheet_name=f'36M Corr to {key}').create_sheet()
        for key, roll_dict in self.data['rolling_stats']['active_stats'].items():
            new_sheets.RatioSheet(writer=self.writer, data=roll_dict[key],
                                  sheet_name=f'Rolling 36M {key}').create_sheet()

    def generate_drawdowns_sheets(self):
        new_sheets.DrawdownMatrixSheet(writer=self.writer, data=self.data['drawdowns']['dd_matrix']).create_sheet()
        new_sheets.CoDrawdownDictSheet(writer=self.writer, data=self.data['drawdowns']['co_dd']).create_sheet()
        new_sheets.DrawdownDictSheet(writer=self.writer, data=self.data['drawdowns']['dd_dict']).create_sheet()

    def generate_quantile_sheets(self):
        for mkt, quantile_dict in self.data['quantiles']['mkt_data'].items():
            new_sheets.QuantileDataSheet(self.writer, quantile_dict,
                                         sheet_name=f'{mkt} Quantile Analysis').create_sheet()

    def generate_best_worst_sheets(self):
        for key in self.data['best_worst_pd']:
            sheet_name = 'Worst Market Quarters' if 'worst' in key else 'Best Market Quarters'
            new_sheets.BestWorstPdDataSheet(self.writer, self.data['best_worst_pd'][key],
                                            sheet_name=sheet_name).create_sheet()

    def generate_analytics_sheets(self, period):
        analytics_dict = self.data['analytics'][period]
        new_sheets.MarketStatsDataSheet(writer=self.writer, data=analytics_dict['market_stats'],
                                        sheet_name=f'Market Statistics ({period})').create_sheet()
        new_sheets.LiquidAltsReturnsStatsSheet(writer=self.writer, data=analytics_dict['return_stats'],
                                               sheet_name=f'Return Statistics ({period})',
                                               include_bmk=self.include_bmk).create_sheet()

    def generate_returns_sheets(self):
        for freq, returns_df in self.data['returns'].items():
            new_sheets.HistReturnSheet(writer=self.writer, data=returns_df,
                                       sheet_name=f'{freq} Historical Returns').create_sheet()

    def generate_mtd_ytd_itd_sheets(self):
        new_sheets.HistReturnMTDYTDSheet(writer=self.writer, data=self.data['mtd_ytd_itd']).create_sheet()


    #
    # def check_data_type(self, ):
    #     if type(self.data) is not dict:
    #         self.data = {'Full': self.returns_data.copy()}
    #         try:
    #             if type(self.mv_data) is not dict:
    #                 self.mv_data = {'Full': self.mv_data.copy()}
    #         except KeyError:
    #             self.mv_data = {'Full': pd.DataFrame()}
    #
    # def generate_report(self):
    #     self.check_data_type()
    #     for key in self.data:
    #         print(f'Computing {key} Analytics...')
    #         # get analytics
    #         returns_df = self.data[key].copy()
    #         try:
    #             mv_df = self.mv_data[key].copy()
    #             returns_df.dropna(axis=1, inplace=True)
    #             mv_df.dropna(axis=1, inplace=True)
    #         except KeyError:
    #             mv_df = pd.DataFrame()
    #         analysis_data = summary.get_alts_data(returns_df, mv_df, include_fi=self.include_fi, freq=self.freq,
    #                                               include_bmk=self.include_bmk, bmk_df=self.bmk_df,
    #                                               bmk_dict=self.bmk_dict)
    #
    #         # create sheets
    #         new_sheets.CorrStatsSheet(self.writer, analysis_data['corr'], sheet_name=f'Correlation Analysis ({key})',
    #                                   include_fi=self.include_fi).create_sheets()
    #         new_sheets.AltsReturnStatsSheet(self.writer, analysis_data['ret_stat_df'],
    #                                         sheet_name=f'Returns Statistics ({key})', include_fi=self.include_fi,
    #                                         include_bmk=self.include_bmk).create_sheets()
    #     # returns_df = returns_data['Full'].copy()
    #     return_sheet_name = dm.switch_freq_string(self.freq) + ' Historical Returns'
    #     new_sheets.HistReturnSheet(self.writer, self.data['Full'], return_sheet_name).create_sheets()
    #     new_sheets.HistReturnMTDYTDSheet(self.writer, summary.all_strat_month_ret_table(self.data['Full'],
    #                                                                                     include_fi=self.include_fi)).create_sheets()


class StratAltsReport(AltsReport):
    def __init__(self, report_name, data_handler, include_hf=False, include_fi=True, include_cm=True, include_fx=True):
        self.include_hf = include_hf
        super().__init__(report_name=report_name, data_handler=data_handler, full_port=False, include_bmk=True,
                         include_fi=include_fi, include_cm=include_cm, include_fx=include_fx)

    def get_analytic_summary(self):
        return summary_new.LiquidAltsStratSummary(data_handler=self.data_handler, include_hf=self.include_hf,
                                                  include_fi=self.include_fi, include_cm=self.include_cm,
                                                  include_fx=self.include_hf)

    def generate_report(self):
        if self.include_hf:
            self.generate_correlation_sheets()
        self.generate_analytics_sheets()
        # self.generate_return_stats_sheets()
        # self.generate_mkt_stats_sheets()
        # self.generate_quantile_sheets()
        self.generate_drawdowns_sheets()
        # self.generate_roll_sheets()
        self.generate_returns_sheets()

    def generate_analytics_sheets(self):
        analytics_dict = self.data['analytics']
        new_sheets.LiquidAltsReturnsStatsSheet(writer=self.writer, data=analytics_dict['return_stats'],
                                               include_bmk=self.include_bmk, strat_report=True).create_sheet()
        new_sheets.MarketStatsDataSheet(writer=self.writer, data=analytics_dict['market_stats'],
                                        partial_stats=True, strat_report=True).create_sheet()

    def generate_correlation_sheets(self):
        corr_dict = self.data['correlations']
        new_sheets.CorrStatsSheet(writer=self.writer, data=corr_dict).create_sheet()
    # def __init__(self, report_name, returns_data, include_fi=True, freq='1M'):
    #     super().__init__(report_name, returns_data, include_fi=include_fi, freq=freq)
    #
    # def generate_report(self):
    #     print('in generate report')
    #     analysis_df = pd.DataFrame()
    #     col_list_1 = list(self.data.keys())
    #     col_list_1[0] = 'Since Inception'
    #     skip = 2 if self.include_fi else 1
    #     col_list_2 = self.data['Full'].columns[skip:].tolist()
    #     header = pd.MultiIndex.from_product([col_list_1, col_list_2])
    #
    #     # loop through frequencies
    #     for key in self.data:
    #         print(f'Computing {key} Analytics...')
    #         # get analytics
    #         analysis_data = summary.get_alts_strat_data(self.data[key], include_fi=self.include_fi, freq=self.freq)
    #         analysis_data.columns = ['port_{}'.format(key), 'bench_{}'.format(key)]
    #         analysis_df = dm.merge_dfs(analysis_df, analysis_data, drop_na=False, how='right')
    #
    #     analysis_df.columns = header
    #
    #     # returns stat sheet
    #     new_sheets.StratAltsReturnStatsSheet(self.writer, analysis_df, sheet_name='Returns Statistics',
    #                                          include_fi=self.include_fi).create_sheets()
    #
    #     # worst_dd sheet
    #     new_sheets.DrawdownSheet(self.writer, dd.get_worst_drawdowns(self.data['Full'][col_list_2[0]], recovery=True),
    #                              'Drawdown Statistics').create_sheets()
    #     # index sheet
    #     new_sheets.RatioSheet(self.writer, dxf.get_price_data(self.data['Full'][col_list_2]),
    #                           sheet_name='Index').create_sheets()
    #
    #     # MTD-YTD sheet
    #     new_sheets.HistReturnMTDYTDSheet(self.writer, summary.all_strat_month_ret_table(self.data['Full'],
    #                                                                                     include_fi=self.include_fi)).create_sheets()
    #
    #     # historical return sheet
    #     return_sheet = dm.switch_freq_string(self.freq) + ' Historical Returns'
    #     new_sheets.HistReturnSheet(self.writer, self.data['Full'][col_list_2], return_sheet).create_sheets()

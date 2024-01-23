# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""

from . import returns_analytics as ra
# from . import risk
# from . import util_new
# from ..datamanager import data_handler as dh
# from ..datamanager import data_manager_new as dm
from ..datamanager.data_xformer_new import copy_data
import pandas as pd


class eqHedgeReportAnalytic(ra.eqHedgeReturnsDictAnalytic):
    def __init__(self, data_handler, freq_list=['Monthly', 'Weekly'], new_strat=False, weighted=True, selloffs=True):

        self.returns = None
        self.mkt_returns = None
        self.wgts_df = pd.DataFrame()
        self.weighted = weighted
        self.new_strat = new_strat
        self.selloffs = selloffs
        self.freq_list = freq_list if any(freq_list) else [next(iter(data_handler.returns))]
        self.main_key = self.freq_list[0]
        self.get_dh_data(data_handler)

        super().__init__(self.returns, main_key=self.main_key, include_fi=self.include_fi,
                         mkt_data=self.mkt_returns, mkt_key=self.mkt_key)

        self.reporting_data = None

    def get_dh_data(self, data_handler):
        if self.weighted:
            data_handler.get_weighted_returns(self.new_strat)
            self.returns = data_handler.weighted_returns
            self.wgts_df = data_handler.get_weights_df()
        else:
            self.returns = copy_data(data_handler.returns)
        self.include_fi = data_handler.include_fi
        self.mkt_returns = data_handler.mkt_returns
        self.mkt_key = data_handler.mkt_key

    def get_analytics(self):
        self.get_corr_stats_dict(self.freq_list)
        self.get_returns_stats_dict(self.freq_list)
        self.get_hedge_metrics_dict(self.freq_list)
        self.get_quantile_stats()
        if self.selloffs:
            self.get_hist_selloff()

    def format_data(self):
        self.reporting_data = {}
        analytics_dict = {}
        for freq_string in self.freq_list:
            analytics_dict[freq_string] = self.format_analytics_data(freq_string)
        self.reporting_data['analytics'] = analytics_dict
        self.reporting_data['returns'] = self.format_returns_data()
        self.reporting_data['quantiles'] = self.format_quantile_data()
        if self.selloffs:
            self.reporting_data['selloffs'] = copy_data(self.historical_selloff_data)

    def format_quantile_data(self):
        quantile_mkt_data = self.quantile_stats_data['mkt_data']
        quantile_dict = {}
        for mkt in self.mkt_key:
            temp_dict = {}
            for quantile in quantile_mkt_data:
                temp_dict[quantile] = quantile_mkt_data[quantile][mkt]
            quantile_dict[mkt] = temp_dict
        return quantile_dict

    def format_analytics_data(self, freq_string):
        return_stats_idx_list = ['Time Frame', f'No. of {freq_string} Observations', 'Annualized Return',
                                 'Annualized Volatility', 'Return/Volatility',
                                 'Max DD', 'Return/Max DD', 'Max 1M DD', 'Max 1M DD Date', 'Ret/Max 1M DD',
                                 'Max 3M DD', 'Max 3M DD Date', 'Ret/Max 3M DD', 'Skewness',
                                 'Avg Pos Return/Avg Neg Return', 'Downside Deviation', 'Sortino Ratio',
                                 f'VaR {(1 - self.p):.0%}', f'CVaR {(1 - self.p):.0%}']

        corr_stats_data = copy_data(self.corr_stats_dict[freq_string])
        return_stats_data = {'ret_stats_df': self.returns_stats_dict[freq_string].loc[return_stats_idx_list],
                             'title': f'Return Statistics ({freq_string} Returns)'}
        hedge_metrics_data = {'hm_df': copy_data(self.hedge_metrics_dict[freq_string]),
                              'title': f'Hedging Framework Metrics ({freq_string} Returns)'}
        weighting_data = {'wgts_df': copy_data(self.wgts_df),
                          'title': 'Portfolio Weightings'}

        return {'correlations': corr_stats_data, 'weighting': weighting_data,
                'return_stats': return_stats_data, 'hedge_metrics': hedge_metrics_data}

    def format_returns_data(self):
        if self.selloffs:
            return {freq: self.returns_dict[freq] for freq in [*self.freq_list, *['Daily']]}
        else:
            return {freq: self.returns_dict[freq] for freq in self.freq_list}

    def get_reporting_data(self):
        self.get_analytics()
        self.format_data()


class histSellOffReportAnalytic(eqHedgeReportAnalytic):
    def __init__(self, data_handler, new_strat=False, weighted=False):

        super().__init__(data_handler, freq_list=['Daily'], new_strat=new_strat, weighted=weighted, selloffs=True)

    def get_dh_data(self, data_handler):
        if self.weighted:
            data_handler.get_weighted_returns(self.new_strat)
            self.returns = {'Daily': data_handler.weighted_returns['Daily']}
        else:
            self.returns = {'Daily': copy_data(data_handler.returns['Daily'])}
        self.include_fi = data_handler.include_fi
        self.mkt_returns = {'Daily': data_handler.mkt_returns['Daily']}
        self.mkt_key = data_handler.mkt_key

    def get_analytics(self):
        self.get_hist_selloff()

    def format_returns_data(self):
        return copy_data(self.returns_dict)

    def format_data(self):
        self.reporting_data = {'returns': self.format_returns_data(),
                               'selloffs': copy_data(self.historical_selloff_data)}

    def get_reporting_data(self):
        self.get_analytics()
        self.format_data()

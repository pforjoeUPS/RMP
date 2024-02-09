# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""
import calendar

import pandas as pd
from copy import deepcopy
from . import returns_analytics as ra, returns_stats_new as rs
from ..datamanager import data_manager_new as dm
from ..datamanager.data_xformer_new import copy_data, get_data_dict


class AnalyticsSummary:

    def __init__(self, data_handler, include_bmk=False, include_eq=True, include_fi=False):
        self.ra = None
        self.reporting_data = None
        self.data_handler = data_handler
        self.include_bmk = include_bmk
        self.include_eq = include_eq
        self.include_fi = include_fi
        self.returns = {}
        self.bmk_returns = {}
        self.mkt_returns = {}
        self.bmk_key = {}
        self.mkt_key = {}
        self.get_dh_data()
        self.get_ra()

    def get_ra(self):
        self.ra = ra.ReturnsAnalytic(self.returns, include_bmk=self.include_bmk,
                                     bmk_df=self.bmk_returns, bmk_key=self.bmk_key,
                                     include_eq=self.include_eq, include_fi=self.include_fi,
                                     mkt_df=self.mkt_returns, mkt_key=self.mkt_key)

    def get_dh_data(self):
        self.get_return_data()
        self.get_bmk_data()
        self.get_mkt_data()

    def get_return_data(self):
        self.returns = copy_data(self.data_handler.returns)

    def get_include_mkt_data(self):
        if self.data_handler.include_eq is False:
            self.include_eq = self.data_handler.include_eq
        if self.data_handler.include_fi is False:
            self.include_fi = self.data_handler.include_fi

    def get_bmk_data(self):
        try:
            if self.include_bmk:
                self.bmk_returns = copy_data(self.data_handler.bmk_returns)
                self.bmk_key = copy_data(self.data_handler.bmk_key)
        except AttributeError:
            pass

    def get_mkt_data(self):
        self.get_include_mkt_data()
        self.mkt_returns = copy_data(self.data_handler.mkt_returns)
        self.mkt_key = copy_data(self.data_handler.mkt_key)

    def get_reporting_data(self, **kwargs):
        self.get_analytics(**kwargs)
        self.format_data(**kwargs)

    def get_analytics(self, **kwargs):
        pass

    def format_data(self, **kwargs):
        pass

    def format_mkt_quantile_data(self):
        quantile_mkt_data = self.ra.quantile_stats_data['mkt_data']
        quantile_dict = {}
        for mkt in next(iter(quantile_mkt_data.values())):
            temp_dict = {}
            for quantile in quantile_mkt_data:
                temp_dict[quantile] = quantile_mkt_data[quantile][mkt]
            quantile_dict[mkt] = temp_dict
        return quantile_dict

    def format_ret_quantile_data(self):
        quantile_ret_data = self.ra.quantile_stats_data['returns_data']
        quantile_dict = {}
        for strat in next(iter(quantile_ret_data.values())):
            temp_dict = {}
            for quantile in quantile_ret_data:
                quantile_df = quantile_ret_data[quantile][strat]
                temp_dict[quantile] = self.reorder_quantile_df(quantile_df, strat)
            quantile_dict[strat] = temp_dict
        return quantile_dict

    def format_monthly_returns_data(self):
        pass

    @staticmethod
    def reorder_quantile_df(quantile_df, strat):
        strat_list = list(quantile_df.columns)
        strat_list.remove(strat)
        strat_list.insert(0, strat)
        quantile_df = quantile_df[strat_list]
        return quantile_df

    def get_mtd_ytd_itd_returns_dict(self, monthly_returns_df):
        mtd_ytd_itd_returns_dict = {}
        print('Computing MTD YTD ITD returns...')
        for strat in monthly_returns_df:
            mtd_ytd_itd_returns_dict[strat] = self.get_mtd_ytd_itd_returns_df(monthly_returns_df[strat])
        return mtd_ytd_itd_returns_dict

    def get_mtd_ytd_itd_returns_df(self, monthly_returns_series):
        return pd.concat([self.group_monthly_returns_by_year(monthly_returns_series),
                          self.get_ytd_itd_returns_df(monthly_returns_series)], axis=1)

    @staticmethod
    def group_monthly_returns_by_year(monthly_returns_series):
        """

        Parameters
        ----------
        monthly_returns_series : Data Frame

        Returns
        -------
        Data Frame

        """
        # pull monthly returns from dictionary
        returns_df = pd.DataFrame(dm.drop_nas(monthly_returns_series))

        # create monthly return data frame with index of years
        returns_df['year'] = returns_df.index.year
        returns_df['month'] = returns_df.index.month

        # change monthly returns into a table with x axis as months and y axis as years
        grouped_returns_df = returns_df.groupby(['year', 'month']).sum()

        mtd_returns_by_year_df = grouped_returns_df.unstack()

        # drop first row index
        mtd_returns_by_year_df = mtd_returns_by_year_df.droplevel(level=0, axis=1)

        mtd_returns_by_year_df.columns = [calendar.month_abbr[x] for x in list(mtd_returns_by_year_df.columns)]
        # re order columns
        # mtd_returns_by_year_df = mtd_returns_by_year_df[
        #     ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
        #
        # # Join yearly returns to the monthly returns table
        # mtd_ytd_itd_returns_df = pd.concat([mtd_returns_by_year_df, ytd_itd_returns_df], axis=1)
        # mtd_ytd_itd_returns_df.index.names = [returns_series.name]

        return mtd_returns_by_year_df

    @staticmethod
    def get_ytd_itd_returns_df(monthly_returns_series):
        monthly_returns_df = pd.DataFrame(dm.drop_nas(monthly_returns_series))
        monthly_returns_df['year'] = monthly_returns_df.index.year

        years = list(monthly_returns_df['year'].unique())
        ytd_returns_list = []
        itd_returns_list = []
        for year in years:
            # isolate monthly returns for single year
            mtd_returns_series = monthly_returns_df.loc[monthly_returns_df.year == year][monthly_returns_series.name]
            # calculate ytd and itd returns
            ytd_returns_list.append(rs.get_cum_ret(mtd_returns_series))
            itd_returns_list.append(rs.get_cum_ret(pd.Series(ytd_returns_list)))

        return pd.DataFrame({"YTD": ytd_returns_list, "ITD": itd_returns_list}, index=list(years))


class EqHedgeAnalyticSummary(AnalyticsSummary):

    def __init__(self, data_handler, freq_list=None, include_fi=False, new_strat=False, weighted=True, selloffs=True,
                 include_quantile=True):

        if freq_list is None:
            freq_list = ['Monthly', 'Weekly']
        self.weights_df = pd.DataFrame()
        self.weighted = weighted
        self.new_strat = new_strat
        self.selloffs = selloffs
        self.include_quantile = include_quantile
        self.freq_list = freq_list if any(freq_list) else [next(iter(data_handler.returns))]
        self.main_key = self.freq_list[0]

        super().__init__(data_handler, include_bmk=False, include_eq=True, include_fi=include_fi)

    def get_ra(self):
        self.ra = ra.EqHedgeReturnsDictAnalytic(self.returns, main_key=self.main_key,
                                                include_fi=self.include_fi,
                                                mkt_data=self.mkt_returns, mkt_key=self.mkt_key)

    def get_return_data(self):
        if self.weighted:
            self.data_handler.get_weighted_returns(self.new_strat)
            self.returns = copy_data(self.data_handler.weighted_returns)
            self.weights_df = self.data_handler.get_weights_df()
        else:
            self.returns = copy_data(self.data_handler.returns)

    def get_reporting_data(self):
        self.get_analytics()
        self.format_data()

    def get_analytics(self):
        self.ra.get_corr_stats_dict(self.freq_list)
        self.ra.get_returns_stats_dict(self.freq_list)
        self.ra.get_hedge_metrics_dict(self.freq_list)
        if self.include_quantile:
            self.ra.get_quantile_stats()
        if self.selloffs:
            self.ra.get_hist_selloff()

    def format_data(self):
        analytics_dict = {}
        for freq_string in self.freq_list:
            analytics_dict[freq_string] = self.format_analytics_data(freq_string)
        self.reporting_data = {'analytics': analytics_dict, 'returns': self.format_returns_data(),
                               'mtd_ytd_itd': self.format_monthly_returns_data()}
        if self.include_quantile:
            self.reporting_data['quantiles'] = self.format_mkt_quantile_data()
        if self.selloffs:
            self.reporting_data['selloffs'] = copy_data(self.ra.historical_selloff_data)

    def format_analytics_data(self, freq_string):
        return {'correlations': self.format_corr_stats_data(freq_string), 'weighting': self.format_weights(),
                'return_stats': self.format_return_stats_data(freq_string),
                'hedge_metrics': self.format_hedge_metrics_data(freq_string)}

    def format_corr_stats_data(self, freq_string):
        corr_stats_data = copy_data(self.ra.corr_stats_dict[freq_string])
        if self.weighted:
            for key in corr_stats_data:
                column_list = corr_stats_data[key]['corr_df'].columns.tolist()
                drop_list = [x for x in column_list if "Weighted Strats" in x]
                corr_stats_data[key]['corr_df'] = dm.drop_data(corr_stats_data[key]['corr_df'],
                                                               drop_list, drop_row=True)
        return corr_stats_data

    def format_return_stats_data(self, freq_string):
        return_stats_data = copy_data(self.ra.returns_stats_dict[freq_string])
        ret_stats_idx_list = ['Time Frame', f'No. of {freq_string} Observations', 'Annualized Return',
                              'Annualized Volatility', 'Return/Volatility', 'Max DD', 'Return/Max DD', 'Max 1M DD',
                              'Max 1M DD Date', 'Ret/Max 1M DD', 'Max 3M DD', 'Max 3M DD Date', 'Ret/Max 3M DD',
                              'Skewness', 'Avg Pos Return/Avg Neg Return', 'Downside Deviation', 'Sortino Ratio',
                              f'VaR {(1 - self.ra.p):.0%}', f'CVaR {(1 - self.ra.p):.0%}']

        return {'ret_stats_df': return_stats_data.reindex(index=ret_stats_idx_list),
                'title': f'Return Statistics ({freq_string} Returns)'}

    def format_hedge_metrics_data(self, freq_string):
        return {'hm_df': copy_data(self.ra.hedge_metrics_dict[freq_string]),
                'title': f'Hedging Framework Metrics ({freq_string} Returns)'}

    def format_weights(self):
        return {'weights_df': copy_data(self.weights_df), 'title': 'Portfolio Weightings'}

    def format_returns_data(self):
        mkt_return_dict = dm.merge_dicts(self.mkt_returns, self.returns, drop_na=False)

        if self.selloffs:
            selloff_freq_list = self.freq_list if 'Daily' in self.freq_list else [*self.freq_list, *['Daily']]
            return dm.filter_data_dict(mkt_return_dict, selloff_freq_list)
        else:
            return dm.filter_data_dict(mkt_return_dict, self.freq_list)

    def format_monthly_returns_data(self):
        monthly_returns_data = dm.merge_dfs(self.ra.mkt_ret_data, self.ra.returns_df, drop_na=False)
        return self.get_mtd_ytd_itd_returns_dict(monthly_returns_data)


class HistSellOffAnalyticSummary(EqHedgeAnalyticSummary):

    def __init__(self, data_handler, include_fi=False, new_strat=False, weighted=False):

        super().__init__(data_handler, freq_list=['Daily'], include_fi=include_fi, new_strat=new_strat,
                         weighted=weighted, selloffs=True, include_quantile=False)

    def get_return_data(self):
        if self.weighted:
            self.data_handler.get_weighted_returns(self.new_strat)
            self.returns = {'Daily': self.data_handler.weighted_returns['Daily']}
        else:
            self.returns = {'Daily': copy_data(self.data_handler.returns['Daily'])}

    def get_mkt_data(self):
        self.get_include_mkt_data()
        self.mkt_returns = {'Daily': copy_data(self.data_handler.mkt_returns['Daily'])}
        self.mkt_key = copy_data(self.data_handler.mkt_key)

    def get_analytics(self):
        self.ra.get_hist_selloff()

    def format_data(self):
        self.reporting_data = {'selloffs': copy_data(self.ra.historical_selloff_data),
                               'returns': self.format_returns_data()}


class LiquidAltsAnalyticSummary(AnalyticsSummary):

    def __init__(self, data_handler, full_port=False, sub_port='Global Macro', add_composite_data=True,
                 include_bmk=True, include_fi=True, include_cm=True, include_fx=True,
                 include_dd=False, include_quantile=False, include_best_worst_pd=False, include_roll_stats=False):
        """

        Args:
            data_handler: LiqAltsPortHandler instance
            full_port: bool
            sub_port: string
            add_composite_data: bool
            include_bmk: bool
            include_fi: bool
            include_cm: bool
            include_fx: bool
        """
        self.full_port = full_port
        self.sub_port = sub_port
        self.add_composite_data = add_composite_data
        self.include_cm = include_cm
        self.include_fx = include_fx
        self.include_dd = include_dd
        self.include_best_worst_pd = include_best_worst_pd
        self.include_quantile = include_quantile
        self.include_roll_stats = include_roll_stats

        super().__init__(data_handler, include_bmk=include_bmk, include_eq=True, include_fi=include_fi)

        self.period_list = list(self.returns.keys())

    def get_ra(self):
        self.ra = ra.LiquidAltsPeriodAnalytic(returns_dict=self.returns, include_bmk=self.include_bmk,
                                              bmk_data=self.bmk_returns, bmk_key=self.bmk_key,
                                              include_fi=self.include_fi, include_cm=self.include_cm,
                                              include_fx=self.include_fx,
                                              mkt_data=self.mkt_returns, mkt_key=self.mkt_key)

    def get_return_data(self):
        if self.full_port:
            self.returns = dm.get_period_dict(self.data_handler.returns)
        else:
            return_data = copy_data(self.data_handler.sub_ports[self.sub_port]['returns'])
            if self.add_composite_data and self.sub_port != 'Total Liquid Alts':
                sub_port_data = copy_data(self.data_handler.sub_ports['Total Liquid Alts']['returns'])
                return_data = dm.merge_dfs(return_data, sub_port_data, False)
            self.returns = dm.get_period_dict(return_data)

    def get_include_mkt_data(self):
        if self.data_handler.include_eq is False:
            self.include_eq = self.data_handler.include_eq
        if self.data_handler.include_fi is False:
            self.include_fi = self.data_handler.include_fi
        if self.data_handler.include_cm is False:
            self.include_cm = self.data_handler.include_cm
        if self.data_handler.include_fx is False:
            self.include_fx = self.data_handler.include_fx

    def get_analytics(self):
        sub_list_data = {'ret_stats': ['up_down_dev', 'ret_vol', 'sortino', 'ret_dd'],
                         'active_stats': ['bmk_beta', 'te_downside_te', 'ir', 'ir_asym'],
                         'mkt_stats': ['beta', 'corr']
                         }
        self.ra.get_corr_stats_dict(self.ra.get_key_list(self.period_list))
        self.ra.get_mkt_stats_dict(self.ra.get_key_list(self.period_list))
        self.ra.get_returns_stats_dict(self.ra.get_key_list(self.period_list, []))
        if self.include_dd is True:
            self.ra.get_dd_stats()
        if self.include_roll_stats is True:
            self.ra.get_roll_stats(sub_list_data)
        if self.include_quantile is True:
            self.ra.get_quantile_stats()
        if self.include_best_worst_pd is True:
            self.ra.get_best_worst_pd_stats()

    def format_data(self):
        # self.reporting_data = {}
        analytics_dict = {}
        correlations_dict = {}
        for period in self.returns:
            try:
                analytics_dict[period] = self.format_analytics_data(period)
                correlations_dict[period] = self.format_corr_stats_data(period)
            except KeyError:
                pass
        self.reporting_data = {'analytics': analytics_dict, 'correlations': correlations_dict,
                               'returns': self.format_returns_data(), 'mtd_ytd_itd': self.format_monthly_returns_data()}
        if self.include_dd is True:
            self.reporting_data['drawdowns'] = self.format_dd_stats_data()
        if self.include_quantile is True:
            self.reporting_data['quantiles'] = self.format_quantile_stats_data()
        if self.include_best_worst_pd is True:
            self.reporting_data['best_worst_pd'] = self.format_best_worst_pd_data()
        if self.include_roll_stats is True:
            self.reporting_data['rolling_stats'] = self.format_roll_stats_data()

    def format_analytics_data(self, period):
        partial_stats = False
        if period.__eq__('3 Year') or period.__eq__('1 Year'):
            partial_stats = True
        return {'return_stats': self.format_returns_stats_data(period),
                'market_stats': self.format_mkt_stats_data(period, partial_stats)}

    def format_returns_stats_data(self, period):
        returns_stats_data = copy_data(self.ra.returns_stats_dict[period])
        ret_stats_idx_list = ['Time Frame', 'No. of Monthly Observations', 'Bmk Name', 'Annualized Return',
                              'Excess Return (Ann)', 'Bmk Beta', 'Median Period Return', 'Avg. Period Return',
                              'Avg. Period Up Return', 'Avg. Period Down Return', 'Avg Pos Return/Avg Neg Return',
                              'Best Period', 'Worst Period', '% Positive Periods', '% Negative Periods',
                              'Annualized Volatility',
                              'Upside Deviation', 'Downside Deviation', 'Tracking Error (TE)', 'Downside TE',
                              'Upside to Downside Deviation Ratio', 'Vol to Downside Deviation Ratio',
                              'TE to Downside TE Ratio', 'Skewness', 'Kurtosis', 'Max DD', 'Return/Volatility',
                              'Sortino Ratio', 'Return/Max DD', 'Information Ratio (IR)', 'Asymmetric IR']
        if self.include_bmk is False:
            ret_stats_idx_list = [stat for stat in ret_stats_idx_list if stat not in list(ra.ACTIVE_COL_DICT.values())]
        return returns_stats_data.reindex(index=ret_stats_idx_list)
        # return {'ret_stats_df': returns_stats_data.reindex(index=ret_stats_idx_list),
        #         'title': f'Returns Statistics ({period})'}

    def format_mkt_stats_data(self, period, partial_stats=False):
        mkt_stats_data = copy_data(self.ra.mkt_stats_dict[period])
        mkt_stats_idx_list = ['EQ Alpha', 'EQ Beta', 'EQ Correlation', 'FI Alpha', 'FI Beta', 'FI Correlation',
                              'CM Alpha', 'CM Beta', 'CM Correlation', 'FX Alpha', 'FX Beta', 'FX Correlation']
        if period.__eq__('3 Year') or period.__eq__('1 Year'):
            mkt_stats_data = mkt_stats_data.reindex(index=mkt_stats_idx_list)
        # return {'mkt_stats_df': mkt_stats_data, 'title': f'Market Statistics ({period})'}
        return mkt_stats_data

    def format_corr_stats_data(self, period):
        corr_stats_data = copy_data(self.ra.corr_stats_dict[period])
        if period.__eq__('3 Year'):
            return {key: corr_stats_data[key] for key in [self.ra.main_key]}
        else:
            return corr_stats_data

    def format_dd_stats_data(self):
        formatted_data = {}
        for dd_key, dd_stats_data in self.ra.dd_stats_data.items():
            if 'dd_matrix' in dd_key:
                formatted_data[dd_key] = dd_stats_data
            if 'co_dd' in dd_key:
                temp_dd_dict = {}
                for strat in dd_stats_data:
                    temp_dd_dict[strat] = {strat: dd_stats_data[strat], 'title': f'{strat} Co-Drawdown Table'}
                formatted_data[dd_key] = temp_dd_dict
            if dd_key.__eq__('dd_dict'):
                temp_dd_dict = {}
                for strat in dd_stats_data:
                    num_dd = len(dd_stats_data[strat])
                    temp_dd_dict[strat] = {strat: dd_stats_data[strat],
                                           'title': f'{strat} {num_dd} Worst Drawdowns'}
                formatted_data[dd_key] = temp_dd_dict
        formatted_data['co_dd'] = formatted_data['mkt_co_dd_dict'] | formatted_data['co_dd_dict']
        return dm.filter_data_dict(formatted_data, ['dd_matrix', 'co_dd', 'dd_dict'])

    def format_rolling_return_stats_data(self, rolling_stats_data, window):
        formatted_data = {}
        for key in rolling_stats_data:
            formatted_data[key] = {key: rolling_stats_data[key],
                                   'title': f'Rolling {window}{self.ra.freq} {ra.PORT_COL_DICT[key]}'}
        return formatted_data

    def format_rolling_active_stats_data(self, rolling_stats_data, window):
        formatted_data = {}
        for key in rolling_stats_data:
            formatted_data[key] = {key: rolling_stats_data[key],
                                   'title': f'Rolling {window}{self.ra.freq} {ra.ACTIVE_COL_DICT[key]}'}
        return formatted_data

    def format_rolling_mkt_stats_data(self, rolling_stats_data, window):
        formatted_data = {}
        for mkt_stat in rolling_stats_data:
            rolling_mkt_data = rolling_stats_data[mkt_stat]
            rolling_mkt_dict = {}
            for asset_class in self.mkt_key:
                rolling_mkt_df = pd.DataFrame()
                for strat in rolling_mkt_data:
                    rolling_mkt_df = pd.concat([rolling_mkt_df, rolling_mkt_data[strat][asset_class]],
                                               axis=1)
                rolling_mkt_df.columns = list(rolling_mkt_data.keys())
                rolling_mkt_df = rolling_mkt_df.sort_index()
                title = self.format_rolling_title('mkt_stats', mkt_stat, window)
                rolling_mkt_dict[asset_class] = {asset_class: rolling_mkt_df,
                                                 'title': title + f' to {asset_class} Market'}
            formatted_data[mkt_stat] = rolling_mkt_dict
        return formatted_data

    def format_rolling_title(self, roll_stats, key, window):
        roll_title_dict = {'ret_stats': ra.PORT_COL_DICT, 'active_stats': ra.ACTIVE_COL_DICT,
                           'mkt_stats': ra.MKT_COL_DICT["analytics"]}
        return f'Rolling {window}{self.ra.freq} {roll_title_dict[roll_stats][key]}'

    def format_roll_stats_data(self):
        roll_data = copy_data(self.ra.roll_stats_data)
        roll_stats_function_dict = {'ret_stats': self.format_rolling_return_stats_data,
                                    'active_stats': self.format_rolling_active_stats_data,
                                    'mkt_stats': self.format_rolling_mkt_stats_data
                                    }
        roll_stats_data = {}
        window = self.ra.rolling_years * dm.switch_freq_int(self.ra.freq)
        for key in roll_data:
            try:
                roll_format_function = roll_stats_function_dict[key]
                kwargs = {'rolling_stats_data': roll_data[key],
                          'window': window}
                roll_stats_data[key] = roll_format_function(*kwargs.values())
            except KeyError:
                pass
        return roll_stats_data

    def format_quantile_stats_data(self):
        return {'returns_data': self.format_ret_quantile_data(),
                'mkt_data': self.format_mkt_quantile_data()}

    def format_best_worst_pd_data(self):
        best_worst_mkt_pd_data = {}
        for period, period_dict in self.ra.best_worst_period_stats_data.items():
            best_worst_mkt_pd_data[period] = period_dict['mkt_data']
        return best_worst_mkt_pd_data

    # def format_best_pd_data(self):
    #     for key, data_dict in self.ra.best_worst_period_stats_data['worst'.items():
    #
    #     return {'worst_mkt_periods': self.ra.best_worst_period_stats_dict}
    #
    # def formatworst_pd_data(self):
    #     return {'worst_mkt_periods': self.ra.best_worst_period_stats_dict}

    def format_returns_data(self):
        if self.include_bmk:
            returns_data = dm.merge_df_lists(df_list=[self.mkt_returns, self.bmk_returns,
                                                      self.returns[self.ra.main_key]], drop_na=False, how='inner')
        else:
            returns_data = dm.merge_dfs(self.mkt_returns, self.returns[self.ra.main_key], drop_na=False, how='inner')

        return get_data_dict(returns_data, drop_na=False)

    def format_monthly_returns_data(self):
        df_list = [self.ra.bmk_df, self.ra.returns_df] if self.include_bmk else [self.ra.returns_df]
        monthly_returns_data = dm.merge_df_lists([*[self.ra.mkt_ret_data], *df_list], drop_na=False)
        return self.get_mtd_ytd_itd_returns_dict(monthly_returns_data)


class LiquidAltsStratSummary(LiquidAltsAnalyticSummary):

    def __init__(self, data_handler, include_hf=False, include_fi=True, include_cm=True, include_fx=True,
                 include_dd=False, include_quantile=False, include_best_worst_pd=False, include_roll_stats=False):
        self.include_hf = include_hf
        self.data_handler = self.add_bmk_data(data_handler)
        super().__init__(data_handler=self.data_handler, full_port=True, include_bmk=True,
                         include_fi=include_fi, include_cm=include_cm, include_fx=include_fx, include_dd=include_dd,
                         include_quantile=include_quantile, include_best_worst_pd=include_best_worst_pd,
                         include_roll_stats=include_roll_stats)
        self.hf_ra = None
        if self.include_hf:
            self.get_hf_analytic()

    @staticmethod
    def add_bmk_data(data_handler):
        updated_dh = deepcopy(data_handler)
        updated_dh.returns = dm.merge_dfs(updated_dh.returns, updated_dh.bmk_returns[[updated_dh.bmk_name]])
        return updated_dh

    def get_hf_analytic(self):
        self.data_handler.get_hf_returns()
        strat_list = self.data_handler.col_list
        returns_data = dm.merge_dfs(self.data_handler.returns[strat_list], self.data_handler.hf_returns, drop_na=True,
                                    how='inner')
        period_data = dm.get_period_dict(returns_data)
        self.hf_ra = ra.LiquidAltsPeriodAnalytic(returns_dict=period_data, include_bmk=False,
                                                 include_fi=self.include_fi, include_cm=self.include_cm,
                                                 include_fx=self.include_fx, mkt_data=self.mkt_returns,
                                                 mkt_key=self.mkt_key)

    def get_analytics(self):
        if self.include_hf:
            self.hf_ra.get_corr_stats()
        self.ra.get_mkt_stats_dict(self.period_list)
        self.ra.get_returns_stats_dict(self.period_list)
        self.ra.get_dd_stats()

    def format_data(self):
        self.reporting_data = {'analytics': self.format_analytics_data(),
                               'drawdowns': self.format_dd_stats_data(),
                               'returns': self.format_returns_data()}
        if self.include_hf:
            self.reporting_data['correlations'] = copy_data(self.hf_ra.corr_stats_data)
            self.reporting_data['returns'] = get_data_dict(dm.merge_dfs(self.hf_ra.mkt_ret_data, self.hf_ra.returns_df))

    def format_analytics_data(self):
        col_list_1 = list(self.returns.keys())
        col_list_1[0] = 'Since Inception'
        col_list_2 = list(self.data_handler.returns.columns)
        header = pd.MultiIndex.from_product([col_list_1, col_list_2])
        returns_stats_df = self.format_analytic_df(header)
        if self.include_bmk:
            returns_stats_df.drop(['Bmk Name', 'No. of Monthly Observations'], inplace=True)
        market_stats_df = self.format_analytic_df(header, return_stats=False)

        return {'return_stats': returns_stats_df, 'market_stats': market_stats_df}

    def format_analytic_df(self, header, return_stats=True):
        analytics_df = pd.DataFrame()
        for period in self.returns:
            # get analytics
            if return_stats:
                analytics_data = self.format_returns_stats_data(period)
            else:
                analytics_data = self.format_mkt_stats_data(period, partial_stats=True)
            analytics_data.columns = [f'port_{period}', f'bench_{period}']
            analytics_df = dm.merge_dfs(analytics_df, analytics_data, drop_na=False, how='right')
        analytics_df.columns = header
        return analytics_df

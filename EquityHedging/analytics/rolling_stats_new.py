# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 14:51:37 2024

@author: NVG9HXP
"""

from inspect import signature
import pandas as pd
from . import returns_stats_new as rs
from ..datamanager import data_manager_new as dm

RET_STATS_DICT = {'ann_ret': 'get_ann_return', 'median_ret': 'get_median',
                  'avg_ret': 'get_mean', 'avg_pos_ret': 'get_avg_pos_neg',
                  'avg_neg_ret': 'get_avg_pos_neg', 'avg_pos_neg_ret': 'get_avg_pos_neg_ratio',
                  'best_period': 'get_max', 'worst_period': 'get_min',
                  'pct_pos_periods': 'get_pct_pos_neg_periods', 'pct_neg_periods': 'get_pct_pos_neg_periods',
                  'ann_vol': 'get_ann_vol', 'up_dev': 'get_updown_dev',
                  'down_dev': 'get_updown_dev', 'up_down_dev': 'get_up_down_dev_ratio',
                  'skew': 'get_skew', 'kurt': 'get_kurtosis', 'max_dd': 'get_max_dd',
                  'ret_vol': 'get_sharpe_ratio', 'sortino': 'get_sortino_ratio',
                  'ret_dd': 'get_ret_max_dd_ratio', 'var': 'get_var', 'cvar': 'get_cvar'
                  }

RET_STAT_KWARGS_DICT = {'avg_neg_ret': {'pos': False}, 'pct_neg_periods': {'pos': False}, 'down_dev': {'up': False}}


# RET_STATS_FREQ_LIST = ['ann_ret', 'ann_vol', 'up_dev', 'down_dev', 'up_down_dev', 'ret_vol', 'sortino', 'ret_dd']
# RET_STATS_LIST = ['median_ret', 'avg_ret', 'avg_pos_ret', 'avg_neg_ret', 'avg_pos_neg_ret', 'best_period',
#                   'worst_period', 'pct_pos_periods', 'pct_neg_periods', 'skew', 'kurt', 'max_dd', 'var', 'cvar']


# def get_arg_no(function):
#     sig = signature(function)
#     params = sig.parameters
#     return len(params)


class RollingStats:
    def __init__(self, returns_df, years=3, rfr=0.0, target=0.0, p=0.05):

        self.returns_df = returns_df
        self.freq = dm.get_freq(self.returns_df)
        self.years = years
        self.window = self.get_window_len()
        self.rfr = rfr
        self.target = target
        self.p = p
        self.rs_obj = rs.ReturnsStats(freq=self.freq, rfr=self.rfr, target=self.target, p=self.p)
        # self.rolling_stats = None
        # self.rolling_data = {}

    # def get_rolling_data(self, sub_list_data=None):
    #     if sub_list_data is None:
    #         sub_list_data = {'ret_stats': None, 'mkt_stats': None, 'active_stats': None}
    #
    #     self.get_rolling_stat_data(sub_list_data['ret_stats'])

    def get_window_len(self):
        return int(self.years * dm.switch_freq_int(self.freq))

    @staticmethod
    def get_clean_series(data_series, name):
        data_series.dropna(inplace=True)
        data_series.name = name
        return data_series

    def get_method_data(self, ret_stat):
        method_name = RET_STATS_DICT.get(ret_stat)
        method = getattr(self.rs_obj, method_name)
        kwargs = {}
        if method_name in RET_STAT_KWARGS_DICT.keys():
            kwargs = RET_STAT_KWARGS_DICT[method_name]
        return {'method': method, 'kwargs': kwargs}

    def get_rolling_series(self, return_series, method, kwargs=None):
        if kwargs is None:
            kwargs = {}
        return return_series.rolling(self.window).apply(method, kwargs=kwargs)

    def get_rolling_stat(self, return_series, ret_stat):
        method_dict = self.get_method_data(ret_stat)
        rolling_stat_series = self.get_rolling_series(return_series=return_series, method=method_dict['method'],
                                                      kwargs=method_dict['kwargs'])
        return self.get_clean_series(rolling_stat_series, return_series.name)

    def get_rolling_stat_df(self, ret_stat):
        rolling_stat_df = pd.DataFrame()
        for strat in self.returns_df:
            rolling_stat_df = pd.concat([rolling_stat_df, self.get_rolling_stat(self.returns_df[strat], ret_stat)],
                                        axis=1)
        rolling_stat_df = rolling_stat_df.sort_index()
        return rolling_stat_df

    def get_rolling_stat_data(self, sub_list=None):
        if sub_list is None:
            sub_list = list(RET_STATS_DICT.keys())
        print(f'Computing {self.window}{self.freq} rolling return stats')
        rolling_stats = {}
        for ret_stat in sub_list:
            rolling_stats[ret_stat] = self.get_rolling_stat_df(ret_stat)
        return rolling_stats
        # self.rolling_data['ret_stats'] = self.rolling_stats


class RollingCorrStats(RollingStats):
    def __init__(self, returns_df, years=3, rfr=0.0, target=0.0, p=0.05):

        super().__init__(returns_df, years, rfr, target, p)

        # self.rolling_corr_stats = None

    # def get_rolling_data(self, sub_list_data=None):
    #     if sub_list_data is None:
    #         sub_list_data = {'ret_stats': None, 'mkt_stats': None, 'active_stats': None}
    #
    #     self.get_rolling_stat_data(sub_list_data['ret_stats'])
    #     self.get_rolling_corr_data()

    def get_rolling_corr(self, ret_series_1, ret_series_2):
        """
        Get rolling correlation between 2 return series

        Parameters
        ----------
        ret_series_1 : Series
            returns.
        ret_series_2 : Series
            returns.

        Returns
        -------
        rolling_corr : series
            correlation series.

        """
        rolling_corr_series = ret_series_1.rolling(self.window).corr(ret_series_2)
        return self.get_clean_series(rolling_corr_series, ret_series_2.name)

    def get_rolling_corr_df(self, return_series, returns_df):
        rolling_corr_df = pd.DataFrame()
        for strat in returns_df:
            rolling_corr_series = self.get_rolling_corr(return_series, returns_df[strat])
            # do not include correlation of same return_series
            if len(rolling_corr_series) == round(rolling_corr_series.sum()):
                pass
            else:
                rolling_corr_df = pd.concat([rolling_corr_df, rolling_corr_series], axis=1)
                rolling_corr_df = rolling_corr_df.sort_index()
        return rolling_corr_df

    def get_rolling_corr_data(self):
        """
        Get a dictionary containing rolling correlations of each strategy in df_returns vs the other strategies

        Returns
        -------
        rolling_corr_dict : Dictionary
            DESCRIPTION.

        """
        print(f'Computing {self.window}{self.freq} rolling correlation stats')
        rolling_corr_stats = {}
        for strat in self.returns_df:
            rolling_corr_stats[strat] = self.get_rolling_corr_df(self.returns_df[strat], self.returns_df)
        # self.rolling_data['corr_stats'] = self.rolling_corr_stats
        return rolling_corr_stats


class RollingMarketStats(RollingCorrStats):
    def __init__(self, returns_df, mkt_df, years=3, rfr=0.0, target=0.0, p=0.05):

        super().__init__(returns_df, years, rfr, target, p)

        self.mkt_df = mkt_df
        # self.rolling_mkt_stats = None

    # def get_rolling_data(self, sub_list_data=None):
    #     if sub_list_data is None:
    #         sub_list_data = {'ret_stats': None, 'mkt_stats': None, 'active_stats': None}
    #
    #     self.get_rolling_stat_data(sub_list_data['ret_stats'])
    #     self.get_rolling_corr_data()
    #     self.get_rolling_mkt_data(sub_list_data['mkt_stats'])

    def get_rolling_beta(self, return_series, mkt_series):
        rolling_beta_series = return_series.rolling(self.window).cov(mkt_series) / mkt_series.rolling(self.window).var()
        return self.get_clean_series(rolling_beta_series, mkt_series.name)

    def get_rolling_alpha(self, return_series, mkt_series):
        rolling_beta_series = self.get_rolling_beta(return_series, mkt_series)
        rolling_mkt_ret_series = self.get_rolling_stat(mkt_series, 'ann_ret')
        rolling_ret_series = self.get_rolling_stat(return_series, 'ann_ret')
        rolling_alpha_series = (rolling_ret_series
                                - (self.rfr + rolling_beta_series * (rolling_mkt_ret_series - self.rfr)))
        return self.get_clean_series(rolling_alpha_series, mkt_series.name)

    def get_rolling_mkt_df(self, return_series, alpha=False):
        rolling_mkt_df = pd.DataFrame()
        for mkt in self.mkt_df:
            if alpha:
                rolling_mkt_series = self.get_rolling_alpha(return_series, self.mkt_df[mkt])
            else:
                rolling_mkt_series = self.get_rolling_beta(return_series, self.mkt_df[mkt])
            rolling_mkt_df = pd.concat([rolling_mkt_df, rolling_mkt_series], axis=1)
            rolling_mkt_df = rolling_mkt_df.sort_index()
        return rolling_mkt_df

    def get_rolling_mkt_data(self, sub_list=None):
        print(f'Computing {self.window}{self.freq} rolling mkt stats')

        rolling_mkt_method_dict = {'alpha': self.get_rolling_mkt_df, 'beta': self.get_rolling_mkt_df,
                                   'corr': self.get_rolling_corr_df
                                   }
        rolling_mkt_stats = {}
        if sub_list is None:
            sub_list = list(rolling_mkt_method_dict.keys())
        for mkt_stat in sub_list:
            # make a dict to collect the data
            rolling_data = {}
            mkt_method = rolling_mkt_method_dict.get(mkt_stat)
            # iterate through items
            for strat in self.returns_df:
                try:
                    kwargs = {'return_series': self.returns_df[strat]}
                    if mkt_stat == 'corr':
                        kwargs['returns_df'] = self.mkt_df
                    else:
                        kwargs['alpha'] = True if mkt_stat == 'alpha' else False
                    rolling_df = mkt_method(*kwargs.values())
                    if rolling_df.empty is False:
                        rolling_data[strat] = rolling_df.sort_index()
                except KeyError:
                    print(f'Missing {mkt_stat} data for {strat}...check mkt_df')
                    pass
            rolling_mkt_stats[mkt_stat] = rolling_data
        # self.rolling_data['mkt_stats'] = self.rolling_mkt_stats
        return rolling_mkt_stats


class RollingActiveStats(RollingMarketStats):
    def __init__(self, returns_df, bmk_df=pd.DataFrame(), bmk_key=None,
                 mkt_df=pd.DataFrame(), years=3, rfr=0.0, target=0.0, p=0.05):
        super().__init__(returns_df, mkt_df, years, rfr, target, p)
        if bmk_key is None:
            bmk_key = {}
        self.bmk_df = bmk_df
        self.bmk_key = bmk_key
        self.active_stats_dict = self.get_active_stats_dict()

        # self.rolling_active_stats = None

    # def get_rolling_data(self, sub_list_data=None):
    #     if sub_list_data is None:
    #         sub_list_data = {'ret_stats': None, 'mkt_stats': None, 'active_stats': None}
    #
    #     self.get_rolling_stat_data(sub_list_data['ret_stats'])
    #     self.get_rolling_corr_data()
    #     self.get_rolling_mkt_data(sub_list_data['mkt_stats'])
    #     self.get_rolling_active_data(sub_list_data['active_stats'])

    @staticmethod
    def get_active_data(return_series, bmk_series):
        df_port_bmk = dm.merge_dfs(return_series, bmk_series)
        name_key = {'port': return_series.name, 'bmk': bmk_series.name}
        active_series = df_port_bmk[name_key['port']] - df_port_bmk[name_key['bmk']]
        active_series.name = name_key['port']
        return {'port': df_port_bmk[name_key['port']], 'bmk': df_port_bmk[name_key['bmk']], 'active': active_series}

    def get_active_stats_dict(self):
        return {'bmk_beta': self.get_rolling_bmk_beta, 'excess_ret': self.get_rolling_excess_ret,
                'te': self.get_rolling_te, 'downside_te': self.get_rolling_te,
                'te_downside_te': self.get_rolling_te_dwn_te, 'ir': self.get_rolling_ir, 'ir_asym': self.get_rolling_ir
                }

    def get_rolling_active_data(self, sub_list):
        print(f'Computing {self.window}{self.freq} rolling active stats')
        rolling_active_stats = {}
        if sub_list is None:
            sub_list = list(self.active_stats_dict.keys())
        for active_stat in sub_list:
            rolling_active_stats[active_stat] = self.get_rolling_active_df(active_stat)
        # self.rolling_data['active_stats'] = self.rolling_active_stats
        return rolling_active_stats

    def get_rolling_active_df(self, active_stat='bmk_beta'):
        # make a df to collect the data
        rolling_active_df = pd.DataFrame()
        # iterate through items
        for strat in self.returns_df:
            try:
                bmk_name = self.bmk_key[strat]
                active_dict = self.get_active_data(self.returns_df[strat], self.bmk_df[bmk_name])
                rolling_active_series = self.get_rolling_active_stat(active_dict, active_stat)
                rolling_active_df = pd.concat([rolling_active_df, rolling_active_series], axis=1)
                rolling_active_df = rolling_active_df.sort_index()
            except KeyError:
                print(f'Missing bmk data for {strat}...check bmk_df or bmk_key')
                pass
        return rolling_active_df

    def get_rolling_active_stat(self, active_dict, active_stat='bmk_beta'):
        active_function = self.active_stats_dict.get(active_stat)
        kwargs = {'active_dict': active_dict}
        if 'te' in active_stat:
            kwargs['downside'] = False if active_stat.__eq__('te') else True
        if 'ir' in active_stat:
            kwargs['asym'] = False if active_stat.__eq__('ir') else True
        return active_function(*kwargs.values())

    def get_rolling_bmk_beta(self, active_dict):
        rolling_beta = self.get_rolling_beta(active_dict['port'], active_dict['bmk'])
        return self.get_clean_series(rolling_beta, active_dict['port'].name)

    def get_rolling_excess_ret(self, active_dict):
        rolling_excess_ret = (self.get_rolling_stat(active_dict['port'], 'ann_ret')
                              - self.get_rolling_stat(active_dict['bmk'], 'ann_ret'))
        return self.get_clean_series(rolling_excess_ret, active_dict['port'].name)

    def get_rolling_te(self, active_dict, downside=False):
        if downside:
            return self.get_rolling_stat(active_dict['active'], 'down_dev')
        else:
            return self.get_rolling_stat(active_dict['active'], 'ann_vol')

    def get_rolling_te_dwn_te(self, active_dict, downside=True):
        return self.get_rolling_te(active_dict) / self.get_rolling_te(active_dict, downside)

    def get_rolling_ir(self, active_dict, asym=False):
        rolling_excess_ret = self.get_rolling_excess_ret(active_dict)
        rolling_te = self.get_rolling_te(active_dict, downside=asym)
        return self.get_clean_series(rolling_excess_ret / rolling_te, active_dict['port'].name)

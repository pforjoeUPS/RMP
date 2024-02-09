# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 14:51:37 2024

@author: NVG9HXP
"""

from inspect import signature
import pandas as pd
from . import returns_stats_new as rs
from ..datamanager import data_manager_new as dm

RET_STATS_DICT = {'ann_ret': rs.get_ann_return, 'median_ret': rs.get_median,
                  'avg_ret': rs.get_mean, 'avg_pos_ret': rs.get_avg_pos_neg,
                  'avg_neg_ret': rs.get_avg_pos_neg, 'avg_pos_neg_ret': rs.get_avg_pos_neg_ratio,
                  'best_period': rs.get_max, 'worst_period': rs.get_min,
                  'pct_pos_periods': rs.get_pct_pos_neg_periods, 'pct_neg_periods': rs.get_pct_pos_neg_periods,
                  'ann_vol': rs.get_ann_vol, 'up_dev': rs.get_updown_dev,
                  'down_dev': rs.get_updown_dev, 'up_down_dev': rs.get_up_down_dev_ratio,
                  'skew': rs.get_skew, 'kurt': rs.get_kurtosis, 'max_dd': rs.get_max_dd,
                  'ret_vol': rs.get_sharpe_ratio, 'sortino': rs.get_sortino_ratio,
                  'ret_dd': rs.get_ret_max_dd_ratio, 'var': rs.get_var, 'cvar': rs.get_cvar
                  }

RET_STATS_FREQ_LIST = ['ann_ret', 'ann_vol', 'up_dev', 'down_dev', 'up_down_dev', 'ret_vol', 'sortino', 'ret_dd']
RET_STATS_LIST = ['median_ret', 'avg_ret', 'avg_pos_ret', 'avg_neg_ret', 'avg_pos_neg_ret', 'best_period',
                  'worst_period', 'pct_pos_periods', 'pct_neg_periods', 'skew', 'kurt', 'max_dd', 'var', 'cvar']


def get_rolling_data(returns_df, years=3, sub_list_data=None, rfr=0.0, target=0.0, p=0.05, include_bmk=False,
                     bmk_df=pd.DataFrame(), bmk_key={}, include_mkt=False, mkt_df=pd.DataFrame()):
    if sub_list_data is None:
        sub_list_data = {'ret_stats': None, 'mkt_stats': None, 'active_stats': None}

    roll_stats = RollingActiveStats(returns_df, bmk_df, bmk_key, mkt_df, years, rfr, target, p)

    roll_stats.get_rolling_stat_data(sub_list_data['ret_stats'])
    roll_stats.get_rolling_corr_data()

    if include_mkt:
        roll_stats.get_rolling_mkt_data(sub_list_data['mkt_stats'])

    if include_bmk:
        roll_stats.get_rolling_active_data(sub_list_data['active_stats'])

    return roll_stats.rolling_data


def get_arg_no(function):
    sig = signature(function)
    params = sig.parameters
    return len(params)


def get_clean_series(data_series, name):
    data_series.dropna(inplace=True)
    data_series.name = name
    # data_series = data_series.sort_index()
    return data_series


def get_rolling_series(data_series, window, function, kwargs={}):
    return data_series.rolling(window).apply(function, kwargs=kwargs)


def get_active_data(return_series, bmk_series):
    df_port_bmk = dm.merge_dfs(return_series, bmk_series)
    name_key = {'port': return_series.name, 'bmk': bmk_series.name}
    active_series = df_port_bmk[name_key['port']] - df_port_bmk[name_key['bmk']]
    active_series.name = name_key['port']
    return {'port': df_port_bmk[name_key['port']], 'bmk': df_port_bmk[name_key['bmk']], 'active': active_series}


class RollingStats:
    def __init__(self, returns_df, years=3, rfr=0.0, target=0.0, p=0.05):

        self.returns_df = returns_df
        self.freq = dm.get_freq(self.returns_df)
        self.years = years
        self.window = self.get_window_len()
        self.rfr = rfr
        self.target = target
        self.p = p

        self.rolling_stats = None
        self.rolling_data = {}

    def get_window_len(self):
        return int(self.years * dm.switch_freq_int(self.freq))

    def get_function_data(self, ret_stat):
        function = RET_STATS_DICT.get(ret_stat)
        func_len = get_arg_no(function)
        kwargs = {}
        if ret_stat in RET_STATS_LIST:
            if func_len == 2:
                if 'neg' in ret_stat:
                    kwargs = {'pos': False}
                elif 'var' in ret_stat:
                    kwargs = {'p': self.p}
        elif ret_stat in RET_STATS_FREQ_LIST:
            if func_len < 3:
                kwargs = {'freq': self.freq}
            elif func_len > 3 and ret_stat == 'sortino':
                kwargs = {'freq': self.freq, 'target': self.target, 'rfr': self.rfr}
            elif ret_stat == 'ret_vol':
                kwargs = {'freq': self.freq, 'rfr': self.rfr}
            else:
                kwargs = {'freq': self.freq, 'target': self.target}
        return {'function': function, 'kwargs': kwargs}

    def get_rolling_stat(self, return_series, ret_stat):
        function_dict = self.get_function_data(ret_stat)
        rolling_stat_series = get_rolling_series(return_series, self.window, function_dict['function'],
                                                 function_dict['kwargs'])
        return get_clean_series(rolling_stat_series, return_series.name)

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
        self.rolling_stats = {}
        for ret_stat in sub_list:
            self.rolling_stats[ret_stat] = self.get_rolling_stat_df(ret_stat)
        self.rolling_data['ret_stats'] = self.rolling_stats
        # return rolling_stats


class RollingCorrStats(RollingStats):
    def __init__(self, returns_df, years=3, rfr=0.0, target=0.0, p=0.05):

        super().__init__(returns_df, years, rfr, target, p)

        self.rolling_corr_stats = None

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
        return get_clean_series(rolling_corr_series, ret_series_2.name)

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
        self.rolling_corr_stats = {}
        for strat in self.returns_df:
            self.rolling_corr_stats[strat] = self.get_rolling_corr_df(self.returns_df[strat], self.returns_df)
        self.rolling_data['corr_stats'] = self.rolling_corr_stats
        # return rolling_corr_stats


class RollingMarketStats(RollingCorrStats):
    def __init__(self, returns_df, mkt_df, years=3, rfr=0.0, target=0.0, p=0.05):

        super().__init__(returns_df, years, rfr, target, p)

        self.mkt_df = mkt_df
        self.rolling_mkt_stats = None
        # self.rolling_beta_stats = None
        # self.rolling_alpha_stats = None
        # self.rolling_mkt_corr_stats = None

    def get_rolling_beta(self, return_series, mkt_series):
        rolling_beta_series = return_series.rolling(self.window).cov(mkt_series) / mkt_series.rolling(self.window).var()
        return get_clean_series(rolling_beta_series, mkt_series.name)

    def get_rolling_alpha(self, return_series, mkt_series):
        rolling_beta_series = self.get_rolling_beta(return_series, mkt_series)
        rolling_mkt_ret_series = self.get_rolling_stat(mkt_series, 'ann_ret')
        rolling_ret_series = self.get_rolling_stat(return_series, 'ann_ret')
        rolling_alpha_series = rolling_ret_series - (
                self.rfr + rolling_beta_series * (rolling_mkt_ret_series - self.rfr))
        return get_clean_series(rolling_alpha_series, mkt_series.name)

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

    # def get_rolling_alpha_data(self):
    #     self.rolling_alpha_stats = self.get_rolling_mkt_data('alpha')

    # def get_rolling_beta_data(self):
    #     self.rolling_beta_stats = self.get_rolling_mkt_data('beta')

    # def get_rolling_mkt_corr_data(self):
    #     self.rolling_mkt_corr_stats = self.get_rolling_mkt_data('corr')

    def get_rolling_mkt_data(self, sub_list=None):
        print(f'Computing {self.window}{self.freq} rolling mkt stats')

        rolling_mkt_dict = {'alpha': self.get_rolling_mkt_df,
                            'beta': self.get_rolling_mkt_df,
                            'corr': self.get_rolling_corr_df
                            }
        self.rolling_mkt_stats = {}
        if sub_list is None:
            sub_list = list(rolling_mkt_dict.keys())
        for mkt_stat in sub_list:
            # make a dict to collect the data
            rolling_data = {}
            mkt_function = rolling_mkt_dict.get(mkt_stat)
            # iterate through items
            for strat in self.returns_df:
                try:
                    kwargs = {'return_series': self.returns_df[strat]}
                    if mkt_stat == 'corr':
                        kwargs['returns_df'] = self.mkt_df
                    else:
                        kwargs['alpha'] = True if mkt_stat == 'alpha' else False
                    rolling_df = mkt_function(*kwargs.values())
                    if rolling_df.empty is False:
                        # rolling_mkt_df = rolling_mkt_df.sort_index()
                        rolling_data[strat] = rolling_df.sort_index()
                except KeyError:
                    print(f'Missing {mkt_stat} data for {strat}...check mkt_df')
                    pass
            self.rolling_mkt_stats[mkt_stat] = rolling_data
        self.rolling_data['mkt_stats'] = self.rolling_mkt_stats


class RollingActiveStats(RollingMarketStats):
    def __init__(self, returns_df, bmk_df=pd.DataFrame(), bmk_key={},
                 mkt_df=pd.DataFrame(), years=3, rfr=0.0, target=0.0, p=0.05):
        super().__init__(returns_df, mkt_df, years, rfr, target, p, )
        self.bmk_df = bmk_df
        self.bmk_key = bmk_key
        self.active_stats_dict = self.get_active_stats_dict()

        self.rolling_active_stats = None

    def get_active_stats_dict(self):
        return {'bmk_beta': self.get_rolling_bmk_beta, 'excess_ret': self.get_rolling_excess_ret,
                'te': self.get_rolling_te, 'downside_te': self.get_rolling_te,
                'te_downside_te': self.get_rolling_te_dwn_te, 'ir': self.get_rolling_ir, 'ir_asym': self.get_rolling_ir
                }

    def get_rolling_active_data(self, sub_list):
        print(f'Computing {self.window}{self.freq} rolling active stats')
        self.rolling_active_stats = {}
        if sub_list is None:
            sub_list = list(self.active_stats_dict.keys())
        for active_stat in sub_list:
            self.rolling_active_stats[active_stat] = self.get_rolling_active_df(active_stat)
        self.rolling_data['active_stats'] = self.rolling_active_stats

    def get_rolling_active_df(self, active_stat='bmk_beta'):
        # make a df to collect the data
        rolling_active_df = pd.DataFrame()
        # iterate through items
        for strat in self.returns_df:
            try:
                bmk_name = self.bmk_key[strat]
                active_dict = get_active_data(self.returns_df[strat], self.bmk_df[bmk_name])
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
        return get_clean_series(rolling_beta, active_dict['port'].name)

    def get_rolling_excess_ret(self, active_dict):
        rolling_excess_ret = self.get_rolling_stat(active_dict['port'], 'ann_ret') - self.get_rolling_stat(
            active_dict['bmk'], 'ann_ret')
        return get_clean_series(rolling_excess_ret, active_dict['port'].name)

    def get_rolling_te(self, active_dict, downside=False):
        if downside:
            return self.get_rolling_stat(active_dict['active'], 'down_dev')
        else:
            return self.get_rolling_stat(active_dict['active'], 'ann_vol')

    def get_rolling_te_dwn_te(self, active_dict, downside=True):
        return self.get_rolling_te(active_dict)/self.get_rolling_te(active_dict, downside)

    def get_rolling_ir(self, active_dict, asym=False):
        rolling_excess_ret = self.get_rolling_excess_ret(active_dict)
        rolling_te = self.get_rolling_te(active_dict, downside=asym)
        return get_clean_series(rolling_excess_ret / rolling_te, active_dict['port'].name)


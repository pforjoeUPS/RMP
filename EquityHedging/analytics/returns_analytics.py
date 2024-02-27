# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 21:23:33 2022

@author: NVG9HXP
"""

# from copy import deepcopy
from itertools import compress

import pandas as pd

from . import corr_stats_new as cs
from . import drawdowns as dd
from . import hedge_metrics_new as hm
from . import returns_stats_new as rs
from . import rolling_stats_new as roll
from .period_stats import BestWorstPeriods
from .historical_selloffs_new import get_hist_sim_table
from .quantile_stats import get_all_quantile_data
# from .rolling_stats_new import get_rolling_data
from ..datamanager import data_xformer_new as dxf
from .util_new import convert_dict_to_df
from ..datamanager import data_manager_new as dm

ACTIVE_COL_DICT = {'bmk_name': 'Bmk Name', 'bmk_beta': 'Bmk Beta', 'excess_ret': 'Excess Return (Ann)',
                   'te': 'Tracking Error (TE)', 'downside_te': 'Downside TE',
                   'te_downside_te': 'TE to Downside TE Ratio',
                   'ir': 'Information Ratio (IR)', 'ir_asym': 'Asymmetric IR'}

PORT_COL_DICT = {'ann_ret': 'Annualized Return', 'median_ret': 'Median Period Return', 'avg_ret': 'Avg. Period Return',
                 'avg_pos_ret': 'Avg. Period Up Return', 'avg_neg_ret': 'Avg. Period Down Return',
                 'avg_pos_neg_ret': 'Avg Pos Return/Avg Neg Return',
                 'best_period': 'Best Period', 'worst_period': 'Worst Period', 'pct_pos_periods': '% Positive Periods',
                 'pct_neg_periods': '% Negative Periods', 'ann_vol': 'Annualized Volatility',
                 'up_dev': 'Upside Deviation',
                 'down_dev': 'Downside Deviation', 'up_down_dev': 'Upside to Downside Deviation Ratio',
                 'vol_down_dev': 'Vol to Downside Deviation Ratio',
                 'skew': 'Skewness', 'kurt': 'Kurtosis', 'max_dd': 'Max DD', 'max_1m_dd': 'Max 1M DD',
                 'max_1m_dd_date': 'Max 1M DD Date',
                 'max_3m_dd': 'Max 3M DD', 'max_3m_dd_date': 'Max 3M DD Date', 'ret_vol': 'Return/Volatility',
                 'sortino': 'Sortino Ratio', 'ret_dd': 'Return/Max DD', 'ret_1m_dd': 'Ret/Max 1M DD',
                 'ret_3m_dd': 'Ret/Max 3M DD'
                 }

MKT_COL_DICT = {'asset_id': {'Equity': 'EQ', 'Fixed Income': 'FI', 'Commodities': 'CM', 'FX': 'FX'},
                'analytics': {'alpha': 'Alpha', 'beta': 'Beta', 'up_beta': 'Upside Beta', 'dwn_beta': 'Downside Beta',
                              'corr': 'Correlation', 'up_corr': 'Upside Correlation',
                              'dwn_corr': 'Downside Correlation'}
                }


def get_time_frame(returns_df):
    """
    Returns a time frame (MM/DD/YYYY - MM/DD/YYYY) 
    for each strategy/manager in returns_df

    Parameters
    ----------
    returns_df : Dataframe
        returns data

    Returns
    -------
    period : Series
        Time frame--MM/DD/YYYY - MM/DD/YYYY

    """
    start = []
    end = []
    for i in range(len(returns_df.columns)):
        temp_start = returns_df.iloc[:, i].first_valid_index()
        temp_end = returns_df.iloc[:, i].last_valid_index()
        start.append(temp_start)
        end.append(temp_end)

    period = []
    for i in range(len(start)):
        per = start[i].strftime('%m/%d/%Y') + '-' + end[i].strftime('%m/%d/%Y')
        period.append(per)
    period = pd.Series(period, index=returns_df.columns)
    return period


def add_mkt_data(mkt_df, mkt_key, asset_class):
    return mkt_df[[mkt_key[asset_class]]]


def all_same(data_list):
    return len(set(data_list)) < 2


class ReturnsAnalytic:
    def __init__(self, returns_df, rfr=0.0, target=0.0, p=0.05, rolling_years=3,
                 include_bmk=False, bmk_df=pd.DataFrame(), bmk_key={},
                 include_eq=True, include_fi=False, mkt_df=pd.DataFrame(), mkt_key={}):

        self.returns_df = returns_df
        self.freq = dm.get_freq(self.returns_df)
        self.freq_string = dm.switch_freq_string(self.freq)
        self.rfr = rfr
        self.target = target
        self.p = p
        self.rolling_years = rolling_years
        self.include_bmk = include_bmk
        self.bmk_df = bmk_df
        self.bmk_key = bmk_key
        self.include_eq = include_eq
        self.include_fi = include_fi
        self.mkt_bool_dict = self.get_mkt_bool_data()
        self.mkt_key = mkt_key
        self.mkt_ret_data = self.get_mkt_ret_data(mkt_df)

        self.dd_stats_data = None
        self.corr_stats_data = None
        self.mkt_stats_data = None
        self.returns_stats_data = None
        self.roll_stats_data = None
        self.quantile_stats_data = None
        self.best_worst_period_stats_data = None

    def get_roll_stats(self, sub_list_data=None):
        if sub_list_data is None:
            sub_list_data = {'ret_stats': None, 'mkt_stats': None, 'active_stats': None}
        roll_stats = roll.RollingActiveStats(returns_df=self.returns_df, bmk_df=self.bmk_df, bmk_key=self.bmk_key,
                                             mkt_df=self.mkt_ret_data, years=self.rolling_years, rfr=self.rfr,
                                             target=self.target, p=self.p)
        self.roll_stats_data = {'ret_stats': roll_stats.get_rolling_stat_data(sub_list_data['ret_stats']),
                                'corr_stats': roll_stats.get_rolling_corr_data()}
        if any(self.mkt_bool_dict.values()):
            self.roll_stats_data['mkt_stats'] = roll_stats.get_rolling_mkt_data(sub_list_data['mkt_stats'])
        if self.include_bmk:
            self.roll_stats_data['active_stats'] = roll_stats.get_rolling_active_data(sub_list_data['active_stats'])

    def get_quantile_stats(self):
        print('Computing Quantile data...')
        self.quantile_stats_data = get_all_quantile_data(returns_df=self.returns_df, mkt_df=self.mkt_ret_data)

    def get_best_worst_pd_stats(self, freq='Q', num_periods=10):
        if dm.check_freq(self.returns_df, freq=freq):
            best_worst_pd = BestWorstPeriods(returns_df=self.returns_df,
                                             mkt_df=self.mkt_ret_data, num_periods=num_periods)
        else:
            returns_freq_df = dxf.convert_freq(self.returns_df, freq=freq)
            mkt_freq_df = dxf.convert_freq(self.mkt_ret_data, freq=freq)
            best_worst_pd = BestWorstPeriods(returns_df=returns_freq_df,
                                             mkt_df=mkt_freq_df, num_periods=num_periods)

        self.best_worst_period_stats_data = {'worst_periods': best_worst_pd.worst_periods_data,
                                             'best_periods': best_worst_pd.best_periods_data}

    def get_mkt_bool_data(self):
        return {'Equity': self.include_eq, 'Fixed Income': self.include_fi}

    def get_mkt_ret_data(self, mkt_df):
        mkt_ret_df = pd.DataFrame(index=mkt_df.index)
        for asset_class in self.mkt_bool_dict:
            if self.mkt_bool_dict[asset_class]:
                try:
                    mkt_ret_df = dm.merge_dfs(mkt_ret_df, mkt_df[[self.mkt_key[asset_class]]])
                except KeyError:
                    self.mkt_bool_dict[asset_class] = False
                    pass
        mkt_ret_df.columns = list(compress(list(self.mkt_bool_dict.keys()), list(self.mkt_bool_dict.values())))
        return mkt_ret_df

    def get_dd_stats(self, desc=''):
        if desc:
            print(f'Computing {desc} Drawdown analytics...')
        else:
            print('Computing Drawdown analytics...')
        if self.mkt_ret_data.empty:
            self.dd_stats_data = {'dd_matrix': dd.get_dd_matrix(self.returns_df),
                                  'co_dd_dict': dd.get_co_drawdown_data(self.returns_df),
                                  'dd_dict': dd.get_drawdown_data(self.returns_df, recovery=True)}
        else:
            self.dd_stats_data = {
                'dd_matrix': dd.get_dd_matrix(dm.merge_dfs(self.mkt_ret_data, self.returns_df, False)),
                'mkt_co_dd_dict': dd.get_co_drawdown_data(self.mkt_ret_data, self.returns_df),
                'co_dd_dict': dd.get_co_drawdown_data(self.returns_df),
                'dd_dict': dd.get_drawdown_data(self.returns_df, recovery=True)}

    def get_corr_stats(self, desc=''):
        if desc:
            print(f'Computing {desc} Correlation analytics...')
        else:
            print('Computing Correlation analytics...')
        corr_stats = cs.CorrStats(self.returns_df)
        if self.mkt_ret_data.empty:
            self.corr_stats_data = corr_stats.get_corr_analysis()
        else:
            merged_returns_df = dm.merge_dfs(self.mkt_ret_data, self.returns_df, drop_na=False)
            corr_stats = cs.CorrStats(merged_returns_df)
            self.corr_stats_data = corr_stats.get_corr_analysis()
            for asset_class in self.mkt_bool_dict:
                if self.mkt_bool_dict[asset_class]:
                    self.corr_stats_data[asset_class] = corr_stats.get_conditional_corr(asset_class)

    def get_mkt_index_list(self):
        mkt_list = []
        for asset_class in self.mkt_bool_dict:
            mkt_list = mkt_list + [MKT_COL_DICT['asset_id'][asset_class]
                                   + ' '
                                   + value
                                   for value in list(MKT_COL_DICT['analytics'].values())]
        return mkt_list

    def get_mkt_stats(self, desc=''):
        if self.mkt_ret_data.empty:
            print('Market data empty...')
            return None
        else:
            if desc:
                print(f'Computing {desc} Market analytics...')
            else:
                print('Computing Market analytics...')
            mkt_stats_dict = {}
            for strat in self.returns_df:
                returns_series = self.returns_df[strat]
                mkt_ret_df = dm.merge_dfs(self.mkt_ret_data, returns_series)

                mkt_analytics = {}
                mkt_returns_stats = rs.MktReturnsStats(freq=self.freq, rfr=self.rfr)
                for asset_class in self.mkt_bool_dict:
                    mkt_series = pd.Series(dtype='float64')
                    empty = True
                    if self.mkt_bool_dict[asset_class]:
                        mkt_series = mkt_ret_df[asset_class]
                        empty = False
                    mkt_analytics[asset_class] = mkt_returns_stats.get_mkt_analytics(returns_series=returns_series,
                                                                                     mkt_series=mkt_series, empty=empty)

                mkt_stats_dict[strat] = self.get_mkt_analytics_list(mkt_analytics)

            self.mkt_stats_data = convert_dict_to_df(mkt_stats_dict, self.get_mkt_index_list())
            # TODO: not needed
            for asset_class in self.mkt_bool_dict:
                if self.mkt_bool_dict[asset_class] is False:
                    try:
                        drop_list = [asset_class + ' ' + value
                                     for value in list(MKT_COL_DICT['analytics'].values())]
                        self.mkt_stats_data.drop(drop_list, inplace=True)
                    except KeyError:
                        pass

    @staticmethod
    def get_mkt_analytics_list(mkt_analytics):
        mkt_list = []
        for asset_class in mkt_analytics:
            mkt_list = mkt_list + list(mkt_analytics[asset_class].values())
        return mkt_list

    def get_returns_stats(self, desc='', drop_active=False):
        if desc:
            print(f'Computing {desc} Returns analytics...')
        else:
            print('Computing Returns analytics...')
        returns_stats_dict = {}
        period = get_time_frame(self.returns_df)
        # returns_stats = rs.ReturnsStats(freq=self.freq, rfr=self.rfr, target=self.target, p=self.p)
        returns_stats = rs.ActiveReturnsStats(freq=self.freq, rfr=self.rfr, target=self.target, p=self.p)
        # if self.include_bmk:
            # returns_stats = rs.ActiveReturnsStats(freq=self.freq, rfr=self.rfr, target=self.target, p=self.p)
        for strat in self.returns_df:
            returns_series = dm.remove_na(self.returns_df, strat)[strat]
            time_frame = period[strat]
            obs = len(returns_series)
            port_analytics = returns_stats.get_port_analytics(returns_series)
            bmk_series = pd.Series(dtype='float64')
            empty = True
            if self.include_bmk is True:
            # if strat not in self.bmk_key.values():
                bmk_series = self.bmk_df[self.bmk_key[strat]]
                empty = False  # if self.include_bmk else True
            active_analytics = returns_stats.get_active_analytics(returns_series=returns_series, bmk_series=bmk_series,
                                                                  empty=empty)

            returns_stats_dict[strat] = [*list(active_analytics.values())[0:1], *[time_frame, obs],
                                         *list(port_analytics.values()), *list(active_analytics.values())[1:]
                                         ]

        self.returns_stats_data = convert_dict_to_df(returns_stats_dict, [*list(ACTIVE_COL_DICT.values())[0:1],
                                                                          *['Time Frame',
                                                                            f'No. of {self.freq_string} Observations'],
                                                                          *list(PORT_COL_DICT.values()),
                                                                          *[f'VaR {(1 - self.p):.0%}',
                                                                            f'CVaR {(1 - self.p):.0%}'],
                                                                          *list(ACTIVE_COL_DICT.values())[1:]])

        if self.include_bmk is False:
            self.returns_stats_data.drop(list(ACTIVE_COL_DICT.values()), inplace=True)
        if drop_active:
            try:
                self.returns_stats_data.drop(list(ACTIVE_COL_DICT.values()), inplace=True)
            except KeyError:
                pass


class LiqAltsReturnsAnalytic(ReturnsAnalytic):

    def __init__(self, returns_df, rfr=0.0, target=0.0,
                 include_bmk=False, bmk_df=dm.pd.DataFrame(), bmk_key={},
                 include_eq=True, include_fi=True, include_cm=True, include_fx=True,
                 mkt_df=pd.DataFrame(), mkt_key={}):
        self.include_cm = include_cm
        self.include_fx = include_fx

        super().__init__(returns_df=returns_df, rfr=rfr, target=target,
                         include_bmk=include_bmk, bmk_df=bmk_df, bmk_key=bmk_key,
                         include_eq=include_eq, include_fi=include_fi,
                         mkt_df=mkt_df, mkt_key=mkt_key)

    def get_mkt_bool_data(self):
        return {'Equity': self.include_eq, 'Fixed Income': self.include_fi,
                'Commodities': self.include_cm, 'FX': self.include_fx}


class EqHedgeReturnsAnalytic(ReturnsAnalytic):

    def __init__(self, returns_df, rfr=0.0, target=0.0, p=0.05,
                 include_bmk=False, bmk_df=dm.pd.DataFrame(), bmk_key={},
                 include_eq=True, include_fi=False, mkt_df=pd.DataFrame(), mkt_key={}):

        super().__init__(returns_df=returns_df, rfr=rfr, target=target, p=p, include_bmk=include_bmk, bmk_df=bmk_df,
                         bmk_key=bmk_key, include_eq=include_eq, include_fi=include_fi,
                         mkt_df=mkt_df, mkt_key=mkt_key)
        self.hedge_metrics_data = None
        self.historical_selloff_data = None

    def get_hedge_metrics(self, desc='', mkt='Equity', full_list=True):
        if desc:
            print(f'Computing {desc} Hedge Metrics...')
        else:
            print('Computing Hedge Metrics...')
        hedge_metrics = hm.HedgeMetrics(freq=self.freq)
        hedge_metrics_dict = {}
        for strat in self.returns_df:
            returns_series = dm.remove_na(self.returns_df, strat)[strat]
            mkt_series = self.mkt_ret_data[mkt]
            hm_analytics = hedge_metrics.get_hm_analytics(returns_series, mkt_series, full_list)
            hedge_metrics_dict[strat] = list(hm_analytics.values())

        self.hedge_metrics_data = convert_dict_to_df(hedge_metrics_dict, hedge_metrics.get_hm_index_list(full_list))

        if dm.switch_freq_int(self.freq) <= 12:
            self.hedge_metrics_data.drop(['Decay Days (50% retrace)', 'Decay Days (25% retrace)',
                                          'Decay Days (10% retrace)'], inplace=True)

    def get_hist_selloff(self):
        print('Computing Historical Sell-Offs...')
        if self.freq == 'D':
            hs_df = dm.merge_dfs(self.mkt_ret_data, self.returns_df, drop_na=False, fillzeros=True)
            self.historical_selloff_data = get_hist_sim_table(hs_df)
        else:
            print(
                f'Return data frequency is {dm.switch_freq_string(self.freq)}, Daily data is used for this computation')


class ReturnsDictAnalytic(ReturnsAnalytic):

    def __init__(self, returns_dict, main_key='Monthly', rfr=0.0, target=0.0, p=0.05, rolling_years=3,
                 include_bmk=False, bmk_data={}, bmk_key={},
                 include_eq=True, include_fi=False, mkt_data={}, mkt_key={}):

        self.returns_dict = returns_dict
        self.main_key = main_key
        self.mkt_key = mkt_key
        self.include_bmk = include_bmk
        self.include_eq = include_eq
        self.include_fi = include_fi
        self.mkt_key = mkt_key
        self.bmk_dict = self.check_data(bmk_data) if self.include_bmk else self.get_empty_dict()
        self.mkt_dict = self.check_data(mkt_data, 'mkt')

        super().__init__(returns_df=self.returns_dict[self.main_key], rfr=rfr, target=target, p=p,
                         rolling_years=rolling_years, include_bmk=self.include_bmk, bmk_df=self.bmk_dict[self.main_key],
                         bmk_key=bmk_key, include_eq=include_eq, include_fi=include_fi,
                         mkt_df=self.mkt_dict[self.main_key], mkt_key=self.mkt_key)

        self.analytics_dict = None
        self.dd_stats_dict = None
        self.corr_stats_dict = None
        self.mkt_stats_dict = None
        self.returns_stats_dict = None
        self.roll_stats_dict = None
        self.quantile_stats_dict = None
        self.best_worst_period_stats_dict = None
        self.get_analytics_dict()

    def get_return_analytic(self, key):
        return ReturnsAnalytic(returns_df=self.returns_dict[key], rfr=self.rfr, target=self.target, p=self.p,
                               include_bmk=self.include_bmk, bmk_df=self.bmk_dict[key], bmk_key=self.bmk_key,
                               include_eq=self.include_eq, include_fi=self.include_fi, mkt_df=self.mkt_dict[key],
                               mkt_key=self.mkt_key)

    # def check_data(self, data):
    #     print(f'Checking data...')
    #     if isinstance(data, dict):
    #         if bool(data):
    #             return data
    #         else:
    #             return self.get_empty_dict()
    #     else:
    #         self.convert_data(data)

    # def check_bmk_data(self, bmk_data):
    #     print(f'Checking bmk data...')
    #     if self.include_bmk:
    #         if isinstance(bmk_data, dict):
    #             if bool(bmk_data):
    #                 return bmk_data
    #                 # self.bmk_dict = bmk_data
    #             else:
    #                 return self.get_empty_dict()
    #                 # self.bmk_dict = self.get_empty_dict()
    #         else:
    #             return self.convert_data(bmk_data)
    #             # self.bmk_dict = self.convert_data(bmk_data)
    #     else:
    #         return self.get_empty_dict()
    #         # self.bmk_dict = self.get_empty_dict()

    def get_analytics_dict(self):
        self.analytics_dict = {}
        for key in self.returns_dict:
            self.analytics_dict[key] = self.get_return_analytic(key)

    def check_data(self, data, desc='bmk'):
        print(f'Checking {desc} data...')
        if isinstance(data, dict):
            if bool(data):
                return data
                # self.mkt_dict = mkt_data
            else:
                return self.get_empty_dict()
                # self.mkt_dict = self.get_empty_dict()
        else:
            return self.convert_data(data)
            # self.mkt_dict = self.convert_data(mkt_data)

    def get_empty_dict(self):
        return {key: pd.DataFrame() for key in self.returns_dict.keys()}

    def convert_data(self, data):
        if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
            data_dict = {}
            freq_data = dm.get_freq_data(data)
            for key in self.returns_dict:
                temp_freq_data = dm.get_freq_data(self.returns_dict[key])
                if freq_data['freq_int'] < temp_freq_data['freq_int']:
                    index_data = dxf.PriceData(data).price_data
                    data_dict[key] = dxf.format_df(index_data, temp_freq_data['freq'], False)
                elif freq_data['freq_int'] == temp_freq_data['freq_int']:
                    data_dict[key] = data
            return data_dict
        else:
            return data

    @staticmethod
    def check_freq(main_df, new_df):
        return dm.get_freq(main_df) == dm.get_freq(new_df)

    def get_stats_dict(self, key_list, stat_type, years=None):
        stats_dict = {}

        for key in key_list:
            if years is not None:
                getattr(self.analytics_dict[key], f'get_{stat_type}_stats')(key, years)
            else:
                getattr(self.analytics_dict[key], f'get_{stat_type}_stats')(key)
            stats_dict[key] = getattr(self.analytics_dict[key], f'{stat_type}_stats_data')

        return stats_dict

    def get_roll_stats_dict(self, key_list, years=3):
        self.roll_stats_dict = self.get_stats_dict(key_list, 'roll', years)

    def get_quantile_stats_dict(self, key_list):
        self.quantile_stats_dict = self.get_stats_dict(key_list, 'quantile')

    def get_best_worst_pd_stats_dict(self, key_list):
        self.best_worst_period_stats_dict = {}
        for key in key_list:
            self.analytics_dict[key].get_best_worst_pd_stats()
            self.quantile_stats_dict[key] = self.analytics_dict[key].get_best_worst_pd_stats_data

    def get_dd_stats_dict(self, key_list):
        self.dd_stats_dict = self.get_stats_dict(key_list, 'dd')

    def get_corr_stats_dict(self, key_list):
        self.corr_stats_dict = self.get_stats_dict(key_list, 'corr')

    def get_mkt_stats_dict(self, key_list):
        self.mkt_stats_dict = self.get_stats_dict(key_list, 'mkt')

    def get_returns_stats_dict(self, key_list):
        self.returns_stats_dict = self.get_stats_dict(key_list, 'returns')


class LiqAltsReturnsDictAnalytic(ReturnsDictAnalytic):

    def __init__(self, returns_dict, main_key='Monthly', rfr=0.0, target=0.0,
                 include_bmk=False, bmk_data={}, bmk_key={},
                 include_eq=True, include_fi=True, include_cm=True, include_fx=True,
                 mkt_data={}, mkt_key={}):
        self.include_cm = include_cm
        self.include_fx = include_fx

        super().__init__(returns_dict=returns_dict, main_key=main_key, rfr=rfr, target=target,
                         include_bmk=include_bmk, bmk_data=bmk_data, bmk_key=bmk_key,
                         include_eq=include_eq, include_fi=include_fi, mkt_data=mkt_data, mkt_key=mkt_key)
        # self.update_mkt_data()

    def update_mkt_bool_dict(self):
        self.mkt_bool_dict = self.mkt_bool_dict | {'Commodities': self.include_cm, 'FX': self.include_fx}
        self.mkt_ret_data = self.get_mkt_ret_data(self.mkt_dict[self.main_key])
        # self.mkt_bool_dict['Commodities'] = self.include_cm
        # self.mkt_bool_dict['FX'] = self.include_fx

    def get_return_analytic(self, key):
        self.update_mkt_bool_dict()
        return LiqAltsReturnsAnalytic(returns_df=self.returns_dict[key], rfr=self.rfr, target=self.target,
                                      include_bmk=self.include_bmk, bmk_df=self.bmk_dict[key], bmk_key=self.bmk_key,
                                      include_eq=self.include_eq, include_fi=self.include_fi,
                                      include_cm=self.include_cm, include_fx=self.include_fx,
                                      mkt_df=self.mkt_dict[key], mkt_key=self.mkt_key)


class LiquidAltsPeriodAnalytic(LiqAltsReturnsDictAnalytic):

    def __init__(self, returns_dict, main_key='Full', rfr=0.0, target=0.0,
                 include_bmk=False, bmk_data={}, bmk_key={},
                 include_eq=True, include_fi=True, include_cm=True, include_fx=True,
                 mkt_data={}, mkt_key={}):
        super().__init__(returns_dict=returns_dict, main_key=main_key, rfr=rfr, target=target,
                         include_bmk=include_bmk, bmk_data=bmk_data, bmk_key=bmk_key,
                         include_eq=include_eq, include_fi=include_fi, include_cm=include_cm,
                         include_fx=include_fx, mkt_data=mkt_data, mkt_key=mkt_key)

        # self.get_corr_stats_dict(self.get_key_list())
        # self.get_mkt_stats_dict(self.get_key_list())
        # self.get_returns_stats_dict(self.get_key_list([]))
        # self.get_dd_stats()
        # self.get_roll_stats()

    @staticmethod
    def get_key_list(period_list, remove_list=['1 Year']):
        sub_list = dm.copy_data(period_list)
        return [x for x in sub_list if x not in remove_list]


class EqHedgeReturnsDictAnalytic(ReturnsDictAnalytic):

    def __init__(self, returns_dict, main_key='Monthly', rfr=0.0, target=0.0, p=0.05,
                 include_bmk=False, bmk_data={}, bmk_key={},
                 include_eq=True, include_fi=False, mkt_data={}, mkt_key={}):

        super().__init__(returns_dict=returns_dict, main_key=main_key, rfr=rfr, target=target, p=p,
                         include_bmk=include_bmk, bmk_data=bmk_data, bmk_key=bmk_key,
                         include_eq=include_eq, include_fi=include_fi, mkt_data=mkt_data, mkt_key=mkt_key)

        self.historical_selloff_data = None
        self.hedge_metrics_dict = None

    def get_return_analytic(self, key):
        return EqHedgeReturnsAnalytic(returns_df=self.returns_dict[key], rfr=self.rfr, target=self.target, p=self.p,
                                      include_bmk=self.include_bmk, bmk_df=self.bmk_dict[key], bmk_key=self.bmk_key,
                                      include_eq=self.include_eq, include_fi=self.include_fi,
                                      mkt_df=self.mkt_dict[key], mkt_key=self.mkt_key)

    def get_hist_selloff(self):
        try:
            self.analytics_dict['Daily'].get_hist_selloff()
            self.historical_selloff_data = self.analytics_dict['Daily'].historical_selloff_data
        except KeyError:
            pass

    def get_hedge_metrics_dict(self, key_list):
        self.hedge_metrics_dict = {}
        for key in key_list:
            self.analytics_dict[key].get_hedge_metrics(key)
            self.hedge_metrics_dict[key] = self.analytics_dict[key].hedge_metrics_data

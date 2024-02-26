# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi
"""

import numpy as np
from scipy.interpolate import interp1d

from . import util_new
from ..datamanager import data_manager_new as dm
from ..datamanager.data_xformer_new import PriceData


class ReturnsStats:
    def __init__(self, freq='M', rfr=0.0, target=0.0, p=0.05):
        self.freq = freq
        self.rfr = rfr
        self.target = target
        self.p = p

    def get_port_analytics(self, returns_series):
        ann_ret = self.get_ann_return(returns_series=returns_series)
        ann_vol = self.get_ann_vol(returns_series=returns_series)
        med_ret = self.get_median(returns_series=returns_series)
        avg_ret = self.get_mean(returns_series=returns_series)
        avg_pos_ret = self.get_avg_pos_neg(returns_series=returns_series, pos=True)
        avg_down_ret = self.get_avg_pos_neg(returns_series=returns_series, pos=False)
        avg_pos_neg = self.get_avg_pos_neg_ratio(returns_series=returns_series)
        best_period = self.get_max(returns_series=returns_series)
        worst_period = self.get_min(returns_series=returns_series)
        pct_pos_periods = self.get_pct_pos_neg_periods(returns_series=returns_series, pos=True)
        pct_neg_periods = self.get_pct_pos_neg_periods(returns_series=returns_series, pos=False)
        up_dev = self.get_updown_dev(returns_series=returns_series, up=True)
        down_dev = self.get_updown_dev(returns_series=returns_series, up=False)
        up_down_dev_ratio = self.get_up_down_dev_ratio(returns_series=returns_series)
        skew = self.get_skew(returns_series=returns_series)
        kurt = self.get_kurtosis(returns_series=returns_series)
        max_dd = self.get_max_dd(returns_series)
        max_1m_dd_dict = self.get_max_dd_freq(returns_series=returns_series, max_3m_dd=False)
        max_3m_dd_dict = self.get_max_dd_freq(returns_series=returns_series, max_3m_dd=True)
        ret_vol = self.get_sharpe_ratio(returns_series=returns_series)
        sortino = self.get_sortino_ratio(returns_series=returns_series)
        ret_dd = self.get_ret_max_dd_ratio(returns_series=returns_series)
        ret_1m_dd = self.get_ret_max_dd_freq_ratio(returns_series=returns_series, max_3m_dd=False)
        ret_3m_dd = self.get_ret_max_dd_freq_ratio(returns_series=returns_series, max_3m_dd=True)
        var = self.get_var(returns_series=returns_series)
        cvar = self.get_cvar(returns_series=returns_series)
        return {'ann_ret': ann_ret, 'median_ret': med_ret, 'avg_ret': avg_ret,
                'avg_pos_ret': avg_pos_ret, 'avg_neg_ret': avg_down_ret,
                'avg_pos_neg_ret': avg_pos_neg, 'best_period': best_period,
                'worst_period': worst_period, 'pct_pos_periods': pct_pos_periods,
                'pct_neg_periods': pct_neg_periods, 'ann_vol': ann_vol,
                'up_dev': up_dev, 'down_dev': down_dev, 'up_down_dev': up_down_dev_ratio,
                'vol_down_dev': ann_vol / down_dev, 'skew': skew, 'kurt': kurt, 'max_dd': max_dd,
                'max_1m_dd': max_1m_dd_dict['max_dd'], 'max_1m_dd_date': max_1m_dd_dict['index'],
                'max_3m_dd': max_3m_dd_dict['max_dd'], 'max_3m_dd_date': max_3m_dd_dict['index'],
                'ret_vol': ret_vol, 'sortino': sortino, 'ret_dd': ret_dd, 'ret_1m_dd': ret_1m_dd,
                'ret_3m_dd': ret_3m_dd, f'VaR {(1 - self.p):.0%}': var, f'CVaR {(1 - self.p):.0%}': cvar
                }

    @staticmethod
    def get_cumulative_returns(returns_series):
        return returns_series.add(1).prod(axis=0) - 1

    def get_ann_return(self, returns_series):
        """
        Return annualized return for a return series.

        Parameters
        ----------
        returns_series : pandas series
        Returns
        -------
        double
            Annualized return.

        """
        # compute the annualized return
        d = len(returns_series)
        return returns_series.add(1).prod() ** (dm.switch_freq_int(self.freq) / d) - 1

    def get_ann_vol(self, returns_series):
        """
        Return annualized volatility for a return series.

        Parameters
        ----------
        returns_series : pandas series

        Returns
        -------
        double
            Annualized volatility.

        Args:
            return_series:

        """
        # compute the annualized volatility
        return np.std(returns_series, ddof=1) * np.sqrt(dm.switch_freq_int(self.freq))

    def get_up_down_capture_ratio(self, returns_series, mkt_series, upside=True):
        mkt_cap = util_new.get_pos_neg_df(mkt_series, pos=upside)
        ret_cap = dm.merge_dfs(mkt_cap, returns_series, True)[returns_series.name]
        return self.get_cumulative_returns(ret_cap) / self.get_cumulative_returns(mkt_cap)

    @staticmethod
    def get_max_dd(returns_series):
        """
        Return maximum draw down (Max DD) for a price series.
        Returns
        -------
        double
            Max DD.

        """
        price_series = PriceData(returns_series).price_data
        # we are going to use the length of the series as the window
        window = len(price_series)

        # calculate the max drawdown in the past window periods for each period in the series.
        roll_max = price_series.rolling(window, min_periods=1).max()
        drawdown = price_series / roll_max - 1.0

        return drawdown.min()

    def get_max_dd_freq(self, returns_series, max_3m_dd=False):
        """
        Return dictionary (value and date) of either Max 1M DD or Max 3M DD

        Parameters
        ----------
        returns_series: Pandas Series
        max_3m_dd : boolean, optional
            Compute Max 3M DD. The default is False.

        Returns
        -------
        dictionary
        """
        price_series = PriceData(returns_series).price_data
        # get int frequency
        int_freq = dm.switch_freq_int(self.freq)

        # compute 3M or 1M returns
        if max_3m_dd:
            periods = round((3 / 12) * int_freq)
            dd_return_series = price_series.pct_change(periods)
        else:
            periods = round((1 / 12) * int_freq)
            dd_return_series = price_series.pct_change(periods)
        dd_return_series.dropna(inplace=True)

        # compute Max 1M/3M DD
        max_dd_freq = dd_return_series.min()

        # get Max 1M/3M DD date
        index_list = dd_return_series.index[dd_return_series == max_dd_freq].tolist()

        # return dictionary
        return {'max_dd': max_dd_freq, 'index': index_list[0].strftime('%m/%d/%Y')}

    def get_avg_pos_neg(self, returns_series, pos=True):
        """
        Average positive returns/ Average negative returns
        of a strategy

        Parameters
        ----------
        returns_series: Pandas Series
        pos : bool, optional
        Returns
        -------
        double

        """

        # filter positive and negative returns
        pos_neg_series = util_new.get_pos_neg_df(return_series=returns_series, pos=pos, target=self.target)

        return pos_neg_series.mean()

    def get_avg_pos_neg_ratio(self, returns_series):
        """
        Return Average positive returns/ Average negative returns
        of a strategy

        Returns
        -------
        double

        """
        # compute means
        avg_pos = self.get_avg_pos_neg(returns_series)
        avg_neg = self.get_avg_pos_neg(returns_series, pos=False)

        try:
            return avg_pos / abs(avg_neg)
        except ZeroDivisionError:
            return float('inf')

    def get_pct_pos_neg_periods(self, returns_series, pos=True):
        pos_neg_series = util_new.get_pos_neg_df(return_series=returns_series, pos=pos, target=self.target)
        return len(pos_neg_series) / len(returns_series)

    def get_updown_dev(self, returns_series, up=True):
        """
        Compute annualized upside/downside dev

        Parameters
        ----------
        returns_series: pandas.Series
        up : bool, optional
        Returns
        -------
        double
            upside / downside std deviation.

        Args:
            returns_series:

        """
        # create an upside/downside return column with the positive/negative returns only
        up_down_series = returns_series >= self.target if up else returns_series < self.target

        up_down_side_returns = returns_series.loc[up_down_series]

        # return annualized std dev of downside
        return self.get_ann_vol(up_down_side_returns)

    def get_up_dev(self, returns_series):
        """
        Compute annualized upside/downside dev

        Returns
        -------
        double
            upside / downside std deviation.

        """
        # create an upside/downside return column with the positive/negative returns only
        up_series = returns_series >= self.target

        up_side_returns = returns_series.loc[up_series]

        # return annualized std dev of downside
        return self.get_ann_vol(up_side_returns)

    def get_down_dev(self, returns_series):
        """
        Compute annualized upside/downside dev

        Returns
        -------
        double
            upside / downside std deviation.

        """
        # create an upside/downside return column with the positive/negative returns only
        down_series = returns_series < self.target

        down_side_returns = returns_series.loc[down_series]

        # return annualized std dev of downside
        return self.get_ann_vol(down_side_returns)

    def get_up_down_dev_ratio(self, returns_series):
        return self.get_updown_dev(returns_series, up=True) / self.get_updown_dev(returns_series, up=False)

    def get_sortino_ratio(self, returns_series):
        """
        Compute Sortino ratio

        Returns
        -------
        double
            sortino ratio
        """
        # calculate annualized return and std dev of downside
        ann_ret = self.get_ann_return(returns_series)
        down_stddev = self.get_updown_dev(returns_series)

        # calculate the sortino ratio
        return (ann_ret - self.rfr) / down_stddev

    def get_sharpe_ratio(self, returns_series):
        """
        Compute Return/Vol ratio

        Returns
        -------
        double
            Return/vol ratio

        """
        ann_return = self.get_ann_return(returns_series)
        ann_vol = self.get_ann_vol(returns_series)

        # calculate ratio
        return (ann_return - self.rfr) / ann_vol

    def get_ret_max_dd_ratio(self, returns_series):
        """
        Compute Return/Max DD ratio

        Returns
        -------
        double
            Return/Max DD ratio

        """
        # compute Max DD
        max_dd = self.get_max_dd(returns_series)
        # calculate ratio
        return self.get_ann_return(returns_series) / abs(max_dd)

    @staticmethod
    def get_skew(returns_series):
        """
        Compute skew of a return series

        Returns
        -------
        double
            skew.

        """
        return returns_series.skew()

    @staticmethod
    def get_kurtosis(returns_series):
        """
        Compute kurtosis of a return series

        Returns
        -------
        double
            kurtosis.

        """
        return returns_series.kurtosis()

    @staticmethod
    def get_median(returns_series):
        """
        Compute median of a return series

        Returns
        -------
        double
            skew.

        """
        return returns_series.median()

    @staticmethod
    def get_mean(returns_series):
        """
        Compute mean of a return series

        Returns
        -------
        double
            kurtosis.

        """
        return returns_series.mean()

    @staticmethod
    def get_max(returns_series):
        """
        Compute skew of a return series

        Returns
        -------
        double
            skew.

        """
        return returns_series.max()

    @staticmethod
    def get_min(returns_series):
        """
        Compute kurtosis of a return series

        Parameters
        ----------
        returns_series: Pandas Series
        Returns
        -------
        double
            kurtosis.

        """
        return returns_series.min()

    def get_ret_max_dd_freq_ratio(self, returns_series, max_3m_dd=False):
        """
        Compute Return/Max 1M/3M DD ratio

        Parameters
        ----------
        returns_series: Pandas Series
        max_3m_dd : boolean, optional
            Compute Max 3M DD. The default is False.

        Returns
        -------
        double
            Return/Max 1M/3M DD ratio

        """
        # calculate annual return
        max_freq_dd = self.get_max_dd_freq(returns_series=returns_series, max_3m_dd=max_3m_dd)['max_dd']

        # compute ratio
        return self.get_ann_return(returns_series=returns_series) / abs(max_freq_dd)

    def get_var(self, returns_series):
        obs = len(returns_series)
        location = self.p * obs

        # sort returns
        ranked_returns = list(returns_series.sort_values())

        rank = list(range(1, obs + 1))

        # interp = scipy.interpolate.interp1d(rank, ranked_returns, fill_value='extrapolate')
        interp = interp1d(rank, ranked_returns, fill_value='extrapolate')

        return float(interp(location))

    def get_cvar(self, returns_series):
        var = self.get_var(returns_series)

        cvar_series = returns_series.loc[returns_series < var]

        return cvar_series.mean()

    @staticmethod
    def get_beta(returns_series, mkt_series):
        return returns_series.cov(mkt_series) / mkt_series.var()


class MktReturnsStats(ReturnsStats):

    def __init__(self, freq='M', rfr=0.0):
        super().__init__(freq=freq, rfr=rfr)

    @staticmethod
    def get_mkt_conditional_returns(returns_series, mkt_series, up=True):
        mkt_ret_df = dm.merge_dfs(main_df=mkt_series, new_df=returns_series)
        if up is True:
            return mkt_ret_df[mkt_series > 0]
        else:
            return mkt_ret_df[mkt_series <= 0]

    def get_mkt_analytics(self, returns_series, mkt_series, empty=False):
        empty_analytics = {'alpha': None, 'beta': None, 'up_beta': None, 'dwn_beta': None,
                           'corr': None, 'up_corr': None, 'dwn_corr': None}

        if empty:
            return empty_analytics
        else:
            try:
                mkt_name = mkt_series.name
                strategy = returns_series.name
                mkt_up_df = self.get_mkt_conditional_returns(returns_series=returns_series, mkt_series=mkt_series,
                                                             up=True)
                mkt_dwn_df = self.get_mkt_conditional_returns(returns_series=returns_series, mkt_series=mkt_series,
                                                              up=False)
                mkt_up_series = mkt_up_df[mkt_name]
                mkt_dwn_series = mkt_dwn_df[mkt_name]
                returns_up_series = mkt_up_df[strategy]
                returns_dwn_series = mkt_dwn_df[strategy]
                mkt_alpha = self.get_alpha(returns_series=returns_series, mkt_series=mkt_series)
                mkt_beta = self.get_beta(returns_series=returns_series, mkt_series=mkt_series)
                mkt_up_beta = self.get_beta(returns_series=returns_up_series, mkt_series=mkt_up_series)
                mkt_dwn_beta = self.get_beta(returns_series=returns_dwn_series, mkt_series=mkt_dwn_series)
                mkt_corr = mkt_series.corr(returns_series)
                mkt_up_corr = mkt_up_series.corr(returns_up_series)
                mkt_dwn_corr = mkt_dwn_series.corr(returns_dwn_series)
                return {'alpha': mkt_alpha, 'beta': mkt_beta, 'up_beta': mkt_up_beta, 'dwn_beta': mkt_dwn_beta,
                        'corr': mkt_corr, 'up_corr': mkt_up_corr, 'dwn_corr': mkt_dwn_corr}
            except KeyError:
                return empty_analytics

    def get_alpha(self, returns_series, mkt_series):
        try:
            ann_return = self.get_ann_return(returns_series=returns_series)
            mkt_beta = self.get_beta(returns_series=returns_series, mkt_series=mkt_series)
            mkt_return = self.get_ann_return(returns_series=mkt_series)
            return ann_return - (self.rfr + mkt_beta * (mkt_return - self.rfr))
        except KeyError:
            return ann_return


class ActiveReturnsStats(ReturnsStats):
    def __init__(self, freq='M', rfr=0.0, target=0.0, p=0.05):
        super().__init__(freq=freq, rfr=rfr, target=target, p=p)
        # self.active_series = self.get_active_series()

    def get_excess_returns(self, returns_series, bmk_series):
        port_bmk_df = self.get_port_bmk_df(returns_series=returns_series, bmk_series=bmk_series)
        return self.get_ann_return(port_bmk_df['port']) - self.get_ann_return(port_bmk_df['bmk'])

    def get_tracking_error(self, returns_series, bmk_series, downside=False):
        active_series = self.get_active_series(returns_series=returns_series, bmk_series=bmk_series)
        if downside is True:
            return self.get_updown_dev(returns_series=active_series)
        else:
            return self.get_ann_vol(returns_series=active_series)

    def get_information_ratio(self, returns_series, bmk_series, asym=False):
        excess_return = self.get_excess_returns(returns_series=returns_series, bmk_series=bmk_series)
        te = self.get_tracking_error(returns_series=returns_series, bmk_series=bmk_series, downside=asym)
        if te == 0.0:
            return None
        else:
            return excess_return / te

    def get_active_analytics(self, returns_series, bmk_series, empty=False):
        empty_analytics = {'bmk_name': None, 'bmk_beta': None, 'excess_ret': None,
                           'te': None, 'downside_te': None, 'te_downside_te': None, 'ir': None, 'ir_asym': None}
        if empty:
            return empty_analytics
        else:
            try:
                bmk_name = bmk_series.name
                beta_bmk = self.get_beta(returns_series=returns_series, mkt_series=bmk_series)
                excess_ret = self.get_excess_returns(returns_series=returns_series, bmk_series=bmk_series)
                # active_series = self.get_active_series(returns_series=returns_series, bmk_series=bmk_series)
                te = self.get_tracking_error(returns_series=returns_series, bmk_series=bmk_series)
                dwnside_te = self.get_tracking_error(returns_series=returns_series, bmk_series=bmk_series,
                                                     downside=True)
                ir = self.get_information_ratio(returns_series=returns_series, bmk_series=bmk_series)
                ir_asym = self.get_information_ratio(returns_series=returns_series, bmk_series=bmk_series, asym=True)
                return {'bmk_name': bmk_name, 'bmk_beta': beta_bmk, 'excess_ret': excess_ret, 'te': te,
                        'downside_te': dwnside_te, 'te_downside_te': te / dwnside_te, 'ir': ir, 'ir_asym': ir_asym}
            except KeyError:
                print(f'Skipping active stats for {returns_series.name}.')
                return empty_analytics

    def get_active_series(self, returns_series, bmk_series):
        port_bmk_df = self.get_port_bmk_df(returns_series, bmk_series)
        port_bmk_df['active'] = port_bmk_df['port'] - port_bmk_df['bmk']
        return port_bmk_df['active']

    @staticmethod
    def get_port_bmk_df(returns_series, bmk_series):
        port_bmk_df = dm.merge_dfs(main_df=returns_series, new_df=bmk_series)
        port_bmk_df.columns = ['port', 'bmk']
        return port_bmk_df

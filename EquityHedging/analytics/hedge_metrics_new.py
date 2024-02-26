# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""

from .decay_new import get_decay_days
from .util_new import get_pos_neg_df
from ..datamanager import data_manager_new as dm

HEDGE_METRICS_INDEX = ['Benefit Count', 'Benefit Median', 'Benefit Mean', 'Benefit Cum',
                       'Downside Reliability', 'Upside Reliability',
                       'Convexity Count', 'Convexity Median', 'Convexity Mean', 'Convexity Cum',
                       'Cost Count', 'Cost Median', 'Cost Mean', 'Cost Cum',
                       'Decay Days (50% retrace)', 'Decay Days (25% retrace)', 'Decay Days (10% retrace)']


class HedgeMetrics:
    def __init__(self, freq='M'):
        self.freq = freq

    @staticmethod
    def get_hm_index_list(full_list=True):
        if full_list:
            return HEDGE_METRICS_INDEX
        else:
            return ['Benefit', 'Downside Reliability', 'Upside Reliability', 'Tail Reliability',
                    'Non Tail Reliability', 'Convexity', 'Cost', 'Decay', 'Average Return']

    @staticmethod
    def get_pct_index(return_series, pct, less_than=True):
        # compute the pct percentile
        percentile = return_series.quantile(pct)

        if less_than:
            # get the all data that is less than/equal to the pct percentile
            return return_series.index[return_series <= percentile]
        else:
            # get the all data that is greater than the pct percentile
            return return_series.index[return_series > percentile]

    def get_hm_stats(self, return_series, pct=.98, less_than=True, pos=True):
        if pos:
            pos_ret = return_series.loc[self.get_pct_index(return_series, pct, less_than)]
            hm_ret = get_pos_neg_df(pos_ret, pos)
        else:
            hm_ret = get_pos_neg_df(return_series, pos)

        return {'count': hm_ret.count(), 'mean': hm_ret.mean(),
                'med': hm_ret.median(), 'cumulative': hm_ret.sum()
                }

    def get_benefit_stats(self, return_series, pct=.98):
        """
        Return count, mean, mode and cumulative of all positive returns
        less than the 98th percentile rank

        Parameters
        ----------
        return_series : series
            returns series.
        pct: float, optional
        Returns
        -------
        benefit : dictionary
            {count: double, mean: double, median: double, cumulative: double}

        """
        return self.get_hm_stats(return_series, pct)

    def get_convexity_stats(self, return_series, pct=.98):
        """
        Return count, mean, mode and cumulative of all positive returns
        greater than the 98th percentile rank

        Parameters
        ----------
        return_series : series
            returns series.
        pct: float, optional
        Returns
        -------
        convexity : dictionary
            {count: double, mean: double, median: double, cumulative: double}
        """
        return self.get_hm_stats(return_series, pct, less_than=False)

    # TODO: revisit decay
    def get_decay_stats(self, return_series):
        """
        Return decay stats of returns

        Parameters
        ----------
        return_series : series
            returns series.

        Returns
        -------
        decay_dict : dictionary
            {key: decay_percent, value: int}

        """

        # Compute decay values only if data is daily or weekly
        if dm.switch_freq_int(self.freq) >= 12:
            decay_half = get_decay_days(return_series, self.freq)
            decay_quarter = get_decay_days(return_series, self.freq, .25)
            decay_tenth = get_decay_days(return_series, self.freq, .10)
        else:
            decay_half = 0
            decay_quarter = 0
            decay_tenth = 0

        # create decay dictionary
        decay_dict = {'half': decay_half,
                      'quarter': decay_quarter,
                      'tenth': decay_tenth
                      }

        return decay_dict

    def get_cost_stats(self, return_series):
        """
        Return count, mean, mode and cumulative of all negative returns

        Parameters
        ----------
        return_series : series
            returns series.

        Returns
        -------
        cost : dictionary
            {count: double, mean: double, median: double, cumulative: double}

        """
        return self.get_hm_stats(return_series, pos=False)

    def get_reliability_stats(self, return_series, mkt_series, tail=False):
        """
        Return correlation of strategy to equity benchmark downside returns and upside returns

        Parameters
        ----------
        return_series : series
            returns series.
        mkt_series : series
            mkt series.
        tail: Boolean, optional
            get tail correlation, Default is False
        Returns
        -------
        reliability : dictionary
            dict(down: double, up: double,
                 tail: double, non_tail: double).

        """
        # merge return and mkt series
        mkt_ret_df = dm.merge_dfs(mkt_series, return_series)
        mkt_id = mkt_series.name
        strat_id = return_series.name

        # create dataframes containing only data when mkt is <= 0 and > 0
        mkt_up_df = mkt_ret_df[mkt_ret_df[mkt_id] > 0]
        mkt_dwn_df = mkt_ret_df[mkt_ret_df[mkt_id] <= 0]

        # create reliability dictionary
        if tail:
            tail = mkt_dwn_df.loc[self.get_pct_index(mkt_dwn_df[mkt_id], 0.1)]
            non_tail = mkt_dwn_df.loc[self.get_pct_index(mkt_dwn_df[mkt_id], 0.1, False)]
            return {'down': mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat_id]),
                    'up': mkt_up_df[mkt_id].corr(mkt_up_df[strat_id]),
                    'tail': tail[mkt_id].corr(tail[strat_id]),
                    'non_tail': non_tail[mkt_id].corr(non_tail[strat_id])
                    }
        else:
            return {'down': mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat_id]),
                    'up': mkt_up_df[mkt_id].corr(mkt_up_df[strat_id])
                    }

    def get_hm_analytics(self, return_series, mkt_series, full_list=True):
        benefit = self.get_benefit_stats(return_series)
        convexity = self.get_convexity_stats(return_series)
        cost = self.get_cost_stats(return_series)
        decay = self.get_decay_stats(return_series)

        if full_list:
            reliability = self.get_reliability_stats(return_series, mkt_series)
            hm_list = [*list(benefit.values()), *list(reliability.values()), *list(convexity.values()),
                       *list(cost.values()), *list(decay.values())]
        else:
            reliability = self.get_reliability_stats(return_series, mkt_series, True)
            avg_ret = benefit['cumulative'] + convexity['cumulative'] + cost['cumulative']
            hm_list = [*[benefit['cumulative']], *list(reliability.values()),
                       *[convexity['cumulative'], cost['cumulative'], decay['half'], avg_ret]]

        return dict(zip(self.get_hm_index_list(full_list), hm_list))

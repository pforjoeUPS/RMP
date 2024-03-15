# -*- coding: utf-8 -*-
"""
Created on Sun Feb 4 2024

@author: Powis Forjoe
"""
import pandas as pd
from ..datamanager import data_manager_new as dm

# TODO: Add flexibility to take all data with/without dropping nas
# TODO: Refactor to create reusable class where you can keep changing returns and mkt data

class BestWorstPeriods:
    def __init__(self, returns_df, mkt_df=pd.DataFrame, num_periods=10):
        self.returns_df = returns_df
        self.freq = dm.get_freq(self.returns_df)
        self.period = self.switch_freq_to_period(self.freq)
        self.mkt_df = mkt_df
        self.num_periods = num_periods
        self.best_periods_data = self.get_best_worst_pds_data()
        self.worst_periods_data = self.get_best_worst_pds_data(best=False)

    def get_best_worst_pds_df(self, strat, best=True):
        if best:
            best_periods_df = self.returns_df.nlargest(self.num_periods, strat)
            return dm.format_date_index(data_df=best_periods_df, freq=self.freq)
        else:
            worst_periods_df = self.returns_df.nsmallest(self.num_periods, strat)
            return dm.format_date_index(data_df=worst_periods_df, freq=self.freq)

    # TODO: add drop_na variable
    def get_mkt_best_worst_pds_df(self, mkt, best=True):
        mkt_ret_df = dm.merge_dfs(self.mkt_df[[mkt]], self.returns_df)
        if best:
            best_mkt_periods_df = mkt_ret_df.nlargest(self.num_periods, mkt)
            return dm.format_date_index(data_df=best_mkt_periods_df, freq=self.freq)
        else:
            worst_mkt_periods_df = mkt_ret_df.nsmallest(self.num_periods, mkt)
            return dm.format_date_index(data_df=worst_mkt_periods_df, freq=self.freq)

    def get_best_worst_pds_dict(self, best=True):
        best_worst_dict = {}
        self.print_best_worst_string(best)
        for strat in self.returns_df:
            best_worst_dict[strat] = self.get_best_worst_pds_df(strat=strat, best=best)
        return best_worst_dict

    def get_mkt_best_worst_pds_dict(self, best=True):
        mkt_best_worst_dict = {}
        self.print_best_worst_string(best, mkt_data=True)
        for mkt in self.mkt_df:
            mkt_best_worst_dict[mkt] = self.get_mkt_best_worst_pds_df(mkt=mkt, best=best)
        return mkt_best_worst_dict

    def get_best_worst_pds_data(self, best=True):
        best_worst_pds_data = {'returns_data': self.get_best_worst_pds_dict(best=best)}
        if self.mkt_df.empty is False:
            best_worst_pds_data['mkt_data'] = self.get_mkt_best_worst_pds_dict(best=best)
        return best_worst_pds_data

    def print_best_worst_string(self, best=True, mkt_data=False):
        best_worst_string = 'Best' if best else 'Worst'
        mkt_strat_string = 'Market' if mkt_data else 'Strategy'
        print(f'Computing {self.num_periods} {best_worst_string} {mkt_strat_string} {self.period} vs returns')

    @staticmethod
    def switch_freq_to_period(freq):
        """
        Return a period equivalent to freq
        eg: switch_freq_to_period('D') returns 'Days'

        Parameters:
        arg -- string ('D', 'W', 'M')

        Returns:
        string
        """
        switcher = {
            "D": "Days",
            "B": "Days",
            "W": "Weeks",
            "M": "Months",
            "Q": "Quarters",
            "A": "Years",
            "Y": "Years",
        }
        return switcher.get(freq, 'Months')


class BestWorstDictPeriods:
    def __init__(self, returns_dict, mkt_dict, freq_list=None, num_periods=10):
        if freq_list is None:
            freq_list = ['Monthly', 'Quarterly']
        self.returns_dict = returns_dict
        self.mkt_dict = mkt_dict
        self.freq_list = self.check_freq(freq_list)
        # self.freq_list = dm.main_freq
        self.num_periods = num_periods
        self.best_worst_pds_dict = self.get_best_worst_pds_dict()

    def check_freq(self, freq_list):
        drop_list = list(set(freq_list).difference(set(self.returns_dict.keys())))
        if drop_list is True:
            for freq in drop_list:
                freq_list.remove(freq)
            if freq_list is True:
                return freq_list
            else:
                print(f'Warning: No elements in freq_list are present in the returns_dict')
        else:
            return freq_list

    def get_best_worst_pds_dict(self):
        best_worst_pds_dict = {}
        for freq in self.returns_dict:
            best_worst_pd = BestWorstPeriods(returns_df=self.returns_dict[freq], mkt_df=self.mkt_dict[freq],
                                             num_periods=self.num_periods)
            best_worst_pds_dict[freq] = {'worst_periods': best_worst_pd.worst_periods_data,
                                         'best_periods': best_worst_pd.best_periods_data}
        return best_worst_pds_dict

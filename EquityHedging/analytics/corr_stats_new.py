# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe
"""

import numpy as np
import pandas as pd

from ..datamanager import data_manager_new as dm


class CorrStats:
    def __init__(self, returns_df):
        self.returns_df = returns_df

    def get_corr_analysis(self):
        """
        Returns a dict of correlation matrices:
            full correlation, when equity up, when equity down

        Returns
        -------
        corr_dict : dictionary
            {key: string, value: list[dataframe, string]}

        """
        title = f'Correlation of {len(self.returns_df)} Historical Observations ({self.get_data_range()})'
        return {'Full': {'corr_df': self.returns_df.corr(),
                         'title': title
                         }
                }

    def get_data_range(self):
        dates = dm.get_min_max_dates(self.returns_df)
        return str(dates['start']).split()[0] + ' to ' + str(dates['end']).split()[0]

    def get_conditional_corr(self, strat_id):
        strat_up = (self.returns_df[self.returns_df[strat_id] > 0])
        strat_down = (self.returns_df[self.returns_df[strat_id] < 0])
        return {'corr_df': self.get_up_lwr_corr(strat_up, strat_down),
                'title': f'Conditional correlation where {strat_id} > 0 (upper) and < 0 (lower)'
                }

    @staticmethod
    def get_up_lwr_corr(up_df, lwr_df):
        up_array = np.triu(up_df.corr().values)
        lwr_array = np.tril(lwr_df.corr().values)
        temp_array = up_array + lwr_array
        for i in range(0, len(temp_array)):
            temp_array[i][i] = 1

        return pd.DataFrame(temp_array, index=lwr_df.columns, columns=up_df.columns)


class CorrStatsRank(CorrStats):
    def __init__(self, returns_df, mkt_df, buckets):
        self.mkt_df = mkt_df
        self.buckets = buckets
        super().__init__(returns_df=returns_df)

    def get_corr_rank_data(self, mkt):
        """
        Creates a dictionary of correlation dataframes ranked based on the
        mkt returns

        Returns
        -------
        corr_pack : dictionary
            {key: string, value: list[dataframe, string]}.

        """

        data_df = dm.merge_dfs(self.mkt_df, self.returns_df, drop_na=False)

        # create a ranking for the equity index returns
        data_df['Rank'] = pd.qcut(x=data_df[mkt], q=self.buckets, labels=np.arange(0, self.buckets, 1))

        # create a list of dataframes with each bucket
        list_df = []
        for rank in range(self.buckets):
            list_df.append(data_df[data_df['Rank'] == rank])

        # delete bucket column
        for i in range(self.buckets):
            del list_df[i]['Rank']

        del data_df['Rank']

        # create correlation dictionary
        corr_pack = self.get_corr_analysis()

        for rank in range(0, len(list_df)):
            key = f'corr_{str(rank + 1)}'
            title = f'Correlation Analysis for rank {str(rank + 1)}'
            min_value = list_df[rank][mkt].min()
            min_string = "Min = " + "{:.2%}".format(min_value)
            max_value = list_df[rank][mkt].max()
            max_string = "   Max = " + "{:.2%}".format(max_value)
            mean_value = list_df[rank][mkt].mean()
            mean_string = "   Mean = " + "{:.2%}".format(mean_value)
            value = title + "   " + min_string + max_string + mean_string
            corr_pack[key] = {'corr_df': list_df[rank].corr(),
                              'title': value
                              }
        return corr_pack

    def get_corr_rank_mkt_data(self):
        """
        Creates a dictionary of correlation dataframes ranked based on the
        mkt returns

        Returns
        -------
        corr_pack : dictionary
            {key: string, value: {'corr_df': dataframe, 'title': string}}.

        """

        mkt_corr_pack = {}
        for mkt in self.mkt_df:
            mkt_corr_pack[mkt] = self.get_corr_rank_data(mkt)
        return mkt_corr_pack

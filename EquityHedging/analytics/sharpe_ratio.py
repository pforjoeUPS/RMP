# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 21:11:03 2022

@author: Thiago De Frietas, Powis Forjoe
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gmean

from ..datamanager import data_manager_new as dm


class Sratio:
    # Class attribute
    confidence = 1.96

    def __init__(self, returns, freq):
        self.returns = returns
        self.t_scale = freq
        self.n = self.returns.count()
        self.serial_corr = self.returns.autocorr(lag=1)
        self.t_corr = (self.serial_corr * (self.n - 2) ** 0.5) / ((1 - self.serial_corr ** 2) ** 0.5)
        self.p = 2 * (1 - stats.t.cdf(np.abs(self.t_corr), df=2))

    def sharpe_ratio(self):
        plus1 = self.returns + 1
        sharpe_ratio = (gmean(plus1) - 1) / np.std(self.returns, ddof=1)
        stand_error = ((1 + 1 / 2 * (sharpe_ratio ** 2)) / self.n) ** 0.5
        lower_bound = sharpe_ratio - Sratio.confidence * stand_error
        upper_bound = sharpe_ratio + Sratio.confidence * stand_error

        ann_figures = self.annualize(sharpe_ratio, lower_bound, upper_bound)

        print('Sharpe Ratio: {:.2f}'.format(ann_figures[0]) + '  Lower Bound: {:.2f}'.format(
            ann_figures[1]) + '  Upper Bound: {:.2f}'.format(ann_figures[2]) + '  1-Lag Auto Correlation: {:.2f}'.format(
            self.serial_corr) + '  p-Value of Auto Correlation: {:.2f}'.format(self.p))

        # Create dataframe output

        data = {'Sharpe Ratio': [ann_figures[0]],
                'Lower Bound': [ann_figures[1]],
                'Upper Bound': [ann_figures[2]],
                '1-Lag Auto Correlation': [self.serial_corr],
                'p-Value of Auto Correlation': [self.p]}

        df = pd.DataFrame(data)

        return df

    def boot_sharpe_ratio(self):
        plus1 = self.returns + 1
        sharpe_ratio = (gmean(plus1) - 1) / np.std(self.returns, ddof=1)
        stand_error = ((1 + 1 / 2 * (sharpe_ratio ** 2)) / self.n) ** 0.5
        t_array = np.empty(5000)
        boot_lower = 0.0
        boot_upper = 0.0

        for i in range(0, 5000):
            sample = np.random.choice(self.returns, size=self.n)
            sample1 = sample + 1
            samples_r = (gmean(sample1) - 1) / np.std(sample, ddof=1)
            sample_st_error = ((1 + 1 / 2 * (samples_r ** 2)) / self.n) ** 0.5
            t_array[i] = (samples_r - sharpe_ratio) / sample_st_error
            left_tail = np.percentile(t_array, 2.5)
            right_tail = np.percentile(t_array, 97.5)
            boot_lower = sharpe_ratio - np.abs(left_tail) * stand_error
            boot_upper = sharpe_ratio + np.abs(right_tail) * stand_error

        ann_figures = self.annualize(sharpe_ratio, boot_lower, boot_upper)

        print('Sharpe Ratio: {:.2f}'.format(ann_figures[0]) + '  Lower Bound: {:.2f}'.format(
            ann_figures[1]) + '  Upper Bound: {:.2f}'.format(ann_figures[2]) + '  1-Lag Auto Correlation: {:.2f}'.format(
            self.serial_corr) + '  p-Value of Auto Correlation: {:.2f}'.format(self.p))

        # Create dataframe output

        data = {'Sharpe Ratio': [ann_figures[0]],
                'Lower Bound': [ann_figures[1]],
                'Upper Bound': [ann_figures[2]],
                '1-Lag Auto Correlation': [self.serial_corr],
                'p-Value of Auto Correlation': [self.p]}

        df = pd.DataFrame(data)

        return df

    def annualize(self, sharpe_ratio, lower_bound, upper_bound):
        ann_sharpe_ratio = sharpe_ratio * dm.switch_freq_int(self.t_scale) ** 0.5
        ann_lower_bound = lower_bound * dm.switch_freq_int(self.t_scale) ** 0.5
        ann_upper_bound = upper_bound * dm.switch_freq_int(self.t_scale) ** 0.5

        return ann_sharpe_ratio, ann_lower_bound, ann_upper_bound

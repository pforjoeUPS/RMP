# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 22:07:33 2022

@author: Thiago
"""

from numpy.linalg import multi_dot

from ..datamanager.data_manager_new import switch_freq_int


# Thiago code with some edits to make it run
class Risk:
    def __init__(self, returns, weights, freq='1M'):
        self.returns = returns
        self.t_scale = switch_freq_int(freq)
        self.weights = weights.transpose()
        self.covariance = self.returns.cov()
        self.total_var = multi_dot([self.weights.transpose(),
                                    self.covariance,
                                    self.weights])[0][0]
        self.mctr = self.get_mctr_df()

    def port_vol(self):
        return self.total_var ** 0.5 * self.t_scale ** 0.5

    def risk_contribution(self):
        marginal = self.covariance @ self.weights

        return marginal.mul(self.weights) / self.total_var

    def get_mctr_df(self):
        df_mctr = self.risk_contribution()
        df_mctr.columns = ['MCTR']
        return df_mctr.transpose()

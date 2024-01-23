# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 22:07:33 2022

@author: Thiago
"""

from numpy.linalg import multi_dot

from ..datamanager.data_manager import switch_freq_int


class Risk():
    def __init__(self, returns, wts, freq='1M'):
        self.returns = returns
        self.tscale = switch_freq_int(freq)
        self.wts = wts.transpose()
        self.covariance = self.returns.cov()  
        self.totalvar = multi_dot([self.wts.transpose(),
                                   self.covariance,
                                   self.wts])[0][0]
        self.mctr = self.get_mctr_df()
    
    def portvol(self):
        return self.totalvar**0.5 * self.tscale**0.5
        
    
    def riskcontribution(self):
        
        marginal = self.covariance @ self.wts

        return marginal.mul(self.wts)/self.totalvar
    
    def get_mctr_df(self):
        df_mctr = self.riskcontribution()
        df_mctr.columns = ['MCTR']
        return df_mctr.transpose()
        
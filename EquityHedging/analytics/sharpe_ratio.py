# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 21:11:03 2022

@author: Thiago De Frietas, Powis Forjoe
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gmean
from ..datamanager import data_manager as dm

class Sratio():
    #Class attribute
    confidence = 1.96
    
    def __init__(self, returns, freq):
        self.returns = returns
        self.tscale = freq
        self.n = self.returns.count()
        self.serialcorr = self.returns.autocorr(lag=1)
        self.tcorr = (self.serialcorr*(self.n - 2)**0.5)/((1 - self.serialcorr**2)**0.5)
        self.p = 2 * (1 - stats.t.cdf(np.abs(self.tcorr), df=2) )
    
    def sharperatio(self):
        plus1 = self.returns + 1
        sratio = (gmean(plus1) - 1)/np.std(self.returns, ddof = 1)
        standerror = ((1 + 1/2*(sratio**2))/self.n)**0.5
        lowerbound = sratio - Sratio.confidence * standerror
        upperbound = sratio + Sratio.confidence * standerror
            
        annfigures = self.annualize(sratio, lowerbound, upperbound)
        
        print('Sharpe Ratio: {:.2f}'.format(annfigures[0])+'  Lower Bound: {:.2f}'.format(annfigures[1])+'  Upper Bound: {:.2f}'.format(annfigures[2])+'  1-Lag Auto Correlation: {:.2f}'.format(self.serialcorr)+'  p-Value of Auto Correlation: {:.2f}'.format(self.p))
    
        #Create dataframe output
        
        data = {'Sharpe Ratio':[annfigures[0]],
                'Lower Bound':[annfigures[1]],
                'Upper Bound':[annfigures[2]],
                '1-Lag Auto Correlation':[self.serialcorr],
                'p-Value of Auto Correlation':[self.p]}
        
        df = pd.DataFrame(data)
        
        return(df)
    
    
    def bootsharperatio(self):
        plus1 = self.returns + 1
        sratio = (gmean(plus1) - 1)/np.std(self.returns, ddof = 1)
        standerror = ((1 + 1/2*(sratio**2))/self.n)**0.5
        tarray = np.empty(5000)
        
        for i in range(0, 5000):
            sample = np.random.choice(self.returns, size = self.n)
            sample1 = sample + 1
            samplesr = (gmean(sample1) - 1)/np.std(sample, ddof = 1)
            samplesterror = ((1 + 1/2*(samplesr**2))/self.n)**0.5
            tarray[i] = (samplesr-sratio)/samplesterror
            lefttail = np.percentile(tarray, 2.5)
            righttail = np.percentile(tarray, 97.5)
            bootlower = sratio - np.abs(lefttail)*standerror
            bootupper = sratio + np.abs(righttail)*standerror
        
        annfigures = self.annualize(sratio, bootlower, bootupper)
        
        print('Sharpe Ratio: {:.2f}'.format(annfigures[0])+'  Lower Bound: {:.2f}'.format(annfigures[1])+'  Upper Bound: {:.2f}'.format(annfigures[2])+'  1-Lag Auto Correlation: {:.2f}'.format(self.serialcorr)+'  p-Value of Auto Correlation: {:.2f}'.format(self.p))
        
        #Create dataframe output
        
        data = {'Sharpe Ratio':[annfigures[0]],
                'Lower Bound':[annfigures[1]],
                'Upper Bound':[annfigures[2]],
                '1-Lag Auto Correlation':[self.serialcorr],
                'p-Value of Auto Correlation':[self.p]}
        
        df = pd.DataFrame(data)
        
        return(df)
    
        
    def annualize(self, sratio, lowerbound, upperbound):
        
        annsratio = sratio * dm.switch_freq_int(self.tscale) ** 0.5
        annlowerbound = lowerbound * dm.switch_freq_int(self.tscale) ** 0.5
        annupperbound = upperbound * dm.switch_freq_int(self.tscale) ** 0.5
                   
        return(annsratio, annlowerbound, annupperbound)
     
    
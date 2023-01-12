# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 22:18:15 2022

@author: NVG9HXP
"""

import pandas as pd
import os
from .import data_manager as dm

CWD = os.getcwd()
RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\'
BMK_DATA_FP = RETURNS_DATA_FP+'bmk_returns.xlsx'
EQUITY_HEDGING_RETURNS_DATA = RETURNS_DATA_FP + 'ups_equity_hedge\\returns_data.xlsx'
NEW_DATA = RETURNS_DATA_FP + 'new_strats\\'
UPDATE_DATA = RETURNS_DATA_FP + 'update_strats\\'
EQUITY_HEDGE_DATA = RETURNS_DATA_FP + 'ups_equity_hedge\\'
NEW_DATA_COL_LIST = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                    'Vortex', 'VOLA I', 'VOLA II','Dynamic VOLA','Dynamic Put Spread',
                    'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)', 'Def Var (Wed)']

LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A','Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital'],
                     'Trend Following': ['1907 ARP TF','1907 Campbell TF', '1907 Systematica TF',
                                         'One River Trend'],
                     'Absolute Return':['1907 ARP EM',  '1907 III CV', '1907 III Class A',
                                        'ABC Reversion','Acadian Commodity AR',
                                        'Blueshift', 'Duality', 'Elliott'],
                     }

class bmkHandler():
    
    def __init__(self, equity_bmk = 'M1WD',include_fi = True, all_data=False):
        
        self.bmk_fp = BMK_DATA_FP
        self.equity_bmk = equity_bmk
        self.include_fi = include_fi
        self.all_data = all_data
        self.bmk_returns = self.get_bmk_returns()
        
    def get_bmk_returns(self):
        returns_dict = {}
        freqs = ['1D', '1W', '1M', '1Q', '1Y']
        for freq in freqs:
            freq_string = dm.switch_freq_string(freq)
            temp_ret = pd.read_excel(self.bmk_fp,
                                     sheet_name=freq_string,
                                     index_col=0)
            temp_ret = dm.get_real_cols(temp_ret)
            if self.all_data:
                returns_dict[freq_string] = temp_ret.copy()
            else:    
                if freq != '1D':
                    if self.include_fi:
                        temp_ret['FI Benchmark'] = (temp_ret['Long Corp'] + temp_ret['STRIPS'])/2
                        returns_dict[freq_string] = temp_ret[[self.equity_bmk, 'FI Benchmark']]
                    else:
                        returns_dict[freq_string] = temp_ret[[self.equity_bmk]]
                else:
                    returns_dict[freq_string] = temp_ret[[self.equity_bmk]]
                returns_dict[freq_string].index.names = ['Date']
        
        return returns_dict
        
        
    


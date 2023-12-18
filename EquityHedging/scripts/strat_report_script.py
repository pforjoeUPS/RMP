# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 22:21:38 2022

@author: RRQ1FYQ
"""
import os
CWD = os.getcwd()
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import summary, util
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as fmt
import pandas as pd

equity_bmk = 'SPTR'
strat_drop_list = ['SPTR', 'Down Var', 'Vortex', 'Dynamic Put Spread',
                   'Def Var','GW Dispersion', 'Corr Hedge', 'VOLA', 'Commodity Basket', 'ESPRSO', 'EVolCon', 'Moments']
include_fi = False

#create returns data dictionary for equity benchmark
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list, only_equity=False)
MXWDIM_prices = pd.read_excel(CWD+'\\RStrats\\' + 'Commods Example.xlsx', sheet_name = 'MXWDIM', index_col = 0)
mxwdim_dict = dm.get_data_dict(MXWDIM_prices)
full_data_dict = dm.merge_dicts(mxwdim_dict, returns)
# =============================================================================
# #when analyzing VRR
# #VRR_Port weighting
# two=700
# T=250
# TOT=two+T
# VRR2_weight = two/TOT
# VRRT_weight = T/TOT
#     
# freqs = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
# for freq in freqs:
#     returns[freq]['VRR Portfolio'] = returns[freq]['VRR 2'] * VRR2_weight + returns[freq]['VRR Trend'] * VRRT_weight
#     returns[freq].drop(['VRR 2','VRR Trend'],inplace=True,axis=1)
# =============================================================================

# =============================================================================
# filename = 'Commods Example.xlsx'
# sheet_name_list = ['MXWDIM', 'Macq', 'Barclays', 'BofA', 'BNP', 'JPM', 'MS', 'CITI']
# full_data_dict = returns.copy()
# for name in sheet_name_list:
#     new_strat = pd.read_excel(dm.NEW_DATA+filename, sheet_name = name, index_col = 0)
#     new_strat_dict = dm.get_data_dict(new_strat)
#     full_data_dict = dm.merge_dicts(full_data_dict, new_strat_dict)
# =============================================================================
    

#Get new strategy returns
new_strat = pd.read_excel(dm.NEW_DATA + 'UPS - Defensive Rates tracks.xlsx',
                                           sheet_name = 'Sheet1', index_col=0)
new_strat_dict = dm.get_data_dict(new_strat)


new_strat = pd.read_excel(dm.NEW_DATA + 'Nomura Rates Strats.xlsm',
                                           sheet_name = 'Sheet4', index_col=0)
new_strat_dict1 = dm.get_data_dict(new_strat)

#merge dictionaries
full_data_dict = dm.merge_dicts_list([full_data_dict, new_strat_dict1])

strat_report_name = 'Rates Strategy Analysis (VRR,UBS,Nomura).xlsx'
selloffs = True
rp.generate_strat_report(strat_report_name, full_data_dict, selloffs = True)

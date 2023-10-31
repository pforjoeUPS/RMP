# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 22:21:38 2022

@author: RRQ1FYQ
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import summary, util
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as fmt
import pandas as pd

equity_bmk = 'SPTR'
strat_drop_list = ['Down Var', 'Vortex', 'Dynamic Put Spread',
                   'Def Var','GW Dispersion', 'Corr Hedge', 'VOLA', 'Commodity Basket', 'ESPRSO', 'EVolCon']
include_fi = False

#create returns data dictionary for equity benchmark
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list, only_equity=False)

#when analyzing VRR
#VRR_Port weighting
two=700
T=250
TOT=two+T
VRR2_weight = two/TOT
VRRT_weight = T/TOT
    
freqs = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
for freq in freqs:
    returns[freq]['VRR Portfolio'] = returns[freq]['VRR 2'] * VRR2_weight + returns[freq]['VRR Trend'] * VRRT_weight
    returns[freq].drop(['VRR 2','VRR Trend'],inplace=True,axis=1)



#Get new strategy returns
filename = 'UBS Def Rates Overly.xlsx'
sheet_name = 'Sheet1'
new_strat = pd.read_excel(dm.NEW_DATA + filename,
                                           sheet_name = sheet_name, index_col=0)
new_strat_dict = dm.get_data_dict(new_strat)

filename = 'Nomura Rate Time Series.xlsm'
sheet_name = 'Sheet1'
new_strat = pd.read_excel(dm.NEW_DATA + filename,
                                           sheet_name = sheet_name, index_col=0)
new_strat_dict1 = dm.get_data_dict(new_strat)

#merge dictionaries
full_data_dict = dm.merge_dicts_list([returns, new_strat_dict, new_strat_dict1])
full_data_dict = dm.merge_dicts_list([full_data_dict, new_strat_dict1])

strat_report_name = 'Rates Strategies (BNP, UBS, Nomura) Comparison Analysis.xlsx'
selloffs = True
rp.generate_strat_report(strat_report_name, full_data_dict, selloffs = True)

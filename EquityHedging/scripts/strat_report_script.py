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
strat_drop_list = ['99%/90% Put Spread','Down Var', 'Vortex', 'Dynamic Put Spread',
                   'Def Var','Corr Hedge', 'VOLA', 'GW Dispersion', 'VRR 2', 'VRR Trend', 'Commodity Basket', 'ESPRSO', 'EVolCon']
include_fi = False

#create returns data dictionary for equity benchmark
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list, only_equity=False)

#when analyzing VRR
# =============================================================================
# #VRR_Port weighting
# two=815.4
# T=267.9
# TOT=two+T
# VRR2_weight = two/TOT
# VRRT_weight = T/TOT
#     
# freqs = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
# for freq in freqs:
#     returns[freq]['VRR Portfolio'] = returns[freq]['VRR 2'] * VRR2_weight + returns[freq]['VRR Trend'] * VRRT_weight
#     returns[freq].drop(['VRR 2','VRR Trend'],inplace=True,axis=1)
# =============================================================================


#Get new strategy returns
filename = 'UBS_defensive_skew_data.xlsx'
sheet_name = 'Sheet1'
new_strat = pd.read_excel(dm.NEW_DATA + filename,
                                           sheet_name = 'Sheet1', index_col=0)
new_strat_dict = dm.get_data_dict(new_strat)

#merge dictionaries
full_data_dict = dm.merge_dicts_list([returns, new_strat_dict])

strat_report_name = 'UBS_Defensive_Skew_Report_wo_BMK'
selloffs = True
rp.generate_strat_report(strat_report_name, new_strat_dict, selloffs = True)

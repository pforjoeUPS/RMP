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
                   'Def Var','Corr Hedge', 'VOLA', 'VRR 2', 'VRR Trend', 'GW Dispersion']
include_fi = False

#create returns data dictionary for equity benchmark
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list, only_equity=False)

#Get new strategy returns
filename = 'Commodity Core Absolute Return Portfolio - Apr 2023.xlsx'
sheet_name = 'Sheet1'
new_strat = pd.read_excel(dm.NEW_DATA + filename,
                                           sheet_name = sheet_name, index_col=0)
new_strat_dict1 = dm.get_data_dict(new_strat)

#merge dictionaries
full_data_dict = dm.merge_dicts(returns, new_strat_dict, fillzeros=False)

strat_report_name = 'Commodities Equity Hedge Analysis'
selloffs = True
rp.generate_strat_report(strat_report_name, full_data_dict, selloffs = True, remove_bmk = False )

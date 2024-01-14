# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 15:08:28 2024

@author: RRQ1FYQ
"""

#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots

#import returns data
returns_dict = dm.get_equity_hedge_returns(all_data=True)

#Add new strat to returns data
filename = 'defvar.xlsx'
sheet_name = ['Sheet1','Sheet2','Sheet3']
strategy_list = []
new_returns_dict ={}
for i in sheet_name:
    new_strategy = dm.get_new_strategy_returns_data(filename, i)
    returns_dict = dm.merge_dicts(returns_dict, dm.get_data_dict(new_strategy, data_type='index'))
    
#reorder columns
for freq in returns_dict:
    returns_dict[freq] = returns_dict[freq][['SPTR', 'SX5T', 'M1WD', 'Down Var', 'Vortex', 'VOLA I', 'VOLA II',
       'Dynamic VOLA', 'Dynamic Put Spread', 'VRR', 'VRR 2', 'VRR Trend',
       'GW Dispersion', 'Corr Hedge', 'Def Var (Fri)', 'Def Var (Mon)',
       'Def Var (Wed)', 'Def Var II (Mon)', 'Def Var II (Wed)', 'Def Var II (Fri)','Commodity Basket', 'ESPRSO', 'EVolCon']]
    
#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)

    
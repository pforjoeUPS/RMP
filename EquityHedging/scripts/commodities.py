# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 14:10:54 2022

@author: RRQ1FYQ
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import summary, util
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as fmt
import pandas as pd

benchmark = pd.read_excel(dm.NEW_DATA+'Commodities.xlsx',
                                           sheet_name = 'BCOM', index_col=0)
benchmark_dict = dm.get_data_dict(benchmark)

no_strat = 1

if no_strat>1:
   
    new_strat1 = pd.read_excel(dm.NEW_DATA+'Commodities.xlsx',
                                               sheet_name = 'Backwardation', index_col=0, header = 1)
    
    new_strat2 = pd.read_excel(dm.NEW_DATA+'Commodities.xlsx',
                               sheet_name = 'Barc Back', index_col=0, header = 0)
    
    new_strat = dm.merge_data_frames(new_strat1, new_strat2)
else:
    new_strat = pd.read_excel(dm.NEW_DATA+'Commod Misc.xlsx',
                                               sheet_name = 'Sheet4', index_col=0, header = 1)
    
    
    
new_strat_dict = dm.get_data_dict(new_strat)

#merge dictionaries
full_data_dict = dm.merge_dicts(benchmark_dict,new_strat_dict, fillzeros=False)

strat_report = 'Commodity_Misc_analysis'
selloffs = True
rp.generate_strat_report(strat_report, full_data_dict, selloffs = True)

#################################################################################
backward= pd.read_excel(dm.NEW_DATA+'Commodities.xlsx', sheet_name = 'Backwardation', index_col=0, header = 1)
    
barclays_backwardation = pd.read_excel(dm.NEW_DATA+'Commodities.xlsx', sheet_name = 'Barc Back', index_col=0, header = 0)
backwardation = dm.merge_data_frames(df_main, df_new)

import riskfolio as rp
port = rp.Portfolio(returns=full_data_dict['Daily'])
port.assets_stats(method_mu='hist', method_cov='hist', d=0.94)
w_rp = port.rp_optimization(
    model="Classic",  # use historical
    rm="MV",  # use mean-variance optimization
    hist=True,  # use historical scenarios
    rf=0,  # set risk free rate to 0
    b=None  # don't use constraints
)

ax = rp.plot_pie(w=w_rp)
ax = rp.plot_risk_con(
    w_rp,
    cov=port.cov,
    returns=port.returns,
    rm="MV",
    rf=0,
)

###method to create portfolio with weights found above
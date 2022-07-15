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
strat_drop_list = ['99%/90% Put Spread','Down Var', 'Vortex', 'VOLA 3', 'Dynamic Put Spread', 'VRR',
       'GW Dispersion', 'Corr Hedge', 'Def Var']
include_fi = False
#create returns data dictionary for equity benchmark
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)
returns = returns['Monthly']
#returns['Daily'] = returns['Daily'].iloc[list(range(13,len(returns['Daily']))),:]

mix_spx = pd.read_excel(dm.NEW_DATA+'Historical Monthly Data Series v2 6_30_22.xlsx',
                                           sheet_name = 'Sheet1', index_col=0)

data_dict ={'Monthly': dm.merge_data_frames(returns, mix_spx)}
#create returns data dictionary for strategy

#merge dictionaries
#full_data_dict = dm.merge_dicts(returns,full_data_dict, fillzeros=True)

strat_report = 'atl_capital_v2_6_30_22_analysis'
selloffs = True
rp.generate_strat_report(strat_report, data_dict, selloffs = False)

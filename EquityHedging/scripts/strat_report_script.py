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
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list, only_equity=True)#
#returns['Daily'] = returns['Daily'].iloc[list(range(13,len(returns['Daily']))),:]

qsp = pd.read_excel(dm.NEW_DATA+'QSP DHS Time Series.xlsx',
                                           sheet_name = 'data', index_col=0)
qsp_dict = dm.get_data_dict(qsp)
#data_dict ={'Monthly': dm.merge_data_frames(returns, mix_spx)}
#create returns data dictionary for strategy

#merge dictionaries
full_data_dict = dm.merge_dicts(returns,qsp_dict, fillzeros=False)

strat_report = 'qsp_dhs_analysis'
selloffs = True
rp.generate_strat_report(strat_report, full_data_dict, selloffs = True)

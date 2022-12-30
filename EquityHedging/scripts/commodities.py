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

new_strat = pd.read_excel(dm.NEW_DATA+'Commodities.xlsx',
                                           sheet_name = 'Carry', index_col=0, header = 1)
new_strat_dict = dm.get_data_dict(new_strat)

#merge dictionaries
full_data_dict = dm.merge_dicts(benchmark_dict,new_strat_dict, fillzeros=False)

strat_report = 'Commodity_Curve_analysis'
selloffs = True
rp.generate_strat_report(strat_report, full_data_dict, selloffs = True)

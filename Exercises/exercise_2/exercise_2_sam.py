# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 09:27:15 2022

@author: LGQ0NLN
"""

Python Exercise 2
Aim: Create an excel report using generate_strat_report function for the CS strategies with SPTR as the benchmark

Steps:
        
#1 Collecting equity hedge returns
import pandas as pd
from EquityHedging.datamanager import data_manager as dm
sptr_dict = dm.get_equity_hedge_returns(equity='SPTR', include_fi=False, strat_drop_list=[],only_equity=False,all_data=False)

#2 pulling credit suisse data
cs_data = pd.read_excel('C://Users/LGQ0NLN/Documents/GitHub/Exercises/2/data.xlsx',sheet_name='data',index_col=0)

#3 turn data from CS file to dict
cs_dict = dm.get_data_dict(cs_data,data_type='index')

#4 merging SPTR dict and CS dict
ret_dict = dm.merge_dicts(sptr_dict, cs_dict)

#5 returning excel file
from EquityHedging.reporting.excel import reports as rp
strat_report_sam = rp.generate_strat_report('strat_report_sam', ret_dict)

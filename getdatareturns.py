# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 13:09:25 2022

@author: LGQ0NLN
"""

#import os
#os.chdir("..\..")
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp

returns_dict = dm.get_equity_hedge_returns(all_data=True)

#create dictionary that contains updated returns
new_data_dict = dm.create_update_dict()

returns_dict = dm.update_returns_data(returns_dict,new_data_dict)
rp.get_returns_report('returns_data_new', returns_dict)

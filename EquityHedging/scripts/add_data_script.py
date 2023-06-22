# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 22:35:26 2021

@author: gcz5chn
"""
import os
os.chdir("..\..")
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp

returns_dict = dm.update_returns_data()

#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)



#testing function here

returns_dict = dm.add_new_strat_to_returns_data(new_strat_name= 'Test', filename = 'macq_basket.xlsx', sheet_name='Sheet2')
rp.get_returns_report('returns_data_test', returns_dict)


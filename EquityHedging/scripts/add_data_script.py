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

new_strat = pd.read_excel('C:\\Users\\PCR7FJW\\Documents\\RMP\\EquityHedging\\data\\new_strats\\' + 'evolcon.xlsx',
                                           sheet_name = 'Sheet1', index_col=0)
new_strat_dict = dm.get_data_dict(new_strat)
returns_dict = dm.merge_dicts(returns_dict, new_strat_dict)

#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)





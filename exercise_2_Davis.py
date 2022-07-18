# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 10:40:08 2022

@author: GMS0VSB
"""

#import the goods
import pandas as pd
from EquityHedging.datamanager import data_manager as dm

#make SnP dict

sptr_dict = dm.get_equity_hedge_returns(equity='SPTR', include_fi=False, strat_drop_list=[], only_equity=True, all_data=False)

#importing the Credit Suisse stuff
cs_data = pd.read_excel('C:\\Users\\GMS0VSB\\Documents\\GitHub\\Credit Suisse Systematic Defensive Skew_Index_20220305_out.xlsx', 
                        sheet_name='EZ', index_col=(0))

#turn credit suisse data into a freq dictionary
cs_dict = dm.get_data_dict(cs_data, data_type='index')

#merge the dicts

ret_dicts = dm.merge_dicts(cs_dict, sptr_dict)

#generate report

from EquityHedging.reporting.excel import reports as rp

rp.generate_strat_report('strat_report_Davis', ret_dicts)






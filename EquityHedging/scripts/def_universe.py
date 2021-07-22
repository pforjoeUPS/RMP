# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 14:11:19 2021

@author: Powis Forjoe
"""

from EquityHedging.datamanager import bbg_manager as bbg
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.analytics import util
from EquityHedging.analytics import hedge_metrics as hm

def_uni = bbg.get_price_data(['PUT Index','TLT Equity', 'UBCITCCC Index', 'IEF US Equity','UX1 Index','XAU Curncy'], '2007-12-28','2021-03-31')
def_uni.columns = ['SPX PUT', '20+ Yr Rates', 'Commdty Curve Carry', '10+ Yr Rates', 'VIX Calls', 'Gold']
def_uni = dm.get_data_dict(def_uni)
rp.get_returns_report('def_uni',def_uni)

strategy_list = []
filename = 'def_uni.xlsx'
sheet_name = 'Weekly'
new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
returns_dict = dm.get_equity_hedge_returns(all_data=True)
weekly_ret = returns_dict['Weekly'].copy()
weekly_ret = dm.merge_data_frames(weekly_ret,new_strategy)

hm_df = hm.get_hedge_metrics(weekly_ret,'1W', False)
norm_df = util.get_normalized_data(hm_df.transpose())
norm_df = util.reverse_signs_in_col(hm_df.transpose(), 'Downside Reliability')
norm_df = util.get_normalized_data(norm_df)


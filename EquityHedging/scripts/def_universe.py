# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 14:11:19 2021

@author: Powis Forjoe
"""

from EquityHedging.datamanager import bbg_manager as bbg
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp
def_uni = bbg.get_price_data(['PUT Index','TLT Equity', 'CCRV US Equity', 'IEF US Equity','UX1 Index','XAU Curncy'], '2007-12-28','2021-03-31')
def_uni.columns = ['SPX PUT', '20+ Yr Rates', 'Commdty Curve Carry', '10+ Yr Rates', 'VIX Calls', 'Gold']
def_uni = dm.get_data_dict(def_uni)
rp.get_returns_report('def_uni',def_uni)
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
import pandas as pd

jpm = pd.read_excel(dm.NEW_DATA+'def_strats.xlsx',sheet_name='JPM')
jpm_tickers = jpm['Ticker'].tolist()
jpm_alias = jpm['Alias'].tolist()
cs = pd.read_excel(dm.NEW_DATA+'def_strats.xlsx',sheet_name='CS')
cs_tickers = cs['Ticker'].tolist()
cs_alias = cs['Alias'].tolist()
ubs = pd.read_excel(dm.NEW_DATA+'def_strats.xlsx',sheet_name='UBS')
ubs_alias = ubs['Alias'].tolist()
ubs_tickers = ubs['Ticker'].tolist()

def_tickers=['GSVILP01 Index','TLT Equity','IEF US Equity','UX1 Index','XAU Curncy']
def_alias =['SPX ATM PUT', '20+ Yr Rates', '10+ Yr Rates', 'VIX Calls', 'Gold']
    
jpm_uni = bbg.get_price_data(jpm_tickers, '2007-12-20','2021-06-30')
cs_uni = bbg.get_price_data(cs_tickers, '2007-12-28','2021-06-30')
ubs_uni = bbg.get_price_data(ubs_tickers, '2007-12-20','2021-06-30')
def_uni = bbg.get_price_data(def_tickers, '2007-12-28','2021-06-30')

file_path = 'def_strats_index.xlsx'
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
jpm_uni.to_excel(writer,sheet_name='jpm')
cs_uni.to_excel(writer,sheet_name='cs')
ubs_uni.to_excel(writer,sheet_name='ubs')
def_uni.to_excel(writer,sheet_name='def')
writer.save()

for sheet in sheet_list:
    temp_df = pd.read_excel('def_strats_index.xlsx', sheet_name=sheet, index_col=0)
    df_dict[sheet] = temp_df.copy()


DEF_UNI_TICKERS=['GSVILP01 Index','TLT Equity','IEF US Equity','UX1 Index','XAU Curncy']
DEF_UNI_ALIAS =['SPX ATM PUT', '20+ Yr Rates', '10+ Yr Rates', 'VIX Calls', 'Gold']




def_uni = bbg.get_price_data(['GSVILP01 Index','TLT Equity', 'UBCITCCC Index', 'IEF US Equity','UX1 Index','XAU Curncy'], '2007-12-28','2021-03-31')
def_uni.columns = ['SPX ATM PUT', '20+ Yr Rates', 'Commdty Curve Carry', '10+ Yr Rates', 'VIX Calls', 'Gold']
def_uni = dm.get_data_dict(def_uni)
rp.get_returns_report('def_uni',def_uni)
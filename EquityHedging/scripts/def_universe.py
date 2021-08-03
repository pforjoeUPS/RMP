# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 14:11:19 2021

@author: Powis Forjoe
"""
import os

os.chdir('..\..')

from EquityHedging.datamanager import bbg_manager as bbg
from EquityHedging.datamanager import data_manager as dm
import pandas as pd

cs_list = ['cs_2','cs_3','cs_4','cs_5']
bar_list = ['bar_1','bar_2','bar_3','bar_4','bar_5','bar_6','bar_7']
ubs_list = ['ubs', 'ubs def ports']

cs = pd.read_excel(dm.EQUITY_HEDGE_DATA+'def_uni_final.xlsx', sheet_name='cs_1', index_col=0)
for sheet in cs_list:
    temp_df = pd.read_excel(dm.EQUITY_HEDGE_DATA+'def_uni_final.xlsx', sheet_name=sheet, index_col=0)
    temp_df = dm.get_real_cols(temp_df)
    cs = dm.merge_data_frames(cs, temp_df)

bar = pd.read_excel(dm.EQUITY_HEDGE_DATA+'def_uni_final.xlsx', sheet_name='bar_1', index_col=0)
for sheet in bar_list:
    temp_df = dm.get_real_cols(temp_df)
    bar = dm.merge_data_frames(bar, temp_df)

ubs = pd.read_excel(dm.EQUITY_HEDGE_DATA+'def_uni_final.xlsx', sheet_name='ubs', index_col=0)
temp_df = pd.read_excel(dm.EQUITY_HEDGE_DATA+'def_uni_final.xlsx', sheet_name='cs_2', index_col=0)
ubs = dm.merge_data_frames(ubs, temp_df)

sg = pd.read_excel(dm.EQUITY_HEDGE_DATA+'def_uni_final.xlsx', sheet_name='sg', index_col=0)

jpm = pd.read_excel(dm.EQUITY_HEDGE_DATA+'def_uni_final.xlsx', sheet_name='jpm', index_col=0)

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

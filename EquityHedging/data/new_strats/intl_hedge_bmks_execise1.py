# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 11:21:29 2021

@author: sqy5spk
"""
import pandas as pd
from EquityHedging.datamanager import data_manager as dm
bmks=pd.read_excel("intl_hedge_bmks.xlsx",sheet_name="bmks", index_col=0)
bmks
puts=pd.read_excel("intl_hedge_bmks.xlsx",sheet_name="puts", index_col=0)
puts

bmks_d=bmks.copy()
bmks_d=bmks_d.resample('1D').ffill()
bmks_d=bmks_d.pct_change(1)
bmks_d.dropna(inplace=True)

bmks_w=bmks.copy()
bmks_w=bmks_w.resample('1W').ffill()
bmks_w=bmks_w.pct_change(1)
bmks_w.dropna(inplace=True)

bmks_m=bmks.copy()
bmks_m=bmks_m.resample('1M').ffill()
bmks_m=bmks_m.pct_change(1)
bmks_m.dropna(inplace=True)

bmksdict=dm.get_data_dict(bmks, "index")

#daily, weekly, monthly returns for puts sheet
puts_d=puts.copy()
puts_d=puts_d.resample('1D').ffill()
puts_d=puts_d.pct_change(1)
puts_d.dropna(inplace=True)

puts_w=puts.copy()
puts_w=puts_w.resample('1W').ffill()
puts_w=puts_w.pct_change(1)
puts_w.dropna(inplace=True)

puts_m=puts.copy()
puts_m=puts_m.resample('1M').ffill()
puts_m=puts_m.pct_change(1)
puts_m.dropna(inplace=True)

putsdict=dm.get_data_dict(puts,"index")


#merge bmks and puts
from EquityHedging.datamanager import data_manager as dm
intl_hedge=dm.merge_data_frames(bmks, puts)
intl_hedge

#convert to daily, monthly, and weekly return
intl_hedge_d= intl_hedge.copy()
intl_hedge_d= intl_hedge_d.resample("1D").ffill()
intl_hedge_d=intl_hedge_d.pct_change(1)
intl_hedge_d.dropna(inplace=True)

intl_hedge_w= intl_hedge.copy()
intl_hedge_w= intl_hedge_w.resample("1W").ffill()
intl_hedge_w=intl_hedge_w.pct_change(1)
intl_hedge_w.dropna(inplace=True)

intl_hedge_m= intl_hedge.copy()
intl_hedge_m= intl_hedge_m.resample("1M").ffill()
intl_hedge_m=intl_hedge_m.pct_change(1)
intl_hedge_m.dropna(inplace=True)

intl_hedge_dict=dm.get_data_dict(intl_hedge,"index")


#merge bmks dict and puts dict
intl_hedge_dict_2= dm.merge_dicts(bmksdict, putsdict)

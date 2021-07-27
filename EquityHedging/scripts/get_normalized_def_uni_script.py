# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 23:41:33 2021

@author: nvg9hxp
"""
import os

os.chdir('..\..')

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import  util
from EquityHedging.analytics import summary 
import pandas as pd

#get equity portfolio weekly data
print('get equity portfolio weekly data')
equity_bmk = 'SPTR'
strat_drop_list = []
returns = dm.get_equity_hedge_returns(equity_bmk, strat_drop_list = strat_drop_list)
weekly_ret=returns['Weekly'].copy()

#compute weighted hedges
print('compute weighted hedges')
notional_weights = dm.get_notional_weights(returns['Weekly'])
df_weighted_hedges = util.get_weighted_hedges(weekly_ret, notional_weights)

#get def universe
print('get def universe')
def_uni = pd.read_excel(dm.EQUITY_HEDGE_DATA+'def_uni.xlsx',sheet_name='Weekly', index_col=0)
def_uni.drop(['VIX Calls'], axis=1, inplace=True)

#merge with equity portfolio data
print('merge with equity portfolio data')
def_data = dm.merge_data_frames(df_weighted_hedges, def_uni)

#compute raw and normalized scores
print('compute raw and normalized scores')
def_dict = summary.get_norm_hedge_metrics(def_data)

#store in excel
print('store in excel')
file_path = dm.EQUITY_HEDGE_DATA+'def_uni_hedge_metrics.xlsx'
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
def_dict['Hedge Metrics'].to_excel(writer,sheet_name='Hedge Metrics')
def_dict['Normalized Data'].to_excel(writer,sheet_name='Normalized Data')
writer.save()
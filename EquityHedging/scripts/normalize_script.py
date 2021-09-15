# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 13:49:08 2021

@author: Maddie Choi & Powis Forjoe
"""
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import  util
from EquityHedging.analytics import summary 
import pandas as pd

equity_bmk = 'SPTR'
strat_drop_list = ['99%/90% Put Spread']
returns = dm.get_equity_hedge_returns(equity_bmk, strat_drop_list = strat_drop_list)
weekly_ret=returns['Weekly'].copy()

notional_weights = dm.get_notional_weights(returns['Weekly'])

hmf_dict_1 = summary.get_norm_hedge_metrics(weekly_ret, notional_weights, weighted=True)
hmf_dict_2 = summary.get_norm_hedge_metrics_2(weekly_ret, notional_weights, weighted=True)

df_weighted_hedges = util.get_weighted_hedges(weekly_ret, notional_weights)
def_uni = pd.read_excel(dm.EQUITY_HEDGE_DATA+'def_uni.xlsx',sheet_name='Weekly', index_col=0)

def_data = dm.merge_data_frames(df_weighted_hedges, def_uni)

def_dict = summary.get_norm_hedge_metrics(def_data)









file_path = 'def_uni_hedge_metrics.xlsx'
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
def_dict['Hedge Metrics'].to_excel(writer,sheet_name='Hedge Metrics')
def_dict['Normalized Data'].to_excel(writer,sheet_name='Normalized Data')
writer.save()

# -*- coding: utf-8 -*-
"""
Created on Sun May 15 21:50:52 2022

@author: nvg9hxp
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import returns_stats as rs
import pandas as pd
from EquityHedging.reporting.excel import reports as rp

asset_df = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\Historical Returns.xls', sheet_name='Historical Returns')
asset_df.columns = ['Name', 'Account Id', 'Return Type', 'Date',
       'Market Value', 'Return']
asset_ret = asset_df.pivot_table(values='Return', index='Date', columns='Name')
asset_ret /= 100
asset_mv = asset_df.pivot_table(values='Market Value', index='Date', columns='Name')


trend = asset_ret[['1907 ARP TF', '1907 Campbell TF', '1907 Systematica TF','One River Trend','Trend Following', 'Total Liquid Alts']]

trend_mv = asset_mv[['1907 ARP TF', '1907 Campbell TF', '1907 Systematica TF','One River Trend','Trend Following', 'Total Liquid Alts']]

sptr = dm.get_equity_hedge_returns(only_equity=True)['Monthly']
trend = dm.merge_data_frames(sptr,trend,True)
trend = trend.iloc[24:,]
trend_cum_ret = trend.copy()
for col in trend.columns:
    trend_cum_ret[col] = trend[col].rolling(window=6).apply(rs.get_cum_ret)
    
report_name = 'trend_rolling_6m_1'
file_path = rp.get_report_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_hist_return_sheet(writer,trend_cum_ret, '6m_rolling')
rp.sheets.set_hist_return_sheet(writer,trend, 'returns')
rp.sheets.set_hist_return_sheet(writer,trend, 'returns')

writer.save()
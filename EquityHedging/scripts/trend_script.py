# -*- coding: utf-8 -*-
"""
Created on Sun May 15 21:50:52 2022

@author: nvg9hxp
"""

from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import drawdowns as dd
from EquityHedging.analytics import summary
from EquityHedging.analytics import returns_stats as rs
import pandas as pd
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler()
sub_port = 'Trend Following'

df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports[sub_port]['returns'], False)
df_returns = dm.merge_data_frames(df_returns, liq_alts_p.sub_ports['Total Liquid Alts']['returns']['Trend Following'], False)
df_returns = dm.merge_data_frames(df_returns, liq_alts_b.returns['Monthly']['SG Trend'], False)

df_returns = df_returns.iloc[118:,]
return_dict = dm.get_monthly_dict(df_returns)
# df_mv = liq_alts_p.sub_ports[sub_port]['mv'].copy()
rp.get_alts_report('{}_report'.format(sub_port),return_dict)

rolling_ret = df_returns.copy()
for col in rolling_ret.columns:
    rolling_ret[col] = df_returns[col].rolling(window=36).apply(rs.get_ann_return)
rolling_ret.dropna(inplace=True)

rolling_vol = df_returns.copy()
for col in rolling_vol.columns:
    rolling_vol[col] = df_returns[col].rolling(window=36).apply(rs.get_ann_vol)
rolling_vol.dropna(inplace=True)

rolling_ddev = df_returns.copy()
for col in rolling_ddev.columns:
    rolling_ddev[col] = df_returns[col].rolling(window=36).apply(rs.get_updown_dev)
rolling_ddev.dropna(inplace=True)

rolling_sharpe = rolling_ret.copy()
for col in rolling_sharpe.columns:
    rolling_sharpe[col] = rolling_ret[col]/rolling_vol[col]

rolling_sortino = rolling_ret.copy()
for col in rolling_sortino.columns:
    rolling_sortino[col] = rolling_ret[col]/rolling_ddev[col]
    
    
report_name = '36m_rolling_trend'
file_path = rp.get_filepath_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_hist_return_sheet(writer,rolling_ret, '36M Rolling Ret (Ann)')
rp.sheets.set_hist_return_sheet(writer,rolling_vol, '36M Rolling Vol (Ann)')
rp.sheets.set_hist_return_sheet(writer,rolling_ddev, '36M Rolling Ddev (Ann)')
rp.sheets.set_ratio_sheet(writer,rolling_sharpe, '36M Rolling Ret_Vol')
rp.sheets.set_ratio_sheet(writer,rolling_sortino, '36M Rolling Sortino')

writer.save()



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

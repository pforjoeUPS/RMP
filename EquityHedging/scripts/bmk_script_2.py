# -*- coding: utf-8 -*-
"""
Created on Sun May 15 21:50:52 2022

@author: nvg9hxp
"""

from ipywidgets import interact, interact_manual
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import util
from EquityHedging.analytics import summary
from EquityHedging.analytics import premia_metrics as pm
from EquityHedging.analytics import returns_stats as rs
from EquityHedging.reporting import formatter as fmt, plots
import pandas as pd
import plotly.graph_objects as go

asset_df = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\Historical Returns.xls', sheet_name='Historical Returns')
asset_df.columns = ['Name', 'Account Id', 'Return Type', 'Date',
       'Market Value', 'Return']
asset_ret = asset_df.pivot_table(values='Return', index='Date', columns='Name')
asset_ret /= 100
eq_fi_df = asset_ret[['Total EQ w/o Derivatives', 'Total Fixed Income']]

bmk_df = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\bmk_data.xlsx', sheet_name='data_m', index_col=0)
bmk_df = bmk_df[['HFRXM Index','HFRIMI Index',
                  'SGIXTFXA Index', 'NEIXCTAT Index',
                 'HFRXAR Index', 'HFRXEW Index', 
                 'HEDGGLMA Index', 'CSLABT18 Index']]
#rename columns
bmk_df.columns = ['HFRX Macro/CTA', 'HFRI Macro Total Index',
                  'SGI Cross Asset Trend', 'SG Trend Index',
                  'HFRX Abs Ret', 'HFRX Equal Wgtd', 
                  'CS Global Macro', 'CS Managed Fut-18% vol']

bmk_df = dm.format_data(bmk_df)

#group indicies into sub portfolios
sp_ind_dict = {'Global Macro':['HFRX Macro/CTA', 'HFRI Macro Total Index','CS Global Macro'],
            'Absolute Return':['HFRX Abs Ret', 'HFRX Equal Wgtd'],
                'Trend Following':['SGI Cross Asset Trend', 'SG Trend Index','CS Managed Fut-18% vol']}
#create bmk_dict with sub portfolios as keys
bmk_dict = {}
for key in sp_ind_dict:
    bmk_dict[key] = bmk_df[sp_ind_dict[key]].copy()
    
    
liq_alts_df = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\mgr_data_m.xlsx', sheet_name='bny',index_col=0)
liq_alts_sp = liq_alts_df[['Total Liquid Alts',  'Global Macro',  'Trend Following','Alt Risk Premia']]
liq_alts_sp = liq_alts_sp.iloc[52:,]
liq_alts_mgr = liq_alts_df[['1907 ARP EM', '1907 ARP TF', '1907 CFM ISE Risk Premia','1907 Campbell TF', '1907 III CV',
                            '1907 III Class A', '1907 Kepos RP','1907 Penso Class A', '1907 Systematica TF',
                            'ABC Reversion','Acadian Commodity AR', 'Black Pearl RP','Blueshift', 'Bridgewater Alpha',
                            'DE Shaw Oculus Fund', 'Duality','Element Capital', 'Elliott', 'One River Trend']]

sp_mgr_dict = {'Global Macro':['1907 Penso Class A', 'Bridgewater Alpha','DE Shaw Oculus Fund', 'Element Capital', 'Elliott'],
                'Absolute Ret':['1907 ARP EM','1907 III Class A', '1907 III CV', '1907 Kepos RP',
                            'ABC Reversion','Blueshift', 'Duality'],
                'Trend Following':['1907 ARP TF','1907 Campbell TF', '1907 Systematica TF', 'One River Trend']}

liq_alts_dict = {}
for key in sp_mgr_dict:
    liq_alts_dict[key] = liq_alts_df[sp_mgr_dict[key]].copy()
    liq_alts_dict[key].dropna(inplace=True)

# sp_df = liq_alts_df[['Total Liquid Alts']]

for key in liq_alts_dict:
    liq_alts_dict[key][key] = liq_alts_dict[key].sum(axis=1)/len(liq_alts_dict[key].columns)
#     sp_df = dm.merge_data_frames(sp_df,liq_alts_dict[key][[key]])


returns_dict = {}

for key in liq_alts_dict:
    temp_liq_alts_df = liq_alts_dict[key].copy()
    temp_bmk_df = bmk_dict[key].copy()
    returns_dict[key] = dm.merge_data_frames(temp_liq_alts_df,temp_bmk_df)

corr_dict = {}    
for key in returns_dict:
    temp_dict = summary.get_corr_analysis(returns_dict[key],include_fi=True)
    corr_dict[key] = temp_dict

analytics_dict = {}
for key in returns_dict:
    temp_dict = summary.get_analysis(returns_dict[key], include_fi=True)
    analytics_dict[key] = temp_dict

quintile_df = summary.get_grouped_data(returns_dict['Global Macro'])

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
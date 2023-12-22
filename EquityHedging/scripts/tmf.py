# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 07:43:33 2022

@author: NVG9HXP
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

strat_name = 'penso'

filename='liq_alts\\penso_returns.xlsx'
sheet = 'data'
sub_port = 'Global Macro'
# Add JSC data
js_data = dm.get_new_strat_data('liq_alts\\jsc.xlsx')
js_van = js_data[['John Street Vantage']]
js_van.columns = ['JSC Vantage']
liq_alts_p = dh.liqAltsPortHandler()
sub_port_group = 'Global Macro'
allocation = 150000000
liq_alts_p.add_new_mgr(js_van,sub_port_group,allocation)


newhf_data = dm.get_new_strat_data(filename,sheet)
newhf_data.columns = [strat_name]
dd.get_worst_drawdowns(newhf_data)

# Add HF bmks
# hf_bmks = dm.get_new_strat_data('liq_alts\\mkts_hfs.xlsx', index_data=True)
hf_bmks = dm.transform_bbg_data(dm.DATA_FP+'liq_alts\\mkts_hfs.xlsx')
hf_bmks = hf_bmks.resample('1M').ffill()
hf_bmks.columns = ['HFRX Macro/CTA', 'SG Trend', 'HFRX Absolute Return', 'Equity',
                   'EM Equity', 'Gov Bonds', 'Agg Bonds', 'EM Bonds', 'High Yield',
                   'BCOM', 'S&P GSCI', 'Volatility', 'EM FX', 'FX Carry', 'Commo Carry',
                   'CTAs', 'HFRX Systematic Macro', 'HFRX Rel Val Arb', 'HFRX Global',
                   'HFRX Eq Hedge', 'HFRX Event driven', 'HFRX Convert Arb',
                   'HFRX EM', 'HFRX Commodities', 'HFRX RV']
hf_bmks = dm.format_data(hf_bmks)
# , 'HFRX Global']

newhf_full = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], welwing, False)
newhf_full = dm.merge_data_frames(newhf_full, hf_bmks, True)

dd.get_co_drawdowns(newhf_full[['M1WD']], newhf_full[[strat_name]])
# Run report
newhf_dict = dm.get_monthly_dict(newhf_full)
rp.get_alts_report('welwing_full',newhf_dict)

window =18
rolling_ret = newhf_full.copy()
for col in rolling_ret.columns:
    rolling_ret[col] = newhf_full[col].rolling(window=window).apply(rs.get_ann_return)
rolling_ret= rolling_ret.iloc[window:,]

rolling_vol = newhf_full.copy()
for col in rolling_vol.columns:
    rolling_vol[col] = newhf_full[col].rolling(window=window).apply(rs.get_ann_vol)
rolling_vol= rolling_vol.iloc[window:,]

rolling_ddev = newhf_full.copy()
for col in rolling_ddev.columns:
    rolling_ddev[col] = newhf_full[col].rolling(window=window).apply(rs.get_updown_dev)
rolling_ddev= rolling_ddev.iloc[window:,]

rolling_sharpe = rolling_ret.copy()
for col in rolling_sharpe.columns:
    rolling_sharpe[col] = rolling_ret[col]/rolling_vol[col]

rolling_sortino = rolling_ret.copy()
for col in rolling_sortino.columns:
    rolling_sortino[col] = rolling_ret[col]/rolling_ddev[col]


report_name = '{}_{}M_rolling'.format(strat_name,window)
file_path = rp.get_filepath_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_hist_return_sheet(writer,rolling_ret, '{}M Rolling Ret (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_vol, '{}M Rolling Vol (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_ddev, '{}M Rolling Ddev (Ann)'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_sharpe, '{}M Rolling Ret_Vol'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_sortino, '{}M Rolling Sortino'.format(window))

writer.save()

# XM Allocation - TMF
newhf_allocation = 50000000
liq_alts_p.add_new_mgr(newhf_data,sub_port_group,newhf_allocation)
return_dict = {}
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports[sub_port]['returns'], False)
df_returns = df_returns.iloc[120:,]
return_dict[sub_port] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns = df_returns.iloc[104:,]
return_dict['Total Liquid Alts'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.returns, False)
return_dict['Managers'] = dm.get_monthly_dict(df_returns)
mv_dict = {}
mv_dict[sub_port] = liq_alts_p.sub_ports[sub_port]['mv'].copy()    
mv_dict['Total Liquid Alts'] = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
mv_dict['Managers'] = liq_alts_p.mvs.copy()
for key in return_dict:
    rp.get_alts_report('{}_{}-100M'.format(key, report_name),return_dict[key],mv_dict[key])


#Portfolio fit
newhf_allocation = 75000000
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_p.add_new_mgr(js_van,sub_port_group,allocation)

total_la_dict = dm.get_agg_data(liq_alts_p.sub_ports['Total Liquid Alts']['returns'], 
                                 liq_alts_p.sub_ports['Total Liquid Alts']['mv'], 'Total Liquid Alts')

df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports[sub_port]['returns'], False)
df_returns = dm.merge_data_frames(df_returns, newhf_data, False)
df_returns = dm.merge_data_frames(df_returns, liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns = dm.merge_data_frames(df_returns, total_la_dict['returns'], False)
df_returns = df_returns.iloc[120:,]

pfit_dict = dm.get_monthly_dict(df_returns)
rp.get_alts_report('{}_pfit'.format(strat_name),pfit_dict)

window =12
rolling_ret = df_returns.copy()
for col in rolling_ret.columns:
    rolling_ret[col] = df_returns[col].rolling(window=window).apply(rs.get_ann_return)
rolling_ret= rolling_ret.iloc[window:,]

rolling_vol = df_returns.copy()
for col in rolling_vol.columns:
    rolling_vol[col] = df_returns[col].rolling(window=window).apply(rs.get_ann_vol)
rolling_vol= rolling_vol.iloc[window:,]

rolling_ddev = df_returns.copy()
for col in rolling_ddev.columns:
    rolling_ddev[col] = df_returns[col].rolling(window=window).apply(rs.get_updown_dev)
rolling_ddev= rolling_ddev.iloc[window:,]

rolling_sharpe = rolling_ret.copy()
for col in rolling_sharpe.columns:
    rolling_sharpe[col] = rolling_ret[col]/rolling_vol[col]

rolling_sortino = rolling_ret.copy()
for col in rolling_sortino.columns:
    rolling_sortino[col] = rolling_ret[col]/rolling_ddev[col]


report_name = '{}_{}M_pfit_rolling'.format(strat_name,window)
file_path = rp.get_filepath_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_hist_return_sheet(writer,rolling_ret, '{}M Rolling Ret (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_vol, '{}M Rolling Vol (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_ddev, '{}M Rolling Ddev (Ann)'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_sharpe, '{}M Rolling Ret_Vol'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_sortino, '{}M Rolling Sortino'.format(window))

writer.save()



return_dict[sub_port] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns = df_returns.iloc[104:,]
return_dict['Total Liquid Alts'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.returns, False)
return_dict['Managers'] = dm.get_monthly_dict(df_returns)
mv_dict = {}
mv_dict[sub_port] = liq_alts_p.sub_ports[sub_port]['mv'].copy()    
mv_dict['Total Liquid Alts'] = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
mv_dict['Managers'] = liq_alts_p.mvs.copy()
for key in return_dict:
    rp.get_alts_report('{}_{}-100M'.format(key, report_name),return_dict[key],mv_dict[key])






liq_alts_p = dh.liqAltsPortHandler()
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports[sub_port]['returns'], False)
df_returns.columns
df_returns = df_returns[['M1WD', 'FI Benchmark', 'Bridgewater Alpha',
       'DE Shaw Oculus Fund', 'Element Capital']]
df_returns = dm.merge_data_frames(df_returns, penso, False)
df_returns = df_returns[['M1WD', 'FI Benchmark', '1907 Penso Class A', 'Bridgewater Alpha',
       'DE Shaw Oculus Fund', 'Element Capital']]
df_returns = df_returns.iloc[48:,]
df_returns = df_returns.iloc[9:,]
pfit_dict = dm.get_monthly_dict(df_returns)
rp.get_alts_report('Penso_full_data',pfit_dict)

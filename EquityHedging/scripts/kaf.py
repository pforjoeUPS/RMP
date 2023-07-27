# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 07:43:33 2022

@author: NVG9HXP
"""

from EquityHedging.reporting.excel import new_reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.datamanager import data_transformer as dt
from EquityHedging.analytics import drawdowns as dd
from EquityHedging.analytics import summary
from EquityHedging.analytics import returns_stats as rs
import pandas as pd
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler()

# Import Penso, JSC, TMF
penso = dm.get_new_strat_data('liq_alts\\penso_returns.xlsx')
jsc = dm.get_new_strat_data('liq_alts\\jsc.xlsx')
tmf = dm.get_new_strat_data('liq_alts\\tmf.xlsx')

cfm = dm.get_new_strat_data('liq_alts\\discus.xlsx')

# Add KAF data
kaf = dm.get_new_strat_data('liq_alts\\kaf.xlsx')
dd.get_worst_drawdowns(kaf)

# Add HF bmks
kaf_full = dm.merge_data_frames(liq_alts_p.mkt_returns,br_disc)
kaf_full = dm.merge_data_frames(kaf_full, liq_alts_p.hf_returns,False)
kaf_full.drop(['iShares MSCI USA Value',
                'iShares US SmallCap Equity', 'iShares Factors US Growth',
                'iShares MSCI US Min Vol', 'iShares MSCI USA Momentum', 'R1K Value',
                'R1K Size', 'R1K Mtum', 'R1K LowVol', 'R1K Quality', 'Bbg US Value',
                'Bbg US Growth', 'Bbg US Vol', 'Bbg US Size', 'Bbg US Momentum',
                'Bbg US Profitability', 'Bbg US Earnings Var', 'Bbg US Div Yield',
                'Bbg US Leverage', 'Bbg US Trading Activity', 'EQ-Discretionary',
                'EQ-Staples', 'EQ-Energy', 'EQ-Comm Services', 'EQ-Financials',
                'EQ-Health Care', 'EQ-Industrials', 'EQ-Technology', 'EQ-Materials',
                'EQ-Utilities', 'EQ-Real Estate'], axis=1, inplace=True)
kaf_full.dropna(inplace=True)



kaf_full = kaf_full[['M1WD', 'FI Benchmark', 'Kepos Alpha Fund', 'HFRX Macro/CTA',
       'SG Trend', 'HFRX Absolute Return', 'DM Equity', 'EM Equity',
       'Gov Bonds', 'Agg Bonds', 'EM Bonds', 'High Yield', 'BCOM',
       'S&P GSCI TR', 'Equity Volatility', 'EM FX', 'FX Carry', 'Commo Carry',
       'CTAs', 'HFRX Systematic Macro', 'HFRX Rel Val Arb', 'HFRX Global',
       'HFRX Eq Hedge', 'HFRX Event driven', 'HFRX Convert Arb', 'HFRX EM',
       'HFRX Commodities', 'HFRX RV', 'iShares MSCI USA Value',
       'iShares US SmallCap Equity', 'iShares Factors US Growth',
       'iShares MSCI US Min Vol', 'iShares MSCI USA Momentum', 'R1K Value',
       'R1K Size', 'R1K Mtum', 'R1K LowVol', 'R1K Quality', 'Bbg US Value',
       'Bbg US Growth', 'Bbg US Vol', 'Bbg US Size', 'Bbg US Momentum',
       'Bbg US Profitability', 'Bbg US Earnings Var', 'Bbg US Div Yield',
       'Bbg US Leverage', 'Bbg US Trading Activity', 'EQ-Discretionary',
       'EQ-Staples', 'EQ-Energy', 'EQ-Comm Services', 'EQ-Financials',
       'EQ-Health Care', 'EQ-Industrials', 'EQ-Technology', 'EQ-Materials',
       'EQ-Utilities', 'EQ-Real Estate']]
# Run report
kaf_dict = dm.get_period_dict(kaf_full)
rp.get_alts_report('br_disc-full',kaf_dict)


dd.get_co_drawdowns(kaf_full[['M1WD']], kaf_full[['Welton_GM']])
dd.get_co_drawdowns(kaf_full[['FI Benchmark']], kaf_full[['Welton_GM']])
dd.get_co_drawdowns(kaf_full[['FI Benchmark']], kaf_full[['Kepos Alpha Fund']],10)
dd.get_co_drawdowns(kaf_full[['M1WD']], kaf_full[['Kepos Alpha Fund']],10)

kaf_full_q = kaf_full.resample('Q').agg(lambda x: (x+1).prod() - 1)
eq_worst_qtr = kaf_full_q.sort_values(by=['M1WD'], ascending=True)
fi_worst_qtr = kaf_full_q.sort_values(by=['FI Benchmark'], ascending=True)

window =36
rolling_ret = kaf_full.copy()
for col in rolling_ret.columns:
    rolling_ret[col] = kaf_full[col].rolling(window=window).apply(rs.get_ann_return)
rolling_ret= rolling_ret.iloc[window:,]

rolling_vol = kaf_full.copy()
for col in rolling_vol.columns:
    rolling_vol[col] = kaf_full[col].rolling(window=window).apply(rs.get_ann_vol)
rolling_vol= rolling_vol.iloc[window:,]

rolling_ddev = kaf_full.copy()
for col in rolling_ddev.columns:
    rolling_ddev[col] = kaf_full[col].rolling(window=window).apply(rs.get_updown_dev)
rolling_ddev= rolling_ddev.iloc[window:,]

rolling_sharpe = rolling_ret.copy()
for col in rolling_sharpe.columns:
    rolling_sharpe[col] = rolling_ret[col]/rolling_vol[col]

rolling_sortino = rolling_ret.copy()
for col in rolling_sortino.columns:
    rolling_sortino[col] = rolling_ret[col]/rolling_ddev[col]


report_name = 'kafpfit_{}M_rolling'.format(window)
file_path = rp.get_filepath_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_hist_return_sheet(writer,rolling_ret, '{}M Rolling Ret (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_vol, '{}M Rolling Vol (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_ddev, '{}M Rolling Ddev (Ann)'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_sharpe, '{}M Rolling Ret_Vol'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_sortino, '{}M Rolling Sortino'.format(window))

writer.save()

kaf_strat_dict = dm.get_period_dict(kaf_strat)
rp.get_strat_alts_report('kaf_strat_demo', kaf_strat_dict)

# 100M Allocation - KAF-Co
kaf_allocation = 100000000
liq_alts_p.add_new_mgr(kaf_co,sub_port_group,kaf_allocation)
return_dict = {}
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Global Macro']['returns'], False)
df_returns = df_returns.iloc[97:,]
return_dict['Global Macro'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns = df_returns.iloc[104:,]
return_dict['Total Liquid Alts'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.returns, False)
return_dict['Managers'] = dm.get_period_dict(df_returns)
mv_dict = {}
mv_dict['Global Macro'] = liq_alts_p.sub_ports['Global Macro']['mv'].copy()    
mv_dict['Total Liquid Alts'] = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
mv_dict['Managers'] = liq_alts_p.mvs.copy()
for key in return_dict:
    rp.get_alts_report('{}_kaf-co-100M'.format(key),return_dict[key],mv_dict[key])

# 100M Allocation - KAF-SMA
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_p.add_new_mgr(js_van,sub_port_group,allocation)
liq_alts_p.add_new_mgr(kaf_sma,sub_port_group,kaf_allocation)
return_dict = {}
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Global Macro']['returns'], False)
df_returns = df_returns.iloc[97:,]
return_dict['Global Macro'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns = df_returns.iloc[104:,]
return_dict['Total Liquid Alts'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.returns, False)
return_dict['Managers'] = dm.get_perod_dict(df_returns)
mv_dict = {}
mv_dict['Global Macro'] = liq_alts_p.sub_ports['Global Macro']['mv'].copy()    
mv_dict['Total Liquid Alts'] = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
mv_dict['Managers'] = liq_alts_p.mvs.copy()
for key in return_dict:
    rp.get_alts_report('{}_kaf-sma-100M'.format(key),return_dict[key],mv_dict[key])


# 150M Allocation - KAF-Co
kaf_allocation = 150000000
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_p.add_new_mgr(js_van,sub_port_group,allocation)
liq_alts_p.add_new_mgr(kaf_co,sub_port_group,kaf_allocation)
return_dict = {}
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Global Macro']['returns'], False)
df_returns = df_returns.iloc[97:,]
return_dict['Global Macro'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns = df_returns.iloc[104:,]
return_dict['Total Liquid Alts'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.returns, False)
return_dict['Managers'] = dm.get_period_dict(df_returns)
mv_dict = {}
mv_dict['Global Macro'] = liq_alts_p.sub_ports['Global Macro']['mv'].copy()    
mv_dict['Total Liquid Alts'] = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
mv_dict['Managers'] = liq_alts_p.mvs.copy()
for key in return_dict:
    rp.get_alts_report('{}_kaf-co-150M'.format(key),return_dict[key],mv_dict[key])


# 150M Allocation - KAF-SMA
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_p.add_new_mgr(js_van,sub_port_group,allocation)
liq_alts_p.add_new_mgr(kaf_sma,sub_port_group,kaf_allocation)
return_dict = {}
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Global Macro']['returns'], False)
df_returns = df_returns.iloc[65:,]
return_dict['Global Macro'] = dm.get_period_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns = df_returns.iloc[104:,]
return_dict['Total Liquid Alts'] = dm.get_period_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.returns, False)
return_dict['Managers'] = dm.get_period_dict(df_returns)
mv_dict = {}
mv_dict['Global Macro'] = liq_alts_p.sub_ports['Global Macro']['mv'].copy()    
mv_dict['Total Liquid Alts'] = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
mv_dict['Managers'] = liq_alts_p.mvs.copy()
for key in return_dict:
    rp.get_alts_report('{}_kaf-sma-150M'.format(key),return_dict[key],mv_dict[key])



df_returns_gm = dm.merge_data_frames(liq_alts_p.mkt_returns, liq_alts_p.sub_ports['Global Macro']['returns'], False)
df_returns_gm.drop(['1907 Penso Class A','JSC Vantage', 'Global Macro'], axis=1, inplace=True)
df_returns_gm = dm.merge_data_frames(df_returns_gm,penso, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,jsc, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,tmf, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,kaf, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,gm_qm, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,edl, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,br_disc, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,astignes, False)
# df_returns_gm = dm.merge_data_frames(df_returns_gm,campbell_ar, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,modular, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm, liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns_gm = df_returns_gm.iloc[93:,]
df_returns_gm = df_returns_gm[:-2]

rp.get_returns_report_1('test_new_sheets', {'Monthly':df_returns})

ret_dict_gm = dm.get_period_dict(df_returns_gm)
rp.get_alts_report('br_disc-pfit',ret_dict_gm)

df_returns_tf = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Trend Following']['returns'], False)
df_returns_tf.drop(['Trend Following'], axis=1, inplace=True)
df_returns_tf = dm.merge_data_frames(df_returns_tf,welton_tf_strats, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,welton_tf_hypo, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,aqr_tf, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,aspect, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf, liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns_tf = df_returns_tf.iloc[90:,]
df_returns_tf = df_returns_tf[:-2]
ret_dict_tf = dm.get_period_dict(df_returns_tf)
rp.get_alts_report('welton-hypo-fit',ret_dict_tf)

df_returns_ar = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Absolute Return']['returns'], False)
df_returns_ar.drop(['Absolute Return'], axis=1, inplace=True)
# df_returns_ar = dm.merge_data_frames(df_returns_ar,welwing, False)
# df_returns_ar = dm.merge_data_frames(df_returns_ar,eof, False)
# df_returns_ar = dm.merge_data_frames(df_returns_ar,east_value, False)
df_returns_ar = dm.merge_data_frames(df_returns_ar,voleon, False)
df_returns_ar = dm.merge_data_frames(df_returns_ar,voloridge, False)
# df_returns_ar = dm.merge_data_frames(df_returns_ar,gemini, False)
df_returns_ar = dm.merge_data_frames(df_returns_ar, liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns_ar = df_returns_ar[:-6]
df_returns_ar = df_returns_ar.iloc[13:,]

ret_dict_ar = dm.get_period_dict(df_returns_ar)
rp.get_alts_report('liq_alts-fit',ret_dict_ar)

#DD MAtrix
df_ret = df_returns_gm.copy()
report_name = 'br_disc_dd'
dd_dict = {}

for mgr in df_ret.columns:
    print(mgr)
    dd_dict[mgr] = dd.get_co_drawdowns(df_ret[[mgr]], df_ret.drop([mgr], axis=1))
    
dd_df = dm.pd.DataFrame(columns=['peak', 'trough', 'drawdown'] + list(df_ret.columns))
for key in dd_dict:
  dd_df = dm.pd.concat([dd_df,dd_dict[key].head(1)])
  
dd_df= dd_df.set_index(df_ret.columns, drop=False).rename_axis(None)
dd_df.rename(columns={'peak':'Start Date', 'trough':'End Date', 'drawdown':'Strategy Max DD'}, inplace=True)
file_path = rp.get_filepath_path(report_name)
writer = dm.pd.ExcelWriter(file_path, engine='xlsxwriter')
rp.sheets.set_hist_sheet(writer, dd_df, 'Max DD vs Strats')

writer.save()
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 07:43:33 2022

@author: NVG9HXP
"""

from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.datamanager import data_xformer as dt
from EquityHedging.analytics import drawdowns as dd
from EquityHedging.analytics import summary
from EquityHedging.analytics import corr_stats
from EquityHedging.analytics import returns_stats as rs
import pandas as pd
import copy
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler1()

# Import Penso, JSC, TMF
penso = dm.get_new_strat_data('liq_alts\\penso_returns.xlsx')
jsc = dm.get_new_strat_data('liq_alts\\jsc.xlsx')
tmf = dm.get_new_strat_data('liq_alts\\tmf.xlsx')

cfm = dm.get_new_strat_data('liq_alts\\discus.xlsx')

# Add KAF data
kaf = dm.get_new_strat_data('liq_alts\\kaf.xlsx')
dd.get_worst_drawdowns(aqr_tf)

# Add HF bmks
kaf_full = dm.merge_data_frames(liq_alts_p.mkt_returns,wb_rv)
kaf_full = dm.merge_data_frames(kaf_full,wb_ms,False)
kaf_full = dm.merge_data_frames(kaf_full,voleon,False)
kaf_full = dm.merge_data_frames(kaf_full, liq_alts_p.hf_returns,False)
kaf_full.dropna(inplace=True)
kaf_full.drop(['Commo Carry'], axis=1, inplace=True)

# Run report
kaf_dict = dm.get_period_dict(kaf_full)
rp.get_alts_report('wb-full',kaf_dict)


dd.get_co_drawdowns(kaf_full[['M1WD']], kaf_full[['EDL-A']])
dd.get_co_drawdowns(kaf_full[['FI Benchmark']], kaf_full[['EDL-A']])
dd.get_co_drawdowns(kaf_full[['FI Benchmark']], kaf_full[['EDL-A']],10)
dd.get_co_drawdowns(kaf_full[['M1WD']], kaf_full[['EDL-A']],10)

kaf_full_q = kaf_full.resample('Q').agg(lambda x: (x+1).prod() - 1)
eq_worst_qtr = kaf_full_q.sort_values(by=['M1WD'], ascending=True)
fi_worst_qtr = kaf_full_q.sort_values(by=['FI Benchmark'], ascending=True)


#TODO: add as report
window =36
# kaf_full = overlay_dict_2['Weekly'].copy()
rolling_ret = kaf_full.copy()
rolling_vol = kaf_full.copy()
rolling_ddev = kaf_full.copy()
for col in rolling_ret.columns:
    rolling_ret[col] = kaf_full[col].rolling(window=window).apply(rs.get_ann_return)
    rolling_vol[col] = kaf_full[col].rolling(window=window).apply(rs.get_ann_vol)
    rolling_ddev[col] = kaf_full[col].rolling(window=window).apply(rs.get_updown_dev)
rolling_ret= rolling_ret.iloc[window:,]
rolling_vol= rolling_vol.iloc[window:,]
rolling_ddev= rolling_ddev.iloc[window:,]

rolling_sharpe = rolling_ret.copy()
rolling_sortino = rolling_ret.copy()
for col in rolling_sharpe.columns:
    rolling_sharpe[col] = rolling_ret[col]/rolling_vol[col]
    rolling_sortino[col] = rolling_ret[col]/rolling_ddev[col]

rolling_excess = rolling_ret[list(rolling_ret.columns[4:])].copy()
rolling_te = rolling_excess.copy()
rolling_te_asym = rolling_excess.copy()
for col in rolling_excess.columns:
    bmk_name = 'HFRX Absolute Return'
    df_port_bmk = dm.merge_data_frames(kaf_full[[col]],liq_alts_p.bmk_returns[[bmk_name]])
    df_port_bmk.columns = ['port', 'bmk']
    df_port_bmk[col] = df_port_bmk['port'] - df_port_bmk['bmk']
    
    rolling_excess[col] = kaf_full[col].rolling(window=window).apply(rs.get_ann_return) - liq_alts_p.bmk_returns[bmk_name].rolling(window=window).apply(rs.get_ann_return)
    rolling_te[col] = df_port_bmk[col].rolling(window=window).apply(rs.get_ann_vol)
    rolling_te_asym[col] = df_port_bmk[col].rolling(window=window).apply(rs.get_updown_dev)
   
rolling_ir = rolling_excess.copy()
rolling_ir_asym = rolling_excess.copy()
for col in rolling_ir.columns:
    rolling_ir[col] = rolling_excess[col]/rolling_te[col]
    rolling_ir_asym[col] = rolling_excess[col]/rolling_te_asym[col]

corr_df = returns_df.copy()
strat = corr_df.columns[2]
strat_corr_df=corr_df.corr()

rolling_corr = corr_df.rolling(window=window).corr().unstack()
rolling_corr.dropna(inplace=True)

rolling_corr_dict = {}
for col in corr_df:
    print(col)
    rolling_corr_temp= rolling_corr.loc[:, ([col], list(corr_df.columns))]
    rolling_corr_temp= rolling_corr_temp.droplevel(level=0, axis=1)
    rolling_corr_temp.drop([col], axis=1, inplace=True)
    rolling_corr_dict[col] = rolling_corr_temp.iloc[window-1:,]

rolling_corr= rolling_corr.loc[:, ([strat], list(corr_df.columns))]
rolling_corr= rolling_corr.droplevel(level=0, axis=1)
rolling_corr.drop([strat], axis=1, inplace=True)
rolling_corr = rolling_corr.iloc[window-1:,]

def get_rolling_corr(ret_series_1, ret_series_2, window):
    rolling_corr = pd.DataFrame(ret_series_1.rolling(window).corr(ret_series_2), columns=[ret_series_2.name])
    rolling_corr.dropna(inplace=True)
    return rolling_corr

rolling_corr_dict_1 = {}
for col in corr_df:
    print(col)
    temp_strat_list = list(corr_df.columns).copy()
    temp_strat_list.remove(col)
    rolling_corr_temp = get_rolling_corr(corr_df[col],corr_df[col], window)
    for x in temp_strat_list:
        rolling_corr_temp = dm.merge_data_frames(rolling_corr_temp, get_rolling_corr(corr_df[col],corr_df[x], window),False)
    rolling_corr_temp.drop([col], axis=1, inplace=True)
    rolling_corr_dict_1[col] = rolling_corr_temp

    rolling_corr_temp= rolling_corr.loc[:, ([col], list(corr_df.columns))]
    rolling_corr_temp= rolling_corr_temp.droplevel(level=0, axis=1)
    rolling_corr_temp.drop([col], axis=1, inplace=True)
    rolling_corr_dict[col] = rolling_corr_temp.iloc[window-1:,]


report_name = f'whitebox_{window}M_rolling'
file_path = rp.get_filepath_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_hist_return_sheet(writer,rolling_ret, '{}M Rolling Ret (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_vol, '{}M Rolling Vol (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_ddev, '{}M Rolling Ddev (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_excess, '{}M Rolling Excess Ret (Ann)'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_te, '{}M Rolling TE'.format(window))
rp.sheets.set_hist_return_sheet(writer,rolling_te_asym, '{}M Rolling TE Asymm'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_sharpe, '{}M Rolling Ret_Vol'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_sortino, '{}M Rolling Sortino'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_ir, '{}M Rolling IR'.format(window))
rp.sheets.set_ratio_sheet(writer,rolling_ir_asym, '{}M Rolling IR Asymm'.format(window))
rp.sheets.set_hist_return_sheet(writer,kaf_full)
rp.sheets.set_ratio_sheet(writer,rolling_corr, '{}M Rolling Corr'.format(window))

writer.save()

corr_df = kaf_full.copy()
strat = corr_df.columns[2]
strat_corr_df=corr_df.corr()

rolling_corr = corr_df.rolling(window=window).corr().unstack()
rolling_corr.dropna(inplace=True)
rolling_corr= rolling_corr.loc[:, ([strat], list(corr_df.columns))]
rolling_corr= rolling_corr.droplevel(level=0, axis=1)
rolling_corr.drop([strat], axis=1, inplace=True)
rolling_corr = rolling_corr.iloc[window-1:,]
report_name = f'edl-{window}M_rolling_corr-3'
file_path = rp.get_filepath_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_ratio_sheet(writer,rolling_corr, '{}M Rolling Corr'.format(window))

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
# df_returns_gm = dm.merge_data_frames(liq_alts_p.mkt_returns, liq_alts_p.bmk_returns['HFRX Macro/CTA'], False)
# df_returns_gm = liq_alts_p.returns.copy()
df_returns_gm.drop(['1907 Penso Class A','JSC Vantage', 'Capula TM Fund', 'KAF'], axis=1, inplace=True)
df_returns_gm = dm.merge_data_frames(df_returns_gm,penso, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,jsc, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,tmf, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,kaf, False)
# df_returns_gm = dm.merge_data_frames(df_returns_gm,hfrxsvd_aifa, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,edl_c, False)
df_returns_gm = df_returns_gm[['MSCI ACWI', 'FI Benchmark','1907 Penso Class A', 'Bridgewater Alpha', 'DE Shaw Oculus Fund',
                               'Element Capital',  'JSC Vantage','Capula TM Fund', 'KAF', 'EDL-C']]
df_returns_gm = dm.merge_data_frames(df_returns_gm,dymon_asia, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,gm_qm_a, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,gmo_sys, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,wellington[['WMSF Composite1']], False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,astignes, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,campbell_ar, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,modular, False)
df_returns_gm = dm.merge_data_frames(df_returns_gm,liq_alts_p.sub_ports['Trend Following']['returns'], False)
df_returns_gm.drop(['Trend Following', '1907 ARP TF'], axis=1, inplace=True)
df_returns_gm = dm.merge_data_frames(df_returns_gm, liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns_gm = df_returns_gm[['SG Trend','Trend Following','1907 Penso Class A', 'Bridgewater Alpha', 'DE Shaw Oculus Fund',
                               'Element Capital',  'JSC Vantage','Capula TM Fund', 'KAF', 'EDL-A', 'Graham QM (0% Trend)',
'Graham QM (10% Trend)', 'Graham QM (15% Trend)',
'Graham QM (Unrestricted)', 'Global Macro',
'Absolute Return', 'Total Liquid Alts']]
df_returns_gm = df_returns_gm.iloc[130:,]
df_returns_gm = df_returns_gm[:-1]


df_returns_gm = df_returns_gm.iloc[12:,]
rp.get_returns_report_1('test_new_sheets', {'Monthly':df_returns})

df_returns_gm = df_returns_gm.iloc[(165-133):,]
ret_dict_gm = dm.get_period_dict(df_returns_gm)
mv_dict_gm = dm.get_period_dict(liq_alts_p.sub_ports['Global Macro']['mv'])
import copy
bmk_dict = copy.deepcopy(liq_alts_p.mgr_bmk_dict)
for col in ['EDL-C', 'Dymon Asia', 'Astignes', 'Modular']:
    bmk_dict[col] = 'HFRX Macro/CTA'
rp.get_alts_report('Dymon_asia-full',ret_dict_gm,include_bmk=True, df_bmk=liq_alts_p.bmk_returns, bmk_dict=bmk_dict)

df_ret_tf = dm.merge_data_frames(liq_alts_p.mkt_returns, liq_alts_p.bmk_returns['SG Trend'], False)
df_ret_tf = dm.merge_data_frames(df_ret_tf, liq_alts_p.sub_ports['Trend Following']['returns'], False)
df_mv_tf = liq_alts_p.sub_ports['Trend Following']['mv'].copy()
df_ret_tf = df_ret_tf.iloc[117:,]
df_mv_tf = df_mv_tf.iloc[117:,]

ret_dict_tf = dm.get_period_dict(df_ret_tf)
mv_dict_tf = dm.get_period_dict(liq_alts_p.sub_ports['Trend Following']['mv'])
rp.get_alts_report('tf-fit',ret_dict_tf, mv_dict_tf, include_bmk=True)


df_returns_tf = dm.merge_data_frames(liq_alts_p.mkt_returns, liq_alts_p.sub_ports['Trend Following']['returns'], False)
df_returns_tf.drop(['Trend Following'], axis=1, inplace=True)
df_returns_tf = dm.merge_data_frames(df_returns_tf,welton_tf_strats, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,welton_tf_hypo, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,aqr_tf, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,aspect, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf, liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns_tf = df_returns_tf.iloc[90:,]
df_returns_tf = df_returns_tf[:-3]
ret_dict_tf = dm.get_period_dict(df_returns_tf)
rp.get_alts_report('welton-hypo-fit',ret_dict_tf)

df_returns_ar = dm.merge_data_frames(liq_alts_p.mkt_returns, liq_alts_p.sub_ports['Absolute Return']['returns'], False)
df_returns_ar = dm.merge_data_frames(df_returns_ar,wb_rv, False)
df_returns_ar = dm.merge_data_frames(df_returns_ar,wb_ms, False)
df_returns_ar = dm.merge_data_frames(df_returns_ar,rathmore, False)
df_returns_ar = dm.merge_data_frames(df_returns_ar,tcc, False)

df_returns_ar = dm.merge_data_frames(df_returns_ar, liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns_ar = df_returns_ar[['MSCI ACWI', 'FI Benchmark','1907 III Class A','Acadian Commodity AR',
                               'Elliott', 'Duality', '1907 III CV','Whitebox RV', 'Whitebox Multi-Strat',
                               'Global Macro', 'Trend Following','Absolute Return', 'Total Liquid Alts']]
df_returns_ar = df_returns_ar[:-1]
df_returns_ar = df_returns_ar.iloc[100:,]

ret_dict_ar = dm.get_period_dict(df_returns_ar)
bmk_dict = copy.deepcopy(liq_alts_p.mgr_bmk_dict)
for col in ['Whitebox RV', 'Whitebox Multi-Strat','Rathmore', 'TCC']:
    bmk_dict[col] = 'HFRX Absolute Return'
rp.get_alts_report('Whitebox-fit',ret_dict_ar,include_bmk=True, df_bmk=liq_alts_p.bmk_returns, bmk_dict=bmk_dict)

#TODO: Make this method in drawdown.py
#DD MAtrix
df_ret = df_returns_ar.copy()
report_name = 'ar_ml_dd'
dd_dict = {}

for mgr in df_ret.columns:
    # print(mgr)
    dd_dict[mgr] = dd.get_co_drawdowns(df_ret[[mgr]], df_ret.drop([mgr], axis=1))
    
dd_df = dm.pd.DataFrame(columns=['peak', 'trough', 'drawdown'] + list(df_ret.columns))
for key in dd_dict:
  dd_df = dm.pd.concat([dd_df,dd_dict[key].head(1)])
  
dd_df= dd_df.set_index(df_ret.columns, drop=False).rename_axis(None)
dd_df.rename(columns={'peak':'Start Date', 'trough':'End Date', 'drawdown':'Strategy Max DD'}, inplace=True)
dd_df = dd.get_dd_matrix(df_returns_ar)
file_path = rp.get_filepath_path(report_name)
writer = dm.pd.ExcelWriter(file_path, engine='xlsxwriter')
rp.sheets.set_hist_sheet(writer, dd_df, 'Max DD vs Strats')

writer.save()

df_returns_tf = dm.merge_data_frames(liq_alts_p.mkt_returns, liq_alts_p.sub_ports['Trend Following']['returns'], False)
df_returns_tf.drop(['Trend Following'], axis=1, inplace=True)
df_returns_tf = dm.merge_data_frames(df_returns_tf,welton_tf, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,transtrend, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,aspect, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,aqr_tf, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf,one_river_alt, False)
df_returns_tf = dm.merge_data_frames(df_returns_tf, liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns_tf = df_ret_tf.iloc[117:,]
df_returns_tf = df_returns_tf[:-2]
df_returns_tf = df_returns_tf.iloc[58:,]
df_returns_tf = df_returns_tf.iloc[2:,]
ret_dict_tf = dm.get_period_dict(df_returns_tf)
rp.get_alts_report('welton-hypo-fit-tf',ret_dict_tf)

from EquityHedging.analytics import summary
import pandas as pd
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp
fi_data = dm.get_new_strat_data('liq_alts\\fi_data.xlsx','full')
analytics = summary.get_fi_data(fi_data)

fi_dict = dm.get_period_dict(fi_data)
del fi_dict['10 Year']
rp.get_fi_report('fi-report',fi_dict)
fi_2 = fi_data[['M1WD', 'FI', 'Jennison','Jennison Active']]
fi_dict_2 = dm.get_period_dict(fi_2)
del fi_dict_2['10 Year']
rp.get_strat_alts_report('fi_strats', fi_dict_2)


df_returns = fi_data.copy()
freq='1M'
mkt_list = [df_returns.columns[0]]
col = 'DCI'
df_strat = dm.remove_na(df_returns, col)[col]
temp_df = df_returns[mkt_list + [col]].copy()
temp_df.dropna(inplace=True)
mkt_strat = temp_df[mkt_list[0]]
active_strat = df_strat - mkt_strat


fi_1 = fi_data[['Barclay', 'Jennison']]
fi_dict_1 = dm.get_period_dict(fi_1)
del fi_dict_1['10 Year']
from EquityHedging.reporting.excel import reports as rp
rp.get_strat_fi_report('fi_jennison', fi_dict_1)


rename_cols = ['Equities','FI Benchmark','Macro','Trend','Absolute Return','DM Equities','EM Equities',
 'Gov Bonds','Agg Bonds','EM Bonds','High Yield','Commodities (BCOM)','Commodities (GSCI)',
 'Equity Vol','EM FX','FX Carry','CTAs','Systematic Macro','Relative Value Arbitrage',
 'Hedge Funds','Equity Long/Short','Event Driven','Convertible Arbitrage','HFRX EM',
 'HFRX Commodities','Relative Value']

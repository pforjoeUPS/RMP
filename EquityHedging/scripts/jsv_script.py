# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 00:04:33 2022

@author: NVG9HXP
"""

from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import drawdowns as dd
from EquityHedging.analytics import summary

liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler()
js_data = dm.get_new_strat_data('liq_alts\\jsc.xlsx')
hf_bmks = dm.get_new_strat_data('liq_alts\\mkts_hfs.xlsx', index_data=True)
qis = dm.get_new_strat_data('liq_alts\\equity_hedge_analysis_102022.xlsx')
js_van = js_data[['John Street Vantage']]
js_van.columns = ['JSC Vantage']

#Invst Perf
js_van_ym = dm.month_ret_table(js_van, 'John Street Vantage')
js_dd = dd.get_worst_drawdowns(js_van,10)
bmks = dh.bmkHandler()
jsv_full = dm.merge_data_frames(bmks.bmk_returns['Monthly'], js_van)
hf_bmks = dm.get_new_strat_data('liq_alts\\mkts_hfs.xlsx', index_data=True)
jsv_full = dm.merge_data_frames(jsv_full, hf_bmks)
jsv_dict_full = dm.get_monthly_dict(jsv_full)
rp.get_alts_report('jsv_full-3',jsv_dict_full)

jsc_v_spd = dm.get_new_strat_data('liq_alts\\jsc.xlsx', 'speed')
jsc_v_ctrb = dm.get_new_strat_data('liq_alts\\jsc.xlsx', 'ctrb')

spd_ym = summary.all_strat_month_ret_table(jsc_v_spd)

ctrb_ym = summary.all_strat_month_ret_table(jsc_v_ctrb)


liq_alts_p = dh.liqAltsPortHandler()
sub_port_group = 'Global Macro'
allocation = 150000000
liq_alts_p.add_new_mgr(js_van,sub_port_group,allocation)


allocation = 150000000
liq_alts_p.add_new_mgr(kaf_co,sub_port_group,allocation)
return_dict = {}
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Global Macro']['returns'], False)
df_returns = df_returns.iloc[97:,]
return_dict['Global Macro'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns = df_returns.iloc[104:,]
return_dict['Total Liquid Alts'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.returns, False)
return_dict['Managers'] = dm.get_monthly_dict(df_returns)
mv_dict = {}

for key in liq_alts_p.sub_ports:
    mv_dict[key] = liq_alts_p.sub_ports[key]['mv'].copy()
mv_dict['Global Macro'] = liq_alts_p.sub_ports['Global Macro']['mv'].copy()    
mv_dict['Total Liquid Alts'] = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
mv_dict['Managers'] = liq_alts_p.mvs.copy()
for key in return_dict:
    rp.get_alts_report('{}_kaf-co-150M'.format(key),return_dict[key],mv_dict[key])
    
    
bmks = dh.bmkHandler()

jsv_full = dm.merge_data_frames(bmks.bmk_returns['Monthly'], js_van)
jsv_oct = jsv_full.iloc[3:,]

jsv_dict_full = dm.get_monthly_dict(jsv_full)
jsv_dict_oct = dm.get_monthly_dict(jsv_oct)

rp.get_alts_report('jsv_full',jsv_dict_full)
rp.get_alts_report('jsv_oct',jsv_dict_oct)
    


file_path = rp.get_filepath_path('jsv_month-year')
writer = dm.pd.ExcelWriter(file_path,engine='xlsxwriter')
js_van_ym.to_excel(writer, sheet_name='data', startrow=0, startcol=0)
rp.print_report_info('jsv_month-year', file_path)
writer.save()

file_path = rp.get_filepath_path('jsv_dd')
writer = dm.pd.ExcelWriter(file_path,engine='xlsxwriter')
js_dd.to_excel(writer, sheet_name='dd', startrow=0, startcol=0)
rp.print_report_info('jsv_dd', file_path)
writer.save()

tf_df = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Global Macro']['returns'][['JSC Vantage']], False)

tf_df = dm.merge_data_frames(tf_df, liq_alts_p.sub_ports['Trend Following']['returns'], False)

tf_df = dm.merge_data_frames(tf_df, liq_alts_p.sub_ports['Total Liquid Alts']['returns'][['Trend Following']], False)

tf_df = dm.merge_data_frames(tf_df, hf_bmks[['NEIXCTAT Index']], False)

tf_df.columns = ['M1WD', 'FI Benchmark', 'JSC Vantage', '1907 ARP TF', '1907 Campbell TF',
       '1907 Systematica TF', 'One River Trend',
       'Trend Following', 'SG Trend Index']

tf_dict = dm.get_monthly_dict(tf_df)
rp.get_alts_report('jsv_tf_analysis-',tf_dict)

df_ret = liq_alts_p.sub_ports['Total Liquid Alts']['returns'].copy()
df_ret = df_ret.iloc[79:,]
df_mv = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
df_mv = df_mv.iloc[79:,]
df_ret['Total Liquid Alts'] = dm.get_agg_data(df_ret, df_mv, 'Total Liquid Alts')['returns']
df_mv['Total Liquid Alts'] = dm.get_agg_data(df_ret, df_mv, 'Total Liquid Alts')['mv']

jsv_pfit = dm.merge_data_frames(df_returns, df_ret)
pfit = dm.get_monthly_dict(jsv_pfit)
rp.get_alts_report('pfit_w_JSV-3', pfit)
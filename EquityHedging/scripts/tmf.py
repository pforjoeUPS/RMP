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
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler()

# Add JSC data
js_data = dm.get_new_strat_data('liq_alts\\jsc.xlsx')
js_van = js_data[['John Street Vantage']]
js_van.columns = ['JSC Vantage']
liq_alts_p = dh.liqAltsPortHandler()
sub_port_group = 'Global Macro'
allocation = 150000000
liq_alts_p.add_new_mgr(js_van,sub_port_group,allocation)

tmf_data = dm.get_new_strat_data('liq_alts\\tmf.xlsx')
dd.get_worst_drawdowns(tmf_data)

# Add HF bmks
hf_bmks = dm.get_new_strat_data('liq_alts\\mkts_hfs.xlsx', index_data=True)
tmf_full = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], tmf_data, False)
tmf_full = dm.merge_data_frames(tmf_full, hf_bmks, True)

# Run report
tmf_dict = dm.get_monthly_dict(tmf_full)
rp.get_alts_report('tmf_full',tmf_dict)









# 100M Allocation - KAF-Co
tmf_allocation = 100000000
liq_alts_p.add_new_mgr(tmf_data,sub_port_group,tmf_allocation)
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
mv_dict['Global Macro'] = liq_alts_p.sub_ports['Global Macro']['mv'].copy()    
mv_dict['Total Liquid Alts'] = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
mv_dict['Managers'] = liq_alts_p.mvs.copy()
for key in return_dict:
    rp.get_alts_report('{}_tmf-100M'.format(key),return_dict[key],mv_dict[key])

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
return_dict['Managers'] = dm.get_monthly_dict(df_returns)
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
return_dict['Managers'] = dm.get_monthly_dict(df_returns)
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
df_returns = df_returns.iloc[97:,]
return_dict['Global Macro'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
df_returns = df_returns.iloc[104:,]
return_dict['Total Liquid Alts'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.returns, False)
return_dict['Managers'] = dm.get_monthly_dict(df_returns)
mv_dict = {}
mv_dict['Global Macro'] = liq_alts_p.sub_ports['Global Macro']['mv'].copy()    
mv_dict['Total Liquid Alts'] = liq_alts_p.sub_ports['Total Liquid Alts']['mv'].copy()
mv_dict['Managers'] = liq_alts_p.mvs.copy()
for key in return_dict:
    rp.get_alts_report('{}_kaf-sma-150M'.format(key),return_dict[key],mv_dict[key])


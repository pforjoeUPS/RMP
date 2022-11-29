# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 00:04:33 2022

@author: NVG9HXP
"""

from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler()
js_data = dm.get_new_strat_data('liq_alts\\Johns Street.xlsx')
hf_bmks = dm.get_new_strat_data('liq_alts\\hf_bmks.xlsx', index_data=True)
js_van = js_data[['John Street Vantage']]

#Invst Perf
bmks = dh.bmkHandler()
jsv_full = dm.merge_data_frames(bmks.bmk_returns['Monthly'], js_van)
hf_bmks = dm.get_new_strat_data('liq_alts\\hf_bmks.xlsx', index_data=True)
jsv_full = dm.merge_data_frames(jsv_full, hf_bmks)
jsv_dict_full = dm.get_monthly_dict(jsv_full)
rp.get_alts_report('jsv_full',jsv_dict_full)


sub_port_group = 'Global Macro'
allocation = 100000000
liq_alts_p.add_new_mgr(js_van,sub_port_group,allocation)
return_dict = {}
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Global Macro']['returns'], False)
return_dict['Global Macro'] = dm.get_monthly_dict(df_returns)
df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'], False)
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
    rp.get_alts_report('{}_capula100M'.format(key),return_dict[key],mv_dict[key])
    
    
bmks = dh.bmkHandler()

jsv_full = dm.merge_data_frames(bmks.bmk_returns['Monthly'], js_van)
jsv_oct = jsv_full.iloc[3:,]

jsv_dict_full = dm.get_monthly_dict(jsv_full)
jsv_dict_oct = dm.get_monthly_dict(jsv_oct)

rp.get_alts_report('jsv_full',jsv_dict_full)
rp.get_alts_report('jsv_oct',jsv_dict_oct)
    

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 07:47:44 2023

@author: NVG9HXP
"""

from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.datamanager import data_xformer_new as dxf
from EquityHedging.datamanager import data_updater_new as du
from EquityHedging.analytics import drawdowns as dd
from EquityHedging.analytics import summary
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler1()

itd_dxf = dxf.bbgDataXformer(du.UPDATE_DATA_FP+'itd_overlay_data.xlsx',freq='1D', col_list=['SPX_ODTE', 'SPX', 'NDX_BNP', 'NDX_BX', 'APAC', 'SX5E', 'WTI_SHORT', 'WTI', 'NG_SHORT', 'GC_SG', 'GC_MS']) 
df_returns_w = dm.merge_data_frames(liq_alts_b.mkt_returns['Weekly'], liq_alts_b.bmk_returns['Weekly'][['SG Trend']], True)
df_ret_w = dm.merge_data_frames(df_returns_w,itd_dxf.data_xform['Weekly'])

ret_dict_w = dm.get_period_dict(df_ret_w, '1W')
rp.get_alts_report('ups_itd-sep2023',ret_dict_w, include_bmk=False, freq='1W')

overlay_wts_dict = {'Alt 1': [.05, .07, .04, .06, .03, .12, .04, .11, .04, .05, .39],
                    'Alt 2': [.10, .13, .08, .11, .06, .23, .02, .08, .10, .01, .09],
                    'Alt 3': [.08, .10, .06, .09, .04, .18, .04, .11, .10, .02, .18],
                    'Alt 4': [.10, .10, .06, .09, .05, .15, .05, .10, .10, .05, .15],
                    'Alt 5': [.10, .10, .09, .09, .06, .10, .07, .07, .10, .05, .17],
                    'Alt 6': [.10, .10, .09, .09, .06, .11, .05, .10, .10, .05, .15],
                    'Full':  [.08, .06, .05, .09, .08, .20, .02, .03, .04, .08, .26],
                    '5Y':    [.09, .06, .05, .09, .08, .20, .02, .02, .04, .08, .26],
                    '3Y':    [.06, .07, .06, .08, .06, .17, .04, .03, .02, .06, .35],
                    '1Y':    [.06, .08, .05, .09, .05, .14, .04, .13, .01, .04, .29]
                    }

itd_strats = df_ret_w.iloc[:,5:].copy()
df_overlay_w = df_ret_w.copy()
for key in overlay_wts_dict:
    df_overlay_w[key] = itd_strats.dot(overlay_wts_dict[key])
ret_overlay_dict_w = dm.get_period_dict(df_overlay_w, '1W')
rp.get_alts_report('ups_itd-overlay-sep2023',ret_overlay_dict_w, include_bmk=False, freq='1W')

report_name = 'itd_overlay_dd'
dd_dict = {}
file_path = rp.get_filepath_path(report_name)
writer = dm.pd.ExcelWriter(file_path, engine='xlsxwriter')
dd_matrix = dd.get_dd_matrix(df_ret_w)
rp.sheets.set_hist_sheet(writer, dd_matrix, 'DD Matrix')

for idx in df_ret_w.columns:
    print(idx)
    dd_df = dd.get_co_drawdowns(df_overlay_w[[idx]], df_overlay_w, num_worst=10)
    dd_df.dropna(inplace=True)
    dd_df.rename(columns={'peak':'Start Date', 'trough':'End Date'}, inplace=True)
    rp.sheets.set_hist_sheet(writer, dd_df, idx)
writer.save()

import copy
overlay_dict = copy.deepcopy(itd_dxf.data_xform)
for freq in overlay_dict:
    for key in overlay_wts_dict:
        overlay_dict[freq][key] = itd_dxf.data_xform[freq].dot(overlay_wts_dict[key])
    overlay_dict[freq].drop(itd_dxf.col_list, axis=1, inplace=True)
    
for freq in overlay_dict:
    temp_df = dm.merge_data_frames(liq_alts_b.mkt_returns[freq], liq_alts_b.hf_returns[freq][['Managed Futures', 'Manged Futures 15 vol']], True)
    overlay_dict[freq] = dm.merge_data_frames(temp_df,overlay_dict[freq], True)
    if freq == 'Monthly':
        overlay_dict[freq] = dm.merge_data_frames(overlay_dict[freq], liq_alts_p.returns[['1907 Campbell TF', '1907 Systematica TF', 'One River Trend', 'Trend Following']], True)
    for key in overlay_wts_dict:
        overlay_dict[freq][f'MF 15vol+{key}'] =  (overlay_dict[freq]['Manged Futures 15 vol'] + overlay_dict[freq][key])
        if freq == 'Monthly':
            overlay_dict[freq][f'TF+{key}'] =  (overlay_dict[freq]['Trend Following'] + overlay_dict[freq][key])

bmk_dict = {}
for strat in overlay_dict['Monthly']:
    bmk_dict[strat] = 'SG Trend'

ret_dict_overlay = {}
for key in ['Daily', 'Weekly', 'Monthly']:
    ret_dict_overlay[key] = dm.get_period_dict(overlay_dict[key],dm.switch_string_freq(key))
    include_fi = False if key=='Daily' else True
    rp.get_alts_report(f'ITD_Overlay_analysis-{key}',ret_dict_overlay[key],include_fi=include_fi,
                       freq=dm.switch_string_freq(key),include_bmk=True, 
                       df_bmk=liq_alts_b.bmk_returns[key], bmk_dict=bmk_dict)

overlay_dict_2 = copy.deepcopy(overlay_dict)
for key in overlay_dict_2:
    overlay_dict_2[key].drop(list(overlay_wts_dict.keys()), axis=1, inplace=True)

overlay_dict_2['Monthly']=overlay_dict_2['Monthly'][['MSCI ACWI', 'FI Benchmark', 'Commodities (BCOM)', 'U.S. Dollar Index','1907 Campbell TF', '1907 Systematica TF', 'One River Trend', 'Managed Futures', 'Manged Futures 15 vol','Trend Following',
        'MF 15vol+Alt 1', 'MF 15vol+Alt 2','MF 15vol+Alt 3', 'MF 15vol+Alt 4', 'MF 15vol+Alt 5','MF 15vol+Alt 6',
       'MF 15vol+Full', 'MF 15vol+5Y', 'MF 15vol+3Y', 'MF 15vol+1Y',
       'TF+Alt 1','TF+Alt 2','TF+Alt 3','TF+Alt 4','TF+Alt 5','TF+Alt 6',
      'TF+Full','TF+5Y', 'TF+3Y', 'TF+1Y']]   

ret_dict_overlay_2 = {}
for key in ['Daily', 'Weekly', 'Monthly']:
    ret_dict_overlay_2[key] = dm.get_period_dict(overlay_dict_2[key],dm.switch_string_freq(key))
    include_fi = False if key=='Daily' else True
    rp.get_alts_report(f'ITD_Overlay_analysis-{key}-3',ret_dict_overlay_2[key],include_fi=include_fi,
                       freq=dm.switch_string_freq(key),include_bmk=True, 
                       df_bmk=liq_alts_b.bmk_returns[key], bmk_dict=bmk_dict)
    
analytics_dict = {}
for key in ['Daily', 'Weekly', 'Monthly']:
    include_fi = False if freq=='Daily' else True
    analytics_dict[key]= summary.get_alts_data(overlay_dict_2[key],include_fi=include_fi,freq=dm.switch_string_freq(key),include_bmk=True, 
    df_bmk=liq_alts_b.bmk_returns[key], bmk_dict=bmk_dict)['ret_stat_df']
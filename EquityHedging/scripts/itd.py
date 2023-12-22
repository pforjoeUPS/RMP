# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 11:22:48 2023

@author: NVG9HXP
"""
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.datamanager import data_xformer as dxf
from EquityHedging.analytics import drawdowns as dd
from EquityHedging.analytics import summary
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler1()

itd_bbg = dxf.transform_bbg_data(dm.DATA_FP+'liq_alts\\itd.xlsx',freq='1D',sheet_name='data')
sg_itd = dm.get_new_strat_data('liq_alts\\custom_itd_data.xlsx',sheet_name='sg',freq='1D', index_data=True)
jpm_itd = dm.get_new_strat_data('liq_alts\\custom_itd_data.xlsx',sheet_name='jpm',freq='1D', index_data=True)
ms = dm.pd.read_excel(dm.DATA_FP+'liq_alts\\ms_itd_2.xlsx', sheet_name=['SPX','NDX', 'SX5E', 'Gold', 'NKY', 'Crude Oil'], usecols=[0,2], index_col=0)    
ms_dict = {}

for key in ms:
    ms_dict[key] = dm.get_data_dict(ms[key])
    
ms_itd_dict = ms_dict['SPX']

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['NDX'],drop_na=True)

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['SX5E'],drop_na=True)

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['Gold'],drop_na=True)

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['NKY'],drop_na=True)

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['Crude Oil'],drop_na=True)

for key in ms_itd_dict:
    ms_itd_dict[key].columns = ['MS_ITD US_EQ 1.5','MS_ITD US_EQ_NASDAQ 1.5','MS_ITD EU_EQ 1.5','MS_ITD CM_GC 1.5','MS_ITD US_EQ_JP 1.5','MS_ITD CM_WTI 1.5']
    
itd_w = dm.merge_data_frames(itd_w, ms_itd_dict['Weekly'])    
    
sgites3 = dm.pd.read_excel(dm.DATA_FP+'liq_alts\\sgites3.xlsx', sheet_name=0, usecols=[0,1], index_col=0)    

sgites3.columns = ['SG_ITD US_EQ 3']

sgites3_dict = dm.get_data_dict(sgites3)


itd_w = dm.merge_data_frames(itd_w, sgites3_dict['Weekly'])    


itd_bbg.columns = ['UBS_ITD US_EQ','UBS_ITD US_EQ_NASDAQ','UBS_ITD CM_NG_SHORT','UBS_ITD CM_BRENT',
                   'UBS_ITD CM_BRENT_SHORT','UBS_ITD CM_WTI','UBS_ITD CM_WTI_SHORT','UBS_ITD CM_NG',
                   'UBS_ITD CM_NG_MR','SG_ITD US_EQ','SG_ITD US_EQ_SHORT','SG_ITD US_EQ_NASDAQ',
                   'SG_ITD VIX','SG_ITD CM_NG','SG_ITD CM_BRENT','SG_ITD CM_WTI',
                   'JPM_ITD US_EQ','JPM_ITD US_EQ_VIX_signal','JPM_ITD US_EQ_Gamma_signal',
                   'JPM_ITD US_EQ_ODTE','JPM_ITD US_EQ_Var_Spread','JPM_ITD VIX','JPM_ITD VIX_vol_regime',
                   'JPM_ITD US_EQ_NASDAQ','JPM_ITD JP_EQ','JPM_ITD JP_EQ II','BNP_ITD US_EQ_NASDAQ_Dynamic',
                   'BNP_ITD US_EQ_Dynamic','BNP_ITD CM_NG','BNP_ITD CM_WTI','BNP_ITD US_EQ I','BNP_ITD US_EQ II',
                   'BNP_ITD US_EQ_NASDAQ','BX_ITD US_EQ','BX_ITD US_EQ_NASDAQ','BX_ITD US_EQ_TH','BX_ITD US_EQ_NASDAQ_TH',
                   'BX_ITD US_EQ_TH_EE','BX_ITD US_EQ_NASDAQ_TH_EE','BX_ITD AP_EQ','BX_ITD AP_EQ_TH','BX_ITD JP_EQ',
                   'BX_ITD HK_EQ','BX_ITD HKCN_EQ','BX_ITD CN_EQ','BX_ITD AU_EQ','BX_ITD EQ','MQ_ITD CM','MQ_ITD US_EQ',
                   'MQ_ITD FX','MQ_ITD CM_WTI','MQ_ITD CM_CO','MQ_ITD CM_XB','MQ_ITD CM_HO','MQ_ITD CM_LA','MQ_ITD CM_LX',
                   'MQ_ITD CM_LP','MQ_ITD CM_NG','MQ_ITD CM_GC','MQ_ITD US_EQ_EE','MQ_ITD US_EQ_VIX_Filter',
                   'MQ_ITD US_EQ_NASDAQ','MS_ITD US_EQ','MS_ITD US_EQ_NASDAQ','MS_ITD US_EQ_RUSS2K','MS_ITD EU_EQ',
                   'MS_ITD JP_EQ','MS_ITD CM_WTI','MS_ITD CM_NG','MS_ITD CM_CN','MS_ITD CM_GC','MS_ITD US_EQ 2',
                   'MS_ITD US_EQ_NASDAQ 2','MS_ITD US_EQ_RUSS2K 2','MS_ITD EU_EQ 2','MS_ITD JP_EQ 2','MS_ITD CM_WTI 2',
                   'MS_ITD CM_NG 2','MS_ITD CM_CN 2','MS_ITD CM_GC 2']
itd_dict = dm.get_data_dict(itd_bbg, dropna=True)
sg_itd_dict = dm.get_data_dict(sg_itd,'ret', dropna=True)
jpm_itd_dict = dm.get_data_dict(jpm_itd,'ret', dropna=True)

itd_dict = dm.merge_dicts_list([itd_dict,sg_itd_dict, jpm_itd_dict, ms_itd_dict, sgites3_dict], drop_na=False)

col_list = ['XUBSEHIT Index', 'XUBSNHIT Index', 'XUBSCINS Index', 'XUBSCIBE Index',
               'XUBSCIBS Index', 'XUBSCIWE Index', 'XUBSCIWS Index', 'XUBSCINE Index',
               'XUBSCIEN Index', 'SGITES2 Index', 'SGITESS2 Index', 'SGIDTNQ Index',
               'SGITVXL Index', 'SG_ITD CM_GC', 'SGMDDNGE Index', 'SGMDDCOE Index', 'SGIDTWTI Index',
               'JPM_ITD US_EQ_AGG','JPUSQEM2 Index', 'JPUSQEM4 Index', 'JPUSQEM5 Index', 'JPOSIGHO Index',
               'JPOSIVSU Index', 'JPUSQEV2 Index', 'JPUSQEVR Index', 'JPUSNQIM Index',
               'JPOSJHIT Index', 'JPOSJHT2 Index', 'BNPXDITT Index', 'BNPXDITU Index',
               'BNPXING1 Index', 'BNPXICL1 Index', 'BNPXITU1 Index', 'BNPXITU2 Index',
               'BNPXITT1 Index', 'BXIIIDME Index', 'BXIIIDMN Index', 'BXIIIDE1 Index',
               'BXIIIDN1 Index', 'BXIIIDV1 Index', 'BXIIIVN1 Index', 'BXIIAIDC Index',
               'BXIIAITC Index', 'BXIINIDB Index', 'BXIIHIDB Index', 'BXIIEIDB Index',
               'BXIICIDB Index', 'BXIIOIDB Index', 'BXIIGIDB Index', 'MQCP697E Index',
               'MQIS301M Index', 'MQIS601 Index', 'MQCPM2CL Index', 'MQCPM2CO Index',
               'MQCPM2XB Index', 'MQCPM2HO Index', 'MQCPM2LA Index', 'MQCPM2LX Index',
               'MQCPM2LP Index', 'MQCPM2NG Index', 'MQCPM2GC Index', 'MQIS301R Index',
               'MQIS303M Index', 'MQIS305M Index', 'MSISL1ES Index', 'MSISL1NQ Index',
               'MSISL1RT Index', 'MSISL1VG Index', 'MSISL1NK Index', 'MSCBL1CL Index',
               'MSCBL1CN Index', 'MSCBL1GC Index', 'MSCBL1UX Index', 'MSISL3ES Index',
               'MSISL3NQ Index', 'MSISL3RT Index', 'MSISL3VG Index', 'MSISL3NK Index',
               'MSCBL3CL Index', 'MSCBL3NG Index', 'MSCBL3GC Index', 'MSCBL3UX Index']

col_list = ['BNPXDITU Index','BNPXDITT Index','SGIDTNQ Index','MSISL3NQ Index','BXIIIVN1 Index',
               'BXIIAITC Index','BXIIHIDB Index','BXIINIDB Index','XUBSCINS Index','BNPXING1 Index',
               'BNPXICL1 Index', 'SG_ITD CM_GC', 'MSCBL3GC Index','MSISL3VG Index','MSCBL3CL Index']
               
nisa_dict={
    'Alternative 1B':[0,0,0,0,0.22,
                      0,0.4,0,0.22,0.18,
                      0,0.5,0.5,0.5,0.4],
    'Alternative 2B':[0,0,0,0,0.18,
                      0,0.42,0,0.22,0.18,
                      0,0.5,0.5,0.5,0.38],
    'Alternative 3B':[0,0,0,0,0.5,
                      0,0.44,0,0.36,0.22,
                      0,0.5,0.5,0.32,0.35],
    'Alternative 3C':[0.45,0.24,0.08,0.16,0.26,
                      0.38,0.04,0.02,0.12,0.08,
                      0.02,0.5,0.5,0,0.17]}

for key in itd_dict:
    itd_dict[key] = itd_dict[key][col_list]
    

rp.get_returns_report('itd_returns', itd_dict, True)

itd_m = dm.pd.read_excel(dm.RETURNS_DATA_FP+'itd_returns.xlsx', sheet_name = 'Monthly', index_col=0)
itd_w = dm.pd.read_excel(dm.RETURNS_DATA_FP+'itd_returns.xlsx', sheet_name = 'Weekly', index_col=0)

itd_US_EQ = ['UBS_ITD US_EQ', 'SG_ITD US_EQ', 
             'JPM_ITD US_EQ_AGG', 'JPM_ITD US_EQ','JPM_ITD US_EQ_VIX_signal', 
             'JPM_ITD US_EQ_Gamma_signal','JPM_ITD US_EQ_ODTE', 'JPM_ITD US_EQ_Var_Spread',
             'BNP_ITD US_EQ_Dynamic','BNP_ITD US_EQ I', 'BNP_ITD US_EQ II',
             'BX_ITD US_EQ', 'BX_ITD US_EQ_TH','BX_ITD US_EQ_TH_EE',
             'MQ_ITD US_EQ', 'MQ_ITD US_EQ_EE', 'MQ_ITD US_EQ_VIX_Filter',
             'MS_ITD US_EQ', 'MS_ITD US_EQ_RUSS2K','MS_ITD US_EQ 2','MS_ITD US_EQ_RUSS2K 2','MS_ITD US_EQ 1.5']

itd_US_EQ_NASDAQ = ['UBS_ITD US_EQ_NASDAQ', 'SG_ITD US_EQ_NASDAQ',
                    'JPM_ITD US_EQ_NASDAQ','BNP_ITD US_EQ_NASDAQ_Dynamic','BNP_ITD US_EQ_NASDAQ',
                    'BX_ITD US_EQ_NASDAQ','BX_ITD US_EQ_NASDAQ_TH','BX_ITD US_EQ_NASDAQ_TH_EE',
                    'MQ_ITD US_EQ_NASDAQ','MS_ITD US_EQ_NASDAQ','MS_ITD US_EQ_NASDAQ 2','MS_ITD US_EQ_NASDAQ 1.5']


itd_AP_EQ = ['JPM_ITD JP_EQ','JPM_ITD JP_EQ II',
            'BX_ITD AP_EQ','BX_ITD AP_EQ_TH','BX_ITD JP_EQ', 'BX_ITD HK_EQ', 'BX_ITD HKCN_EQ', 'BX_ITD CN_EQ','BX_ITD AU_EQ',
            'MS_ITD JP_EQ','MS_ITD JP_EQ 2','MS_ITD US_EQ_JP 1.5']

itd_CM_WTI = ['UBS_ITD CM_WTI','UBS_ITD CM_WTI_SHORT','SG_ITD CM_WTI','BNP_ITD CM_WTI',
              'MQ_ITD CM_WTI','MS_ITD CM_WTI','MS_ITD CM_WTI 2','MS_ITD CM_WTI 1.5']

itd_EU_EQ = ['BX_ITD EQ','MS_ITD EU_EQ', 'MS_ITD EU_EQ 2','MS_ITD EU_EQ 1.5']

itd_CM_NG = ['UBS_ITD CM_NG_SHORT','UBS_ITD CM_NG', 'UBS_ITD CM_NG_MR',
            'SG_ITD CM_NG','BNP_ITD CM_NG','MQ_ITD CM_NG','MS_ITD CM_NG 2',]
itd_CM_GC = ['SG_ITD CM_GC', 'MQ_ITD CM_GC','MS_ITD CM_GC', 'MS_ITD CM_GC 2','MS_ITD CM_GC 1.5']

itd_CM = ['UBS_ITD CM_BRENT', 'UBS_ITD CM_BRENT_SHORT','SG_ITD CM_GC', 'SG_ITD CM_BRENT',
          'MQ_ITD CM', 'MQ_ITD CM_CO', 'MQ_ITD CM_XB', 'MQ_ITD CM_HO','MQ_ITD CM_LA',
          'MQ_ITD CM_LX', 'MQ_ITD CM_LP','MQ_ITD CM_GC','MS_ITD CM_CN','MS_ITD CM_GC', 'MS_ITD CM_GC 2','MS_ITD CM_GC 1.5']

itd_VIX_FX = ['SG_ITD VIX','JPM_ITD US_EQ_ODTE','JPM_ITD VIX','JPM_ITD VIX_vol_regime','MS_ITD US_EQ_VIX','MS_ITD US_EQ_VIX 2', 'MQ_ITD FX']

strat_list = ['itd_US_EQ', 'itd_US_EQ_NASDAQ', 'itd_AP_EQ', 'itd_EU_EQ', 'itd_CM_WTI', 'itd_CM_NG', 'itd_CM_GC']

df_returns = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Trend Following']['returns'], False)
df_returns.drop(['Trend Following'], axis=1, inplace=True)
df_returns = dm.merge_data_frames(df_returns,itd_m, True)
df_returns = dm.merge_data_frames(df_returns,liq_alts_b.returns['Monthly'][['SG Trend']], True)
df_returns = dm.merge_data_frames(df_returns, liq_alts_p.sub_ports['Total Liquid Alts']['returns'], True)
ret_dict = dm.get_period_dict(df_returns)
rp.get_alts_report('itd_m-fit',ret_dict)

ups_list = ['JPM_ITD US_EQ_ODTE','BNP_ITD US_EQ_Dynamic','BNP_ITD US_EQ_NASDAQ_Dynamic','BX_ITD US_EQ_NASDAQ_TH_EE',
            'BX_ITD AP_EQ_TH','MS_ITD EU_EQ 2','UBS_ITD CM_WTI_SHORT','MS_ITD CM_WTI 2',
            'UBS_ITD CM_NG_SHORT','SG_ITD CM_GC', 'MS_ITD CM_GC 2']

ups_list_1 = ['JPM_ITD US_EQ_ODTE','BNP_ITD SPX','BNP_ITD NDX','BX_ITD NDX',
            'BX_ITD APAC','MS_ITD SX5E 3','UBS_ITD WTI_SHORT','MS_ITD WTI 1.5',
            'UBS_ITD NG_SHORT','SG_ITD Gold','MS_ITD Gold 3']

ups_itd = itd_w[ups_list]
ups_itd.columns = ups_list_1
df_returns_w = dm.merge_data_frames(liq_alts_b.mkt_returns['Weekly'], liq_alts_b.bmk_returns['Weekly'][['SG Trend']], True)

df_ret_w = dm.merge_data_frames(df_returns_w,ups_itd, False)
ret_dict_w = dm.get_period_dict(df_ret_w, '1W')
rp.get_alts_report('ups_itd-aug2023',ret_dict_w, include_bmk=True, freq='1W')

for strat in strat_list:
    df_ret_w = dm.merge_data_frames(df_returns_w,itd_w[eval(strat)], True)
    
    ret_dict_w = dm.get_period_dict(df_ret_w, '1W')
    rp.get_alts_report('{}-w-fit-8_23'.format(strat),ret_dict_w, include_fi=False,include_bmk=True, freq='1W')

for strat in strat_list:
    df_ret_w = dm.merge_data_frames(df_returns_w,itd_w[eval(strat)], True)
    
    df_ret = df_ret_w.copy()
    report_name = 'ups-itd_dd-stats'
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
    
    
    
for strat in strat_list:
    df_ret_m = df_returns[eval(strat)].copy()
    ret_dict_m = dm.get_period_dict(df_ret_m)
    rp.get_alts_report('{}-m-fit'.format(strat),ret_dict_m)
    
    df_ret_w = df_returns_w[eval(strat)].copy()
    ret_dict_w = dm.get_period_dict(df_ret_w)
    rp.get_alts_report('{}-w-fit'.format(strat),ret_dict_w)
    
report_name = 'itd_overlay_dd'
dd_dict = {}
file_path = rp.get_filepath_path(report_name)
writer = dm.pd.ExcelWriter(file_path, engine='xlsxwriter')

for idx in df_returns_w.columns:
    print(idx)
    dd_df = dd.get_co_drawdowns(df_returns_w[[idx]], itd_w, num_worst=10)
    dd_df.dropna(inplace=True)
    dd_df.rename(columns={'peak':'Start Date', 'trough':'End Date'}, inplace=True)
    rp.sheets.set_hist_sheet(writer, dd_df, idx)
writer.save()    
    
for strat in strat_list:    
    report_name = '{}_dd'.format(strat)
    file_path = rp.get_filepath_path(report_name)
    writer = dm.pd.ExcelWriter(file_path, engine='xlsxwriter')
    
    for idx in df_returns_w.columns:
        print(idx)
        if idx == 'SG Trend':
            dd_df = dd.get_co_drawdowns(df_returns_w[[idx]], itd_w[eval(strat)], num_worst=10)
        else:
            temp_df = dm.merge_data_frames(df_returns_w[['SG Trend']], itd_w[eval(strat)], True)
            dd_df = dd.get_co_drawdowns(df_returns_w[[idx]], temp_df, num_worst=10)
        dd_df.dropna(inplace=True)
        dd_df.rename(columns={'peak':'Start Date', 'trough':'End Date'}, inplace=True)
        rp.sheets.set_hist_sheet(writer, dd_df, idx)
    writer.save()    
    
    
itd_US_EQ = ['UBS_ITD US_EQ','SG_ITD US_EQ','JPM_ITD US_EQ_ODTE',
             'BNP_ITD US_EQ_Dynamic','BX_ITD US_EQ_TH_EE',
             'MS_ITD US_EQ 2','MS_ITD US_EQ_RUSS2K 2']

itd_US_EQ_NASDAQ = ['UBS_ITD US_EQ_NASDAQ', 'SG_ITD US_EQ_NASDAQ',
                    'BNP_ITD US_EQ_NASDAQ_Dynamic','BX_ITD US_EQ_NASDAQ_TH_EE',
                    'MS_ITD US_EQ_NASDAQ 2']


itd_AP_EQ = ['BX_ITD AP_EQ_TH']

itd_CM_WTI = ['UBS_ITD CM_WTI_SHORT','SG_ITD CM_WTI','BNP_ITD CM_WTI',
              'MQ_ITD CM_WTI','MS_ITD CM_WTI 2','MS_ITD CM_WTI 1.5']

itd_EU_EQ = ['MS_ITD EU_EQ 2']

itd_CM_NG = ['UBS_ITD CM_NG_SHORT']

itd_CM_GC = ['SG_ITD CM_GC','MS_ITD CM_GC 2','MS_ITD CM_GC 1.5']

# itd_VIX_FX = ['SG_ITD VIX','JPM_ITD VIX','JPM_ITD VIX_vol_regime', 'MQ_ITD FX']

strat_list = ['itd_US_EQ', 'itd_US_EQ_NASDAQ', 'itd_AP_EQ', 'itd_EU_EQ', 'itd_CM_WTI', 'itd_CM_NG', 'itd_CM_GC']


for strat in strat_list:
    df_ret_w = dm.merge_data_frames(df_ret_w,itd_w[eval(strat)], True)
df_ret_w.columns = ['M1WD','FI Benchmark','SG Trend','UBS_ITD SPX','JPM_ITD US_EQ_ODTE','BNP_ITD SPX',
                    'BX_ITD SPX','MS_ITD SPX 3','MS_ITD RTY 3','UBS_ITD NDX','SG_ITD NDX','BNP_ITD NDX',
                    'BX_ITD NDX','MS_ITD NDX 3','BX_ITD APAC','MS_ITD SX5E 3','UBS_ITD WTI_SHORT','SG_ITD WTI',
                    'BNP_ITD WTI','MQ_ITD WTI','MS_ITD WTI 3','MS_ITD WTI 2','UBS_ITD NG_SHORT','UBS_ITD BRENT_SHORT',
                    'SG_ITD Gold','MQ_ITD CM','MS_ITD Corn 3','MS_ITD Gold 3','MS_ITD Gold 2']
ret_dict_w = dm.get_period_dict(df_ret_w, '1W')
rp.get_alts_report('itd_ups-w-fit-2',ret_dict_w, include_bmk=True, freq='1W')
    
strat_list = ['itd_US_EQ', 'itd_US_EQ_NASDAQ', 'itd_AP_EQ', 'itd_EU_EQ', 'itd_CM_WTI', 'itd_CM_NG', 'itd_CM']
    
    
    
    
sg_itd = dm.get_new_strat_data('liq_alts\\custom_itd_data.xlsx',sheet_name='sg',freq='1D', index_data=True)
ms = dm.pd.read_excel(dm.DATA_FP+'liq_alts\\ms_itd_2.xlsx', sheet_name=['SPX','NDX', 'SX5E', 'Gold', 'NKY', 'Crude Oil'], usecols=[0,2], index_col=0)    
ms_dict = {}

for key in ms:
    ms_dict[key] = dm.get_data_dict(ms[key])
    
ms_itd_dict = ms_dict['SPX']

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['NDX'],drop_na=True)

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['SX5E'],drop_na=True)

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['Gold'],drop_na=True)

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['NKY'],drop_na=True)

ms_itd_dict = dm.merge_dicts(ms_itd_dict,ms_dict['Crude Oil'],drop_na=True)

for key in ms_itd_dict:
    ms_itd_dict[key].columns = ['MS_ITD US_EQ 1.5','MS_ITD US_EQ_NASDAQ 1.5','MS_ITD EU_EQ 1.5','MS_ITD CM_GC 1.5','MS_ITD US_EQ_JP 1.5','MS_ITD CM_WTI 1.5']
    
itd_w = dm.merge_data_frames(itd_w, ms_itd_dict['Weekly'])    
    
sgites3 = dm.pd.read_excel(dm.DATA_FP+'liq_alts\\sgites3.xlsx', sheet_name=0, usecols=[0,1], index_col=0)    

sgites3.columns = ['SG_ITD US_EQ 3']

sgites3_dict = dm.get_data_dict(sgites3)

itd_w = dm.merge_data_frames(itd_w, sgites3_dict['Weekly'])    

# -------------------------------------------------------------------------------------------------------------------------

import pandas as pd
from EquityHedging.reporting.excel import new_reports as rp

ups_tf = ['2018-08', '2021-02', '2023-08']
freq='1M'

trend_exp_dict = {}
for dt in ups_tf:
    trend_exp_dict[dt] = pd.read_excel(dm.DATA_FP+'liq_alts\\Report_UPS Trend_Reg_{}.xlsx'.format(dt),
                                       sheet_name='Default', skiprows=[0,1])
    trend_exp_dict[dt].columns = ['Dates', 'Asset', 'Region', '10 Yr Equiv Gross Notional', '10 Yr Equiv Gross % Notional']
    
trend_exp = pd.DataFrame()
for key in trend_exp_dict:
    trend_exp = pd.concat([trend_exp,trend_exp_dict[key]],axis=0)    

asset_list = [x for x in list(trend_exp.Asset.unique()) if x == x]
    
exposure_dict = {}
for asset in asset_list:
    asset_df = trend_exp.loc[trend_exp['Asset'] == asset]
    exposure_dict[asset] = asset_df.pivot_table(values='10 Yr Equiv Gross Notional', index='Dates', columns='Region')
    exposure_dict[asset] = dm.resample_data(exposure_dict[asset], freq)
    
rp.getMVReport('trend_exposure_report-region', exposure_dict)

exposure_dict = {}
for asset in asset_list:
    asset_df = trend_exp.loc[trend_exp['Asset'] == asset]
    exposure_dict[asset] = asset_df.pivot_table(values='10 Yr Equiv Gross % Notional', index='Dates', columns='Region')
    exposure_dict[asset] = dm.resample_data(exposure_dict[asset], freq)
    
rp.getReturnsReport('trend_exposure_report-region-pct', exposure_dict)

# -------------------------------------------------------------------------------------------------------------------------
ups_tf = ['2018-08', '2021-02', '2023-08']
freq='1M'

trend_exp_dict = {}
for dt in ups_tf:
    trend_exp_dict[dt] = pd.read_excel(dm.DATA_FP+'liq_alts\\Report_UPS Trend_Ind_{}.xlsx'.format(dt), 
                                       sheet_name='Default', skiprows=[0,1])
    trend_exp_dict[dt].columns = ['Dates', 'Asset', 'Industry','Industry Subgroup', '10 Yr Equiv Gross Notional', '10 Yr Equiv Gross % Notional']
    
trend_exp = pd.DataFrame()
for key in trend_exp_dict:
    trend_exp = pd.concat([trend_exp,trend_exp_dict[key]],axis=0)    

asset_list = [x for x in list(trend_exp.Asset.unique()) if x == x]
    
exposure_dict = {}
for asset in asset_list:
    asset_df = trend_exp.loc[trend_exp['Asset'] == asset]
    exposure_dict[asset] = asset_df.pivot_table(values='10 Yr Equiv Gross Notional', index='Dates', columns='Industry')
    exposure_dict[asset] = dm.resample_data(exposure_dict[asset], freq)
    
rp.getMVReport('trend_exposure_report-ind', exposure_dict)

exposure_dict = {}
for asset in asset_list:
    asset_df = trend_exp.loc[trend_exp['Asset'] == asset]
    exposure_dict[asset] = asset_df.pivot_table(values='10 Yr Equiv Gross % Notional', index='Dates', columns='Industry')
    exposure_dict[asset] = dm.resample_data(exposure_dict[asset], freq)
    
rp.getReturnsReport('trend_exposure_report-ind-pct', exposure_dict)


from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.datamanager import data_xformer as dxf
from EquityHedging.analytics import drawdowns as dd
from EquityHedging.analytics import summary
itd_bbg = dxf.transform_bbg_data(dm.DATA_FP+'liq_alts\\itd.xlsx',freq='1D',sheet_name='data')
mkt_dh = dh.mktHandler(equity_bmk='SPTR', include_fi=False)
itd_eq = itd_bbg[['XUBSEHIT Index','SGITES2 Index','JPUSQEM2 Index','BNPXDITU Index','BNPXITU1 Index','BNPXITU2 Index','BXIIIDME Index','BXIIIDE1 Index','BXIIIDV1 Index','MQIS301M Index','MQIS301R Index','MSISL1ES Index','MSISL3ES Index']]
ms_eq = dm.pd.read_excel(dm.DATA_FP+'liq_alts\\ms_itd_2.xlsx', sheet_name='SPX', usecols=[0,2], index_col=0)    
ms_eq_itd_dict = dm.get_data_dict(ms_eq)
sgites3 = dm.pd.read_excel(dm.DATA_FP+'liq_alts\\sgites3.xlsx', sheet_name=0, usecols=[0,1], index_col=0)
sg_eq_itd = dm.get_data_dict(sgites3)
itd_eq_dict = dm.get_data_dict(itd_eq, dropna=False)
itd_eq_dict = dm.merge_dicts_list([mkt_dh.mkt_returns, itd_eq_dict])
rp.generate_hs_report('itd_eq_selloffs-2', itd_eq_dict)
itd_eq_d =dm.format_data(itd_eq, '1D',False)
itd_eq_d =dm.merge_data_frames(itd_eq_d, ms_eq_itd_dict['Daily'][['MSISL2ES Index']], drop_na=False, fillzeros=True)
itd_eq_d =dm.merge_data_frames(itd_eq_d, sg_eq_itd['Daily'][['SGITES3 Index']], drop_na=False, fillzeros=True)

report_name = 'eq_itd_dd-stats'
dd_df=dd.get_co_drawdowns(mkt_dh.mkt_returns['Daily'], itd_eq_d, num_worst=30)
file_path = rp.get_filepath_path(report_name)
writer = dm.pd.ExcelWriter(file_path, engine='xlsxwriter')
rp.sheets.set_hist_sheet(writer, dd_df, 'SPTR DD')
rp.sheets.set_hist_return_sheet(writer, itd_eq_dict['Daily'])



itd_eq_d_roll = itd_eq_dict['Daily'].copy()
window = 5
for col in itd_eq_d_roll:
    itd_eq_d_roll[col] = itd_eq_dict['Daily'][col].rolling(window=window).apply(rs.get_cum_ret)
    
itd_eq_d_roll = itd_eq_d_roll.iloc[(window-1):,]
itd_eq_d_roll = itd_eq_d_roll.sort_values(by=['SPTR'])
itd_eq_d_roll = itd_eq_d_roll[:-3968]
rp.sheets.set_hist_return_sheet(writer, itd_eq_d_roll, sheet_name='5-day SPTR DD')
writer.save()


include_fi=True
include_bmk=False
if include_fi and include_bmk:
    print('skip 2')
elif include_fi or include_bmk:
    print('skip 1')
elif include_bmk:
    print('skip 1--BMK')
    
    
from EquityHedging.datamanager import data_xformer_new as dxf
from EquityHedging.datamanager import data_updater_new as du
itd_dxf = dxf.bbgDataXformer(du.UPDATE_DATA_FP+'itd_overlay_data.xlsx',freq='1D',
                             col_list=['SPX_ODTE', 'SPX', 'NDX_BNP', 'NDX_BX', 'APAC', 'SX5E',
                                       'WTI_SHORT', 'WTI', 'NG_SHORT', 'GC_SG', 'GC_MS']) 
df_returns_w = dm.merge_data_frames(liq_alts_b.mkt_returns['Weekly'], liq_alts_b.bmk_returns['Weekly'][['SG Trend']], True)
df_ret_w = dm.merge_data_frames(df_returns_w,itd_dxf.data_xform['Weekly'], True)
ret_dict_w = dm.get_period_dict(df_ret_w, '1W')
rp.get_alts_report('ups_itd-sep2023',ret_dict_w, include_bmk=False, freq='1W')

overlay_wts_dict = {'Alt 1': [.05, .07, .04, .06, .03, .12, .04, .11, .04, .05, .39],
                    'Alt 2': [.10, .13, .08, .11, .06, .23, .02, .08, .10, .01, .09],
                    'Alt 3': [.08, .10, .06, .09, .04, .18, .04, .11, .10, .02, .18],
                    'Alt 4': [.10, .10, .06, .09, .05, .15, .05, .10, .10, .05, .15],
                    'Alt 5': [.10, .10, .09, .09, .06, .10, .07, .07, .10, .05, .17],
                    'Full':  [.08, .06, .05, .09, .08, .20, .02, .03, .04, .08, .26],
                    '5Y':    [.09, .06, .05, .09, .08, .20, .02, .02, .04, .08, .26],
                    '3Y':    [.06, .07, .06, .08, .06, .17, .04, .03, .02, .06, .35],
                    '1Y':    [.06, .08, .05, .09, .05, .14, .04, .13, .01, .04, .29]
                    }
itd_strats = df_ret_w.iloc[:,3:].copy()
for key in overlay_wts_dict:
    df_ret_w[key] = itd_strats.dot(overlay_wts_dict[key])
    
ret_overlay_dict_w = dm.get_period_dict(df_ret_w, '1W')
rp.get_alts_report('ups_itd-overlay-sep2023-1',ret_overlay_dict_w, include_bmk=False, freq='1W')


report_name = 'itd_overlay_dd'
dd_dict = {}
file_path = rp.get_filepath_path(report_name)
writer = dm.pd.ExcelWriter(file_path, engine='xlsxwriter')
dd_matrix = dd.get_dd_matrix(df_ret_w)
rp.sheets.set_hist_sheet(writer, dd_matrix, 'DD Matrix')

for idx in df_ret_w.columns:
    print(idx)
    dd_df = dd.get_co_drawdowns(df_ret_w[[idx]], df_ret_w, num_worst=10)
    dd_df.dropna(inplace=True)
    dd_df.rename(columns={'peak':'Start Date', 'trough':'End Date'}, inplace=True)
    rp.sheets.set_hist_sheet(writer, dd_df, idx)
writer.save()    
  
['SPTR', 'SX5T', 'MSCI ACWI', 'MSCI ACWI IMI', 'Long Corp', 'STRIPS',
       'HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend', 'DM Equity',
       'EM Equity', 'Gov Bonds', 'Agg Bonds', 'EM Bonds', 'High Yield',
       'Commodities (BCOM)', 'Commodities (GSCI)', 'Equity Volatility',
       'EM FX', 'FX Carry', 'U.S. Dollar Index']




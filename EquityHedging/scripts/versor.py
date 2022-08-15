# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 20:38:07 2022

@author: NVG9HXP
"""

import pandas as pd
import numpy as np
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp

ups_df = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\Historical Returns_equity.xls', sheet_name='Historical Returns')
ups_df.columns = ['Name', 'Account Id', 'Return Type', 'Date',
       'Market Value', 'Return']
ups_df = ups_df.pivot_table(values='Return', index='Date', columns='Name')
ups_df = ups_df[:-1]
ups_df = ups_df[['1907 ARP EM', '1907 ARP TF', '1907 CFM ISE Risk Premia',
       '1907 Campbell TF', '1907 III CV', '1907 III Class A',
       '1907 Kepos RP', '1907 Penso Class A',
       '1907 Systematica TF', 'ABC Reversion',
       'Acadian Commodity AR', 'Alt Risk Premia',
       'BW All Weather',
       'Black Pearl RP',
       'Blueshift', 'Bridgewater Alpha', 'DE Shaw Oculus Fund',
       'Duality',
       'Element Capital', 'Elliott', 'Global Macro',
       'One River Trend','T INTL EQ W/O DERIVATIVES', 'Total Dom Eq w/o Derivatives',
       'Total EQ w/o Derivatives', 'Total Global Equity', 'Total Liquid Alts',
       'Trend Following']]
ups_mv = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\Historical Returns_equity.xls', sheet_name='Historical Returns')
ups_mv.columns = ['Name', 'Account Id', 'Return Type', 'Date',
       'Market Value', 'Return']
ups_mv = ups_mv.pivot_table(values='Market Value', index='Date', columns='Name')
ups_mv = ups_mv[:-1]
ups_mv = ups_mv[['1907 ARP EM', '1907 ARP TF', '1907 CFM ISE Risk Premia',
       '1907 Campbell TF', '1907 III CV', '1907 III Class A',
       '1907 Kepos RP', '1907 Penso Class A',
       '1907 Systematica TF', 'ABC Reversion',
       'Acadian Commodity AR', 'Alt Risk Premia',
       'BW All Weather',
       'Black Pearl RP',
       'Blueshift', 'Bridgewater Alpha', 'DE Shaw Oculus Fund',
       'Duality',
       'Element Capital', 'Elliott', 'Global Macro',
       'One River Trend','T INTL EQ W/O DERIVATIVES', 'Total Dom Eq w/o Derivatives',
       'Total EQ w/o Derivatives', 'Total Global Equity', 'Total Liquid Alts',
       'Trend Following']]
sub_ports_def = {'Abs Ret':['1907 ARP EM',
                            # '1907 CFM ISE Risk Premia',
                            '1907 III CV', '1907 III Class A','1907 Kepos RP',
                            'ABC Reversion',
                            # 'Acadian Commodity AR','Black Pearl RP',
                            'Blueshift','Duality'],
                'Global Macro':['1907 Penso Class A','Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                'Element Capital', 'Elliott'],
                'Trend Following':['1907 ARP TF','1907 Campbell TF',
                                    '1907 Systematica TF','One River Trend'],
                'Equity':['T INTL EQ W/O DERIVATIVES', 'Total Dom Eq w/o Derivatives',
                            'Total Global Equity'],
                'Ports':['Total EQ w/o Derivatives', 'Total Liquid Alts'],
                'Liquid Alts':['Global Macro', 'Trend Following', 'Alt Risk Premia']
                }
data_dict = {}
ret_dict = {}
mv_dict={}

for subport in sub_ports_def:
    temp_dict = {}
    temp_mv = 0
    for key in sub_ports_def[subport]:
        temp_dict[key] = ups_mv[key][-1]
        temp_mv += temp_dict[key]
    temp_dict[subport] = temp_mv
    mv_dict[subport] = temp_dict

wgts_dict={}

for subport in mv_dict:
    temp_dict = {}
    for key in mv_dict[subport]:
        temp_dict[key] = mv_dict[subport][key]/mv_dict[subport][subport]
    wgts_dict[subport] = temp_dict
 

for subport in sub_ports_def:
    ret_dict[subport] = ups_df[sub_ports_def[subport]].copy()
    
for subport in sub_ports_def:
    ret_dict[subport][subport] = 0
    for key in sub_ports_def[subport]:
        ret_dict[subport][subport] = ret_dict[subport][subport] +wgts_dict[subport][key]*ret_dict[subport][key]


ups_mv.sum()
ups_df \=100
ups_df /=100


versor_em = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\versor_UPS_EM.xlsx', sheet_name='data', index_col=0)
data = ups_df[['Alt Risk Premia','T INTL EQ W/O DERIVATIVES', 'Total Dom Eq w/o Derivatives',
       'Total EQ w/o Derivatives', 'Total Global Equity', 'Total Liquid Alts',
       'Trend Following', 'Global Macro']].copy()
data = dm.merge_data_frames(data, asset_ret[['Total Fixed Income']])
data.columns = ['Alt Risk Premia', 'Intl Equity',
       'Dom Equity', 'Total Equity',
       'Global Equity', 'Total Liquid Alts', 'Trend Following',
       'Total Fixed Income', 'Global Macro']
data = data[[ 'Total Equity',
       'Total Fixed Income', 'Global Equity','Dom Equity', 'Intl Equity', 'Total Liquid Alts','Global Macro', 'Trend Following','Alt Risk Premia']]
data = dm.merge_data_frames(data, versor_em)
rp.generate_strat_report('versor_em', {'Monthly':data},freq_list=['Monthly'], include_fi=True)
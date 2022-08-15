# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 22:11:15 2022

@author: NVG9HXP
"""

import pandas as pd
from EquityHedging.datamanager import data_manager as dm
data_dump = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\Historical Asset Class Returns.xls')
data_dump = data_dump[['Account Name\n', 'Account Id\n', 'Return Type\n', 'As Of Date\n',
                       'Market Value\n', 'Account Monthly Return\n']]
data_dump.columns = ['Name', 'Account Id', 'Return Type', 'Date', 'Market Value', 'Return']
liq_alts_ret = data_dump.pivot_table(values='Return', index='Date', columns='Name')
liq_alts_ret /=100
liq_alts_mv = data_dump.pivot_table(values='Market Value', index='Date', columns='Name')
liq_alts_ret.fillna(0)
liq_alts_ret=liq_alts_ret.fillna(0)
liq_alts_mv=liq_alts_mv.fillna(0)
liq_alts_mv.columns
liq_alts_mv=liq_alts_mv[['1907 ARP EM', '1907 ARP TF', '1907 CFM ISE Risk Premia',
       '1907 Campbell TF', '1907 III CV', '1907 III Class A', '1907 Kepos RP', '1907 Penso Class A', 
       '1907 Systematica TF', 'ABC Reversion', 
       'Acadian Commodity AR', 'Alt Risk Premia', 'BW All Weather','Black Pearl RP', 'Blueshift', 'Bridgewater Alpha', 'DE Shaw Oculus Fund', 'Duality',
       'Element Capital', 'Elliott', 'Glen Point EM RV', 'Global Macro',  'One River Trend', 'Total Liquid Alts', 'Trend Following']]
liq_alts_ret=liq_alts_ret[['1907 ARP EM', '1907 ARP TF', '1907 CFM ISE Risk Premia',
       '1907 Campbell TF', '1907 III CV', '1907 III Class A', '1907 Kepos RP', '1907 Penso Class A', 
       '1907 Systematica TF', 'ABC Reversion', 
       'Acadian Commodity AR', 'Alt Risk Premia', 'BW All Weather','Black Pearl RP', 'Blueshift', 'Bridgewater Alpha', 'DE Shaw Oculus Fund', 'Duality',
       'Element Capital', 'Elliott', 'Glen Point EM RV', 'Global Macro',  'One River Trend', 'Total Liquid Alts', 'Trend Following']]
sp_dict = {'Global Macro':[ '1907 Penso Class A','Bridgewater Alpha', 'DE Shaw Oculus Fund','Element Capital'],
'Absolute Return':['1907 ARP EM', '1907 CFM ISE Risk Premia',
        '1907 III CV', '1907 III Class A', '1907 Kepos RP', 'ABC Reversion', 
       'Acadian Commodity AR', 'BW All Weather','Black Pearl RP', 'Blueshift', 'Duality',
       'Glen Point EM RV', 'Elliott']}
liq_alts_ret_t = liq_alts_ret.transpose()
liq_alts_mv_t = liq_alts_mv.transpose()
report_name = 'dd_052022_1'
file_path = rp.get_report_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
liq_alts_ret.to_excel(writer,sheet_name='returns')
from EquityHedging.reporting.excel import reports as rp
report_name = 'upsgt_data'
file_path = rp.get_report_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_hist_return_sheet(writer, liq_alts_ret,sheet_name='Monthly Returns')
rp.sheets.set_mv_sheet(writer, liq_alts_mv)
writer.save()
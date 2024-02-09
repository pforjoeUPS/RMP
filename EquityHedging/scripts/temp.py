# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 13:58:51 2023

@author: NVG9HXP
"""
import os
os.chdir('..\..')
# import pandas as pd
from EquityHedging.analytics import returns_analytics as ra
# from EquityHedging.analytics import returns_stats_new as rs
# from EquityHedging.analytics import util_new
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager_new as dm
from EquityHedging.datamanager import data_xformer_new as dxf
from EquityHedging.analytics import summary_new

penso = dm.get_new_strat_data('liq_alts\\penso_returns.xlsx')
jsc = dm.get_new_strat_data('liq_alts\\jsc.xlsx')
tmf = dm.get_new_strat_data('liq_alts\\tmf.xlsx')
kaf = dm.get_new_strat_data('liq_alts\\kaf.xlsx')
edl_c = dm.get_new_strat_data('liq_alts\\edl.xlsx')
edl_c.columns = ['EDL GOF']

mkt_dh = dh.MktDataHandler()

liq_alts_dh = dh.LiqAltsPortHandler('MSCI ACWI')
drop_mgr = '1907 Penso Class A'
liq_alts_dh.remove_mgr(drop_mgr)
liq_alts_dh.update_mgr('JSC Vantage', jsc)
liq_alts_dh.update_mgr('Capula TM Fund', tmf)
liq_alts_dh.update_mgr('KAF', kaf)
liq_alts_dh.add_mgr(edl_c, 'Global Macro', 125000000)
returns_df = liq_alts_dh.sub_ports['Global Macro']['bmk_returns'].copy()
period_dict = dm.get_period_dict(returns_df)
bmk_data = liq_alts_dh.bmk_returns.copy()
bmk_key = dxf.copy_data(liq_alts_dh.bmk_key)
bmk_key['EDL GOF'] = 'HFRX Macro/CTA'
mkt_data = liq_alts_dh.mkt_returns.copy()
mkt_key = dxf.copy_data(liq_alts_dh.mkt_key)

la_summ = summary_new.LiquidAltsAnalyticSummary(liq_alts_dh)
liq_alts_ra = ra.LiqAltsReturnsAnalytic(returns_df, include_bmk=True, bmk_df=bmk_data, mkt_df=mkt_data,
                                        bmk_key=bmk_key, mkt_key=mkt_key)

liq_alts_ra_dict = ra.LiquidAltsPeriodAnalytic(period_dict, include_bmk=True, bmk_data=bmk_data, mkt_data=mkt_data,
                                               bmk_key=bmk_key, mkt_key=mkt_key)


# C:\Users\nvg9hxp\Documents\Projects\RMP\EquityHedging\datamanager\data_handler.py:165: SettingWithCopyWarning:
# A value is trying to be set on a copy of a slice from a DataFrame.
# Try using .loc[row_indexer,col_indexer] = value instead
# See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
#   self.bmk_returns[freq_string]['Liquid Alts Bmk'] = self.bmk_returns[freq_string].dot([0.5, 0.3, 0.2])#*returns_df['HFRX Macro/CTA'] + 0.3*returns_df['HFRX Absolute Return'] + 0.2*returns_df['SG Trend']
# C:\Users\nvg9hxp\Documents\Projects\RMP\EquityHedging\datamanager\data_handler.py:165: SettingWithCopyWarning:
# A value is trying to be set on a copy of a slice from a DataFrame.
# Try using .loc[row_indexer,col_indexer] = value instead

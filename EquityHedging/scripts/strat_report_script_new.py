# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 2024

@author: RRQ1FYQ, Powis Forjoe
Refactored strat_report_script.py
"""

from EquityHedging.datamanager import data_xformer_new as dxf
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_lists as dl
from EquityHedging.reporting.excel import new_reports as rp

eq_bmk = 'S&P 500'
strat_drop_list = ['Down Var', 'Vortex', 'VOLA I', 'VOLA II', 'Dynamic VOLA', 'VRR', 'VRR 2', 'VRR Trend',
                   'GW Dispersion', 'Corr Hedge', 'Def Var (Fri)', 'Def Var (Mon)', 'Def Var (Wed)', 'Commodity Basket']
include_fi = False

# create qis data handler
qis_dh = dh.QISDataHandler(file_path=dl.EQ_HEDGE_DATA_FP, eq_bmk=eq_bmk, include_fi=include_fi,
                           strat_drop_list=strat_drop_list)

new_strat = True
if new_strat:
    strategy_list = ['esprso']
    file_path = dl.NEW_STRATS_FP + 'esprso.xlsx'
    sheet_name = 'Sheet1'
    notional_list = [1]
    new_strategy = dxf.get_new_strategy_returns_data(file_path=file_path, sheet_name=sheet_name,
                                                     return_data=False, strategy_list=strategy_list)
    new_strategy_dict = dxf.get_data_dict(new_strategy, index_data=False)

    # add new strategies
    qis_dh.add_strategy(new_strategy_dict, notional_list)

strat_report_name = 'test_strat_report-refactor'
selloffs = True
rp.StratReport(strat_report_name, qis_dh, selloffs).run_report()

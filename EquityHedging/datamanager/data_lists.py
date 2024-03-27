# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 11:52:24 2023

@author: NVG9HXP
"""
import os

# File paths
CWD = os.getcwd()

DATA_FP = CWD + '\\EquityHedging\\data\\'
RETURNS_DATA_FP = DATA_FP + 'returns_data\\'
BMK_DATA_FP = RETURNS_DATA_FP + 'bmk_returns-new.xlsx'
HF_BMK_DATA_FP = RETURNS_DATA_FP + 'hf_bmks-new.xlsx'
UPSGT_DATA_FP = RETURNS_DATA_FP + 'upsgt_returns-new.xlsx'
UPSGT_BMK_DATA_FP = RETURNS_DATA_FP + 'upsgt_bmk_returns-new.xlsx'
EQ_HEDGE_DATA_FP = RETURNS_DATA_FP + 'eq_hedge_returns-new.xlsx'
EQUITY_HEDGING_RETURNS_DATA = RETURNS_DATA_FP + 'eq_hedge_returns.xlsx'
EQUITY_HEDGE_DATA = DATA_FP + 'ups_equity_hedge\\'
LIQ_ALTS_BMK_DATA_FP = RETURNS_DATA_FP+'liq_alts_bmks-new.xlsx'
LIQ_ALTS_PORT_DATA_FP = RETURNS_DATA_FP + 'nexen_liq_alts_data-new.xlsx'
# LIQ_ALTS_PORT_DATA_FP = RETURNS_DATA_FP + 'all_liquid_alts_data.xlsx'
IDT_OVERLAY_DATA_FP = RETURNS_DATA_FP + 'itd_overlay_returns.xlsx'
NEW_STRATS_FP = DATA_FP + 'new_strats\\'

UPDATE_DATA_FP = DATA_FP + 'update_data\\'
NEW_DATA_FP = DATA_FP + 'new_strats\\'
UPDATE_DATA = DATA_FP + 'update_strats\\'

QIS_UNIVERSE = CWD + '\\Cluster Analysis\\data\\'

# Constant Dictionaries
NEXEN_DATA_COL_DICT = {'Account Name\n': 'Name', 'Account Id\n': 'Account Id',
                       'Return Type\n': 'Return Type', 'As Of Date\n': 'Dates',
                       'Market Value\n': 'Market Value', 'Account Monthly Return\n': 'Return'}

NEXEN_BMK_DATA_COL_DICT = {'As Of Date\n': 'Dates', 'Benchmark Name\n': 'Benchmark Name',
                           'Benchmark Monthly Return\n': 'Benchmark Return'}

INNOCAP_RET_DATA_COL_DICT = {'Date': 'Dates', 'Account Name': 'Name', 'MTD Return': 'Return',
                             'Market Value': 'Market Value'}
INNOCAP_EXP_DATA_COL_DICT = {'Date': 'Dates', 'Account Name': 'Name', 'Asset Exposure 2': 'Asset Class',
                             '10 Yr Equiv Net % Notional': '10 Yr Equiv Net % Notional'}



NEW_DATA_COL_LIST = ['SPTR', 'SX5T', 'M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                     'Vortex', 'VOLA I', 'VOLA II', 'Dynamic VOLA', 'Dynamic Put Spread',
                     'GW Dispersion', 'Corr Hedge', 'Def Var (Mon)', 'Def Var (Fri)', 'Def Var (Wed)',
                     'Commodity Basket','Def Var II (Mon)', 'Def Var II (Fri)', 'Def Var II (Wed)','ESPRSO',
                     'Moments','EVolCon','UBS GW Dispersion','UBS Dynamic Put Spread']

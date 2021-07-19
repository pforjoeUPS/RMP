# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 10:19:51 2021

@author: GCZ5CHN
"""

import pandas as pd
import ipywidgets as widgets
import datapane as dp 
import plotly.express as px
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as fmt, plots
from ipywidgets import interact, interact_manual
from EquityHedging.reporting.excel import sheets
import os

equity_bmk = 'M1WD'
bmks = dm.get_equity_hedge_returns(equity_bmk, only_equity=True)

CWD = os.getcwd()
NEWSTRAT_DATA_FP = '\\EquityHedging\\data\\'
NEW_STRAT_DATA = CWD + NEWSTRAT_DATA_FP + 'new_strats'
data=pd.read_excel(io="Credit Suisse_SX5E_Tail_FSFVA_20210528_UPS Pension.xlsx", sheet_name="data",index_col=0)

data_dict=dm.get_data_dict(data,'index')
ret_strats=ret_strats=dm.merge_dicts(bmks, data_dict)

corr_freq_list = ['Weekly', 'Monthly']
corr_dict = summary.get_corr_data(ret_strats)
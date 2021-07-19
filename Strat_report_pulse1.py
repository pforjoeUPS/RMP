# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 14:54:01 2021

@author: GCZ5CHN
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 14:54:27 2021

@author: Zach Wells
"""
# 1. Import the bmks sheet from the "intl_hedge_bmks.xlsx" file into a dataframe called bmks

import pandas as pd
from EquityHedging.datamanager import data_manager as dm

# 2. Remove all the columns from the bmks dataframe except for 'SPX Index'
bmks=pd.read_excel("intl_hedge_bmks.xlsx",sheet_name="bmks", index_col=0)
bmks.columns
bmks = bmks[['SPX Index']]
bmks.columns

# 3. Import the Credit Suisse stratgies from the "Credit Suisse_SX5E_Tail_FSFVA_20210528_UPS Pension.xlsx" file into a dataframe called cs_data:
pulse = pd.read_excel('Pulse US at Various Maturities.xlsx',sheet_name = 'Sheet1', index_col=0)

# 4. Merge the bmks and cs_data dataframes with the merge_data_frames function from data_manager (dm). Call this new dataframe ret_strats.
ret_strats = dm.merge_data_frames(bmks, pulse)

# 5. Create a dictionary from ret_strats called ret_strats_dict using the get_data_dict function from dm
ret_strats_dict = dm.get_data_dict(ret_strats,"index")

# 6. Generate the excel strat report ('strat_report_2') using the generate_strat_report function from reports (rp)
from EquityHedging.reporting.excel import reports as rp

rp.generate_strat_report("strat_report_pulse1", ret_strats_dict,selloffs=True)
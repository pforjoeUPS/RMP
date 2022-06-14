# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 15:18:43 2022

@author: Sam Park
"""

#Python Exercise 1
# 1
import pandas as pd
bmks_df = pd.read_excel('C:\\Users\LGQ0NLN\Documents\GitHub\RMP\Exercises\exercise_1\data_for_exercise_1.xlsx',sheet_name='bmks',index_col=0)
strats_df = pd.read_excel('C:\\Users\LGQ0NLN\Documents\GitHub\RMP\Exercises\exercise_1\data_for_exercise_1.xlsx',sheet_name='strats',index_col=0)

# 2
from EquityHedging.datamanager import data_manager as dm
bmks_d = dm.format_data(bmks_df,freq='1D')
bmks_w = dm.format_data(bmks_df,freq='1W')
bmks_m = dm.format_data(bmks_df,freq='1M')
bmks_q = dm.format_data(bmks_df,freq='1Q')
bmks_y = dm.format_data(bmks_df,freq='1Y')

strats_d = dm.format_data(strats_df,freq='1D')
strats_w = dm.format_data(strats_df,freq='1W')
strats_m = dm.format_data(strats_df,freq='1M')
strats_q = dm.format_data(strats_df,freq='1Q')
strats_y = dm.format_data(strats_df,freq='1Y')

#3
bmks_dict = dm.get_data_dict(bmks_df, data_type='index')
strats_dict = dm.get_data_dict(strats_df, data_type='index')

#4
data_df = dm.merge_data_frames(bmks_df, strats_df)

#5
data_df_d = dm.format_data(data_df,freq='1D')
data_df_w = dm.format_data(data_df,freq='1W')
data_df_m = dm.format_data(data_df,freq='1M')

#6
data_dict_1 = dm.get_data_dict(data_df, data_type='index')

#7
data_dict_2 = dm.merge_dicts(bmks_dict, strats_dict)



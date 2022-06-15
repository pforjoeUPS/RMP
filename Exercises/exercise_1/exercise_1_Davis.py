# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 15:19:00 2022

@author: GMS0VSB
"""

import pandas as pd

#1
data_bmk = pd.read_excel('C:\\Users\\GMS0VSB\\Documents\\GitHub\\data_for_exercise_1.xlsx', sheet_name='bmks', index_col=0)
data_strats = pd.read_excel('C:\\Users\\GMS0VSB\\Documents\\GitHub\\data_for_exercise_1.xlsx', sheet_name='strats', index_col=0)

#2

bmks_d = dm.format_data(data_bmk, freq = '1D')
bmks_w = dm.format_data(data_bmk, freq = '1W')
bmks_m = dm.format_data(data_bmk, freq = '1M')
bmks_q = dm.format_data(data_bmk, freq = '1Q')

strats_d = dm.format_data(data_strats, freq = '1D')
strats_w = dm.format_data(data_strats, freq = '1W')
strats_m = dm.format_data(data_strats, freq = '1M')
strats_q = dm.format_data(data_strats, freq = '1Q')

#3

bmks_dict = {'Daily': bmks_d, 'Weekly': bmks_w, 'Monthly': bmks_m, 'Quarterly': bmks_q}
strats_dict = {'Daily': strats_d, 'Weekly': strats_w, 'Monthly': strats_m, 'Quarterly': strats_q}

#4

data_df = dm.merge_data_frames(data_bmk, data_strats)

#5

data_df_d = dm.format_data(data_df, freq = '1D')
data_df_w = dm.format_data(data_df, freq = '1W')
data_df_m = dm.format_data(data_df, freq = '1M')

#6

data_dict_1 = {'Daily': data_df_d, 'Weekly': data_df_w, 'Monthly': data_df_m}

#7

data_dict_2 = dm.merge_dicts(bmks_dict, strats_dict)

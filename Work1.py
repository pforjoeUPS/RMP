# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 13:11:21 2021

@author: gcz5chn
"""

import pandas as pd

df = pd.DataFrame({'Data1': [1,2,3], 'Data2':[4,5,6]})
column_maxes = df.max()
df_max = column_maxes.max()
normalized_df = df / df_max

print(normalized_df)

df2 = pd.DataFrame({'Data1':[-1,2,3],'Data2':[4,-5,6]})
column_maxes = df2.max()
df2_max = column_maxes.max()
column_mins = df2.min()
df2_min = column_mins.min()
normalized_df2= (df2 - df2_min)/(df2_max - df2_min)

print(normalized_df2)


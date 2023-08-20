# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 09:46:13 2023

@author: rrq1fyq
"""

import pandas as pd
import os
from functools import reduce
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from EquityHedging.datamanager import data_manager as dm
CWD = os.getcwd()

#read in macquarie data to left merge dates 
macq_ret= pd.read_excel(CWD + "\\Cluster Analysis\\data\\QIS Universe Returns.xlsx" , sheet_name="Macquarie", 
                         engine='openpyxl', index_col = 0)
#get one column to use for merging data to get exact dates

fmt =  macq_ret['MQCP833E Index']
# Get existing time series
existing_file = 'QIS Universe Time Series.xlsx'

existing_sheet_name = 'BNP'

# Read the original Excel file into a Pandas DataFrame
existing_df = pd.read_excel(CWD + "\\Cluster Analysis\\data\\" +existing_file, sheet_name=existing_sheet_name, 
                           engine='openpyxl', index_col = 0)

#get returns of og file
returns = dm.format_data(existing_df, freq= '1D')



merge_new_data = False
if merge_new_data:
    data = returns.copy()
    
    #loop through new time series, get returns, and merge to original 
    for i in list(range(1,19)):
        new_data =  pd.read_excel(CWD + "\\Cluster Analysis\\data\QIS Tickers\\CS extended.xlsx", sheet_name="Sheet"+str(i), 
                                     engine='openpyxl', index_col = 0)
        new_returns = dm.format_data(new_data, "1D")
        data = dm.merge_data_frames(data, new_returns, fillzeros = True)

fmt_dates = dm.merge_data_frames(fmt, returns, fillzeros=True)
fmt_dates.drop('MQCP833E Index', axis = 1, inplace = True)



import pandas as pd
import numpy as np

path = CWD + "\\Cluster Analysis\\data\\HM_Universe.xlsx" 

book = load_workbook(path)
writer = pd.ExcelWriter(path, engine = 'openpyxl')
writer.book = book

fmt_dates.to_excel(writer, sheet_name="Revised HM", startrow=0, startcol=0)
writer.close()

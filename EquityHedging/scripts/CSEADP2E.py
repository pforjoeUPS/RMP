# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 21:13:32 2021

@author: Zach Wells
"""

from EquityHedging.datamanager import data_manager as dm
import pandas as pd

from EquityHedging.reporting.excel import sheets
import os

#Creating pathway to set up working directory to point where the returns data is
CWD = os.getcwd()
RETURNS_DATA_FP = '\\EquityHedging\\data\\'
EQUITY_HEDGING_RETURNS_DATA = CWD + RETURNS_DATA_FP + 'ups_equity_hedge\\returns_data.xlsx'

#create a list with the name of each sheet on returns_data
freq_list=['Daily','Weekly','Monthly','Quarterly','Yearly']

#create empty dictionary that loop will fill in
returns={}

#create loop that loops through each sheet in the returns_data and read it in
for freq in freq_list:
    returns[freq]=pd.read_excel(EQUITY_HEDGING_RETURNS_DATA, sheet_name=freq, index_col=0)
    
#Add new dynamic put spread
strategy = ['Dynamic Put Spread']
filename = 'CSEADP2E_20210628.xlsx'
sheet_name = 'Sheet1'
new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy)
new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')



#merging returns dictionary and def var returns dictionary 
#returns = dm.merge_dicts(returns, new_strategy_dict)

#seperating each frequency from the dictionary into a data frame
monthly_ret = returns['Monthly'].copy()
monthly_new_strat = new_strategy_dict['Monthly'].copy()
monthly_ret['Dynamic Put Spread']= monthly_new_strat['Dynamic Put Spread']

daily_ret = returns['Daily'].copy()
daily_new_strat = new_strategy_dict['Daily'].copy()
daily_ret['Dynamic Put Spread']= daily_new_strat['Dynamic Put Spread']

quarter_ret = returns['Quarterly'].copy()
quart_new_strat = new_strategy_dict['Quarterly'].copy()
quarter_ret['Dynamic Put Spread'] = quart_new_strat['Dynamic Put Spread']

weekly_ret = returns['Weekly'].copy()
weekly_new_strat = new_strategy_dict['Weekly'].copy()
weekly_ret['Dynamic Put Spread']= weekly_new_strat['Dynamic Put Spread']

yearly_ret = returns['Yearly'].copy()
yearly_new_strat = new_strategy_dict['Yearly'].copy()
yearly_ret['Dynamic Put Spread'] = yearly_new_strat['Dynamic Put Spread']

#creating an excel writer
writer= pd.ExcelWriter('returns_data.xlsx',engine='xlsxwriter')
#create new dictionary to be saved to returns data
new_ret_dict={"Daily":daily_ret, "Weekly":weekly_ret, "Monthly":monthly_ret,"Quarterly":quarter_ret,"Yearly":yearly_ret}

#loop through each sheet (aka frequency) of the returns_data excel file in order to add data to the corresponding sheet
for freq in freq_list:
    sheets.set_hist_return_sheet(writer, new_ret_dict[freq], freq)
writer.save()

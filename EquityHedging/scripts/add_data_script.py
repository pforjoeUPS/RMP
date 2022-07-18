# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 22:35:26 2021

@author: Maddie Choi
"""
import os
os.chdir("..\..")
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp


#get data from returns_data.xlsx into dictionary
returns_dict = dm.get_equity_hedge_returns(all_data=True)

 #create dictionary that contains updated returns
new_data_dict = dm.create_update_dict()

#TODO: make into method in data_manager.py
for key in returns_dict:
    #create returns data frame
    new_ret_df = new_data_dict[key].copy()
    ret_df = returns_dict[key].copy()
    
    #update current year returns 
    if key == 'Yearly':
        if ret_df.index[-1] == new_ret_df.index[-1]:
            ret_df = ret_df[:-1]
            
    #reset both data frames index to make current index (dates) into a column
    new_ret_df.index.names = ['Date']
    new_ret_df.reset_index(inplace = True)
    ret_df.reset_index(inplace=True)
   

    #find difference in dates
    difference = set(new_ret_df.Date).difference(ret_df.Date)
    #find which dates in the new returns are not in the current returns data
    difference_dates = new_ret_df['Date'].isin(difference)
    
    #select only dates not included in original returns df
    new_ret_df = new_ret_df[difference_dates]
    
    
    #set 'Date' column as index for both data frames
    new_ret_df.set_index('Date', inplace = True)
    ret_df.set_index('Date', inplace = True)
    
    #reassign dataframes to dictionaries
    #new_data_dict[key] = new_ret_df
    #returns_dict[key] = ret_df
    
    returns_dict[key] = ret_df.append(new_ret_df)
    

returns_dict = dm.check_returns(returns_dict)


#returns_dict = dm.append_dict(returns_dict, new_data_dict)


#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)




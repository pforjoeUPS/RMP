# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 13:09:25 2022

@author: LGQ0NLN
"""

#import os
#os.chdir("..\..")
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp

#Write two methods
# One method: for the for loop
#   Reference method
# Two method: second method for appending

def get_updated_returns():
    returns_dict = dm.get_equity_hedge_returns(all_data=True)
    #create dictionary that contains updated returns
    new_data_dict = dm.create_update_dict()

    for key in returns_dict:
    #create returns data frame
        new_ret_df = new_data_dict[key]
        ret_df = returns_dict[key]
        
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
        returns_dict[key] = ret_df
        new_data_dict[key] = new_ret_df

#update returns_dict with new_data
    returns_dict = dm.append_dict(returns_dict, new_data_dict)

#create new returns report
    rp.get_returns_report('returns_data_new', returns_dict)

#method one
def method_updating_returns():
    returns_dict = get_equity_hedge_returns(all_data=True)
    #create dictionary that contains updated returns
    new_data_dict = create_update_dict()
    
    for key in returns_dict:
    #create returns data frame
        new_ret_df = new_data_dict[key]
        ret_df = returns_dict[key]
        
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
        returns_dict[key] = ret_df
        new_data_dict[key] = new_ret_df
    returns_dict = append_dict(returns_dict, new_data_dict)
    return returns_dict
    
dm.method_updating_returns()

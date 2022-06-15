# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 22:35:26 2021

@author: gcz5chn
"""
import os
os.chdir("..\..")
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp



#get data from returns_data.xlsx into dictionary
returns_dict = dm.get_equity_hedge_returns(all_data=True)

#create dictionary that contains updated returns
new_data_dict = dm.create_update_dict()

#TODO: make into method
for key in returns_dict:
    
    #create returns fata frame
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
    
    

# # #remove first n rows from daily dataframe
# n = 2
# new_data_dict['Daily'] = new_data_dict['Daily'].iloc[n:,]

# # #remove last n rows from daily dataframe
# n = 1
# new_data_dict['Daily'] = new_data_dict['Daily'][:-n]



# # #remove first n rows from weekly dataframe
# n = 8
# new_data_dict['Weekly'] = new_data_dict['Weekly'].iloc[n:,]

# #remove last row from weekly dataframe
# n = 1
# new_data_dict['Weekly'] = new_data_dict['Weekly'][:-n]


# # #remove first n rows from monthly dataframe
# n = 2
# new_data_dict['Monthly'] = new_data_dict['Monthly'].iloc[n:,]

# # #remove last n rows from monthly dataframe
# n = 1
# new_data_dict['Monthly'] = new_data_dict['Monthly'][:-n]


# # #remove first n rows from quarterly dataframe
# n = 0
# new_data_dict['Quarterly'] = new_data_dict['Quarterly'].iloc[n:,]

# # #remove last n rows from original returns quarterly dataframe
# n = 1
# new_data_dict['Quarterly'] = new_data_dict['Quarterly'][:-n]


# # #remove first n rows from yearly dataframe
# n = 0
# new_data_dict['Yearly'] = new_data_dict['Yearly'].iloc[n:,]

# # #remove last n rows from original returns yearly dataframe
# n = 1
# returns_dict['Yearly'] = returns_dict['Yearly'][:-n]


#update returns_dict with new_data
returns_dict = dm.append_dict(returns_dict, new_data_dict)

#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)

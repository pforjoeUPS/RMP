# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 19:28:50 2022

@author: maddi
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp
import pandas as pd
#get data from returns_data.xlsx into dictionary
returns_dict = dm.get_equity_hedge_returns(all_data=True)

month = returns_dict['Monthly']
#monthly has long corp and strips;
# annualize the monthly returns to make it match up?
year = returns_dict['Yearly']
col = month.columns


# for col in month.columns:
#     #take each strategy's returns
#     month_ret = month[col]
#     #yr_ret = year[col]
#     #yr_ret = pd.DataFrame(yr_ret)
    
#     #convert strategy's return series into a data frame
#     df = pd.DataFrame(month_ret)
    
#     #create new columns with the corresponding year and month to each return
#     df['year'] = df.index.year
#     df['month'] = df.index.month_name().str[:3]
    
#     #group the data by year and month
#     strat_monthly_returns = df.groupby(['year', 'month']).sum()
#     table = strat_monthly_returns.unstack()
#     table = table.droplevel(level = 0, axis = 1)
#     table = table[["Jan", "Feb", "Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]]
#     print(table)

    
def month_ret_table(strategy):
    '''
    

    Parameters
    ----------
    strategy : String
        Strategy to put monthly returns into tabular form.

    Returns
    -------
    Data Frame.

    '''
    #create returns data dict
    returns_dict = dm.get_equity_hedge_returns(all_data=True)

    #get monthly and yearly returns from dictionary
    month = returns_dict['Monthly']
    year = returns_dict['Yearly']
    
    #index input strategy out of monthly and yearly returns df
    month_ret = month[strategy]
    yr_ret  = year[strategy]
    
    #convert yearly returns into a data frame with index of years 
    yr_ret = pd.DataFrame(yr_ret)
    #rename column name
    yr_ret = yr_ret.rename(columns={'Down Var': 'Year'})
    #set index as years instead of date so that you can concatenate later
    yr_ret.set_index(yr_ret.index.year, inplace = True)
    
    #create monthly return data frame with index of years 
    df = pd.DataFrame(month_ret)
    df['year'] = df.index.year
    df['month'] = df.index.month_name().str[:3]
    
    #change monthly returns into a table with x axis as months and y axis as years
    strat_monthly_returns = df.groupby(['year', 'month']).sum()
    month_table = strat_monthly_returns.unstack()
    
    #drop first row index
    month_table = month_table.droplevel(level = 0, axis = 1)
    
    #re order columns
    month_table = month_table[["Jan", "Feb", "Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]]
    
    #Join yearly returns to the monthly returns table
    table = pd.concat([month_table, yr_ret],  axis=1)

    print(table)



month_ret_table('VRR')

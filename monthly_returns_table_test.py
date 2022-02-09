# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 19:28:50 2022

@author: maddi
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.analytics import returns_stats as ret_s
import pandas as pd
import numpy as np
#get data from returns_data.xlsx into dictionary
returns_dict = dm.get_equity_hedge_returns(all_data=True)

def ann_ret_from_monthly(strat_monthly_returns, strategy):
    monthly_ret = strat_monthly_returns.copy()
    monthly_ret["Year"] = monthly_ret.index.get_level_values('year')
    
    years = np.unique(monthly_ret["Year"])
    yr_ret = []
    for i in range(0, len(years)):
        monthly_ret_by_yr = monthly_ret.loc[monthly_ret.Year == years[i]][strategy]
        ann_ret =ret_s.get_ann_return(monthly_ret_by_yr)
        yr_ret.append(ann_ret)
        
    yr_ret = pd.DataFrame( yr_ret, columns = ["Yearly"], index = list(years)) 
    return yr_ret
    

def month_ret_table(returns_dict, strategy):
    '''
    #just use monthly data and annualize using get ann return in return stats.py

    Parameters
    ----------
    returns_dict : Dictionary
        dictionary with Daily, Monthly, Yearly, Quarterly returns
        
    strategy : String
        Strategy name

    Returns
    -------
    Data Frame

    '''
    #pull monthly returns from dictionary 
    month_ret = pd.DataFrame(returns_dict['Monthly'][strategy])
    
    #yr_ret = ret_s.get_ann_return(month_ret, freq = '1M')
    #yr_ret = pd.DataFrame(returns_dict['Yearly'][strategy])
    #rename column name
    #yr_ret.columns = ['Year']
    #set index as years instead of date so that you can concatenate later
    #yr_ret.set_index(yr_ret.index.year, inplace = True)


    #create monthly return data frame with index of years 
    month_ret['year'] = month_ret.index.year
    month_ret['month'] = month_ret.index.month_name().str[:3]
    
    #change monthly returns into a table with x axis as months and y axis as years
    strat_monthly_returns = month_ret.groupby(['year', 'month']).sum()
    yr_ret = ann_ret_from_monthly(strat_monthly_returns, strategy)
       
    month_table = strat_monthly_returns.unstack()
    
    #drop first row index
    month_table = month_table.droplevel(level = 0, axis = 1)
    
    #re order columns
    month_table = month_table[["Jan", "Feb", "Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]]
    
    #Join yearly returns to the monthly returns table
    table = pd.concat([month_table, yr_ret],  axis=1)
    return table

    


month_ret_table(returns_dict, 'Long Corp')


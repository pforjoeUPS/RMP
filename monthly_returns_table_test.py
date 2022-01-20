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
col=month.columns

for i in range(1,len(col)):
    #take each strategy's returns
    strategy = month[col[i]]
    
    #convert strategy's return series into a data frame
    df = pd.DataFrame(strategy)
    
    #create new columns with the corresponding year and month to each return
    df['year'] = df.index.year
    df['month'] = df.index.month
    
    #group the data by year and month
    strat_monthly_returns = df.groupby(['year', 'month']).sum()
    table = strat_monthly_returns.unstack()
    print(table)
    
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
    returns_dict = dm.get_equity_hedge_returns(all_data=True)

    month = returns_dict['Monthly']

    strat = month[strategy]
    
    df = pd.DataFrame(strat)
    df['year'] = df.index.year
    df['month'] = df.index.month
    
    strat_monthly_returns = df.groupby(['year', 'month']).sum()
    table = strat_monthly_returns.unstack()
    print(table)
    
month_ret_table('Down Var')

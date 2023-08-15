# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 10:31:35 2023

@author: RRQ1FYQ
"""
from EquityHedging.datamanager import data_manager as dm
import pandas as pd
import numpy as np

master = pd.read_excel(dm.NEW_DATA+"PE.xlsx", sheet_name="Master Data")
col_names = master.columns
cf = pd.read_excel(dm.NEW_DATA+"PE.xlsx", sheet_name="Sheet1", index_col=0)


def num_investments(data, col_name, ranges = []):
    n = pd.DataFrame()
    #if set ranges
    if len(ranges) !=0:
        for i in list(range(0,len(ranges)-1)):
            n[ranges[i]] = data[(data[col_name]>= ranges[i]) & (data[col_name]<ranges[i+1])]
    else:
        #find unique values in the column
        unique = np.unique(data[col_name])
        
        #loop through unique values and count how often it is listed (i.e how many investments)
        for i in unique:
            n[i] = [list(data[col_name]).count(i)]
        
    return n

def  invested_p(invested):
    invested_p = pd.DataFrame()
    invested_p["Total"] = invested.sum(axis = "columns")
    for i in list(invested.columns):
        invested_p[i] = invested[i]/invested_p["Total"]
    invested["Total"] = 1
    return invested_p


def get_investment_names(data, category, ranges = []):
    investments = {}
    #if set ranges
    if len(ranges) !=0:
        for i in list(range(0,len(ranges)-1)):
            investments[ranges[i]] = list(data["Investment Name"][(data[category]>= ranges[i]) & (data[category]<ranges[i+1])])
    else:
        #get investment names in each category
        funds = data.pivot(values = "Investment Name", columns = category)
        for i in list(funds.columns):
            #find investments per each category
            investments[i] = funds[i].dropna().unique().tolist()
            
    return investments


def get_category_cf(data, cf, category, ranges = []):
    
    total = pd.DataFrame()

    investments = get_investment_names(data,cf,category, ranges)
    
    #loop through investments and drop funds that arent in the category
    for key in investments:
        for x in investments[key]:
            if x not in list(cf.columns):
                investments[key].remove(x)
                
        total[key] = cf[investments[key]].sum(axis = "columns")
    
    return total


def dollar_invested(data, cf, category, ranges = []):
    
    #get joined cashflows for each sub category
    category_cfs = get_category_cf(data, cf, category, ranges = ranges)
    
    dollar_invested = pd.DataFrame()
    for i in list(category_cfs.columns):
        dollar_invested[i] = [-sum(category_cfs[i][category_cfs[i]<=0])]
        
    return dollar_invested



def unrealized(data, cf, category, ranges = []):
    #get joined cashflows for each sub category
    category_cfs = get_category_cf(data, cf, category, ranges = ranges)
    unrealized_cf = pd.DataFrame(category_cfs.iloc[-1]).transpose()

    return unrealized_cf


def realized(data,unrealized, cf, category, ranges = []):
    #get joined cashflows for each sub category
    category_cfs = get_category_cf(data, cf, category, ranges = ranges)
    realized_cf = pd.DataFrame()
    
    #loop through each sub category to find realized cashflows
    for i in list(category_cfs.columns):
        realized= [sum(category_cfs[i][category_cfs[i]>0])]
        realized_cf[i] = realized - unrealized[i]        
    
    return realized_cf

# def irr(data,cf, category, ranges = []):
#     #get joined cashflows for each sub category
#     category_cfs = get_category_cf(data, cf, category, ranges = ranges)
#     x = category_cfs['Encore'][(category_cfs['Encore'] != 0)]
#     np.irr(x.values)
    


def get_entry_exit_values(data, category, value_type, ranges = []):
    investments = get_investment_names(data, category, ranges)
    ee_value = pd.DataFrame()
    master = data[['Investment Name', value_type]].transpose()
    master.columns = master.iloc[0]
    
    for key in investments:
        ee_value[key] = [master[investments[key]].iloc[1].sum()]

    return ee_value


category = "Fund"
no_investments = num_investments(data = master, col_name = category)
invested = dollar_invested(master,cf,category)
invested_percent = invested_p(invested)
unrealized_cf = unrealized(master, cf, category = category)
realized_cf = realized(master,unrealized_cf, cf, category = category)
moic = (realized_cf + unrealized_cf)/invested
dpi = realized_cf/invested
ee_value = get_entry_exit_values(master, category, value_type = "Entry Enterprise Value  ($M)")
e_LTM_rev =  get_entry_exit_values(master, category, value_type = "Entry LTM Revenue ($M)")
e_LTM_ebitda =  get_entry_exit_values(master, category, value_type = "Entry LTM EBITDA ($M)")
e_net_debt = get_entry_exit_values(master, category, value_type = "Entry Net Debt ($M)")







index = ["# of Investments","$ Invested","$ Invested","Realized","Unrealized"]
df = pd.concat([no_investments, invested, invested_percent,  realized_cf, unrealized_cf,], ignore_index = True)
df.set_axis(index, axis = 0, inplace = True)

df.to_excel(writer, sheet_name=category, startrow=0, startcol=0)


report_name = "PE_test1"
file_path = rp.get_report_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
#create writer and workbook
workbook = writer.book

writer.save()   





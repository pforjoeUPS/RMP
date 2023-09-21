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
    df = data[['Investment Name',col_name]]
    df.fillna("NA",inplace = True)
    #if set ranges
    if len(ranges) !=0:
        num_values = df[df[col_name] != "Various"]
        numvalues = num_values[num_values[col_name] != "NA"]
        for i in list(range(0,len(ranges)-1)):
            n[ranges[i]] = [numvalues[(numvalues[col_name]>= ranges[i]) & (numvalues[col_name]<ranges[i+1])]['Investment Name'].count()]
        n["NA"] = [df[df[col_name] == "NA"][col_name].count()]
        n["Various"] = [df[df[col_name] == "Various"][col_name].count()]
        
        
    else:
        
        #find unique values in the column
        unique = np.unique(df[col_name])
        
        #loop through unique values and count how often it is listed (i.e how many investments)
        for i in unique:
            n[i] = [list(df).count(i)]
        
    return n

def  invested_p(invested):
    invested_p = pd.DataFrame()
    total = invested.sum(axis = "columns")
    for i in list(invested.columns):
        invested_p[i] = invested[i]/total
    
    return invested_p


def get_investment_names(data, category, ranges = []):
    investments = {}
    #if set ranges
    if len(ranges) !=0:
        df = data[['Investment Name',category]]
        df.fillna("NA",inplace = True)
        num_values = df[df[category] != "Various"]
        numvalues = num_values[num_values[category] != "NA"]
        
        
        for i in list(range(0,len(ranges)-1)):
            
            investments[ranges[i]] = list(numvalues["Investment Name"][(numvalues[category]>= ranges[i]) & (numvalues[category]<ranges[i+1])])
            investments["NA"] = list(df[df[category] == "NA"]['Investment Name'])
            investments["Various"] = list(df[df[category] == "Various"]['Investment Name'])
    else:
        #get investment names in each category
        funds = data.pivot(values = "Investment Name", columns = category)
        for i in list(funds.columns):
            #find investments per each category
            investments[i] = funds[i].dropna().unique().tolist()
            
    return investments


def get_individual_cfs(data, cf, category, ranges = []):
    
    total = {}

    investments = get_investment_names(data,category, ranges)
    
    #loop through investments and drop funds that arent in the category
    for key in investments:
        for x in investments[key]:
            if x not in list(cf.columns):
                investments[key].remove(x)
                
        total[key] = cf[investments[key]]
    
    return total

def get_category_cf(data, cf, category, ranges = []):
    
    total = pd.DataFrame()

    investments = get_investment_names(data,category, ranges)
    
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
    
def get_distributed_dict(data, cf, category, ranges = []):
    #loop through each calculate max(0, invested-distributed-unrealized)
    cashflows = get_individual_cfs(data, cf, category, ranges)
    #get the status of each individual investment
    status = master[['Investment Name','Status']].set_index('Investment Name').transpose()
    
    distributed_dict = {}
    
    #loop through each sub category cashflows df
    for key in cashflows:
        temp_df = pd.DataFrame()
        
        #loop through each column in the cashdlow
        for col in cashflows[key]:
            tempcf = cashflows[key][col].copy()
            
            #if investment status is unrealized, sum all cfs except the last row
            if status[col].iloc[0] == "Unrealized":
                unrealized_cf = tempcf[:-1]
                distributed = sum(unrealized_cf[unrealized_cf>0])
            
            #if investment status is realized, sum all cfs
            elif status[col].iloc[0] == "Realized":
                 distributed = sum(tempcf[tempcf>0])
            #if investmetn status is anything else, distributed  = 0
            else: distributed = 0
            
            temp_df[col] = [distributed]
        distributed_dict[key]= temp_df
        
    return distributed_dict            


def get_category_distributed_df(data, cf, category, ranges = []):
    #loop through each calculate max(0, invested-distributed-unrealized)
    cashflows = get_individual_cfs(data, cf, category, ranges)
    status = master[['Investment Name','Status']].set_index('Investment Name').transpose()
    
    df= pd.DataFrame()
    
    for key in cashflows:
        temp_df = pd.DataFrame()
        for col in cashflows[key]:
            tempcf = cashflows[key][col].copy()
            
            if status[col].iloc[0] == "Unrealized":
                unrealized_cf = tempcf[:-1]
                distributed = sum(unrealized_cf[unrealized_cf>0])
                
            elif status[col].iloc[0] == "Realized":
                 distributed = sum(tempcf[tempcf>0])
            else: distributed = 0
            
            temp_df[col] = [distributed]
        df[key]= [temp_df.sum().sum()]
        
    return df
        
        
def get_entry_exit_values(data, category, value_type, ranges = []):
    investments = get_investment_names(data, category, ranges)
    ee_value = pd.DataFrame()
    master = data[['Investment Name', value_type]].transpose()
    master.columns = master.iloc[0]
    
    for key in investments:
        ee_value[key] = [master[investments[key]].iloc[1].sum()]

    return ee_value


def get_dollar_losses(data, cf, category, ranges = []):
   
    #loop through each calculate max(0, invested-distributed-unrealized)
    cashflows = get_individual_cfs(data, cf, category, ranges)
    distributed_dict = get_distributed_dict(data, cf, category, ranges)
    
    dollar_loss_dict = {}
    dollar_loss_df = pd.DataFrame()
    for key in cashflows:
        dollar_loss = pd.DataFrame()
        for col in cashflows[key]:
            tempcf = cashflows[key][col].copy()
            invested = -sum(tempcf[tempcf<=0])
            distributed = distributed_dict[key][col].iloc[0]
            unrealized = tempcf.iloc[-1]
            
            dollar_loss[col] = [max(0, (invested-distributed-unrealized))]
            
        dollar_loss_dict[key] = dollar_loss
        dollar_loss_df[key] = [dollar_loss.sum().sum()]
        
    return dollar_loss_df

    
def get_metrics(master, cf, category, ranges = []):

    no_investments = num_investments(data = master, col_name = category, ranges = ranges)
    invested = dollar_invested(master,cf,category,ranges = ranges)
    invested_percent = invested_p(invested)
    follow_on_invested = get_entry_exit_values(master, category, value_type= "Follow-on Invested", ranges = ranges)
    unrealized_cf = unrealized(master, cf, category = category, ranges = ranges)
    realized_cf = realized(master,unrealized_cf, cf, category = category,ranges = ranges)
    distributed = get_category_distributed_df(master, cf, category = category,ranges = ranges)
    moic = (realized_cf + unrealized_cf)/invested.iloc[0]
    dpi = realized_cf/invested.iloc[0]
    entry_enterprise_value = get_entry_exit_values(master, category, value_type = "Entry Enterprise Value",ranges = ranges)
    entry_LTM_rev =  get_entry_exit_values(master, category, value_type = "Entry LTM Revenue",ranges = ranges)
    entry_LTM_ebitda =  get_entry_exit_values(master, category, value_type = "Entry LTM EBITDA",ranges = ranges)
    entry_net_debt = get_entry_exit_values(master, category, value_type = "Entry Net Debt",ranges = ranges)
    entry_enterprise_value_ebitda = entry_enterprise_value/entry_LTM_ebitda
    entry_enterprise_value_rev = entry_enterprise_value/entry_LTM_rev
    debt_ebitda = entry_net_debt/entry_LTM_ebitda
    exit_curr_debt =  get_entry_exit_values(master, category, value_type = "Exit/Current Enterprise Value",ranges = ranges)
    exit_curr_ebitda =  get_entry_exit_values(master, category, value_type = "Exit/Current LTM EBITDA",ranges = ranges)
    exit_curr_debt_ebitda = exit_curr_debt/exit_curr_ebitda
    dollar_losses = get_dollar_losses(master, cf, category = category,ranges = ranges)
    loss_ratio = dollar_losses/invested
    
    df = pd.concat([no_investments,invested,invested_percent, follow_on_invested, unrealized_cf, realized_cf, distributed, moic, dpi , entry_enterprise_value,
                    entry_LTM_rev,entry_LTM_ebitda, entry_net_debt,entry_enterprise_value_ebitda , entry_enterprise_value_rev, 
                    debt_ebitda, exit_curr_debt, exit_curr_ebitda,exit_curr_debt_ebitda, dollar_losses, loss_ratio])
    
    metric_names = ["# of Investments", "$ Invested", "% Invested","Follow On Invested", "Unrealized","Realized", "Distributed", "MOIC","DPI",
                    "Entry Enterprise_value", "Entry LTM Revenue","Entry LTM EBITDA", "Entry Net Debt",  "Entry EV / EBITDA", "Entry EV / Revenue",
                    "Entry Net Debt / EBITDA", "Exit / Current Net Debt", "Exit / Current EBITDA" , "Exit / Current Net Debt / EBITDA", "Dollar Losses","Loss Ratio"]
    df.set_axis(metric_names, inplace = True)
    
    df['Total'] = df.sum(axis = 1)
    metric_df = df.transpose(copy = True)
    
    return metric_df


def set_worksheet_format(workbook):
    """
    Format sheet
    
    Parameters:
    workbook
    """

    cell_format = workbook.add_format()
    cell_format.set_font_name('Calibri')
    cell_format.set_font_size(11)
    cell_format.set_bg_color('#FFFFFF')
    cell_format.set_align('center')
    cell_format.set_align('vcenter')
    return cell_format

def set_title_format(workbook):
    """
    Format title
    
    Parameters:
    workbook
    """
    title_format = workbook.add_format()
    title_format.set_bold()
    title_format.set_font_color('#000000')
    title_format.set_font_name('Calibri')
    title_format.set_font_size(14)
    return title_format

def set_number_format(workbook,num_format, bold=False):
    """
    Format numbers
    
    Parameters:
    workbook
    num_format
    bold -- boolean
    """

    num_format = workbook.add_format({'num_format': num_format, 'bold':bold})
    return num_format

def set_metrics_sheet(writer, data_df, sheet_name, spaces=3):
    """
    Create excel sheet with:
    
    Parameters:
    writer - ExcelWriter
    data_dict -- list
    sheet_name -- string
    spaces -- int

    Returns:
    excel writer
    """

    #create writer and workbook
    workbook = writer.book
    
    #pull out lists from data_dict
    df_list = [data_df]
    title_list = "Fund"
    #format background color of worksheet to white
    cell_format = set_worksheet_format(workbook)
    df_empty = pd.DataFrame()
    df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column(0, 1000, 22, cell_format)
    row = 2
    col = 1
    
    #get formats for worksheet
    #title format
    title_format = set_title_format(workbook)
    #digits format
    digits_fmt = set_number_format(workbook,num_format='0.00')
    #percent format
    pct_fmt = set_number_format(workbook,num_format='0.00%')
    dollar_fmt = set_number_format(workbook,num_format='[$R]#,##0.00')
    int_fmt = set_number_format(workbook, num_format='0')
        
    for n in range(0,len(df_list)):
        try:
            row_dim = row + df_list[n].shape[0]
            col_dim = col + df_list[n].shape[1]
            worksheet.write(row-1, 1, title_list[n], title_format)
            
            #write data into worksheet
            df_list[n].to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=1)   
          
        except AttributeError:
            pass
        
            #format # of investment
            worksheet.conditional_format(row+1,col+2, row_dim, col+1,{'type':'no_blanks',
                                      'format':digits_fmt})
            
            #format $ invested
            worksheet.conditional_format(row+1,col+2, row_dim, col+2,{'type':'no_blanks',
                                      'format':dollar_fmt})
            
            #format % Invested
            worksheet.conditional_format(row+1,col+3, row_dim, col+3,{'type':'no_blanks',
                                      'format':pct_fmt})
            
            #format follow on invested, Realized, Unrealized, Distributed
            worksheet.conditional_format(row+1,col+4, row_dim, col+7,{'type':'no_blanks',
                                      'format':pct_fmt})
            
                        

            row = row_dim + spaces + 1
    
    return 0


categories_list = ["Fund", "Vintage","Entry Ownership Percentage - Fully Diluted", "Status",'Sector',
                   "Geography","Investment Type","Seller","Co-Investors (Y/N)","Exit Type","Entry Enterprise Value",
                   "Entry LTM Revenue","Entry LTM EBITDA","Entry Net Debt / LTM EBITDA","Exit/Current Net Debt / LTM EBITDA",
                   "Exit/Current LTM Revenue","Exit/Current LTM EBITDA"]

test_list = ["Fund", "Entry Ownership Percentage - Fully Diluted", "Status",'Sector',
                   "Geography","Investment Type"]

metrics_dict = {}
for i in test_list:
    ranges = []
    if i == "Entry Ownership Percentage - Fully Diluted":
        ranges = [0,0.25,0.5,0.75,1]
    
    metrics_dict[i] = get_metrics(master, cf, category = i, ranges = ranges)
            
import os
from EquityHedging.reporting.excel import formats

CWD = os.getcwd()
file_path = CWD + "\\EquityHedging\\reports\\PE_wynnchurch.xlsx" 

writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
#create writer and workbook
workbook = writer.book
#format background color of worksheet to white
cell_format = formats.set_worksheet_format(workbook)
df_empty = pd.DataFrame()
df_empty.to_excel(writer, sheet_name="PE Test", startrow=0, startcol=0)
worksheet = writer.sheets["PE Test"]
worksheet.set_column(0, 1000, 22, cell_format)
row = 2
col = 1
for n in metrics_dict:
    row_dim = row + metrics_dict[n].shape[0]
    col_dim = col + metrics_dict[n].shape[1]
    worksheet.write(row-1, 1, n)
    
    #write data into worksheet
    metrics_dict[n].to_excel(writer, sheet_name="PE Test", startrow=row , startcol=1)   
    row = row_dim + 3 + 1


writer.save()   

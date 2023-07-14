# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 15:37:27 2023

@author: RRQ1FYQ
"""

#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots
from EquityHedging.reporting import plots as plt2
import pandas as pd
from EquityHedging.reporting.excel import formats


#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = True
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

returns_df = returns["Yearly"]
df_returns = returns_df[["SPTR","Down Var"]]
report_name = "test.xlsx"
#get file path and create excel writer
file_path = rp.get_report_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')

def get_bar_chart(workbook, worksheet, sheet_name, ret_row_dim, position):
    #specify what type of chart
   returns_chart = workbook.add_chart({'type':'column'})

   #add SPTR returns data to bar chart
   returns_chart.add_series({
       #categories: format is [sheet name, start row, start column, end row, end column]
       #here we start at row1 (skip the title) and column 0 and end at the last row and column 0
       'categories': [sheet_name, 1, 0, ret_row_dim, 0], 
       'values': [sheet_name, 1, 1, ret_row_dim, 1],
       'name':"SPTR Returns"})
   
   #add Strategy returns data to bar chart
   returns_chart.add_series({
       'categories': [sheet_name, 1, 0, ret_row_dim, 0], 
       'values': [sheet_name, 1, 2, ret_row_dim, 2],
       'name': 'Strat Returns'})
   
   #set x axis
   returns_chart.set_x_axis({'label_position' : 'low',
                       'date_axis': True,
                      'num_format' : 'mmm-yy',

                      'num_font':{'rotation':-45,'name': 'Arial','color':'#616161 '},})
   
   #set y axis format
   returns_chart.set_y_axis({'num_format':'0%',
                            'num_font':  {'name': 'Arial', 'color':'#616161 '},
                            'line':{'none':True},
                           'major_gridlines': {
                               'visible' : 1,
                               'line' : { 'color' : '#D3D3D3'}
                               }
                           })
   
   #set chart title
   returns_chart.set_title({'name':" Returns" ,
                            'name_font':  {'name': 'Arial','color':'#616161 ','bold':False}})
   
   returns_chart.set_chartarea({'border':{'none':True}})
   
   #set legend position
   returns_chart.set_legend({'position':'bottom',
                             'font': {'name': 'Arial','color':'#616161 '}
                             })
   returns_chart.set_chartarea({'border':{'none':True}})
   #add chart to sheet and scale
   returns_chart.set_size({'x_scale': 1.5, 'y_scale': 1})
   worksheet.insert_chart(position, returns_chart)   

def get_bar_chart_excel(writer, df_returns, sheet_name):
     workbook = writer.book
     cell_format = formats.set_worksheet_format(workbook)
     df_empty = pd.DataFrame()
     df_empty.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
     worksheet = writer.sheets[sheet_name]
     worksheet.set_column(0, 1000, 21, cell_format)
    
     #start at row 0 and column 0 (i.e. cell A1 in excel)
     row = 0
     col = 0
    #set format for percent positive
     pct_fmt_pos = formats.set_number_format(workbook,num_format='0.00%')
     #percent format with dark red text.
     pct_fmt_neg = workbook.add_format({'num_format': '0.00%',
                                     'bold':False,
                                     'font_color': '#9C0006'})
     
     #date format
     date_fmt = formats.set_number_format(workbook, num_format='mm/dd/yyyy')
         
     #find size of returns data frame
     row_dim = row + df_returns.shape[0]
     col_dim = col + df_returns.shape[1]
     #    worksheet.write(row-1, 1, sheet_name, title_format)
     df_returns.to_excel(writer, sheet_name=sheet_name, startrow=row , startcol=col)   
     
     get_bar_chart(workbook, worksheet, sheet_name, ret_row_dim = row_dim, position = "D3")
     #format from row 2 to length of data frame with percent format
    
     worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                  {'type':'cell',
                                   'criteria': '<',
                                   'value': 0,
                                   'format':pct_fmt_neg})
     worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                  {'type':'cell',
                                   'criteria': '>',
                                   'value': 0,
                                   'format':pct_fmt_pos})
     worksheet.conditional_format(row+1,col+1, row_dim, col_dim,
                                  {'type':'cell',
                                   'criteria': '=',
                                   'value': 0,
                                   'format':pct_fmt_pos})
     #format from row 1 to col 1 with date format
     worksheet.conditional_format(row,col, row_dim, col,{'type':'no_blanks',
                                   'format':date_fmt})


get_bar_chart_excel(writer, df_returns, sheet_name = "Test")
writer.save()
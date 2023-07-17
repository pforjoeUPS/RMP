# -*- coding: utf-8 -*-
"""
Created on Fri July  7 2023

@author: Powis Forjoe
"""

import pandas as pd
from .import formats


class setSheet():
    def __init__(self, writer, sheet_name, row=0, col=0, first_col=0, last_col=1000, col_width=22):
        """
        Create default, formatted excel spread sheet

        Parameters
        ----------
        writer : ExcelWriter
        sheet_name : string
            Excel sheet name.
        row : int, optional
            Row index number. The default is 0.
        col : int, optional
            column index number. The default is 0.
        first_col : int, optional
            First column. The default is 0.
        last_col : int, optional
            Last column. The default is 1000.
        col_width : float, optional
            column width. The default is 22.
        Returns
        -------
        formatted sheet

        """
        self.writer = writer
        self.sheet_name = sheet_name
        self.workbook = self.writer.book
        self.row = row
        self.col = col
        self.cell_format = formats.set_worksheet_format(self.workbook)
        self.df_empty = pd.DataFrame()
        self.df_empty.to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row, startcol=self.col)
        self.worksheet = self.writer.sheets[self.sheet_name]
        self.worksheet.set_column(first_col, last_col, col_width, self.cell_format)
        
        #pct format
        self.pct_fmt = formats.set_number_format(self.workbook,num_format='0.00%')
        
        #percent format with dark red text.
        self.pct_fmt_neg = self.workbook.add_format({'num_format': '0.00%',
                                                    'bold':False,
                                                    'font_color': '#9C0006'})
        
        #percent format with dark green text.
        self.pct_fmt_pos = self.workbook.add_format({'num_format': '0.00%',
                                                    'bold':False,
                                                    'font_color': '#006100'})
    
        #date format
        self.date_fmt = formats.set_number_format(self.workbook, num_format='mm/dd/yyyy')
        self.date_fmt_2 = formats.set_number_format(self.workbook, num_format='d mmmm yyyy')
        
        #title format
        self.title_format = formats.set_title_format(self.workbook)
        
        #digits format
        self.digits_fmt = formats.set_number_format(self.workbook,num_format='0.00')
        
        #currency format
        self.ccy_fmt = formats.set_number_format(self.workbook,num_format='$#,##0.00')
        
        #int format
        self.int_fmt = formats.set_number_format(self.workbook, num_format='0')
        
class setHistReturnSheet(setSheet):
    # def __init__(self, writer, data, sheet_name='Monthly Historical Returns', row=0, col=0):
    def __init__(self, writer, data, sheet_name='Monthly Historical Returns'):
        """
        Create excel sheet for historical returns

        Parameters
        ----------
        writer : ExcelWriter
        data : dataframe
            Returns dataframe.
        sheet_name : string, optional
            Excel sheet name. The default is 'Monthly Historical Returns'.
        row : int, optional
            Row index number. The default is 0.
        col : int, optional
            Column index number. The default is 0.

        Returns
        -------
        Historical returns excel sheet.
        """
        setSheet.__init__(self, writer, sheet_name)
        self.data = data
        #freeze panes
        self.worksheet.freeze_panes(self.row+1, self.col+1)
        self.row_dim = self.row + self.data.shape[0]
        self.col_dim = self.col + self.data.shape[1]
        self.data.to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row , startcol=self.col)   
        #format dates with date_fmt (first column)
        self.worksheet.conditional_format(self.row,self.col, self.row_dim, 
                                          self.col,{'type':'no_blanks','format':self.date_fmt})
        self.format_worksheet_data()
                
    def format_worksheet_data(self):
        #format negative returns with pct_fmt_neg
        self.worksheet.conditional_format(self.row+1,self.col+1, self.row_dim, self.col_dim,
                                         {'type':'cell','criteria': '<','value': 0,'format':self.pct_fmt_neg})
        #format positive returns with pct_fmt
        self.worksheet.conditional_format(self.row+1,self.col+1, self.row_dim, self.col_dim,
                                     {'type':'cell','criteria': '>','value': 0,'format':self.pct_fmt})
        #format zero returns with pct_fmt
        self.worksheet.conditional_format(self.row+1,self.col+1, self.row_dim, self.col_dim,
                                     {'type':'cell','criteria': '=','value': 0,'format':self.pct_fmt})
        
class setMVSheet(setHistReturnSheet):
    def __init__(self, writer, data, sheet_name='market_values'):
        """
        Create excel sheet for historical market values

        Parameters
        ----------
        writer : ExcelWriter
        data : dataframe
            Market value dataframe.
        sheet_name : string, optional
            Excel sheet name. The default is 'Market Values'.
        row : int, optional
            Row index number. The default is 0.
        col : int, optional
            Column index number. The default is 0.

        Returns
        -------
        Market Values excel sheet.
        """
        setHistReturnSheet.__init__(self, writer, data, sheet_name)
        
    def format_worksheet_data(self):
        #format market values with ccy_fmt
        self.worksheet.conditional_format(self.row+1,self.col+1, self.row_dim, 
                                          self.col_dim,{'type':'no_blanks','format':self.ccy_fmt})

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
        self.pct_fmt_neg = self.workbook.add_format({'num_format': '0.00%','bold':False,
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
        

class setDataframeSheet(setSheet):
    def __init__(self, writer, data, sheet_name):
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
        self.row_dim = self.row + self.data.shape[0]
        self.col_dim = self.col + self.data.shape[1]
        self.data.to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row , startcol=self.col)   
        self.format_worksheet_data()
                
    def format_worksheet_data(self):
        pass

class SetDataDictSheet(setSheet):
    def __init__(self, writer, data_dict, sheet_name, spaces=3):
        """
        Create Excel sheet for grouped data

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        quintile_df : DataFrame
            DataFrame for quintile data.
        decile_df : DataFrame
            DataFrame for decile data.
        sheet_name : str, optional
            Excel sheet name. Default is 'Grouped Data'.
        spaces : int, optional
            Number of empty rows between data sections. Default is 3.
        """
        setSheet.__init__(writer, sheet_name,row = 2, col = 1, col_width=22)
        self.title_list = data_dict['title_list']
        self.df_list = data_dict['df_list']
        self.spaces = spaces
        self.format_worksheet_data()
                
    def format_worksheet_data(self):
        pass
                
class setHistReturnSheet(setDataframeSheet):
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
        setDataframeSheet.__init__(self, writer, data, sheet_name)
        #freeze panes
        self.worksheet.freeze_panes(self.row+1, self.col+1)
        
        #format dates with date_fmt (first column)
        self.worksheet.conditional_format(self.row,self.col, self.row_dim, 
                                          self.col,{'type':'no_blanks','format':self.date_fmt})
                
    def format_worksheet_data(self):
        #format negative returns with pct_fmt_neg
        self.worksheet.conditional_format(self.row+1,self.col+1, self.row_dim, self.col_dim,
                                         {'type':'cell','criteria': '<','value': 0,'format':self.pct_fmt_neg})
        #format zero or positive returns with pct_fmt
        self.worksheet.conditional_format(self.row+1,self.col+1, self.row_dim, self.col_dim,
                                     {'type':'cell','criteria': '>=','value': 0,'format':self.pct_fmt})
        
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

#TODO: use setDataframeSheet instead of setSheet
class SetVRRSheet(setSheet):
    def __init__(self, writer, df, sheet_name):
        """
        Create Excel sheet for VRR returns

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        df : DataFrame
            Returns DataFrame.
        sheet_name : str
            Excel sheet name.
        """
        #TODO:I created setDataframeSheet to include data as variable when initializing, so include df
        #TODO: use setDataframeSheet instead of setSheet
        setSheet.__init__(self, writer, sheet_name)
        #TODO: I created setDataframeSheet to include the next 4 lines so you can remove them
        self.data = df
        self.row_dim = self.row + self.data.shape[0]
        self.col_dim = self.col + self.data.shape[1]
        self.data.to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row, startcol=self.col)
        #TODO: Move the digits_fmt to setSheet and rename as digits_fmt_2, 
        self.digits_fmt = formats.set_number_format(self.workbook, num_format='0.000000')  # Override digits_fmt
        #TODO: no need to call this again, inherited from setDataframeSheet
        self.format_worksheet_data()

    #TODO:Update the digits_format to digits_format_2 
    def format_worksheet_data(self):
        #  formatting for columns 1-3 using digits format
        self.worksheet.conditional_format(
            self.row + 1, self.col + 1, self.row_dim, self.col + 3,
            {'type': 'no_blanks', 'format': self.digits_fmt}
        )

        # formatting for column 4 using int format
        self.worksheet.conditional_format(
            self.row + 1, self.col + 4, self.row_dim, self.col + 4,
            {'type': 'no_blanks', 'format': self.int_fmt}
        )

        # formatting for columns 5 and onwards using digits format
        self.worksheet.conditional_format(
            self.row + 1, self.col + 5, self.row_dim, self.col_dim,
            {'type': 'no_blanks', 'format': self.digits_fmt}
        )

        # formatting for the first column using date format
        self.worksheet.conditional_format(
            self.row, self.col, self.row_dim, self.col,
            {'type': 'no_blanks', 'format': self.date_fmt}
        )

#TODO: I've updated sheets.set_grouped_data_sheet(), it now takes in a data_dict instead of quintile_df and decile_df
#TODO: Take a look at it and edit this
#TODO: Also use setDataDictSheet instead of setSheet
class SetGroupedDataSheet(setSheet):
    def __init__(self, writer, quintile_df, decile_df, sheet_name='Grouped Data', spaces=3):
        """
        Create Excel sheet for grouped data

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        quintile_df : DataFrame
            DataFrame for quintile data.
        decile_df : DataFrame
            DataFrame for decile data.
        sheet_name : str, optional
            Excel sheet name. Default is 'Grouped Data'.
        spaces : int, optional
            Number of empty rows between data sections. Default is 3.
        """
        #TODO: use setDataDictSheet instead of setSheet
        setSheet.__init__(writer, sheet_name,row = 2, col = 1, col_width=22)
        #TODO: no need for the next 5 lines if inheriting setDataDictSheet
        self.quintile_df = quintile_df
        self.decile_df = decile_df
        self.title_list = ['Quintile','Decile']
        self.df_list = [self.quintile_df,self.decile_df]
        self.spaces = spaces
        #TODO: no need to call this again, inherited from setSheet
        self.title_format = formats.set_title_format(self.workbook)
        #TODO: no need to call this again, inherited from setSheet
        self.pct_fmt = formats.set_number_format(self.workbook, num_format='0.00%')

    def format_worksheet_data(self):
        for n in range(0,len(self.df_list)):
            try:
                row_dim = self.row + self.df_list.shape[0]
                col_dim = self.col + self.df_list.shape[1]
                self.worksheet.write(self.row - 1, 1, self.title_list[n], self.title_format)
                #write data into worksheet
                self.df_list[n].to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row, startcol=1)
                
            except AttributeError:
                pass
            
            if n == 1:
                   self.worksheet.conditional_format(
            self.row + 1, self.col + 1, row_dim, col_dim, {'type': 'no_blanks', 'format': self.pct_fmt}
        )
            else:
                    self.worksheet.conditional_format(
            self.row + 1, self.col + 1, row_dim, col_dim, {'type': 'no_blanks', 'format': self.pct_fmt}
        )
                    self.row = row_dim + self.spaces + 1

#TODO: I've updated sheets.set_corr_rank_sheet(), it now takes in a data_dict (corr_data_dict) instead of corr_pack
#TODO: Take a look at it and edit this
#TODO: Also use setDataDictSheet instead of setSheet
class SetCorrRankSheet(setSheet):
    def __init__(self, writer, corr_pack, dates, sheet_name='Correlations Ranks', spaces=3):
        """
        Create Excel sheet for correlation ranks

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        corr_pack : dict
            Dictionary containing correlation ranks.
        dates : dict
            Dictionary containing start and end dates.
        sheet_name : str, optional
            Excel sheet name. Default is 'Correlations Ranks'.
        spaces : int, optional
            Number of empty rows between data sections. Default is 3.
        """
        #TODO: use setDataDictSheet instead of setSheet
        setSheet.__init__(writer, sheet_name,row=3,col=1,col_width=19)
        self.dates = dates
        self.header = 'Data from {} to {}'.format(str(dates['start']).split()[0], str(dates['end']).split()[0])
        #TODO: no need for the next 4 lines if inheriting setDataDictSheet
        self.corr_pack = corr_pack
        self.spaces = spaces
        self.title_list = []
        self.corr_list = []
        
        #TODO: NO need for the for loop to unpack corr_pack
        # Unpack corr_pack
        for i in corr_pack:
            self.title_list.append(corr_pack[str(i)][1])
            self.corr_list.append(corr_pack[str(i)][0])

        #TODO no need to define self.title_format and self.digit, inherited from setSheet (it's the same)
        self.title_format = formats.set_title_format(self.workbook)
        self.digits_fmt = formats.set_number_format(self.workbook, num_format='0.00')

    def format_worksheet_data(self):
        #TODO: Why are you defining worksheet, why not just use self.worksheet?
        worksheet = self.worksheet
        worksheet.write(0, 0, self.header, self.title_format)
        #TODO no need to define row and col, use self.row and self.col inherited from setSheet (it's the same)
        row = 3
        col = 1

        for n in range(len(self.corr_list)):
            try:
                #TODO: Use self.row and self.col, unless I'm missing something
                row_dim = row + self.corr_list[n].shape[0]
                col_dim = col + self.corr_list[n].shape[1]
                worksheet.write(row-1, 1, self.title_list[n], self.title_format)
                self.corr_list[n].to_excel(self.writer, sheet_name=self.sheet_name, startrow=row, startcol=1)
                worksheet.conditional_format(
                    row+1, col+1, row_dim, col_dim, {'type': 'duplicate', 'format': self.digits_fmt}
                )
                worksheet.conditional_format(row+1, col+1, row_dim, col_dim, {'type': '3_color_scale'})
                row = row_dim + self.spaces + 1
            except AttributeError:
                pass
                    
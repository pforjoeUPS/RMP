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
        self.digits_fmt2 = formats.set_number_format(self.workbook, num_format='0.000000')
        #currency format
        self.ccy_fmt = formats.set_number_format(self.workbook,num_format='$#,##0.00')
        
        #int format
        self.int_fmt = formats.set_number_format(self.workbook, num_format='0')
        

class setDataframeSheet(setSheet):
    def __init__(self, writer, data, sheet_name, **kwargs):
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
        setSheet.__init__(self, writer, sheet_name, **kwargs)
        
        self.data = data
        self.row_dim = self.row + self.data.shape[0]
        self.col_dim = self.col + self.data.shape[1]
        self.data.to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row , startcol=self.col)   
        self.format_worksheet_data()
                
    def format_worksheet_data(self):
        pass

class SetDataDictSheet(setSheet):
    def __init__(self, writer, data_dict, sheet_name, spaces=3, **kwargs):
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
        setSheet.__init__(self, writer, sheet_name, **kwargs)
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
class SetVRRSheet(setDataframeSheet):
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
        setDataframeSheet.__init__(self, writer, df, sheet_name)        
       
    def format_worksheet_data(self):
        #  formatting for columns 1-3 using digits format
        self.worksheet.conditional_format(
            self.row + 1, self.col + 1, self.row_dim, self.col + 3,
            {'type': 'no_blanks', 'format': self.digits_fmt2}
        )

        # formatting for column 4 using int format
        self.worksheet.conditional_format(
            self.row + 1, self.col + 4, self.row_dim, self.col + 4,
            {'type': 'no_blanks', 'format': self.int_fmt}
        )

        # formatting for columns 5 and onwards using digits format
        self.worksheet.conditional_format(
            self.row + 1, self.col + 5, self.row_dim, self.self.col_dim,
            {'type': 'no_blanks', 'format': self.digits_fmt2}
        )

        # formatting for the first column using date format
        self.worksheet.conditional_format(
            self.row, self.col, self.row_dim, self.col,
            {'type': 'no_blanks', 'format': self.date_fmt}
        )


class setGroupedDataSheet(SetDataDictSheet):
    def __init__(self, writer, data_dict, sheet_name='Grouped Data', spaces=3):
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
        
        SetDataDictSheet.__init__(self, writer, data_dict, sheet_name, row =2, col =1, col_width = 22)
        self.data_dict = data_dict
        self.spaces = spaces
       

    def format_worksheet_data(self):
        for n in range(0,len(self.df_list)):
            try:
                self.row_dim = self.row + self.df_list[n].shape[0]
                self.col_dim = self.col + self.df_list[n].shape[1]
                self.worksheet.write(self.row - 1, 1, self.title_list[n], self.title_format)
                #write data into worksheet
                self.df_list[n].to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row, startcol=1)
                
            except AttributeError:
                pass
            
            if n == 1:
                   self.worksheet.conditional_format(
            self.row + 1, self.col + 1, self.row_dim, self.col_dim, {'type': 'no_blanks', 'format': self.pct_fmt}
        )
            else:
                    self.worksheet.conditional_format(
            self.row + 1, self.col + 1, self.row_dim, self.col_dim, {'type': 'no_blanks', 'format': self.pct_fmt}
        )
                    self.row = self.row_dim + self.spaces + 1


class SetCorrRankSheet(SetDataDictSheet):
    def __init__(self, writer, corr_data_dict, dates, sheet_name='Correlations Ranks', spaces=3):
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
        self.dates = dates
        self.header = 'Data from {} to {}'.format(str(dates['start']).split()[0], str(dates['end']).split()[0])
        SetDataDictSheet.__init__(self, writer, corr_data_dict, sheet_name, spaces, row = 3, col = 1, col_width = 19)
        
        
    def format_worksheet_data(self):
        self.worksheet.write(0, 0, self.header, self.title_format)     
        for n in range(len(self.df_list)):
            try:
                
                self.row_dim = self.row + self.df_list[n].shape[0]
                self.col_dim = self.col + self.df_list[n].shape[1]
                self.worksheet.write(self.row-1, 1, self.title_list[n], self.title_format)
                self.df_list[n].to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row, startcol=1)
                self.worksheet.conditional_format(
                self.row + 1, self.col + 1, self.row_dim, self.col_dim, {'type': 'duplicate', 'format': self.digits_fmt}
            )
                self.worksheet.conditional_format(self.row+1, self.col+1, self.row_dim, self.col_dim, {'type': '3_color_scale'})
                self.row = self.row_dim + self.spaces + 1
            except AttributeError:
                pass
                    
class setHistSheet(setDataframeSheet):
    def __init__(self, writer, df_hist, sheet_name='Historical Sell-offs', spaces=3):
        """
        Create Excel sheet for historical selloffs

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        df_hist : DataFrame
            DataFrame containing historical data.
        sheet_name : str, optional
            Excel sheet name. Default is 'Historical Sell-offs'.
        spaces : int, optional
            Number of empty rows between data sections. Default is 3.
        """
        self.spaces = spaces
        
        setDataframeSheet.__init__(self, writer, df_hist, sheet_name, row =2, col = 1, col_width = 30)
       
        
        
    def format_worksheet_data(self):
      self.worksheet.write(self.row - 1, 1, self.sheet_name, self.title_format)
        # Formatting for dates
      self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col + 2, {'type': 'no_blanks', 'format': self.date_fmt})
      # Formatting equity returns
      self.worksheet.conditional_format(self.row + 1, self.col + 3, self.row_dim, self.col + 3, {'type': 'no_blanks', 'format': self.pct_fmt})
      # Formatting strat returns
      self.worksheet.conditional_format(self.row + 1, self.col + 4, self.row_dim, self.col_dim, {'type': 'cell', 'criteria': '<', 'value': 0, 'format': self.pct_fmt_neg})
      self.worksheet.conditional_format(self.row + 1, self.col + 4, self.row_dim, self.col_dim, {'type': 'cell', 'criteria': '>', 'value': 0, 'format': self.pct_fmt_pos})

class AnalysisSheet(SetDataDictSheet):
    def __init__(self, writer, data_dict, sheet_name = 'Monthly Analysis', spaces=3):
        """
        Create an excel sheet with:
        - Correlation Matrices
        - Portfolio Weightings
        - Return Statistics
        - Hedge Metrics

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        data_dict : dict
            Dictionary containing lists of DataFrames and title strings.
        sheet_name : str
            Excel sheet name.
        spaces : int, optional
            Number of empty rows between data sections. Default is 3.
        """
        #setSheet.__init__(writer, sheet_name, row=2, col=1, col_width=22)
        self.data_dict = data_dict
        self.spaces = spaces
        SetDataDictSheet.__init__(self, writer, data_dict, sheet_name, row=2, col=1, col_width=22)
        
        
        

    def format_worksheet_data(self):
  
        
        for n in range(0, len(self.df_list)):
          try:  
            self.row_dim = self.row + self.df_list[n].shape[0]
            self.col_dim = self.col + self.df_list[n].shape[1]
            self.worksheet.write(self.row-1, 1, self.title_list[n], self.title_format)
            self.df_list[n].to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row , startcol=1)
          except AttributeError:
             pass
         
          if n < 3:
                    self.worksheet.conditional_format(self.row+1, self.col+1, self.row_dim, self.col_dim, {'type': 'duplicate',
                                                                                               'format': self.digits_fmt})
                    self.worksheet.conditional_format(self.row+1, self.col+1, self.row_dim, self.col_dim, {'type': '3_color_scale'})

          elif n == 3 and len(self.df_list[n]) != 0:
                    self.worksheet.conditional_format(self.row+1, self.col+1, self.row+1, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.ccy_fmt})
                    self.worksheet.conditional_format(self.row +2, self.col+1,self.row_dim, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.pct_fmt})

          elif n == 4:
                   #format ann. ret and ann. vol to percent
                   self.worksheet.conditional_format(self.row+1, self.col + 1,self.row + 1, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.pct_fmt})
                   #format ret/vol to digits
                   self.worksheet.conditional_format(self.row +3, self.col + 1, self.row + 3, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.digits_fmt})
                   #format max_dd to percent
                   self.worksheet.conditional_format(self.row + 4, self.col + 1, self.row + 4, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.pct_fmt})
                   #format ret/dd to digits
                   self.worksheet.conditional_format(self.row + 5, self.col + 1, self.row + 5, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.digits_fmt})
                   #format max_1m_dd to percent
                   self.worksheet.conditional_format(self.row + 6, self.col + 1, self.row + 6, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.pct_fmt})
                   #format max_1m_dd date to date
                   #TODO: figure out a way to format date to short date
                   self.worksheet.conditional_format(self.row + 7, self.col + 1, self.row + 7, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.date_fmt_2})
                   #format ret_max1m_dd to digits
                   self.worksheet.conditional_format(self.row + 8, self.col + 1, self.row + 8, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.digits_fmt})

                   #format max_3m_dd to percent
                   self.worksheet.conditional_format(self.row + 9, self.col + 1, self.row + 9, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.pct_fmt})
                   #format max_3m_dd date to date
                   #TODO: figure out a way to format date to short date
                   self.worksheet.conditional_format(self.row + 10, self.col + 1, self.row + 10, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.date_fmt_2})

                   #format ret_max1q_dd to digit
                   self.worksheet.conditional_format(self.row + 11, self.col + 1, self.row + 11, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.digits_fmt})

                   #format skew to digits and avg_pos_ret/avg_neg_ret to digits
                   self.worksheet.conditional_format(self.row + 12, self.col + 1, self.row + 13, self.col_dim,
                                                     {'type': 'no_blanks', 'format': self.digits_fmt})
                    #format downside dev to percent
                   self.worksheet.conditional_format(self.row+14,self.col+1, self.row+14, self.col_dim,{'type':'no_blanks',
                                              'format':self.pct_fmt})
                    #format sortino to digits
                   self.worksheet.conditional_format(self.row+15,self.col+1, self.row+15, self.col_dim,{'type':'no_blanks',
                                              'format':self.digits_fmt})
             #format hedge metrics      
          else:                     # format benefit count to int
                    self.worksheet.conditional_format(self.row+1, self.col + 1, self.row+1, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.int_fmt})
                    # format benefit mean and median to percent
                    self.worksheet.conditional_format(self.row + 2, self.col + 1, self.row + 3, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.pct_fmt})

                    # format benefit cumulative to percent
                    self.worksheet.conditional_format(self.row + 4, self.col + 1, self.row + 4, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.pct_fmt})

                    # format reliability up and down to digits
                    self.worksheet.conditional_format(self.row + 5, self.col + 1, self.row + 6, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.digits_fmt})

                    # format convexity count to int
                    self.worksheet.conditional_format(self.row + 7, self.col + 1, self.row + 7, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.int_fmt})

                    # format convexity mean and median to percent
                    self.worksheet.conditional_format(self.row + 8, self.col + 1, self.row + 9, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.pct_fmt})

                    # format convexity cumulative to percent
                    self.worksheet.conditional_format(self.row + 10, self.col + 1, self.row + 10, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.pct_fmt})

                    # format cost count to int
                    self.worksheet.conditional_format(self.row + 11, self.col + 1, self.row + 11, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.int_fmt})

                    # format cost mean and median to percent
                    self.worksheet.conditional_format(self.row + 12, self.col + 1, self.row + 13, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.pct_fmt})

                    # format cost cumulative to percent
                    self.worksheet.conditional_format(self.row + 14, self.col + 1, self.row + 14, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.pct_fmt})

                    # format decay days to int
                    self.worksheet.conditional_format(self.row + 15, self.col + 1, self.row + 17, self.col_dim,
                                                      {'type': 'no_blanks', 'format': self.int_fmt})
  
                 
          self.row = self.row_dim + self.spaces + 1
         


    

    
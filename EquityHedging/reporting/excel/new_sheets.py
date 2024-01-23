# -*- coding: utf-8 -*-
"""
Created on Fri July  7 2023

@author: Powis Forjoe, Maddie Choi, Devang Ajmera
"""

import pandas as pd

from . import formats
from ...datamanager import data_manager_new as dm


class setSheet:
    def __init__(self, writer, sheet_name, row=0, col=0, first_col=0, last_col=1000, col_width=22, freeze=False):
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
        self.freeze = freeze
        self.cell_format = formats.set_worksheet_format(self.workbook)
        self.index_format = formats.set_index_format(self.workbook)
        self.df_empty = pd.DataFrame()
        self.df_empty.to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row, startcol=self.col)
        self.worksheet = self.writer.sheets[self.sheet_name]
        # self.worksheet.set_column(first_col, first_col, 11, self.cell_format)
        # self.worksheet.set_column(first_col+1, first_col+1, 30, self.index_format)
        self.worksheet.set_column(first_col, last_col, col_width, self.cell_format)

        # pct format
        self.pct_fmt = formats.set_number_format(self.workbook, num_format='0.00%')

        # percent format with dark red text.
        self.pct_fmt_neg = self.workbook.add_format({'num_format': '0.00%', 'bold': False,
                                                     'font_color': '#9C0006'})

        # percent format with dark green text.
        self.pct_fmt_pos = self.workbook.add_format({'num_format': '0.00%',
                                                     'bold': False,
                                                     'font_color': '#006100'})

        # date format
        self.date_fmt = formats.set_number_format(self.workbook, num_format='mm/dd/yyyy')
        self.date_fmt_dd = formats.set_number_format(self.workbook, num_format='d mmmm yyyy')
        self.date_fmt_mm = formats.set_number_format(self.workbook, num_format='mmm yyyy')
        self.date_fmt_yy = formats.set_number_format(self.workbook, num_format='yyyy')

        # title format
        self.title_format = formats.set_title_format(self.workbook)

        # digits format
        self.digits_fmt = formats.set_number_format(self.workbook, num_format='0.00')
        self.digits_fmt2 = formats.set_number_format(self.workbook, num_format='0.000000')
        # currency format
        self.ccy_fmt = formats.set_number_format(self.workbook, num_format='$#,##0.00')

        # int format
        self.int_fmt = formats.set_number_format(self.workbook, num_format='0')


class dataFrameSheet(setSheet):
    def __init__(self, writer, data_df, sheet_name, index=True, **kwargs):
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
        super().__init__(writer, sheet_name, **kwargs)

        self.index = index
        self.data_df = data_df
        self.row_dim = self.row + self.data_df.shape[0]
        self.col_dim = self.col + self.data_df.shape[1]
        # self.format_worksheet_data()
        # self.conditional_worksheet_format()

    def create_sheet(self):
        print(f'Creating {self.sheet_name} sheet')
        self.format_worksheet_data()
        self.conditional_worksheet_format()

    def format_worksheet_data(self):
        try:
            self.data_df.to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row,
                                  startcol=self.col, index=self.index)
        except AttributeError:
            pass

    def conditional_worksheet_format(self):
        pass


# TODO: rethink data_dict, use key-value pairs
class dataDictSheet(setSheet):
    def __init__(self, writer, data, sheet_name, spaces=3, **kwargs):

        super().__init__(writer, sheet_name, **kwargs)
        self.data = self.check_if_dict(data)
        self.spaces = spaces
        self.row_dim = 0
        self.col_dim = 0
        # self.format_worksheet_data()

        # self.format_worksheet_data()
        # self.conditional_worksheet_format()

    def create_sheet(self):
        print(f'Creating {self.sheet_name} sheet')
        self.format_worksheet_data()
        self.conditional_worksheet_format()

    def check_if_dict(self, data):
        if type(data) == dict:
            return data
        else:
            return print('The data tyoe is NOT a dictionary!,Please use a data dictionary for this class')
            # return data

    def format_worksheet_data(self):
        for key in self.data:
            self.set_worksheet(self.data, key, title=key)
            self.conditional_worksheet_format()

    def set_worksheet(self, data_dict, key, title):
        pass

    def conditional_worksheet_format(self):
        pass


# TODO: test
class tsDataDictSheet(dataDictSheet):
    def __init__(self, writer, data, sheet_name, **kwargs):

        super().__init__(writer, data, sheet_name, **kwargs)

    def check_if_dict(self, data):
        if type(data) == dict:
            return data
        else:
            return {self.get_data_freq(data): data}

    def get_data_freq(self, data):
        freq = data.index.inferred_freq[0]
        return dm.switch_freq_string(freq)


class histReturnSheet(dataFrameSheet):
    def __init__(self, writer, returns_df, sheet_name='Monthly Historical Returns', freeze=True):
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
        super().__init__(writer, returns_df, sheet_name, freeze=freeze)

    def format_worksheet_data(self):
        try:
            self.data_df.to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row,
                                  startcol=self.col, index=self.index)
        except AttributeError:
            pass

        # freeze panes
        if self.freeze:
            self.worksheet.freeze_panes(self.row + 1, self.col + 1)

    def conditional_worksheet_format(self):
        # format dates with date_fmt (first column)
        self.worksheet.conditional_format(self.row, self.col, self.row_dim, self.col,
                                          {'type': 'no_blanks', 'format': self.date_fmt})
        # format negative returns with pct_fmt_neg
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '<', 'value': 0, 'format': self.pct_fmt_neg})
        # format zero or positive returns with pct_fmt
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': self.pct_fmt})


class mktValueSheet(histReturnSheet):
    def __init__(self, writer, data_df, sheet_name='market_values', freeze=True):
        """
        Create excel sheet for historical market values

        Parameters
        ----------
        writer : ExcelWriter
        data_df : dataframe
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
        super().__init__(writer, data_df, sheet_name, freeze)

    def conditional_worksheet_format(self):
        # format market values with ccy_fmt
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.ccy_fmt})


class ratioSheet(histReturnSheet):
    def __init__(self, writer, data_df, sheet_name, freeze=True):
        """
        Create excel sheet for historical market values

        Parameters
        ----------
        writer : ExcelWriter
        data_df : dataframe
            Market value dataframe.
        sheet_name : string, optional
            Excel sheet name. The default is 'Market Values'.
        
        Returns
        -------
        ratio excel sheet.
        """
        super().__init__(writer, data_df, sheet_name, freeze)

    def conditional_worksheet_format(self):
        # format market values with 2 digits format
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})


class histSelloffSheet(dataFrameSheet):
    def __init__(self, writer, hist_df, sheet_name='Historical Sell-offs'):
        """
        Create Excel sheet for historical selloffs

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        hist_df : DataFrame
            DataFrame containing historical data.
        sheet_name : str, optional
            Excel sheet name. Default is 'Historical Sell-offs'.
        spaces : int, optional
            Number of empty rows between data sections. Default is 3.
        """
        # self.spaces = spaces
        super().__init__(writer, hist_df, sheet_name, row=2, col=1, col_width=30)

    def conditional_worksheet_format(self):
        self.worksheet.write(self.row - 1, 1, self.sheet_name, self.title_format)
        # Formatting for dates
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col + 2,
                                          {'type': 'no_blanks', 'format': self.date_fmt_dd})
        # Formatting equity returns
        self.worksheet.conditional_format(self.row + 1, self.col + 3, self.row_dim, self.col + 3,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # Formatting strat returns
        self.worksheet.conditional_format(self.row + 1, self.col + 4, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '<', 'value': 0, 'format': self.pct_fmt_neg})
        self.worksheet.conditional_format(self.row + 1, self.col + 4, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '>', 'value': 0, 'format': self.pct_fmt_pos})


class drawdownSheet(dataFrameSheet):
    def __init__(self, writer, drawdown_df, sheet_name='Drawdown Statistics', freq='1M'):
        self.freq = freq
        super().__init__(writer, drawdown_df, sheet_name, row=2, col=1, col_width=30, index=False)

    def switch_date_fmt(self, arg):
        """
        Return an integer equivalent to frequency in years
        
        Parameters:
        arg -- string ('1D', '1W', '1M')
        
        Returns:
        int of frequency in years
        """
        switcher = {
            "1D": self.date_fmt_dd,
            "1W": self.date_fmt_dd,
            "1M": self.date_fmt_mm,
            "1Q": self.date_fmt_mm,
            "1Y": self.date_fmt_yy,
        }
        return switcher.get(arg, self.date_fmt_dd)

    def conditional_worksheet_format(self):
        self.worksheet.write(self.row - 1, self.col, self.sheet_name, self.title_format)

        # format for dates
        self.worksheet.conditional_format(self.row + 1, self.col, self.row_dim, self.col + 2,
                                          {'type': 'no_blanks', 'format': self.switch_date_fmt(self.freq)})
        # format dd
        self.worksheet.conditional_format(self.row + 1, self.col + 3, self.row_dim, self.col + 3,
                                          {'type': 'no_blanks', 'format': self.pct_fmt_neg})
        # format length and recovery
        self.worksheet.conditional_format(self.row + 1, self.col + 4, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.int_fmt})


# TODO: rewrite using analytics and dm classes
class altsReturnStatsSheet(dataFrameSheet):
    def __init__(self, writer, ret_stat_df, sheet_name='Returns Statistics', include_fi=False, include_bmk=False):
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
        self.include_fi = include_fi
        self.include_bmk = include_bmk
        super().__init__(writer, ret_stat_df, sheet_name, row=2, col=1, freeze=True)

    def conditional_worksheet_format(self):
        jump_0 = 0
        jump_1 = 0
        jump_2 = 0
        jump_3 = 0
        jump_4 = 0
        if self.include_bmk and self.include_fi:
            jump_0 = 1
            jump_1 = jump_0 + 2
            jump_2 = jump_1 + 4
            jump_3 = jump_2 + 2
            jump_4 = jump_3 + 2
        elif self.include_fi:
            jump_1 = jump_0 + 1
            jump_2 = jump_1 + 3
            jump_3 = jump_2
            jump_4 = jump_3
        elif self.include_bmk:
            jump_0 = 1
            jump_1 = jump_0 + 1
            jump_2 = jump_1 + 1
            jump_3 = jump_2 + 2
            jump_4 = jump_3 + 2

        if self.include_bmk:
            self.worksheet.freeze_panes(self.row + 2, self.col + 1)
        else:
            self.worksheet.freeze_panes(self.row + 1, self.col + 1)

        # format for return stats
        # format (ann_ret, excess_ret, alphas) to percent
        self.worksheet.conditional_format(self.row + 1 + jump_0, self.col + 1, self.row + 2 + jump_1, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format betas to digits
        self.worksheet.conditional_format(self.row + 3 + jump_1, self.col + 1, self.row + 5 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format returns (med, avg) to percent
        self.worksheet.conditional_format(self.row + 6 + jump_2, self.col + 1, self.row + 9 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format avg_pos_ret to avg_neg_ret ratio to digits
        self.worksheet.conditional_format(self.row + 10 + jump_2, self.col + 1, self.row + 10 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format min, max, vols to percent
        self.worksheet.conditional_format(self.row + 11 + jump_2, self.col + 1, self.row + 17 + jump_3, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format up/dwn dev ratio, skew, kurt to digits
        self.worksheet.conditional_format(self.row + 18 + jump_3, self.col + 1, self.row + 20 + jump_3, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format max_dd to percent
        self.worksheet.conditional_format(self.row + 21 + jump_3, self.col + 1, self.row + 21 + jump_3, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format ret/vol, ir, sortino, ret/dd ratios to digits
        self.worksheet.conditional_format(self.row + 22 + jump_3, self.col + 1, self.row + 24 + jump_4, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format mctr to percent
        self.worksheet.conditional_format(self.row + 25 + jump_4, self.col + 1, self.row + 25 + jump_4, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})


# Done
# TODO: rewrite using analytics and dm classes
class stratAltsReturnStatsSheet(altsReturnStatsSheet):
    def __init__(self, writer, ret_stat_df, sheet_name='Returns Statistics', include_fi=False):
        super().__init__(writer, ret_stat_df, sheet_name, include_fi=include_fi)

    def conditional_worksheet_format(self):
        jump_1 = 0
        jump_2 = jump_1
        jump_3 = jump_2 + 1
        jump_4 = jump_3 + 1

        if self.include_fi:
            jump_1 = 1
            jump_2 = jump_1 + 3

        self.worksheet.write(self.row - 1, 1, self.sheet_name, self.title_format)

        # format for return stats
        # format (ann_ret, excess_ret, alphas) to percent
        self.worksheet.conditional_format(self.row + 3, self.col + 1, self.row + 5 + jump_1, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format betas to digits
        self.worksheet.conditional_format(self.row + 5 + jump_1, self.col + 1, self.row + 9 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format returns (med, avg) to percent
        self.worksheet.conditional_format(self.row + 10 + jump_2, self.col + 1, self.row + 13 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format avg_pos_ret to avg_neg_ret ratio to digits
        self.worksheet.conditional_format(self.row + 14 + jump_2, self.col + 1, self.row + 14 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format avg_pos_ret to avg_neg_ret ratio to pct
        self.worksheet.conditional_format(self.row + 15 + jump_2, self.col + 1, self.row + 23 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format up_down_dev ratio, skew, kurt to digits
        self.worksheet.conditional_format(self.row + 24 + jump_2, self.col + 1, self.row + 26 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format max_dd to percent
        self.worksheet.conditional_format(self.row + 27 + jump_2, self.col + 1, self.row + 27 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format ret/vol, ir, sortino, ret/dd ratios to digits
        self.worksheet.conditional_format(self.row + 28 + jump_2, self.col + 1, self.row + 32 + jump_2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})

# TODO: rewrite using analytics and dm classes
class histReturnMTDYTDSheet(dataDictSheet):
    def __init__(self, writer, returns_data, sheet_name='MTD-YTD-ITD'):
        super().__init__(writer, returns_data, sheet_name, col_width=10.67, spaces=2, row=1)

    def check_if_dict(self, data):
        if isinstance(data, dict):
            return data
        else:
            return {data.index.name: data}

    def format_worksheet_data(self):
        for key in self.data_dict:
            self.set_worksheet(key)
            self.conditional_worksheet_format()
            self.row = self.row_dim + self.spaces + 1

    def set_worksheet(self, key):
        try:
            self.row_dim = self.row + self.data_dict[key].shape[0]
            self.col_dim = self.col + self.data_dict[key].shape[1] + 1
            self.worksheet.write(self.row - 1, 0, f'{key} Return History', self.title_format)
            # write data into worksheet
            self.data_dict[key].to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row, startcol=self.col)
        except AttributeError:
            pass

    def conditional_worksheet_format(self):
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '<', 'value': 0, 'format': self.pct_fmt_neg})
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': self.pct_fmt})

# TODO: rewrite using analytics and dm classes
class corrStatsSheet(dataDictSheet):
    def __init__(self, writer, corr_data, sheet_name='Correlation Analysis', include_fi=False):
        """
        Create Excel sheet for correlation ranks

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        corr_data : dict
            Dictionary containing correlation matrices.
        sheet_name : str, optional
            Excel sheet name. Default is 'Correlation Analysis'.
        """
        super().__init__(writer, corr_data, sheet_name, row=2, col=1, freeze=True)

    def format_worksheet_data(self):
        if self.freeze:
            self.worksheet.freeze_panes(self.row + 1, self.col + 1)

        for key in self.data_dict:
            self.set_worksheet(key)
            self.conditional_worksheet_format()
            self.row = self.row_dim + self.spaces + 1

    def set_worksheet(self, key):
        try:
            self.row_dim = self.row + self.data_dict[key][0].shape[0]
            self.col_dim = self.col + self.data_dict[key][0].shape[1]
            self.worksheet.write(self.row - 1, 1, self.data_dict[key][1], self.title_format)

            # write data into worksheet
            self.data_dict[key][0].to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row,
                                            startcol=self.col)
        except AttributeError:
            pass

    def conditional_worksheet_format(self):
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format matrics using 3 color scale
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': '3_color_scale'})

class vrrSheet(dataFrameSheet):
    def __init__(self, writer, vrr_df, sheet_name):
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
        super().__init__(writer, vrr_df, sheet_name)

    def conditional_worksheet_format(self):
        #  formatting for columns 1-3 using digits format
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col + 3,
                                          {'type': 'no_blanks', 'format': self.digits_fmt2})

        # formatting for column 4 using int format
        self.worksheet.conditional_format(self.row + 1, self.col + 4, self.row_dim, self.col + 4,
                                          {'type': 'no_blanks', 'format': self.int_fmt})

        # formatting for columns 5 and onwards using digits format
        self.worksheet.conditional_format(self.row + 1, self.col + 5, self.row_dim, self.self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt2})

        # formatting for the first column using date format
        self.worksheet.conditional_format(self.row, self.col, self.row_dim, self.col,
                                          {'type': 'no_blanks', 'format': self.date_fmt})

# TODO:review
class quantileDataSheet(dataDictSheet):
    def __init__(self, writer, data_dict, sheet_name='Quantile Data', row=2, col=1, col_width=22):
        """
        Create Excel sheet for grouped data

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        data_dict: dictionary
        sheet_name : str, optional
            Excel sheet name. Default is 'Quantile Data'.
        """

        super().__init__(writer, data_dict, sheet_name, row=row, col=col, col_width=col_width)

    def format_worksheet_data(self):
        for key in self.data:
            self.set_worksheet(self.data, key, title=f'{key} Analysis')
            self.conditional_worksheet_format()
            self.row = self.row_dim + self.spaces + 1

    def set_worksheet(self, data_dict, key, title):
        try:
            self.row_dim = self.row + data_dict[key].shape[0]
            self.col_dim = self.col + data_dict[key].shape[1]
            self.worksheet.write(self.row - 1, 1, title, self.title_format)
            data_dict[key].to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row,
                                    startcol=self.col)
            # self.worksheet.set_column('B:B', 30, self.index_format)
        except AttributeError:
            pass

    def conditional_worksheet_format(self):
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})


# TODO: review
class analysisSheet(quantileDataSheet):
    def __init__(self, writer, data_dict, sheet_name='Monthly Analysis'):
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
        super().__init__(writer, data_dict, sheet_name)

    def format_worksheet_data(self):
        for key in self.data:
            if key == 'correlations':
                # format correlation matrices
                for corr_key in self.data[key]:
                    corr_title = self.data[key][corr_key]['title']
                    self.set_worksheet(self.data[key][corr_key], key='corr_df', title=corr_title)
                    self.conditional_corr_worksheet_format(corr_key)
                    self.row = self.row_dim + self.spaces + 1
            else:
                if key == 'weighting':
                    if self.data[key]['wgts_df'].empty is False:
                        weights_title = self.data[key]['title']
                        self.set_worksheet(self.data[key], key='wgts_df', title=weights_title)
                        self.conditional_port_worksheet_format()
                if key == 'return_stats':
                    # format return statistics
                    return_stats_title = self.data[key]['title']
                    self.set_worksheet(self.data[key], key='ret_stats_df', title=return_stats_title)
                    self.conditional_ret_stat_worksheet_format()
                if key == 'hedge_metrics':
                    # format hedge metrics
                    hedge_metrics_title = self.data[key]['title']
                    self.set_worksheet(self.data[key], key='hm_df', title=hedge_metrics_title)
                    self.conditional_hm_worksheet_format()
            self.row = self.row_dim + self.spaces + 1

    def conditional_corr_worksheet_format(self, corr_key):
        if corr_key == 'full':
            self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                              {'type': 'duplicate', 'format': self.digits_fmt})
        else:
            self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                              {'type': 'no_blanks', 'format': self.digits_fmt})
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': '3_color_scale'})

    def conditional_port_worksheet_format(self):
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row + 1, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.ccy_fmt})
        self.worksheet.conditional_format(self.row + 2, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})

    def conditional_ret_stat_worksheet_format(self):
        # format no. of obs
        self.worksheet.conditional_format(self.row + 2, self.col + 1, self.row + 2, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.int_fmt})

        # format ann. ret and ann. vol to percent
        self.worksheet.conditional_format(self.row + 3, self.col + 1, self.row + 4, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format ret/vol to digits
        self.worksheet.conditional_format(self.row + 5, self.col + 1, self.row + 5, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format max_dd to percent
        self.worksheet.conditional_format(self.row + 6, self.col + 1, self.row + 6, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format ret/dd to digits
        self.worksheet.conditional_format(self.row + 7, self.col + 1, self.row + 7, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format max_1m_dd to percent
        self.worksheet.conditional_format(self.row + 8, self.col + 1, self.row + 8, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format max_1m_dd date to date
        # TODO: figure out a way to format date to short date
        self.worksheet.conditional_format(self.row + 9, self.col + 1, self.row + 9, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.date_fmt})
        # format ret_max1m_dd to digits
        self.worksheet.conditional_format(self.row + 10, self.col + 1, self.row + 10, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})

        # format max_3m_dd to percent
        self.worksheet.conditional_format(self.row + 11, self.col + 1, self.row + 11, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format max_3m_dd date to date
        # TODO: figure out a way to format date to short date
        self.worksheet.conditional_format(self.row + 12, self.col + 1, self.row + 12, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.date_fmt})

        # format ret_max1q_dd to digit
        self.worksheet.conditional_format(self.row + 13, self.col + 1, self.row + 15, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})

        # format skew to digits and avg_pos_ret/avg_neg_ret to digits
        # self.worksheet.conditional_format(self.row + 12, self.col + 1, self.row + 13, self.col_dim,
        #                                   {'type': 'no_blanks', 'format': self.digits_fmt})
        # format downside dev to percent
        self.worksheet.conditional_format(self.row + 16, self.col + 1, self.row + 16, self.col_dim,
                                          {'type': 'no_blanks','format': self.pct_fmt})
        # format sortino to digits
        self.worksheet.conditional_format(self.row + 17, self.col + 1, self.row + 17, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format vaR and cvaR to percent
        self.worksheet.conditional_format(self.row + 18, self.col + 1, self.row + 19, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})

    def conditional_hm_worksheet_format(self):
        # format benefit count to int
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row + 1, self.col_dim,
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


# TODO: Review something's not right
class corrRankSheet(quantileDataSheet):
    def __init__(self, writer, corr_data, dates, sheet_name='Correlations Ranks'):
        """
        Create Excel sheet for correlation ranks

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        corr_data : dict
            Dictionary containing correlation ranks.
        dates : dict
            Dictionary containing start and end dates.
        sheet_name : str, optional
            Excel sheet name. Default is 'Correlations Ranks'.
        spaces : int, optional
            Number of empty rows between data sections. Default is 3.
        """
        self.dates = dates
        self.set_worksheet_header()
        super().__init__(writer, corr_data, sheet_name, row=3, col_width=19)

    def set_worksheet_header(self):
        start_date_string = str(self.dates['start']).split()[0]
        end_date_string = str(self.dates['end']).split()[0]
        header = f'Data from {start_date_string} to {end_date_string}'
        self.worksheet.write(0, 0, header, self.title_format)

    def conditional_worksheet_format(self):
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'duplicate', 'format': self.digits_fmt})
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': '3_color_scale'})

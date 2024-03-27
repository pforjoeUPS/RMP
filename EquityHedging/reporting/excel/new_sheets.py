# -*- coding: utf-8 -*-
"""
Created on Fri July 7, 2023

@author: Powis Forjoe, Maddie Choi, Devang Ajmera
"""

import pandas as pd

from . import formats
from ...datamanager import data_manager_new as dm


class SetSheet:
    def __init__(self, writer, sheet_name, row=0, col=0, first_col=0, last_col=1000, col_width=22, freeze=False):
        """
        Create default, formatted Excel spreadsheet

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
        self.sheet_name = self.format_sheet_name(sheet_name)
        self.workbook = self.writer.book
        self.row = row
        self.col = col
        self.freeze = freeze
        self.cell_format = formats.set_worksheet_format(self.workbook)
        self.index_format = formats.set_index_format(self.workbook)
        self.df_empty = pd.DataFrame()
        self.df_empty.to_excel(self.writer, sheet_name=self.sheet_name, startrow=self.row, startcol=self.col)
        self.worksheet = self.writer.sheets[self.sheet_name]
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

    def freeze_panes(self):
        if self.freeze:
            self.worksheet.freeze_panes(self.row + 1, self.col + 1)

    @staticmethod
    def format_sheet_name(sheet_name):
        diff = -(len(sheet_name) - 31) if len(sheet_name) > 31 else None
        return sheet_name[:diff]


class InfoSheet(SetSheet):
    def __init__(self, writer, sheet_name='Info Sheet', spaces=3):
        super().__init__(writer, sheet_name)
        self.spaces = spaces


class DataSheet(SetSheet):
    def __init__(self, writer, data, sheet_name, **kwargs):
        super().__init__(writer, sheet_name=sheet_name, **kwargs)
        self.data = data
        self.row_dim = 0
        self.col_dim = 0

    def create_sheet(self):
        print(f'Creating {self.sheet_name} sheet')
        self.format_worksheet_data()
        self.conditional_worksheet_format()

    def format_worksheet_data(self, **kwargs):
        pass

    def set_worksheet_title(self, **kwargs):
        pass

    def conditional_worksheet_format(self):
        self.get_conditional_worksheet_format()

    def get_conditional_worksheet_format(self):
        pass

    def conditional_ccy_worksheet_format(self):
        # format market values with 2 digits format
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.ccy_fmt})

    def conditional_digits_worksheet_format(self):
        # format market values with 2 digits format
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})

    def write_data_to_excel(self, **kwargs):
        pass

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

    def conditional_worksheet_date_format(self):
        # format dates with date_fmt (first column)
        self.worksheet.conditional_format(self.row, self.col, self.row_dim, self.col,
                                          {'type': 'no_blanks', 'format': self.date_fmt})

    def conditional_worksheet_pct_format(self):
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})

    def conditional_percent_worksheet_format(self):
        # format negative values with pct_fmt_neg
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '<', 'value': 0, 'format': self.pct_fmt_neg})
        # format zero or positive values with pct_fmt
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': self.pct_fmt})

    def conditional_hist_selloff_worksheet_format(self):
        # Formatting for dates
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col + 2,
                                          {'type': 'no_blanks', 'format': self.date_fmt_dd})
        # Formatting mkt returns
        self.worksheet.conditional_format(self.row + 1, self.col + 3, self.row_dim, self.col + 3,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # Formatting strat returns
        self.worksheet.conditional_format(self.row + 1, self.col + 4, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '<', 'value': 0, 'format': self.pct_fmt_neg})
        self.worksheet.conditional_format(self.row + 1, self.col + 4, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '>', 'value': 0, 'format': self.pct_fmt_pos})

    def conditional_dd_worksheet_format(self):
        # format for dates
        self.worksheet.conditional_format(self.row + 1, self.col, self.row_dim, self.col + 2,
                                          {'type': 'no_blanks', 'format': self.date_fmt})
        # format dd
        self.worksheet.conditional_format(self.row + 1, self.col + 3, self.row_dim, self.col + 3,
                                          {'type': 'no_blanks', 'format': self.pct_fmt_neg})
        # format length and recovery
        self.worksheet.conditional_format(self.row + 1, self.col + 4, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.int_fmt})


class DataFrameSheet(DataSheet):
    def __init__(self, writer, data, sheet_name, index=True, freeze=False, row=2, col=1, **kwargs):
        """
        Create Excel sheet for historical returns

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
        Historical returns Excel sheet.
        """
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, row=row, col=col, freeze=freeze, **kwargs)

        self.index = index
        self.title = sheet_name
        self.row_dim = self.row + self.data.shape[0]
        self.col_dim = self.col + self.data.shape[1]

    def format_worksheet_data(self):
        try:
            self.set_worksheet_title(row=self.row - 1, col=self.col)
            self.write_data_to_excel(start_row=self.row, start_col=self.col)
        except AttributeError:
            pass
        self.freeze_panes()

    def set_worksheet_title(self, row, col):
        self.worksheet.write(row, col, self.title, self.title_format)

    def write_data_to_excel(self, start_row, start_col):
        self.data.to_excel(self.writer, sheet_name=self.sheet_name, startrow=start_row,
                           startcol=start_col, index=self.index)


# TODO: rethink data_dict, use key-value pairs
class DataDictSheet(DataSheet):

    def __init__(self, writer, data, sheet_name, spaces=3, **kwargs):

        super().__init__(writer=writer, data=data, sheet_name=sheet_name, **kwargs)
        self.data = self.check_if_dict(data)
        self.spaces = spaces
        self.row_dim = 0
        self.col_dim = 0

    def create_sheet(self):
        print(f'Creating {self.sheet_name} sheet')
        self.freeze_panes()
        self.format_worksheet_data()

    def check_if_dict(self, data):
        if isinstance(data, dict):
            return data
        else:
            return print('The data type is NOT a dictionary!,Please use a data dictionary for this class')
            # return data

    def format_worksheet_data(self):
        for key in self.data:
            self.set_worksheet(data_df=self.data[key], row=self.row - 1, col=0, title=key)
            self.conditional_worksheet_format()
            self.update_row()

    def set_worksheet(self, data_df, row, col, title, index=True):
        try:
            self.set_worksheet_dims(data_df)
            self.set_worksheet_title(row, col, title)
            self.write_data_to_excel(data_df, start_row=self.row, start_col=self.col, index=index)
        except AttributeError:
            pass

    def set_worksheet_dims(self, data_df):
        self.row_dim = self.row + data_df.shape[0]
        self.col_dim = self.col + data_df.shape[1]

    def set_worksheet_title(self, row, col, title):
        self.worksheet.write(row, col, title, self.title_format)

    def write_data_to_excel(self, data_df, start_row, start_col, index=False):
        data_df.to_excel(self.writer, sheet_name=self.sheet_name, startrow=start_row,
                         startcol=start_col, index=index)

    def update_row(self):
        self.row = self.row_dim + self.spaces + 1


# TODO: test
class TSDataDictSheet(DataDictSheet):

    def __init__(self, writer, data, sheet_name, **kwargs):

        super().__init__(writer, data, sheet_name, **kwargs)

    def check_if_dict(self, data):
        if isinstance(data, dict):
            return data
        else:
            return {self.get_data_freq(data): data}

    @staticmethod
    def get_data_freq(data):
        freq = data.index.inferred_freq[0]
        return dm.switch_freq_string(freq)


class PercentSheet(DataFrameSheet):

    def __init__(self, writer, data, sheet_name='data'):
        """
        Create Excel sheet for historical returns

        Parameters
        ----------
        writer : ExcelWriter
        data : dataframe
            Returns dataframe.
        sheet_name : string, optional
            Excel sheet name. The default is 'data'.

        Returns
        -------
        Historical returns Excel sheet.
        """
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, freeze=True, row=0, col=0)

    def set_worksheet_title(self, row, col):
        pass

    def get_conditional_worksheet_format(self):
        self.conditional_worksheet_date_format()
        self.conditional_percent_worksheet_format()


class MktValueSheet(PercentSheet):

    def __init__(self, writer, data, sheet_name='market_values'):
        """
        Create Excel sheet for historical market values

        Parameters
        ----------
        writer : ExcelWriter
        data : dataframe
            Market value dataframe.
        sheet_name : string, optional
            Excel sheet name. The default is 'Market Values'.

        Returns
        -------
        Market Values Excel sheet.
        """
        super().__init__(writer=writer, data=data, sheet_name=sheet_name)

    def get_conditional_worksheet_format(self):
        self.conditional_worksheet_date_format()
        self.conditional_ccy_worksheet_format()


class RatioSheet(PercentSheet):

    def __init__(self, writer, data, sheet_name):
        """
        Create Excel sheet for historical market values

        Parameters
        ----------
        writer : ExcelWriter
        data : dataframe
            Market value dataframe.
        sheet_name : string, optional
            Excel sheet name. The default is 'Market Values'.

        Returns
        -------
        ratio Excel sheet.
        """
        super().__init__(writer=writer, data=data, sheet_name=sheet_name)

    def get_conditional_worksheet_format(self):
        self.conditional_worksheet_date_format()
        self.conditional_digits_worksheet_format()


class HistSelloffSheet(DataFrameSheet):

    def __init__(self, writer, data, sheet_name='Historical Sell-offs'):
        """
        Create Excel sheet for historical selloffs

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        data : DataFrame
            Historical sell-off dataFrame.
        sheet_name : str, optional
            Excel sheet name. Default is 'Historical Sell-offs'.
        """
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, row=2, col=1, col_width=30)

    def get_conditional_worksheet_format(self):
        self.conditional_hist_selloff_worksheet_format()


# TODO: check
class DrawdownSheet(DataFrameSheet):

    def __init__(self, writer, drawdown_df, sheet_name='Drawdown Statistics', freq='1M'):
        self.freq = freq
        super().__init__(writer=writer, data=drawdown_df, sheet_name=sheet_name, col_width=30, index=False)

    def get_conditional_worksheet_format(self):
        self.conditional_dd_worksheet_format()


# TODO: rewrite using analytics and dm classes
class MarketStatsDataSheet(DataFrameSheet):
    def __init__(self, writer, data, sheet_name='Market Statistics', partial_stats=False, strat_report=False):
        self.partial_stats = partial_stats
        self.strat_report = strat_report
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, freeze=True)

    def increase_row_dim(self):
        if self.strat_report:
            self.row_dim += 2

    def conditional_worksheet_format(self):
        self.increase_row_dim()
        for row_number in range(self.row + 1, self.row_dim + 1):
            conditional_format = self.pct_fmt if (row_number - 2) % 7 == 1 else self.digits_fmt
            if self.partial_stats:
                conditional_format = self.pct_fmt if (row_number - 1) % 3 == 1 else self.digits_fmt
            self.worksheet.conditional_format(row_number, self.col, row_number, self.col_dim,
                                              {'type': 'no_blanks', 'format': conditional_format})


class LiquidAltsReturnsStatsSheet(MarketStatsDataSheet):
    def __init__(self, writer, data, sheet_name='Returns Statistics', include_bmk=True, strat_report=False):
        """
        Create Excel sheet for Liquid Alts Return Statistics Data

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        data : DataFrame
        sheet_name : str, optional
            Excel sheet name. Default is 'Historical Sell-offs'.
        include_bmk : bool, optional
            Default is True.
        """
        self.include_bmk = include_bmk
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, strat_report=strat_report)

    def conditional_worksheet_format(self):
        self.increase_row_dim()
        ann_ret_jump = self.row + 3  # 5
        excess_ret_jump = 0  # 7
        bmk_beta_jump = 0  # 8
        first_col = self.col + 1
        ret_stats_jump = ann_ret_jump + 4  # 9
        avg_pos_neq_ratio_jump = ret_stats_jump + 1  # 10
        period_stats_jump = avg_pos_neq_ratio_jump + 1  # 11
        vol_jump = period_stats_jump + 6  # 17
        dev_ratio_jump = vol_jump + 1  # 18
        kurtosis_jump = dev_ratio_jump + 3  # 21
        max_dd_jump = kurtosis_jump + 1  # 22
        ratios_jump = max_dd_jump + 1  # 23
        if self.include_bmk:
            ann_ret_jump = self.row + 4  # 6
            excess_ret_jump = ann_ret_jump + 1  # 7
            bmk_beta_jump = excess_ret_jump + 1  # 8
            ret_stats_jump = bmk_beta_jump + 4  # 12
            avg_pos_neq_ratio_jump = ret_stats_jump + 1  # 13
            period_stats_jump = avg_pos_neq_ratio_jump + 1  # 14
            vol_jump = period_stats_jump + 8  # 22
            dev_ratio_jump = vol_jump + 1  # 23
            kurtosis_jump = dev_ratio_jump + 4  # 27
            max_dd_jump = kurtosis_jump + 1  # 28
            ratios_jump = max_dd_jump + 1  # 29

        # format for return stats
        if self.include_bmk:
            # format returns(ann_ret, excess_ret) to percent
            self.worksheet.conditional_format(ann_ret_jump, first_col, excess_ret_jump, self.col_dim,
                                              {'type': 'no_blanks', 'format': self.pct_fmt})
            # format bmk_beta to digits
            self.worksheet.conditional_format(bmk_beta_jump, first_col, bmk_beta_jump, self.col_dim,
                                              {'type': 'no_blanks', 'format': self.digits_fmt})
            # format returns (med, avg) to percent
            self.worksheet.conditional_format(bmk_beta_jump + 1, first_col, ret_stats_jump, self.col_dim,
                                              {'type': 'no_blanks', 'format': self.pct_fmt})
        else:
            # format returns(ann_ret, med, avg) to percent
            self.worksheet.conditional_format(ann_ret_jump, first_col, ret_stats_jump, self.col_dim,
                                              {'type': 'no_blanks', 'format': self.pct_fmt})

        # format avg_pos_ret to avg_neg_ret ratio to digits
        self.worksheet.conditional_format(avg_pos_neq_ratio_jump, first_col, avg_pos_neq_ratio_jump, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format min, max, vols to percent
        self.worksheet.conditional_format(period_stats_jump, first_col, vol_jump, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format up/dwn dev ratio, skew, kurt to digits
        self.worksheet.conditional_format(dev_ratio_jump, first_col, kurtosis_jump, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format max_dd to percent
        self.worksheet.conditional_format(max_dd_jump, first_col, max_dd_jump, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # format ret/vol, ir, sortino, ret/dd ratios to digits
        self.worksheet.conditional_format(ratios_jump, first_col, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format mctr to percent
        # self.worksheet.conditional_format(self.row + 25 + jump_4, first_col, self.row + 25 + jump_4, self.col_dim,
        #                                   {'type': 'no_blanks', 'format': self.pct_fmt})


# TODO: rewrite using analytics and dm classes
class StratAltsReturnStatsSheet(LiquidAltsReturnsStatsSheet):
    def __init__(self, writer, ret_stat_df, sheet_name='Returns Statistics', include_fi=False):
        self.include_fi = include_fi
        super().__init__(writer, ret_stat_df, sheet_name)

    def conditional_worksheet_format(self):
        jump_1 = 0
        jump_2 = jump_1
        # jump_4 = jump_3 + 1
        # jump_3 = jump_2 + 1

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


class VRRSheet(DataFrameSheet):
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
        self.worksheet.conditional_format(self.row + 1, self.col + 5, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt2})

        # formatting for the first column using date format
        self.worksheet.conditional_format(self.row, self.col, self.row_dim, self.col,
                                          {'type': 'no_blanks', 'format': self.date_fmt})


# TODO: rewrite using analytics and dm classes

class HistReturnMTDYTDSheet(DataDictSheet):
    def __init__(self, writer, data, sheet_name='MTD-YTD-ITD', **kwargs):
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, col_width=10.67, spaces=2,
                         row=1, **kwargs)

    def check_if_dict(self, data):
        if isinstance(data, dict):
            return data
        else:
            return {data.index.name: data}

    def format_worksheet_data(self):
        for key in self.data:
            self.set_worksheet(data_df=self.data[key], row=self.row - 1, col=0, title=f'{key} Return History')
            self.conditional_worksheet_format()
            self.update_row()

    def get_conditional_worksheet_format(self):
        self.conditional_percent_worksheet_format()


class CorrStatsSheet(DataDictSheet):
    def __init__(self, writer, data, sheet_name='Correlation Analysis', row=2, col=1, freeze=True, **kwargs):
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
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, row=row, col=col, freeze=freeze,
                         **kwargs)

    def format_worksheet_data(self):
        for corr_key, corr_dict in self.data.items():
            self.set_worksheet(data_df=corr_dict['corr_df'], row=self.row - 1, col=1, title=corr_dict['title'])
            self.conditional_worksheet_format()
            self.update_row()

    def get_conditional_worksheet_format(self):
        self.conditional_corr_worksheet_format()

    def conditional_corr_worksheet_format(self):
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': 'no_blanks', 'format': self.digits_fmt})
        # format matrices using 3 color scale
        self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
                                          {'type': '3_color_scale'})


class QuantileDataSheet(CorrStatsSheet):
    def __init__(self, writer, data, sheet_name='Quantile Analysis', **kwargs):
        """
        Create Excel sheet for grouped data

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        data_dict: dictionary
        sheet_name : str, optional
            Excel sheet name. Default is 'Quantile Data'.
        """

        super().__init__(writer=writer, data=data, sheet_name=sheet_name, freeze=False, **kwargs)

    def format_worksheet_data(self):
        for key, mkt_quantile_df in self.data.items():
            self.set_worksheet(data_df=mkt_quantile_df, row=self.row - 1, col=1, title=f'{key} Analysis', index=True)
            self.conditional_worksheet_format()
            self.update_row()

    def get_conditional_worksheet_format(self):
        self.conditional_worksheet_pct_format()


class BestWorstPdDataSheet(QuantileDataSheet):
    def __init__(self, writer, data, sheet_name='Worst Quarters', **kwargs):
        """
        Create Excel sheet for grouped data

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        data_dict: dictionary
        sheet_name : str, optional
            Excel sheet name. Default is 'Worst Quarters'.
        """

        super().__init__(writer=writer, data=data, sheet_name=sheet_name, **kwargs)

    def get_title(self, key):
        title_list = self.sheet_name.split()
        best_worst_string = title_list[0]
        title_list.remove(best_worst_string)
        return " ".join([*[best_worst_string, key], *title_list])

    def format_worksheet_data(self):
        for key, best_worst_pd_df in self.data.items():
            title = self.get_title(key)
            self.set_worksheet(data_df=best_worst_pd_df, row=self.row - 1, col=1, title=title, index=True)
            self.conditional_worksheet_format()
            self.update_row()

    def get_conditional_worksheet_format(self):
        self.conditional_worksheet_date_format()
        self.conditional_worksheet_pct_format()


# TODO:review
class CoDrawdownDictSheet(CorrStatsSheet):
    def __init__(self, writer, data, sheet_name='Co-Drawdowns', **kwargs):
        """
        Create Excel sheet for grouped data

        Parameters:
        writer : ExcelWriter
            Excel writer object.
        data_dict: dictionary
        sheet_name : str, optional
            Excel sheet name. Default is 'Quantile Data'.
        """
        # self.freq = freq
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, **kwargs)

    def format_worksheet_data(self):
        for key, co_dd_dict in self.data.items():
            self.set_worksheet(data_df=co_dd_dict[key], row=self.row - 1, col=1, title=co_dd_dict['title'],
                               index=False)
            self.conditional_worksheet_format()
            self.update_row()

    def freeze_panes(self):
        if self.freeze:
            self.worksheet.freeze_panes(0, self.col + 3)

    def get_conditional_worksheet_format(self):
        self.conditional_co_dd_worksheet_format()

    def conditional_co_dd_worksheet_format(self):
        # Formatting for dates
        self.worksheet.conditional_format(self.row + 1, self.col, self.row_dim, self.col + 1,
                                          {'type': 'no_blanks', 'format': self.date_fmt_dd})
        # Formatting strategy returns
        self.worksheet.conditional_format(self.row + 1, self.col + 2, self.row_dim, self.col + 2,
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
        # Formatting co-strat returns
        self.worksheet.conditional_format(self.row + 1, self.col + 3, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '<', 'value': 0, 'format': self.pct_fmt_neg})
        self.worksheet.conditional_format(self.row + 1, self.col + 3, self.row_dim, self.col_dim,
                                          {'type': 'cell', 'criteria': '>', 'value': 0, 'format': self.pct_fmt_pos})


class DrawdownDictSheet(QuantileDataSheet):
    def __init__(self, writer, data, sheet_name='Strategy Worst Drawdowns', freq='M', **kwargs):
        self.freq = freq
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, **kwargs)

    def format_worksheet_data(self):
        for key, dd_dict in self.data.items():
            self.set_worksheet(data_df=dd_dict[key], row=self.row - 1, col=1, title=dd_dict['title'],
                               index=False)
            self.conditional_worksheet_format()
            self.update_row()

    def get_conditional_worksheet_format(self):
        self.conditional_dd_worksheet_format()


class DrawdownMatrixSheet(HistSelloffSheet):
    def __init__(self, writer, data, sheet_name='Max Drawdown Matrix'):
        super().__init__(writer=writer, data=data, sheet_name=sheet_name)

    # def format_worksheet_data(self):
    #     for key, dd_dict in self.data.items():
    #         if key.__eq__('dd_matrix'):
    #             self.set_worksheet(data_df=dd_dict[key], row=self.row - 1, col=1, title=dd_dict['title'],
    #                                index=True)
    #             self.conditional_worksheet_format()
    #             self.update_row()
    #         if key.__eq__('mkt_co_dd_dict'):
    #             for mkt, mkt_dd_dict in dd_dict.items():
    #                 self.set_worksheet(data_df=mkt_dd_dict[mkt], row=self.row - 1, col=1, title=mkt_dd_dict['title'],
    #                                    index=True)
    #                 self.conditional_worksheet_format()
    #                 self.update_row()
    #
    # def get_conditional_worksheet_format(self):
    #     return self.conditional_hist_selloff_worksheet_format()


# TODO: review
class AnalysisSheet(CorrStatsSheet):
    def __init__(self, writer, data, sheet_name='Monthly Analysis', **kwargs):
        """
        Create an Excel sheet with:
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
        super().__init__(writer=writer, data=data, sheet_name=sheet_name, freeze=False, **kwargs)

    def format_worksheet_data(self):
        for key in self.data:
            if key == 'correlations':
                # format correlation matrices
                for corr_key in self.data[key]:
                    corr_title = self.data[key][corr_key]['title']
                    self.set_worksheet(data_df=self.data[key][corr_key]['corr_df'],
                                       row=self.row - 1, col=1, title=corr_title)
                    self.conditional_worksheet_format()
                    self.update_row()
            else:
                if key == 'weighting':
                    if self.data[key]['weights_df'].empty is False:
                        weights_title = self.data[key]['title']
                        self.set_worksheet(data_df=self.data[key]['weights_df'],
                                           row=self.row - 1, col=1, title=weights_title)
                        self.conditional_port_worksheet_format()
                if key == 'return_stats':
                    # format return statistics
                    return_stats_title = self.data[key]['title']
                    self.set_worksheet(data_df=self.data[key]['ret_stats_df'],
                                       row=self.row - 1, col=1, title=return_stats_title)
                    self.conditional_ret_stat_worksheet_format()
                if key == 'hedge_metrics':
                    # format hedge metrics
                    hedge_metrics_title = self.data[key]['title']
                    self.set_worksheet(data_df=self.data[key]['hm_df'],
                                       row=self.row - 1, col=1, title=hedge_metrics_title)
                    self.conditional_hm_worksheet_format()
                self.update_row()

    # def conditional_corr_worksheet_format(self, corr_key):
    #     if corr_key.__eq__('Full'):
    #         self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
    #                                           {'type': 'duplicate', 'format': self.digits_fmt})
    #     else:
    #         self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
    #                                           {'type': 'no_blanks', 'format': self.digits_fmt})
    #     self.worksheet.conditional_format(self.row + 1, self.col + 1, self.row_dim, self.col_dim,
    #                                       {'type': '3_color_scale'})

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
                                          {'type': 'no_blanks', 'format': self.pct_fmt})
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
class CorrRankSheet(QuantileDataSheet):
    def __init__(self, writer, data, dates, sheet_name='Correlations Ranks'):
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
        super().__init__(writer, data, sheet_name, row=3, col_width=19)

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

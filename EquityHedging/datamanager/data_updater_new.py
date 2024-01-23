# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 20:13:09 2022

@author: Powis Forjoe
"""
import os

import pandas as pd

from . import data_importer as di
from . import data_manager_new as dm
from . import data_xformer_new as dxf
from ..reporting.excel import new_reports as rp

CWD = os.getcwd()
RETURNS_DATA_FP = CWD + '\\EquityHedging\\data\\returns_data\\'
UPDATE_DATA_FP = CWD + '\\EquityHedging\\data\\update_data\\'


def update_columns(df, old_col_list, new_col_list):
    df = df[old_col_list]
    df.columns = new_col_list
    return df


def update_df_dict_columns1(df_dict, old_col_list, new_col_list):
    updated_dict = dxf.copy_data(df_dict)
    for key in updated_dict:
        updated_dict[key] = update_columns(updated_dict[key], old_col_list, new_col_list)
    return updated_dict


def update_df_dict_columns(df_dict, col_dict):
    updated_dict = dxf.copy_data(df_dict)
    for key in updated_dict:
        updated_dict[key] = dm.rename_columns(updated_dict[key], col_dict)
    return updated_dict


def get_data_to_update(col_list, filename, sheet_name='data', put_spread=False):
    '''
    Update data to dictionary

    Parameters
    ----------
    col_list : list
        List of columns for dict
    filename : string        
    sheet_name : string
        The default is 'data'.
    put_spread : boolean
        Describes whether a put spread strategy is used. The default is False.

    Returns
    -------
    data_dict : dictionary
        dictionary of the updated data.

    '''
    # read excel file to dataframe
    data = pd.read_excel(UPDATE_DATA_FP + filename, sheet_name=sheet_name, index_col=0)

    # rename column(s) in dataframe
    data.columns = col_list

    if put_spread:
        # remove the first row of dataframe
        data = data.iloc[1:, ]

        # add column into dataframe
        data = data[['99%/90% Put Spread']]

        # add price into dataframe
        data = dxf.get_prices_df(data)

    data_dict = dxf.get_data_dict(data)
    return data_dict


def match_dict_columns(main_dict, new_dict):
    '''
    Parameters
    ----------
    main_dict : dictionary
    original dictionary
    new_dict : dictionary
    dictionary that needs to have columns matched to main_dict
    Returns
    -------
    new_dict : dictionary
        dictionary with matched columns

    '''

    # iterate through keys in dictionary
    for key in new_dict:
        # set column in the new dictionary equal to that of the main
        new_dict[key] = new_dict[key][list(main_dict[key].columns)]
    return new_dict


def append_dict(main_dict, new_dict):
    '''
    update an original dictionary by adding information from a new one

    Parameters
    ----------
    main_dict : dictionary      
    new_dict : dictionary        

    Returns
    -------
    main_dict : dictionary

    '''
    # iterate through keys in dictionary
    for key in new_dict:
        # add value from new_dict to main_dict
        main_dict[key] = main_dict[key].append(new_dict[key])
    return main_dict


def get_new_returns_df(new_returns_df, returns_df):
    # copy dataframes
    new_ret_df = new_returns_df.copy()
    ret_df = returns_df.copy()

    # reset both data frames index to make current index (dates) into a column
    new_ret_df.index.names = ['Dates']
    ret_df.index.names = ['Dates']
    new_ret_df.reset_index(inplace=True)
    ret_df.reset_index(inplace=True)

    # find difference in dates
    difference = set(new_ret_df.Dates).difference(ret_df.Dates)
    # find which dates in the new returns are not in the current returns data
    difference_dates = new_ret_df['Dates'].isin(difference)

    # select only dates not included in original returns df
    new_ret_df = new_ret_df[difference_dates]

    # set 'Date' column as index for both data frames
    new_ret_df.set_index('Dates', inplace=True)
    ret_df.set_index('Dates', inplace=True)

    return new_ret_df


def check_returns(returns_dict):
    # if the last day of the month is earlier than the last row in weekly returns then drop last row of weekly returns
    if returns_dict['Monthly'].index[-1] < returns_dict['Weekly'].index[-1]:
        returns_dict['Weekly'] = returns_dict['Weekly'][:-1]

    if returns_dict['Monthly'].index[-1] < returns_dict['Quarterly'].index[-1]:
        returns_dict['Quarterly'] = returns_dict['Quarterly'][:-1]

    return returns_dict


def update_data(main_dict, new_dict, freq_data=True):
    updated_dict = {}
    for key in main_dict:
        # create returns data frame
        new_ret_df = new_dict[key].copy()
        ret_df = main_dict[key].copy()

        # update current year returns
        if key == 'Yearly':
            if ret_df.index[-1] == new_ret_df.index[-1]:
                ret_df = ret_df[:-1]
        # get new returns df
        new_ret_df = get_new_returns_df(new_ret_df, ret_df)
        updated_dict[key] = pd.concat([ret_df, new_ret_df])
        updated_dict[key].sort_index(inplace=True)

    if freq_data:
        updated_dict = check_returns(updated_dict)
    return updated_dict


def get_real_cols(df):
    """
    Removes empty columns labeled 'Unnamed: ' after importing data
    
    Parameters:
    df -- dataframe
    
    Returns:
    dataframe
    """
    real_cols = [x for x in df.columns if not x.startswith("Unnamed: ")]
    df = df[real_cols]
    return df


class mainUpdater:
    def __init__(self, filename, report_name):
        self.filename = filename
        self.report_name = report_name
        self.data_xform = self.xform_data()

        self.data_dict = self.calc_data_dict()

    def xform_data(self):
        return dxf.dataXformer(filepath=UPDATE_DATA_FP + self.filename).data_xform

    def calc_data_dict(self):
        return dxf.copy_data(data=self.data_xform)

    def update_report(self):
        pass


class nexenDataUpdater(mainUpdater):
    """
    Class for updating Nexen data.
    
    Args:
        filename (str, optional): Name of the input Excel file containing data. 
            Default is 'Monthly Returns Liquid Alts.xls'.
        report_name (str, optional): Name of the report to generate. 
            Default is 'nexen_liq_alts_data-new'.
    """

    def __init__(self, filename='Monthly Returns Liquid Alts.xls', report_name='nexen_liq_alts_data-new'):
        """
       Initializes the nexenDataUpdater instance.

       Args:
           filename (str, optional): Name of the input Excel file containing data. 
               Default is 'Monthly Returns Liquid Alts.xls'.
           report_name (str, optional): Name of the report to generate. 
               Default is 'nexen_liq_alts_data-new'.
       """
        super().__init__(filename=filename, report_name=report_name)

    def xform_data(self):
        return dxf.nexenDataXformer(filepath=UPDATE_DATA_FP + self.filename).data_xform

    def update_report(self):
        """
        Update the report of Nexen data.

        """
        rp.returnMktValueReport(report_name=self.report_name, data=self.data_dict, data_file=True)


class innocapLiquidAltsDataUpdater(nexenDataUpdater):
    """
    Class for updating Innocap Liquid Alternatives data.
    
    Args:
        filename (str, optional): Name of the input Excel file containing data. 
            Default is '1907_hf_data.xlsx'.
        report_name (str, optional): Name of the report to generate. 
            Default is 'innocap_liq_alts_data-new'.
    """

    def __init__(self, filename='1907_hf_data.xlsx', report_name='innocap_liq_alts_data-new',
                 ret_filename='innocap_liq_alts_data.xlsx'):
        """
        Initializes the innocapLiquidAltsDataUpdater instance.

        Args:
            filename (str, optional): Name of the input Excel file containing data. 
                Default is '1907_hf_data.xlsx'.
            report_name (str, optional): Name of the report to generate. 
                Default is 'innocap_liq_alts_data-new'.
        """
        self.ret_filename = ret_filename
        super().__init__(filename, report_name)

    def xform_data(self):
        return dxf.innocapDataXformer(UPDATE_DATA_FP + self.filename).data_xform

    def calc_data_dict(self):
        """
        Calculate the data dictionary for Innocap data.
 
        Returns:
            data_dict (dict): Calculated data dictionary for Innocap Liquid Alternatives data.
        """
        col_dict = {'1907 Campbell Trend Following LLC': '1907 Campbell TF',
                    '1907 Systematica Trend Following': '1907 Systematica TF',
                    '1907 ARP Trend Following LLC_Class EM': '1907 ARP EM',
                    '1907 III Fund Ltd _ Class CV': '1907 III CV',
                    '1907 Kepos': '1907 Kepos RP'
                    }
        # self.old_col_list = ['1907 Campbell Trend Following LLC', '1907 III Class A','1907 Penso Class A',
        #                 '1907 Systematica Trend Following',
        #                 '1907 ARP Trend Following LLC_Class EM', '1907 III Fund Ltd _ Class CV', '1907 Kepos']
        # self.new_col_list = ['1907 Campbell TF', '1907 III Class A', '1907 Penso Class A', '1907 Systematica TF'
        #                      , '1907 ARP EM', '1907 III CV','1907 Kepos RP']

        updated_dict = update_df_dict_columns(self.data_xform, col_dict)
        data_dict = di.read_excel_data(filepath=RETURNS_DATA_FP + self.ret_filename, sheet_name=None)
        data_dict = update_data(main_dict=data_dict, new_dict=updated_dict, freq_data=False)
        return data_dict


class bbgDataUpdater(mainUpdater):
    """
    Class for updating Bloomberg (BBG) data.
    
    This class inherits from mainUpdater and specializes in updating and transforming Bloomberg data.
    
    Args:
        filename (str): Name of the input Excel file containing data.
        report_name (str): Name of the report to generate.
        col_list (list, optional): List of column names to include in the data. Default is an empty list.
    """

    def __init__(self, filename, report_name, col_list=[]):
        """
      Initializes the bbgDataUpdater instance.

      Args:
          filename (str): Name of the input Excel file containing data.
          report_name (str): Name of the report to generate.
          col_list (list, optional): List of column names to include in the data. Default is an empty list.
      """
        self.col_list = col_list
        super().__init__(filename, report_name)

    def xform_data(self):
        """
        Transform the Bloomberg (BBG) data.

        Returns:
            transformed_data (DataFrame or Dict): Transformed Bloomberg data.
        """
        return dxf.bbgDataXformer(UPDATE_DATA_FP + self.filename).data_xform

    def calc_data_dict(self):
        """
        Calculate the data dictionary for Bloomberg (BBG) data.
        
        Returns:
            data_dict (dict): Calculated data dictionary for Bloomberg data.
        """
        data_dict = dxf.copy_data(self.data_xform)
        if self.col_list:
            for key in data_dict:
                data_dict[key] = data_dict[key][self.col_list]
        return data_dict

    def update_report(self):
        """
        Update the report of Bloomberg (BBG) data.

        """
        rp.returnsReport(self.report_name, self.data_dict, True)


class hfBmkDataUpdater(bbgDataUpdater):
    """
    Class for updating Hedge Fund Benchmark data.

    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'liq_alts_bmk_data.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'hf_bmks-new'.
        col_list (list, optional): List of column names to include in the data.
            Default is an empty list.
    """

    def __init__(self, filename='liq_alts_bmk_data.xlsx', report_name='hf_bmks-new', col_list=[]):
        """
    Initializes the hfBmkDataUpdater instance.
    
    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'liq_alts_bmk_data.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'hf_bmks-new'.
        col_list (list, optional): List of column names to include in the data.
            Default is an empty list.
    """
        super().__init__(filename, report_name, col_list)

    def xform_data(self):
        """
        Transform the Hedge Fund Benchmark data.

        Returns:
            transformed_data (DataFrame or Dict): Transformed Hedge Fund Benchmark data.
        """
        return dxf.bbgDataXformer(UPDATE_DATA_FP + self.filename, sheet_name='bbg_d').data_xform


class liqAltsBmkDataUpdater(hfBmkDataUpdater):
    """
    Class for updating Liquid Alternatives Benchmark data.
    
    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'liq_alts_bmk_data.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'liq_alts_bmks-new'.
        col_list (list, optional): List of column names to include in the data.
            Default is ['HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend'].
    """

    def __init__(self, filename='liq_alts_bmk_data.xlsx', report_name='liq_alts_bmks-new',
                 col_list=['HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']):
        """
       Initializes the liqAltsBmkDataUpdater instance.

       Args:
           filename (str, optional): Name of the input Excel file containing data.
               Default is 'liq_alts_bmk_data.xlsx'.
           report_name (str, optional): Name of the report to generate.
               Default is 'liq_alts_bmks-new'.
           col_list (list, optional): List of column names to include in the data.
               Default is ['HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend'].
       """
        super().__init__(filename, report_name, col_list)

    def xform_data(self):
        """
       Transform the Liquid Alternatives Benchmark data.

       Returns:
           transformed_data (DataFrame or Dict): Transformed Liquid Alternatives Benchmark data.
       """
        return dxf.bbgDataXformer(UPDATE_DATA_FP + self.filename, sheet_name='bbg_d').data_xform


class bmkDataUpdater(bbgDataUpdater):
    """
    Class for updating Benchmark data.
    
    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'bmk_data.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'bmk_returns-new'.
    """

    def __init__(self, filename='bmk_data.xlsx', report_name='bmk_returns-new', ret_filename='bmk_returns-new.xlsx'):
        """
        Initializes the bmkDataUpdater instance.
 
        Args:
            filename (str, optional): Name of the input Excel file containing data.
                Default is 'bmk_data.xlsx'.
            report_name (str, optional): Name of the report to generate.
                Default is 'bmk_returns-new'.
        """
        self.ret_filename = ret_filename
        super().__init__(filename, report_name)

    def xform_data(self):
        """
       Transform the Benchmark data.

       Returns:
           transformed_data (DataFrame or Dict): Transformed Benchmark data.
       """
        return dxf.bbgDataXformer(UPDATE_DATA_FP + self.filename).data_xform

    def calc_data_dict(self):
        """
        Calculate the data dictionary for Benchmark data.

        Returns:
            data_dict (dict): Calculated data dictionary for Benchmark data.
        """
        # TODO: add comments
        data_dict = dxf.copy_data(self.data_xform)
        returns_dict = di.read_excel_data(RETURNS_DATA_FP + self.ret_filename, sheet_name=None)
        data_dict = match_dict_columns(returns_dict, data_dict)
        return update_data(returns_dict, data_dict)


# TODO: get right nexen reports
class gtPortDataUpdater(nexenDataUpdater):
    """
   Class for updating Asset Class Returns data.

   Args:
       filename (str, optional): Name of the input Excel file containing data.
           Default is 'Historical Asset Class Returns.xls'.
       report_name (str, optional): Name of the report to generate.
           Default is 'upsgt_returns-new'.
   """

    def __init__(self, filename='Historical Asset Class Returns w Bmks.xls', report_name='upsgt_returns-new'):
        """
       Initializes the assetClassDataUpdater instance.

       Args:
           filename (str, optional): Name of the input Excel file containing data.
               Default is 'Historical Asset Class Returns.xls'.
           report_name (str, optional): Name of the report to generate.
               Default is 'upsgt_returns-new'.
       """
        super().__init__(filename, report_name)

    def calc_data_dict(self):
        """
        Calculate the data dictionary for Asset Class Returns data.

        Returns:
            data_dict (dict): Calculated data dictionary for Asset Class Returns data.
        """
        col_dict = {'Total Credit': 'Credit', 'Total Equity': 'Public Equity', 'Total Fixed Income': 'Fixed Income',
                    'Total Liquid Alts': 'Liquid Alts', 'Total Private Equity': 'Private Equity',
                    'Total Real Estate': 'Real Estate',
                    'Total UPS Cash': 'Cash', 'UPS GT Total Consolidation': 'Group Trust'}
        data_dict = update_df_dict_columns(self.data_xform, col_dict)
        return data_dict


class gtBmkDataUpdater(gtPortDataUpdater):
    """
   Class for updating Asset Class Returns data.

   Args:
       report_name (str, optional): Name of the report to generate.
           Default is 'upsgt_returns-new'.
   """

    def __init__(self, report_name='upsgt_bmk_returns-new'):
        """
       Initializes the assetClassDataUpdater instance.

       Args:
           report_name (str, optional): Name of the report to generate.
               Default is 'upsgt_returns-new'.
       """
        super().__init__(report_name=report_name)

    def xform_data(self):
        return {'liq_alts_bmk': liqAltsBmkDataUpdater().data_dict['Monthly'],
                'nexen_bmk': dxf.nexenBmkDataXformer(filepath=UPDATE_DATA_FP + self.filename).data_xform}

    def calc_data_dict(self):
        """
        Calculate the data dictionary for Asset Class Returns data.

        Returns:
            data_dict (dict): Calculated data dictionary for Asset Class Returns data.
        """
        liq_alts_bmk_wgts = {'HFRX Macro/CTA': 0.5, 'HFRX Absolute Return': 0.3, 'SG Trend': 0.2}
        self.data_xform['liq_alts_bmk']['Liquid Alts Benchmark'] = self.data_xform['liq_alts_bmk'].dot(
            list(liq_alts_bmk_wgts.values()))
        data = dm.merge_data_frames(self.data_xform['nexen_bmk'],
                                    self.data_xform['liq_alts_bmk']['Liquid Alts Benchmark'], False)

        col_dict = {'Custom Credit Benchmark': 'Credit Benchmark',
                    'Fixed Income Benchmark-Static': 'Fixed Income Benchmark',
                    'MSCI All Country World Investable Market Net Index': 'Public Equity Benchmark',
                    'NCREIF NFI-ODCE Equal Weighted Net Index 1QA^': 'Real Estate Benchmark',
                    'UPS PE FOF Index': 'Private Equity Benchmark'}
        data = dm.rename_columns(data, col_dict)
        return {'bmk': data}

    def update_report(self):
        rp.returnsReport(self.report_name, self.data_dict, data_file=True)


class equityHedgeReturnsUpdater(bmkDataUpdater):
    """
    Class for updating Equity Hedge Returns data.
        
    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'eq_hedge_returns.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'eq_hedge_returns-new'.
    """

    def __init__(self, filename=None, report_name='eq_hedge_returns-new', ret_filename='eq_hedge_returns.xlsx'):
        """
        Initializes the equityHedgeReturnsUpdater instance.

        Args:
            filename (str, optional): Name of the input Excel file containing data.
                Default is 'eq_hedge_returns.xlsx'.
            report_name (str, optional): Name of the report to generate.
                Default is 'eq_hedge_returns-new'.
        """
        super().__init__(filename, report_name, ret_filename)

    def xform_data(self):
        """
        Create a dictionary that updates returns data

        Returns
        -------
        new_data_dict : Dictionary
            Contains the updated information after adding new returns data

        """
        # Import data from bloomberg into dataframe and create dictionary with different frequencies
        new_ups_data_dict = dxf.bbgDataXformer(filepath=UPDATE_DATA_FP + 'ups_data.xlsx', sheet_name='bbg_d').data_xform

        # Import vrr returns dictionary
        vrr_dict = dxf.vrrDataXformer(filepath=UPDATE_DATA_FP + 'vrr_tracks_data.xlsx').data_xform

        # merge returns dictionaries
        new_data_dict = dm.merge_dicts(new_ups_data_dict, vrr_dict)

        return new_data_dict


class liquidAltsReturnsUpdater(mainUpdater):
    def __init__(self, filename=None, report_name="all_liquid_alts_data"):
        super().__init__(filename, report_name)

    def xform_data(self):
        return {'nexen': nexenDataUpdater().data_dict, 'innocap': innocapLiquidAltsDataUpdater().data_dict}

    def calc_data_dict(self):
        data_dict = {}
        # Loop through sheets in nexen_data
        for key in self.data_xform['nexen']:
            nexen_df = self.data_xform['nexen'][key].copy()
            nexen_df.reset_index(inplace=True)
            # Check if the sheet exists in innocap_data
            if key in self.data_xform['innocap']:
                innocap_df = self.data_xform['innocap'][key].copy()
                innocap_df.reset_index(inplace=True)
                # Use combine_first to merge DataFrames and replace values from nexen with innocap where they exist
                merged_df = nexen_df.set_index(nexen_df.columns[0]).combine_first(
                    innocap_df.set_index(innocap_df.columns[0]))

                # Reset the index to move the date column back to its original position
                # merged_df.index.names = ['Dates']
                merged_df.reset_index(inplace=True)

                # Format the first column (dates) as short date format (mm/dd/yyyy)
                # merged_df[merged_df.columns[0]] = merged_df[merged_df.columns[0]].dt.strftime('%m/%d/%Y')

                # Add the merged DataFrame to the dictionary
                merged_df.set_index(merged_df.columns[0], inplace=True)
                merged_df.index.names = ['Dates']
                # merged_df.set_index('Dates', inplace=True)
                data_dict[key] = merged_df
            else:
                # If key doesn't exist in innocap_data, add nexen_df as is
                data_dict[key] = nexen_df

        return data_dict

    def update_report(self):
        rp.returnMktValueReport(self.report_name, self.data_dict, True)

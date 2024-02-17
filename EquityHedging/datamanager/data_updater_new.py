# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 20:13:09 2022

@author: Powis Forjoe
"""
import pandas as pd

from . import data_importer as di
from . import data_manager_new as dm
from . import data_xformer_new as dxf
from . import data_lists as dl
from ..reporting.excel import new_reports as rp


class DataUpdater:
    def __init__(self, filename, report_name):
        self.filename = filename
        self.report_name = report_name
        self.data_xform = self.xform_data()
        self.data_dict = self.calc_data_dict()

    def xform_data(self):
        return dxf.DataXformer(file_path=dl.UPDATE_DATA_FP + self.filename).data_xform

    def calc_data_dict(self):
        return dm.copy_data(data=self.data_xform)

    def get_report_object(self):
        return rp.ReturnsReport(report_name=self.report_name, data=self.data_dict, data_file=True)

    def update_report(self):
        report = self.get_report_object()
        report.run_report()

    def update_df_dict_columns(self, col_dict):
        updated_dict = dm.copy_data(self.data_xform)
        for key, data_df in updated_dict.items():
            updated_dict[key] = dm.rename_columns(data_df, col_dict)
        return updated_dict

    @staticmethod
    def match_dict_columns(main_dict, new_dict):
        """
        Parameters
        ----------
        main_dict : dictionary
        original dictionary
        new_dict : dictionary that needs to have columns matched to main_dict
        Returns
        -------
        new_dict : dictionary

        """

        # iterate through keys in dictionary
        for key, data_df in new_dict.items():
            # set column in the new dictionary equal to that of the main
            new_dict[key] = data_df[list(main_dict[key].columns)]
        return new_dict

    @staticmethod
    def append_dict(main_dict, new_dict):
        """
        update an original dictionary by adding information from a new one

        Parameters
        ----------
        main_dict : dictionary
        new_dict : dictionary

        Returns
        -------
        main_dict : dictionary

        """
        # iterate through keys in dictionary
        for key, data_df in new_dict.items():
            # add value from new_dict to main_dict
            main_dict[key] = main_dict[key].append(data_df)
        return main_dict

    @staticmethod
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

        # set 'Dates' column as index for both data frames
        new_ret_df.set_index('Dates', inplace=True)
        ret_df.set_index('Dates', inplace=True)

        return new_ret_df

    @staticmethod
    def check_returns(returns_dict):
        # if the last date index in monthly returns is earlier than the last date index in weekly returns
        # then drop last row of weekly returns
        if returns_dict['Monthly'].index[-1] < returns_dict['Weekly'].index[-1]:
            returns_dict['Weekly'] = returns_dict['Weekly'][:-1]

        # if returns_dict['Monthly'].index[-1] < returns_dict['Quarterly'].index[-1]:
        #     returns_dict['Quarterly'] = returns_dict['Quarterly'][:-1]

        return returns_dict

    def update_data(self, main_dict, new_dict, freq_data=True):
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
            new_ret_df = self.get_new_returns_df(new_ret_df, ret_df)
            updated_dict[key] = pd.concat([ret_df, new_ret_df])
            updated_dict[key].sort_index(inplace=True)

        if freq_data:
            updated_dict = self.check_returns(updated_dict)
        return updated_dict


class NexenDataUpdater(DataUpdater):
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
        return dxf.NexenDataXformer(file_path=dl.UPDATE_DATA_FP + self.filename).data_xform

    def get_report_object(self):
        """
        Update the report of Nexen data.

        """
        return rp.ReturnMktValueReport(report_name=self.report_name, data=self.data_dict, data_file=True)


class InnocapLiquidAltsDataUpdater(NexenDataUpdater):
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
        return dxf.InnocapDataXformer(dl.UPDATE_DATA_FP + self.filename).data_xform

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

        updated_dict = self.update_df_dict_columns(col_dict)
        data_dict = di.ExcelImporter(file_path=dl.RETURNS_DATA_FP + self.ret_filename,
                                     sheet_name=None).read_excel_data()
        data_dict = self.update_data(main_dict=data_dict, new_dict=updated_dict, freq_data=False)
        return data_dict


class BbgDataUpdater(DataUpdater):
    """
    Class for updating Bloomberg (BBG) data.

    This class inherits from mainUpdater and specializes in updating and transforming Bloomberg data.

    Args:
        filename (str): Name of the input Excel file containing data.
        report_name (str): Name of the report to generate.
        col_list (list, optional): List of column names to include in the data. Default is an empty list.
    """

    def __init__(self, filename, report_name, drop_na=True, col_list=None, new_index=True):
        """
      Initializes the bbgDataUpdater instance.

      Args:
          filename (str): Name of the input Excel file containing data.
          report_name (str): Name of the report to generate.
          col_list (list, optional): List of column names to include in the data. Default is an empty list.
      """
        if col_list is None:
            col_list = []
        self.col_list = col_list
        self.new_index = new_index
        self.drop_na = drop_na
        super().__init__(filename=filename, report_name=report_name)

    def xform_data(self):
        """
        Transform the Bloomberg (BBG) data.

        Returns:
            transformed_data (DataFrame or Dict): Transformed Bloomberg data.
        """
        return dxf.BbgDataXformer(dl.UPDATE_DATA_FP + self.filename, drop_na=self.drop_na).data_xform

    def calc_data_dict(self):
        """
        Calculate the data dictionary for Bloomberg (BBG) data.

        Returns:
            data_dict (dict): Calculated data dictionary for Bloomberg data.
        """
        data_dict = dm.copy_data(self.data_xform)
        if self.col_list:
            for key in data_dict:
                data_dict[key] = data_dict[key][self.col_list]
        return data_dict

    def get_report_object(self):
        """
        Update the report of Bloomberg (BBG) data.

        """
        return rp.ReturnsReport(self.report_name, self.data_dict, True)

    def add_new_index(self, new_index_dict):
        if self.new_index:
            self.data_dict = dm.merge_dicts(self.data_dict, new_index_dict, drop_na=False)
            print(f'Added the following columns: {list(next(iter(new_index_dict.values())).columns)}')


class HFBmkDataUpdater(BbgDataUpdater):
    """
    Class for updating Hedge Fund Benchmark data.

    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'liq_alts_bmk_data.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'hf_bmks-new'.

    """

    def __init__(self, filename='liq_alts_bmk_data.xlsx', report_name='hf_bmks-new', new_index=False):
        """
    Initializes the hfBmkDataUpdater instance.

    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'liq_alts_bmk_data.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'hf_bmks-new'.

    """
        super().__init__(filename=filename, report_name=report_name, new_index=new_index)

    def xform_data(self):
        """
        Transform the Hedge Fund Benchmark data.

        Returns:
            transformed_data (DataFrame or Dict): Transformed Hedge Fund Benchmark data.
        """
        return dxf.BbgDataXformer(dl.UPDATE_DATA_FP + self.filename, sheet_name='bbg_d').data_xform


class LiquidAltsBmkDataUpdater(HFBmkDataUpdater):
    """
    Class for updating Liquid Alternatives Benchmark data.

    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'liq_alts_bmk_data.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'liq_alts_bmks-new'.
    """

    def __init__(self, filename='liq_alts_bmk_data.xlsx', report_name='liq_alts_bmks-new', new_index=False):
        """
       Initializes the liqAltsBmkDataUpdater instance.

       Args:
           filename (str, optional): Name of the input Excel file containing data.
               Default is 'liq_alts_bmk_data.xlsx'.
           report_name (str, optional): Name of the report to generate.
               Default is 'liq_alts_bmks-new'.

       """
        super().__init__(filename=filename, report_name=report_name, new_index=new_index)
        # if col_list is None:
        #     col_list = ['HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']

    def xform_data(self):
        """
       Transform the Liquid Alternatives Benchmark data.

       Returns:
           transformed_data (DataFrame or Dict): Transformed Liquid Alternatives Benchmark data.
       """
        return dxf.BbgDataXformer(dl.UPDATE_DATA_FP + self.filename, sheet_name='bbg_d').data_xform


class BmkDataUpdater(BbgDataUpdater):
    """
    Class for updating Benchmark data.

    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'bmk_data.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'bmk_returns-new'.
    """

    # TODO: Don't need ret_filename

    def __init__(self, filename='bmk_data.xlsx', report_name='bmk_returns-new', ret_filename='bmk_returns-new.xlsx',
                 new_index=True):
        """
        Initializes the bmkDataUpdater instance.

        Args:
            filename (str, optional): Name of the input Excel file containing data.
                Default is 'bmk_data.xlsx'.
            report_name (str, optional): Name of the report to generate.
                Default is 'bmk_returns-new'.
        """
        self.ret_filename = ret_filename
        super().__init__(filename=filename, report_name=report_name, drop_na=False, new_index=new_index)

    def xform_data(self):
        """
       Transform the Benchmark data.

       Returns:
           transformed_data (DataFrame or Dict): Transformed Benchmark data.
       """
        return dxf.BbgDataXformer(dl.UPDATE_DATA_FP + self.filename, drop_na=self.drop_na).data_xform

    def calc_data_dict(self):
        """
        Calculate the data dictionary for Benchmark data.

        Returns:
            data_dict (dict): Calculated data dictionary for Benchmark data.
        """
        # TODO: add comments
        data_dict = dm.copy_data(self.data_xform)
        returns_dict = di.DataImporter.read_excel_data(dl.RETURNS_DATA_FP + self.ret_filename, sheet_name=None)
        data_dict = self.match_dict_columns(returns_dict, data_dict)
        return self.update_data(returns_dict, data_dict)


# TODO: get right nexen reports
class GTPortDataUpdater(NexenDataUpdater):
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
        col_dict = {'Total Equity': 'Public Equity', 'TOTAL EQ W/0 HEDGE + CE': 'Public Equity w/o Hedges',
                    'Total EQ w/o Derivatives': 'Public Equity w/o Derivatives',
                    'Total Fixed Income': 'Fixed Income', 'Total Liquid Alts': 'Liquid Alts',
                    'Total Private Equity': 'Private Equity', 'Total Credit': 'Credit',
                    'Total Real Estate': 'Real Estate', 'Total UPS Cash': 'Cash',
                    'UPS GT Total Consolidation': 'Group Trust'}
        data_dict = self.update_df_dict_columns(col_dict)
        return data_dict


class GTBmkDataUpdater(GTPortDataUpdater):
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
        return {'liq_alts_bmk': LiquidAltsBmkDataUpdater().data_dict['Monthly'],
                'nexen_bmk': dxf.NexenBmkDataXformer(file_path=dl.UPDATE_DATA_FP + self.filename).data_xform}

    def calc_data_dict(self):
        """
        Calculate the data dictionary for Asset Class Returns data.

        Returns:
            data_dict (dict): Calculated data dictionary for Asset Class Returns data.
        """
        liq_alts_bmk_wgts = {'HFRX Macro/CTA': 0.5, 'HFRX Absolute Return': 0.3, 'SG Trend': 0.2}
        self.data_xform['liq_alts_bmk']['Liquid Alts Benchmark'] = self.data_xform['liq_alts_bmk'].dot(
            list(liq_alts_bmk_wgts.values()))
        data = dm.merge_dfs(self.data_xform['nexen_bmk'],
                            self.data_xform['liq_alts_bmk']['Liquid Alts Benchmark'], False)

        col_dict = {'Custom Credit Benchmark': 'Custom Credit Bmk',
                    'Fixed Income Benchmark-Static': 'FI Bmk-Static',
                    'MSCI All Country World Investable Market Net Index': 'Equity-MSCI ACWI IMI-Bmk',
                    'NCREIF NFI-ODCE Equal Weighted Net Index 1QA^': 'RE NCREIF 1QA^ Bmk',
                    'UPS PE FOF Index': 'PE FOF Bmk'}
        data = dm.rename_columns(data, col_dict)
        return {'returns': data}

    def get_report_object(self):
        return rp.ReturnsReport(self.report_name, self.data_dict, data_file=True)


class EquityHedgeReturnsUpdater(BmkDataUpdater):
    """
    Class for updating Equity Hedge Returns data.
        
    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'eq_hedge_returns.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'eq_hedge_returns-new'.
    """

    # TODO: Don't need ret_filename
    def __init__(self, filename=None, report_name='eq_hedge_returns-new', new_strats=False):
        """
        Initializes the equityHedgeReturnsUpdater instance.

        Args:
            filename (str, optional): Name of the input Excel file containing data.
                Default is 'eq_hedge_returns.xlsx'.
            report_name (str, optional): Name of the report to generate.
                Default is 'eq_hedge_returns-new'.
        """
        self.eq_hedge_xform_data = None
        super().__init__(filename=filename, report_name=report_name, new_index=new_strats)

    def xform_data(self):
        """
        Create a dictionary that updates returns data

        Returns
        -------
        new_data_dict : Dictionary
            Contains the updated information after adding new returns data

        """
        # Import data from bloomberg into dataframe and create dictionary with different frequencies
        eq_hedge_strats_data = dxf.BbgDataXformer(file_path=dl.UPDATE_DATA_FP + 'ups_data.xlsx',
                                                  sheet_name='bbg_d').data_xform

        # Import vrr returns dictionary
        vrr_data = dxf.VRRDataXformer(file_path=dl.UPDATE_DATA_FP + 'vrr_tracks_data.xlsx').data_xform

        self.eq_hedge_xform_data = {'eq_hedge_strats_data': eq_hedge_strats_data, 'vrr_data': vrr_data}

        # merge returns dictionaries
        return dm.merge_dicts_list(list(self.eq_hedge_xform_data.values()), drop_na=True)


class LiquidAltsReturnsUpdater(DataUpdater):
    def __init__(self, filename=None, report_name="all_liquid_alts_data"):
        super().__init__(filename, report_name)

    def xform_data(self):
        return {'nexen': NexenDataUpdater().data_dict, 'innocap': InnocapLiquidAltsDataUpdater().data_dict}

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

    def get_report_object(self):
        return rp.ReturnMktValueReport(self.report_name, self.data_dict, True)


class ITDOverlayDataUpdater(BbgDataUpdater):
    def __init__(self, filename='itd_overlay_data.xlsx', report_name='itd_overlay_returns', new_index=False):
        super().__init__(filename=filename, report_name=report_name, drop_na=False, new_index=new_index)

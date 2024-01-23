# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 2023

@author: Powis Forjoe
"""

import copy

import pandas as pd

from . import data_importer as di
from . import data_manager_new as dm


def copy_data(data):
    return copy.deepcopy(data) if type(data) == dict else data.copy()


def resample_data(df, freq):
    data = df.copy()
    data.index = pd.to_datetime(data.index)
    if not (freq == 'D'):
        data = data.resample(freq).ffill()
    return data


def format_data(df_index, freq='M', dropna=True, drop_zero=False):
    """
    Format dataframe, by freq, to return dataframe
    
    Parameters:
    df_index -- dataframe
    
    Returns:
    dataframe
    """
    data = resample_data(df_index, freq)
    data = data.pct_change(1)
    data = data.iloc[1:, ]
    if dropna:
        data.dropna(inplace=True)

    if drop_zero:
        data = data.loc[(data != 0).any(1)]
    return data


def get_data_dict(data, index_data=False, dropna=True, xform=True):
    """
    Converts daily data into a dictionary of dataframes containing returns 
    data of different frequencies
    
    Parameters:
    data -- df
    data_type -- string
    
    Returns:
    dictionary
    """
    freq_data = dm.get_freq(data)
    freq_list = dm.switch_freq_list(freq_data)
    data_dict = {}
    try:
        data.index = pd.to_datetime(data.index)
    except TypeError:
        pass

    if index_data is False:
        # try:
        #     data.index = pd.to_datetime(data.index)
        # except TypeError:
        #     pass
        data = get_prices_df(data)
    for freq in freq_list:
        freq_string = dm.switch_freq_string(freq)
        if xform:
            data_dict[freq_string] = format_data(data, freq, dropna=dropna)
        else:
            data_dict[freq_string] = resample_data(data, freq)
    return data_dict


def get_prices_df(df_returns):
    """"
    Converts returns dataframe to index level dataframe

    Parameters:
    df_returns -- returns dataframe

    Returns:
    index price level - dataframe
    """

    df_index = 100 * (1 + df_returns).cumprod()

    return update_df_index(df_index)


def update_df_index(df_index):
    # insert extra row at top for first month of 100
    data = []
    data.insert(0, {})
    df_prices = pd.concat([pd.DataFrame(data), df_index])

    # fill columns with 100 for row 1
    for col in df_prices.columns:
        df_prices[col][0] = 100

    # update index to prior month
    df_prices.index.names = ['Dates']
    df_prices.reset_index(inplace=True)
    df_prices['Dates'][0] = df_index.index[0] - pd.DateOffset(months=1)
    df_prices.set_index('Dates', inplace=True)

    return df_prices


def get_price_series(return_series):
    price_series = return_series.copy()
    price_series[0] = return_series[0] + 1
    for i in range(1, len(return_series)):
        price_series[i] = (return_series[i] + 1) * price_series[i - 1]
    return price_series


class dataXformer:
    def __init__(self, filepath, sheet_name=0, data_source='custom', col_dict={}
                 , drop_na=True, index_data=False, format_data=False):
        """
        Converts excel file into a dataXformer object

        Parameters
        ----------
        filepath : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of excel sheet(s) or positions. The default is 0.
        data_source : string, optional
            source of excel file. The default is 'custom'.
        freq : string, optional
            frequency of data. The default is '1M'.
        col_list : list of strings, optional
            column names. The default is [].
        drop_na : bool, optional
            drop NaN values. The default is False.
        index_data : bool, optional
            The default is False.
        format_data : bool, optional
            The default is False.

        Returns
        -------
        dataXformer object

        """
        self.filepath = filepath
        self.sheet_name = sheet_name
        self.data_source = data_source
        self.drop_na = drop_na
        self.index_data = index_data
        self.format_data = format_data
        self.col_dict = col_dict
        # imported data
        self.dataImporter = self.get_importer()
        self.data_import = self.dataImporter.data_import
        self.data_dict = self.dataImporter.data_dict
        # transformed data
        self.data_xform = self.xform_data()

    def get_importer(self):
        data_importer = di.dataImporter(filepath=self.filepath, sheet_name=self.sheet_name,
                                        data_source=self.data_source,
                                        col_dict=self.col_dict, drop_na=self.drop_na, index_data=self.index_data)
        if data_importer.data_dict:
            for key in data_importer.data_import:
                if isinstance(data_importer.data_import[key], pd.DataFrame):
                    freq = dm.get_freq(data_importer.data_import[key])
                    data_importer.data_import[key] = dm.resample_data(data_importer.data_import[key], freq)
        return data_importer

    # return dataframe or dictionary of dataframes
    def xform_data(self):
        if self.data_dict:
            return self.data_import.copy()
        else:
            return get_data_dict(self.data_import, self.index_data, xform=self.format_data)


class nexenDataXformer(dataXformer):
    def __init__(self, filepath, data_source='nexen', col_dict=di.NEXEN_DATA_COL_DICT):
        """
        Converts excel file into a nexenDataXformer object

        Parameters
        ----------
        filepath : string
            Valid string path.
        data_source : string, optional
            source of excel file. The default is 'nexen'.
        Returns
        -------
        nexenDataXformer object

        """

        super().__init__(filepath=filepath, data_source=data_source, col_dict=col_dict)

    def get_importer(self):
        return di.nexenDataImporter(filepath=self.filepath, col_dict=self.col_dict)

    # return dictionary of dataframes (returns and market values)
    def xform_data(self):
        # pull out returns data into dataframe
        returns_df = self.data_import.pivot_table(values='Return', index='Dates', columns='Name')
        returns_df /= 100
        # pull out market values data into dataframe
        mv_df = self.data_import.pivot_table(values='Market Value', index='Dates', columns='Name')
        return {'returns': returns_df, 'market_values': mv_df}


class nexenBmkDataXformer(nexenDataXformer):
    def __init__(self, filepath, col_dict=di.NEXEN_DATA_COL_DICT | di.NEXEN_BMK_DATA_COL_DICT):
        """
        Converts excel file into a nexenDataXformer object

        Parameters
        ----------
        filepath : string
            Valid string path.
        data_source : string, optional
            source of excel file. The default is 'nexen'.
        Returns
        -------
        nexenDataXformer object

        """

        super().__init__(filepath=filepath, col_dict=col_dict)

    # return bmk df
    def xform_data(self):
        # pull out returns data into dataframe
        bmk_returns_df = self.data_import.pivot_table(values='Benchmark Return', index='Dates',
                                                      columns='Benchmark Name')
        bmk_returns_df /= 100
        return bmk_returns_df


class bbgDataXformer(dataXformer):
    def __init__(self, filepath, sheet_name='data', data_source='bbg',
                 index_data=True, format_data=True):
        """
        Converts bbg excel file into a bbgDataXformer object

        Parameters
        ----------
        filepath : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of excel sheet(s) or positions. The default is 'data'.
        data_source : string, optional
            source of excel file. The default is 'bbg'.
        col_dict : 
        index_data : bool, optional
            The default is True.
        format_data : bool, optional
            The default is True.

        Returns
        -------
        bbgDataXformer object

        """
        super().__init__(filepath=filepath, sheet_name=sheet_name, data_source=data_source,
                         index_data=index_data, format_data=format_data)
        self.col_dict = self.dataImporter.col_dict

    def get_importer(self):
        return di.bbgDataImporter(filepath=self.filepath, sheet_name=self.sheet_name)


class innocapDataXformer(dataXformer):
    def __init__(self, filepath, sheet_name=0, data_source='innocap',
                 col_dict={'Date': 'Dates', 'Account Name': 'Name', 'MTD Return': 'Return',
                           'Market Value': 'Market Value'}):
        """
        Converts innocap excel file into an innocapDataXformer object

        Parameters
        ----------
        filepath : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of excel sheet(s) or positions. The default is 0.
        data_source : string, optional
            source of excel file. The default is 'innocap'.
        col_dictt : dict, optional
        
        Returns
        -------
        innocapDataXformer object

        """

        super().__init__(filepath=filepath, sheet_name=sheet_name, data_source=data_source, col_dict=col_dict)

    def get_importer(self):
        return di.innocapDataImporter(filepath=self.filepath, col_dict=self.col_dict)

    # return dictionary of dataframes (returns and market values)
    def xform_data(self):
        # pull out returns data into dataframe
        returns_df = self.data_import.pivot_table(values='Return', index='Dates', columns='Name')
        freq = dm.get_freq(returns_df)
        returns_df = resample_data(returns_df, freq)
        returns_df /= 100
        # pull out market values data into dataframe
        mv_df = self.data_import.pivot_table(values='Market Value', index='Dates', columns='Name')
        mv_df = resample_data(mv_df, freq)
        return {'returns': returns_df, 'market_values': mv_df}


# TODO: test
class innocapExpDataXformer(innocapDataXformer):
    def __init__(self, filepath, sheet_name=0, data_source='innocap',
                 col_list=['Dates', 'Name', 'Asset Class', '10 Yr Equiv Net % Notional']):
        """
        Converts innocap exposure excel file into an innocapExpDataXformer object

        Parameters
        ----------
        filepath : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of excel sheet(s) or positions. The default is 0.
        data_source : string, optional
            source of excel file. The default is 'innocap'.
        freq : string, optional
            frequency of data. The default is '1M'.
        col_list : list of strings, optional
            column names. The default is ['Dates', 'Name', 'Asset Class','10 Yr Equiv Net % Notional'].
        
        Returns
        -------
        innocapExpDataXformer object

        """

        super().__init__(filepath, sheet_name, data_source)

    # return dictionary of dataframes (managers asset class exposures)
    def xform_data(self):
        names_list = [x for x in list(self.data_import.Name.unique()) if x == x]
        exposure_dict = {}
        for name in names_list:
            name_df = self.data_import.loc[self.data_import['Name'] == name]
            exposure_dict[name] = name_df.pivot_table(values='10 Yr Equiv Net % Notional', index='Dates',
                                                      columns='Asset Class')
            exposure_dict[name] = resample_data(exposure_dict[name], self.freq)
        return exposure_dict


class vrrDataXformer(dataXformer):
    def __init__(self, filepath, sheet_name=["VRR", "VRR 2", "VRR Trend"], data_source='custom',
                 index_data=True, drop_na=False):
        """
        Converts excel file into a vrrDataXformer object

        Parameters
        ----------
        filepath : string
            Valid string path.
        data_source : string, optional
            source of excel file. The default is 'custom'.
        Returns
        -------
        vrrDataXformer object

        """
        super().__init__(filepath=filepath, sheet_name=sheet_name, data_source=data_source, drop_na=drop_na,
                         index_data=index_data)

    def add_bps(self, vrr_returns_dict, add_back=[.0025, .005, .005]):
        '''
        Adds bps back to the returns for the vrr strategy

        Parameters
        ----------
        vrr_dict : dictionary
            DESCRIPTION.
        add_back : float
            DESCRIPTION. The default is .0025.

        Returns
        -------
        temp_dict : dictionary
            dictionary of VRR returns with bips added to it

        '''
        # create empty dictionary
        temp_dict = {}

        # iterate through keys of a dictionary
        for freq_string in vrr_returns_dict:
            # set dataframe equal to dictionary's key
            temp_df = vrr_returns_dict[freq_string].copy()

            # set variable equal to the frequency of key
            freq = dm.switch_string_freq(freq_string)

            # set annual fees for each frew
            bps = [value / (dm.switch_freq_int(freq)) for value in add_back]

            # add to dataframe
            temp_df += bps

            # add value to the temp dictionary
            temp_dict[freq_string] = temp_df
        return temp_dict

    def xform_data(self):
        data = pd.concat(self.data_import.values(), axis=1)
        vrr_returns_dict = get_data_dict(data, self.index_data)

        return self.add_bps(vrr_returns_dict)

# class putSpreadDataXformer(dataXformer):
#     def __init__(self, filepath, data_source='put_spread'):
#         """
#         Converts excel file into a putSpreadDataXformer object

#         Parameters
#         ----------
#         filepath : string
#             Valid string path.
#         data_source : string, optional
#             source of excel file. The default is 'put_spread'.
#         Returns
#         -------
#         putSpreadDataXformer object

#         """

#         super().__init__(filepath,data_source)

#     def import_data(self):
#         return di.putspreadDataImporter(self.filepath).data_import   

#     def xform_data(self):

#         #only keep 'Put Spread' column
#         data = self.data_import[['Put Spread']]

#         #rename column 
#         data.columns = ['99%/90% Put Spread']

#         #get price dataframe
#         data = get_prices_df(data)

#         #get put spread data dict
#         data_dict = get_data_dict(data, index_data = True)

#         return data_dict

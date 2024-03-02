# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 2023

@author: Powis Forjoe
"""

import pandas as pd
from . import data_importer as di
from . import data_manager_new as dm
from . import data_lists as dl


def get_new_strat_data(file_path, sheet_name='data', freq='M', index_data=False):
    return get_new_strategy_returns_data(file_path=file_path, sheet_name=sheet_name, freq=freq,
                                         return_data=not index_data)


def get_new_strategy_returns_data(file_path, sheet_name, freq='D', return_data=True, strategy_list=None):
    """
    dataframe of strategy returns

    Parameters:
    filename -- string
    sheet_name -- string
    strategy_list -- list

    Returns:
    dataframe
    """
    if strategy_list is None:
        strategy_list = []
    strategy_df = di.ExcelImporter(file_path=file_path, sheet_name=sheet_name, index_col=0).read_excel_data()
    if strategy_list:
        strategy_df.columns = strategy_list
    if return_data:
        return resample_df(strategy_df, freq)
    else:
        return format_df(df_index=strategy_df, freq=freq)


def convert_freq(data_df, freq='M'):
    data_freq = dm.get_freq(data_df)
    if dm.switch_freq_int(data_freq) > dm.switch_freq_int(freq):
        return format_df(PriceData().get_price_data(data_df), freq=freq)
    else:
        print(f'Warning: Cannot convert data freq to {dm.switch_freq_string(freq)}')
        return dm.copy_data(data_df)


def resample_df(df, freq):
    data_df = dm.copy_data(df)
    data_df.index = pd.to_datetime(data_df.index)
    if not (freq == 'D'):
        data_df = data_df.resample(freq).ffill(limit=1)
    return data_df


def resample_df2(df, freq):
    data_df = dm.copy_data(df)
    data_df.index = pd.to_datetime(data_df.index)
    if freq == 'D':
        return data_df.groupby(pd.Grouper(freq='B')).last()
    else:
        return data_df.groupby(pd.Grouper(freq=freq)).last()


def format_df(df_index, freq='M', drop_na=True, drop_zero=False):
    """
    Format dataframe, by freq, to return dataframe

    Parameters:
    df_index -- dataframe

    Returns:
    dataframe
    """
    data_df = resample_df(df_index, freq)
    data_df = data_df.pct_change(1)
    data_df = data_df.iloc[1:, ]
    # data = replace_zero_with_nan(data)
    if drop_na:
        data_df.dropna(inplace=True)

    if drop_zero:
        data_df = data_df.loc[(data_df != 0).any(1)]
    return data_df


def get_data_dict(data_df, index_data=False, drop_na=True, xform=True):
    """
    Converts daily data into a dictionary of dataframes containing returns
    data of different frequencies

    Parameters:
    data -- df
    data_type -- string

    Returns:
    dictionary
    """
    freq_data = dm.get_freq(data_df)
    freq_list = dm.switch_freq_list(freq_data)
    data_dict = {}
    try:
        data_df.index = pd.to_datetime(data_df.index)
    except TypeError:
        pass

    if index_data is False:
        data_df = PriceData().get_price_data(data_df)
    for freq in freq_list:
        freq_string = dm.switch_freq_string(freq)
        if xform:
            data_dict[freq_string] = format_df(data_df, freq, drop_na=drop_na)
        else:
            data_dict[freq_string] = resample_df(data_df, freq)
    return data_dict


class PriceData:
    def __init__(self, multiplier=100):
        self.multiplier = multiplier

    def get_price_data(self, returns_data):
        """"
        Converts returns dataframe to index level dataframe
        Returns:
        index price level - dataframe
        """

        index_data = self.multiplier * (1 + returns_data).cumprod()
        # price_data = self.multiplier * (self.returns_data.add(1).cumprod())
        if isinstance(index_data, pd.Series):
            return self.update_index_data(index_data)[0]
        else:
            return self.update_index_data(index_data)

    def update_index_data(self, index_data):
        # insert extra row at top for first month of 100
        data = [{}]
        freq = dm.get_freq(index_data)
        price_data = pd.concat([pd.DataFrame(data), index_data])

        # fill columns with multiplier for row 1
        for col in price_data:
            idx_int = dm.get_first_valid_index(price_data[col]) - 1
            price_data[col].iloc[idx_int] = self.multiplier

        # update index to prior month
        price_data.index.names = ['Dates']
        price_data.reset_index(inplace=True)
        pd.set_option('mode.chained_assignment', None)
        price_data.loc[:, 'Dates'][0] = index_data.index[0] - dm.get_date_offset(freq)
        price_data.set_index('Dates', inplace=True)

        return price_data


class DataXformer:

    def __init__(self, file_path, sheet_name=0, col_dict=None, drop_na=True, index_data=False,
                 format_data=False):
        """
        Converts Excel file into a dataXformer object

        Parameters
        ----------
        file_path : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of Excel sheet(s) or positions. The default is 0.
        col_dict : dictionary, optional
            The default is {}.
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
        if col_dict is None:
            col_dict = {}
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.drop_na = drop_na
        self.index_data = index_data
        self.format_data = format_data
        self.col_dict = col_dict
        # imported data
        self.dataImporter = self.get_importer()
        self.data_import = self.dataImporter.data_import
        self.data_dict_bool = self.dataImporter.data_dict_bool
        # transformed data
        self.data_xform = self.xform_data()

    def get_importer(self):
        data_importer = di.DataImporter(file_path=self.file_path, sheet_name=self.sheet_name,
                                        col_dict=self.col_dict, drop_na=self.drop_na, index_data=self.index_data)
        if data_importer.data_dict_bool:
            for key in data_importer.data_import:
                if isinstance(data_importer.data_import[key], pd.DataFrame):
                    freq = dm.get_freq(data_importer.data_import[key])
                    data_importer.data_import[key] = resample_df(data_importer.data_import[key], freq)
        return data_importer

    # return dataframe or dictionary of dataframes

    def xform_data(self):
        if self.data_dict_bool:
            return dm.copy_data(self.data_import)
        else:
            return get_data_dict(self.data_import, self.index_data, drop_na=self.drop_na, xform=self.format_data)


class NexenDataXformer(DataXformer):

    def __init__(self, file_path, col_dict=None):
        """
        Converts Excel file into a nexenDataXformer object

        Parameters
        ----------
        file_path : string
            Valid string path.
        Returns
        -------
        nexenDataXformer object

        """
        if col_dict is None:
            col_dict = dl.NEXEN_DATA_COL_DICT
        super().__init__(file_path=file_path, col_dict=col_dict)

    def get_importer(self):
        return di.NexenDataImporter(file_path=self.file_path, col_dict=self.col_dict)

    # return dictionary of dataframes (returns and market values)
    def xform_data(self):
        # pull out returns data into dataframe
        returns_df = self.data_import.pivot_table(values='Return', index='Dates', columns='Name')
        returns_df /= 100
        # pull out market values data into dataframe
        mv_df = self.data_import.pivot_table(values='Market Value', index='Dates', columns='Name')
        return {'returns': returns_df, 'market_values': mv_df}


class NexenBmkDataXformer(NexenDataXformer):

    def __init__(self, file_path):
        """
        Converts Excel file into a nexenDataXformer object

        Parameters
        ----------
        file_path : string
            Valid string path.
        Returns
        -------
        nexenDataXformer object

        """

        super().__init__(file_path=file_path, col_dict=dl.NEXEN_DATA_COL_DICT | dl.NEXEN_BMK_DATA_COL_DICT)

    # return bmk df
    def xform_data(self):
        # pull out returns data into dataframe
        returns_df = self.data_import.pivot_table(values='Benchmark Return', index='Dates',
                                                  columns='Benchmark Name')
        returns_df /= 100
        return returns_df


class BbgDataXformer(DataXformer):

    def __init__(self, file_path, sheet_name='data', drop_na=True, index_data=True, format_data=True):
        """
        Converts bbg Excel file into a bbgDataXformer object

        Parameters
        ----------
        file_path : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of Excel sheet(s) or positions. The default is 'data'.
        index_data : bool, optional
            The default is True.
        format_data : bool, optional
            The default is True.

        Returns
        -------
        bbgDataXformer object

        """
        super().__init__(file_path=file_path, sheet_name=sheet_name, drop_na=drop_na,
                         index_data=index_data, format_data=format_data)
        self.col_dict = self.dataImporter.col_dict

    def get_importer(self):
        return di.BbgDataImporter(file_path=self.file_path, sheet_name=self.sheet_name, drop_na=self.drop_na)


class InnocapDataXformer(DataXformer):

    def __init__(self, file_path, sheet_name=0, freq='M', col_dict=None):
        """
        Converts innocap Excel file into an innocapDataXformer object

        Parameters
        ----------
        file_path : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of Excel sheet(s) or positions. The default is 0.
        col_dict : dict, optional

        Returns
        -------
        innocapDataXformer object

        """
        if col_dict is None:
            col_dict = dl.INNOCAP_RET_DATA_COL_DICT
        self.freq = freq
        super().__init__(file_path=file_path, sheet_name=sheet_name, col_dict=col_dict)

    def get_importer(self):
        return di.InnocapDataImporter(file_path=self.file_path, col_dict=self.col_dict)

    # return dictionary of dataframes (returns and market values)
    def xform_data(self):
        # pull out returns data into dataframe
        returns_df = self.data_import.pivot_table(values='Return', index='Dates', columns='Name')
        # freq = dm.get_freq(returns_df)
        returns_df = resample_df(returns_df, self.freq)
        returns_df /= 100
        # pull out market values data into dataframe
        mv_df = self.data_import.pivot_table(values='Market Value', index='Dates', columns='Name')
        mv_df = resample_df(mv_df, self.freq)
        return {'returns': returns_df, 'market_values': mv_df}


# TODO: test
class InnocapExpDataXformer(InnocapDataXformer):

    def __init__(self, file_path, sheet_name=0, freq='D'):
        """
        Converts innocap exposure Excel file into an innocapExpDataXformer object

        Parameters
        ----------
        file_path : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of Excel sheet(s) or positions. The default is 0.


        Returns
        -------
        innocapExpDataXformer object

        """

        super().__init__(file_path, sheet_name, freq=freq, col_dict=dl.INNOCAP_EXP_DATA_COL_DICT)

    # return dictionary of dataframes (managers asset class exposures)
    def xform_data(self):
        names_list = [x for x in list(self.data_import.Name.unique()) if x == x]
        exposure_dict = {}
        freq = dm.get_freq(self.data_import)
        for name in names_list:
            name_df = self.data_import.loc[self.data_import['Name'] == name]
            exposure_dict[name] = name_df.pivot_table(values='10 Yr Equiv Net % Notional', index='Dates',
                                                      columns='Asset Class')
            exposure_dict[name] = resample_df(exposure_dict[name], freq)
        return exposure_dict


class VRRDataXformer(DataXformer):

    def __init__(self, file_path, sheet_name=None, index_data=True, drop_na=False):
        """
        Converts Excel file into a vrrDataXformer object

        Parameters
        ----------
        file_path : string
            Valid string path.
        Returns
        -------
        vrrDataXformer object

        """
        if sheet_name is None:
            sheet_name = ["VRR", "VRR 2", "VRR Trend"]
        super().__init__(file_path=file_path, sheet_name=sheet_name, drop_na=drop_na, index_data=index_data)

    @staticmethod
    def add_bps(vrr_returns_dict, add_back=None):
        """
        Adds bps back to the returns for the vrr strategy

        Parameters
        ----------
        vrr_returns_dict : dictionary
            DESCRIPTION.
        add_back : float
            DESCRIPTION. The default is .0025.

        Returns
        -------
        temp_dict : dictionary of VRR returns with bips added to it

        """
        # create empty dictionary
        if add_back is None:
            add_back = [.0025, .005, .005]
        temp_dict = {}

        # iterate through keys of a dictionary
        for freq_string in vrr_returns_dict:
            # set dataframe equal to dictionary's key
            temp_df = vrr_returns_dict[freq_string].copy()

            # set variable equal to the frequency of key
            freq = dm.switch_string_freq(freq_string)

            # set annual fees for each freq
            bps = [value / (dm.switch_freq_int(freq)) for value in add_back]

            # add to dataframe
            temp_df += bps

            # add value to the temp dictionary
            temp_dict[freq_string] = temp_df
        return temp_dict

    def xform_data(self):
        data = pd.concat(self.data_import.values(), axis=1)
        vrr_returns_dict = get_data_dict(data_df=data, index_data=self.index_data)

        return self.add_bps(vrr_returns_dict)

# class putSpreadDataXformer(dataXformer):
#     def __init__(self, file_path, data_source='put_spread'):
#         """
#         Converts Excel file into a putSpreadDataXformer object

#         Parameters
#         ----------
#         file_path : string
#             Valid string path.
#         data_source : string, optional
#             source of Excel file. The default is 'put_spread'.
#         Returns
#         -------
#         putSpreadDataXformer object

#         """

#         super().__init__(file_path,data_source)

#     def import_data(self):
#         return di.PutSpreadDataImporter(self.file_path).data_import

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

# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 2023

@author: Powis Forjoe
"""

import pandas as pd
from .import data_importer as di
from .import data_manager as dm

def copy_data(data):
    if type(data) == dict:
        dict_copy = {}
        for key in data:
            dict_copy[key] = data[key].copy()
        return dict_copy
    else:
        return data.copy()
    
def resample_data(df, freq="1M"):
    data = df.copy()
    data.index = pd.to_datetime(data.index)
    if not(freq == '1D'):
       data = data.resample(freq).ffill()
    return data

def format_data(df_index, freq="1M", dropna=True, drop_zero=False):
    """
    Format dataframe, by freq, to return dataframe
    
    Parameters:
    df_index -- dataframe
    freq -- string ('1M', '1W', '1D')
    
    Returns:
    dataframe
    """
    data = resample_data(df_index, freq)
    data = data.pct_change(1)
    data = data.iloc[1:,]
    if dropna:
        data.dropna(inplace=True)
        
    if drop_zero:
        data = data.loc[(data!=0).any(1)]
    return data

def get_data_dict(data, data_type='index', dropna=True, drop_zero=True):
    """
    Converts daily data into a dictionary of dataframes containing returns 
    data of different frequencies
    
    Parameters:
    data -- df
    data_type -- string
    
    Returns:
    dictionary
    """
    freq_list = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
    data_dict = {}
    if data_type != 'index':
        try:
            data.index = pd.to_datetime(data.index)
        except TypeError:
            pass
        data = get_prices_df(data)
    for freq_string in freq_list:
        data_dict[freq_string] = format_data(data, dm.switch_string_freq(freq_string),dropna, drop_zero)
    return data_dict

def get_prices_df(df_returns):
    """"
    Converts returns dataframe to index level dataframe

    Parameters:
    df_returns -- returns dataframe

    Returns:
    index price level - dataframe
    """
    
    df_index = 100*(1 + df_returns).cumprod()
    
    return update_df_index(df_index)

def update_df_index(df_index):
    
    #insert extra row at top for first month of 100
    data = []
    data.insert(0,{})
    df_prices = pd.concat([pd.DataFrame(data), df_index])
    
    #fill columns with 100 for row 1
    for col in df_prices.columns:
        df_prices[col][0] = 100

    #update index to prior month    
    df_prices.index.names = ['Dates']
    df_prices.reset_index(inplace=True)
    df_prices['Dates'][0] = df_index.index[0] - pd.DateOffset(months=1)
    df_prices.set_index('Dates', inplace=True)
    
    return df_prices

def get_price_series(return_series):
    price_series = return_series.copy()
    price_series[0] = return_series[0] + 1
    for i in range(1, len(return_series)):
        price_series[i] = (return_series[i] + 1) * price_series[i-1]
    return price_series

class dataXformer():
    def __init__(self, filepath, sheet_name=0, data_source='custom', freq='1M', col_list=[]
                 , drop_na = True, index_data = False, format_data = False):
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
        self.freq = freq
        self.drop_na = drop_na
        self.index_data = index_data
        self.format_data = format_data
        # self.drop_zero = drop_zero
        self.col_list = col_list
        #imported data
        self.data_import = self.import_data()
        #transformed data
        self.data_xform = self.xform_data()        
    
    def import_data(self):
        #pull data from dataImporter object
        return di.dataImporter(self.filepath, self.sheet_name, data_source=self.data_source, drop_na=self.drop_na,
                                           index_data=self.index_data).data
    #return dataframe or dictionary of dataframes
    def xform_data(self):
        if self.format_data:
            #transform data to dictionary of return dataframes if Freq is Daily
            if self.freq == '1D':
                return get_data_dict(self.data_import)
            else:
                #transform data to return dataframe if index_data is True
                if self.index_data:
                    return format_data(self.data_import,self.freq)
                else:
                    #resample data
                    return resample_data(self.data_import,self.freq)

class nexenDataXformer(dataXformer):
    def __init__(self, filepath, data_source='nexen'):
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
        
        dataXformer.__init__(self,filepath,data_source)
        
    def import_data(self):
        #pull data from nexenDataImporter object
        return di.nexenDataImporter(self.filepath).data
    
    #return dictionary of dataframes (returns and market values)
    def xform_data(self):
        #pull out returns data into dataframe
        returns_df = self.data_import.pivot_table(values='Return', index='Dates', columns='Name')
        returns_df /=100
        #pull out market values data into dataframe
        mv_df = self.data_import.pivot_table(values='Market Value', index='Dates', columns='Name')
        return {'returns': returns_df, 'market_values': mv_df}

class bbgDataXformer(dataXformer):
    def __init__(self, filepath, sheet_name='data', data_source='bbg', freq='1M', col_list=[]
                 , index_data = True, format_data = True):
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
        freq : string, optional
            frequency of data. The default is '1M'.
        col_list : list of strings, optional
            column names. The default is [].
        index_data : bool, optional
            The default is True.
        format_data : bool, optional
            The default is True.

        Returns
        -------
        bbgDataXformer object

        """
        dataXformer.__init__(self,filepath,sheet_name,data_source,freq, col_list
                             ,index_data=index_data, format_data=format_data)
     
    def import_data(self):
        #pull data from bbgDataImporter object
        return di.bbgDataImporter(self.filepath,self.sheet_name, col_list=self.col_list).data
   
    # def xform_data(self):
    #     return resample_data(self.data_import,self.freq)
class innocapDataXformer(dataXformer):
    def __init__(self, filepath,sheet_name=0, data_source='innocap', freq='1M',
                 col_list=['Dates', 'Name', 'Market Value', 'Return']):
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
        freq : string, optional
            frequency of data. The default is '1M'.
        col_list : list of strings, optional
            column names. The default is ['Dates', 'Name', 'Market Value', 'Return'].
        
        Returns
        -------
        innocapDataXformer object

        """
        
        dataXformer.__init__(self,filepath, sheet_name,data_source, freq,col_list)
        
    def import_data(self):
        #pull data from innocapDataImporter object
        return di.innocapDataImporter(self.filepath, col_list=self.col_list).data
    
    #return dictionary of dataframes (returns and market values)
    def xform_data(self):
        #pull out returns data into dataframe
        returns_df = self.data_import.pivot_table(values='Return', index='Dates', columns='Name')
        returns_df = resample_data(returns_df, self.freq)
        returns_df /=100
        #pull out market values data into dataframe
        mv_df = self.data_import.pivot_table(values='Market Value', index='Dates', columns='Name')
        mv_df = resample_data(mv_df, self.freq)
        return {'returns': returns_df, 'market_values': mv_df}

class innocapExpDataXformer(innocapDataXformer):
    def __init__(self, filepath,sheet_name=0, data_source='innocap', freq='1M',
                 col_list=['Dates', 'Name', 'Asset Class','10 Yr Equiv Net % Notional']):
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
        
        innocapDataXformer.__init__(self,filepath,sheet_name,data_source,freq, col_list)
        
    #return dictionary of dataframes (managers asset class exposures)
    def xform_data(self):
        names_list = [x for x in list(self.data_import.Name.unique()) if x == x]
        exposure_dict = {}
        for name in names_list:
            name_df = self.data_import.loc[self.data_import['Name'] == name]
            exposure_dict[name] = name_df.pivot_table(values='10 Yr Equiv Net % Notional', index='Dates', columns='Asset Class')
            exposure_dict[name] = resample_data(exposure_dict[name], self.freq)
        return exposure_dict

#TODO: create vrrDataXformer
class vrrDataXformer():
    pass

#TODO: create putSpreadDataXformer
class putSpreadDataXformer():
    pass                 
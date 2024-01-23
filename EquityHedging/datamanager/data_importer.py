# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 2023

@author: Powis Forjoe
"""

# import os
import re
import zipfile

import pandas as pd

from . import data_manager_new as dm

NEXEN_DATA_COL_DICT = {'Account Name\n': 'Name', 'Account Id\n': 'Account Id',
                       'Return Type\n': 'Return Type', 'As Of Date\n': 'Dates',
                       'Market Value\n': 'Market Value', 'Account Monthly Return\n': 'Return'}
NEXEN_BMK_DATA_COL_DICT = {'As Of Date\n': 'Dates','Benchmark Name\n': 'Benchmark Name',
                           'Benchmark Monthly Return\n': 'Benchmark Return'}
                       
#TODO: add skip_cols
def read_excel_data(filepath, sheet_name=0, index_col = 0, skip_rows = [], use_cols = None):
    """
    Reads an excel file into a dataframe or dictionary 

    Parameters
    ----------
    filepath : string
        Valid string path.
    sheet_name : int, string, list of strings, ints, optional
        name(s) of excel sheet(s) or positions. The default is 0.
    index_col : int, optional
        The default is 0.
    skip_rows : list, optional
        list of rows to skip when importing. The default is [].
    
    Returns
    -------
    dataframe/dictionary of dataframes

    """
    # dm.get_real_cols(ret_data)
    return pd.read_excel(filepath, sheet_name, index_col = index_col, 
                             skiprows=skip_rows)
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

#copied from stackoverflow, only works for xlsx files
#TODO: Add xls if possible
def get_excel_sheet_names(file_path):
    sheets = []
    with zipfile.ZipFile(file_path, 'r') as zip_ref: xml = zip_ref.read("xl/workbook.xml").decode("utf-8")
    for s_tag in  re.findall("<sheet [^>]*", xml) : sheets.append(  re.search('name="[^"]*', s_tag).group(0)[6:])
    return sheets


class dataImporter:
    def __init__(self, filepath, sheet_name=0, index_col = 0, skip_rows = [], 
                 data_source='custom', col_dict = {}, drop_na = True, index_data = False):
        """
        Reads an excel file into a dataImporter object 

        Parameters
        ----------
        filepath : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of excel sheet(s) or positions. The default is 0.
        index_col : int, optional
            The default is 0.
        skip_rows : list, optional
            list of rows to skip when importing. The default is [].
        data_source : string, optional
            source of excel file. The default is 'custom'.
        col_dict : 
        drop_na : bool, optional
            drop NaN values. The default is True.
        index_data : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        dataImporter object

        """
        self.filepath = filepath
        self.sheet_name = sheet_name #if sheet_name != 0 else get_excel_sheet_names(self.filepath)
        self.index_col = index_col
        self.skip_rows = skip_rows
        self.data_source = data_source
        self.col_dict = col_dict
        self.drop_na = drop_na
        self.index_data = index_data
        self.data_import = self.import_data()
        self.data_dict = isinstance(self.data_import, dict)
                
    def import_data(self):
        """
        import data from an excel file into a Dataframe or Dictionary

        Returns
        -------
        dataframe or Dictionary of dataframes
        
        """
        data = read_excel_data(self.filepath, self.sheet_name, index_col = self.index_col, 
                             skip_rows=self.skip_rows)
        #drop nas
        if self.drop_na:
            data = dm.drop_nas(data)
        
        #rename columns
        if bool(self.col_dict):
            data = dm.rename_columns(data, self.col_dict)
        
        if isinstance(data, dict):
            self.data_dict = True
            self.sheet_name = list(data.keys())
        
        return data

class innocapDataImporter(dataImporter):
    def __init__(self, filepath ,sheet_name = 0, index_col=None, skip_rows=[0,1],
                 data_source='innocap', col_dict={}, drop_na=False, index_data = False):
        """
        Reads an excel file into an innocapDataImporter object 

        Parameters
        ----------
        filepath : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of excel sheet(s) or positions. The default is 0.
        index_col : int, optional
            The default is None.
        skip_rows : list, optional
            list of rows to skip when importing. The default is [0,1].
        data_source : string, optional
            source of excel file. The default is 'innocap'.
        col_dict : 
        drop_na : bool, optional
            drop NaN values. The default is False.
        index_data : bool, optional
            is the data index data or return data. The default is False.

        Returns
        -------
        innocapDataImporter object

        """
        super().__init__(filepath, sheet_name, index_col, skip_rows,
                              data_source, col_dict, drop_na, index_data)
            
class bbgDataImporter(innocapDataImporter):
    def __init__(self, filepath, sheet_name=0, index_col=0, skip_rows=[0,1,2,4,5,6],
                 data_source='bbg', drop_na=False, index_data=True):
        """
        Reads an excel file into an bbgDataImporter object 

        Parameters
        ----------
        filepath : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of excel sheet(s) or positions. The default is 0.
        index_col : int, optional
            The default is 0.
        skip_rows : list, optional
            list of rows to skip when importing. The default is [0,1,2,4,5,6].
        data_source : string, optional
            source of excel file. The default is 'bbg'.
        drop_na : bool, optional
            drop NaN values. The default is False.
        index_data : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        bbgDataImporter object

        """
        self.filepath = filepath
        self.col_dict = self.get_col_dict()
        
        super().__init__(filepath=self.filepath, sheet_name=sheet_name, index_col=index_col, skip_rows=skip_rows,
                         data_source=data_source, col_dict=self.col_dict, drop_na=drop_na, index_data=index_data)
        
        #rename index col
        if type(self.data_import) == dict:
            for keys in self.data_import:
                self.data_import[keys].index.names = ['Dates']
        else:
            self.data_import.index.names = ['Dates']
            
    def get_col_dict(self):
        try:
            keys_df = read_excel_data(filepath=self.filepath, sheet_name='key', index_col=None, use_cols='A:B')
            return keys_df.set_index('Index').to_dict()['Description']
        except Exception as e: 
            print(e)
            return {}
                
#TODO: clean this to only have dates , account name, market value and return
class nexenDataImporter(dataImporter):
    def __init__(self, filepath, sheet_name=0, index_col=None, skip_rows=[], data_source='nexen',
                 col_dict=NEXEN_DATA_COL_DICT, drop_na=False, index_data=False):
        """
        Reads an excel file into a nexenDataImporter object 

        Parameters
        ----------
        filepath : string
            Valid string path.
        sheet_name : int, string, list of strings, ints, optional
            name(s) of excel sheet(s) or positions. The default is 0.
        index_col : int, optional
            The default is None.
        skip_rows : list, optional
            list of rows to skip when importing. The default is [].
        data_source : string, optional
            source of excel file. The default is 'nexen'.
        drop_na : bool, optional
            drop NaN values. The default is False.
        index_data : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        nexenDataImporter object

        """
        super().__init__(filepath=filepath, sheet_name=sheet_name, index_col=index_col, skip_rows=skip_rows,
                         data_source=data_source, col_dict=col_dict, drop_na=drop_na, index_data=index_data)
        
        self.data_import = self.data_import[self.col_dict.values()] if bool(self.col_dict) else self.data_import


# class putspreadDataImporter(dataImporter):
#     def __init__(self, filepath ,sheet_name = "Daily", index_col=0, skip_rows=[1],
#                  data_source='custom', drop_na=False, index_data = False):
#         """
#         Reads an excel file into a putspreadDataImporter object 

#         Parameters
#         ----------
#         filepath : string
#             Valid string path.
#         sheet_name : int, string, list of strings, ints, optional
#             name(s) of excel sheet(s) or positions. The default is 0.
#         index_col : int, optional
#             The default is None.
#         skip_rows : list, optional
#             list of rows to skip when importing. The default is [].
#         data_source : string, optional
#             source of excel file. The default is 'nexen'.
#         drop_na : bool, optional
#             drop NaN values. The default is False.
#         index_data : TYPE, optional
#             DESCRIPTION. The default is False.

#         Returns
#         -------
#         putspreadDataImporter object

#         """
#         super().__init__(filepath, sheet_name, index_col, skip_rows,
#                               data_source,drop_na, index_data)
        
#         self.data_import.columns = ['99 Rep','Short Put','Put Spread']



# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 2023

@author: Powis Forjoe
"""

import pandas as pd
from .import data_manager as dm

def read_data(filepath, sheet_name=0, index_col = 0, skip_rows = []):
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
    return pd.read_excel(filepath, sheet_name, index_col = index_col, 
                             skiprows=skip_rows)


class dataImporter():
    def __init__(self, filepath, sheet_name=0, index_col = 0, skip_rows = [], 
                 data_source='custom', drop_na = True, index_data = False):
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
        drop_na : bool, optional
            drop NaN values. The default is True.
        index_data : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        dataImporter object

        """
        self.filepath = filepath
        self.sheet_name = sheet_name
        self.index_col = index_col
        self.skip_rows = skip_rows
        self.data_source = data_source
        self.drop_na = drop_na
        self.index_data = index_data
        self.data_import = self.import_data()
                
    def import_data(self):
        """
        import data from an excel file into a Dataframe or Dictionary

        Returns
        -------
        dataframe or Dictionary of dataframes
        
        """
        data = read_data(self.filepath, self.sheet_name, index_col = self.index_col, 
                             skip_rows=self.skip_rows)
        #drop nas
        if self.drop_na:
            data = dm.drop_nas(data)
            
        return data

class innocapDataImporter(dataImporter):
    def __init__(self, filepath ,sheet_name = 0, index_col=None, skip_rows=[0,1],
                 data_source='innocap', col_list=[],drop_na=False, index_data = False):
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
        col_list : list of strings, optional
            column names. The default is [].
        drop_na : bool, optional
            drop NaN values. The default is False.
        index_data : bool, optional
            is the data index data or return data. The default is False.

        Returns
        -------
        innocapDataImporter object

        """
        super().__init__(filepath, sheet_name, index_col, skip_rows,
                              data_source, drop_na, index_data)
        self.col_list = col_list
        
        #rename columns
        if self.col_list:
            self.data_import = dm.rename_columns(self.data_import, self.col_list)
    
class bbgDataImporter(innocapDataImporter):
    def __init__(self, filepath ,sheet_name = 0, index_col=0,skip_rows=[0,1,2,4,5,6],
                 data_source='bbg', col_list=[], drop_na=False, index_data = True):
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
        col_list : list of strings, optional
            column names. The default is [].
        drop_na : bool, optional
            drop NaN values. The default is False.
        index_data : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        bbgDataImporter object

        """
        super().__init__(filepath, sheet_name, index_col, skip_rows,
                                     data_source,col_list, drop_na, index_data)
        
        #rename index col
        if type(self.data_import) == dict:
            for keys in self.data_import:
                self.data_import[keys].index.names = ['Dates']
        else:
            self.data_import.index.names = ['Dates']

#TODO: clean this to only have dates , account name, market value and return
class nexenDataImporter(dataImporter):
    def __init__(self, filepath ,sheet_name = 0, index_col=None, skip_rows=[],
                 data_source='nexen', drop_na=False, index_data = False):
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
        super().__init__(filepath, sheet_name, index_col, skip_rows,
                              data_source,drop_na, index_data)
        
        self.data_import = self.data_import[['Account Name\n', 'Account Id\n', 'Return Type\n',
                               'As Of Date\n','Market Value\n', 'Account Monthly Return\n']]
        self.data_import.columns = ['Name', 'Account Id', 'Return Type', 'Dates', 'Market Value', 'Return']

#TODO: make data_source 'custom'
class putspreadDataImporter(dataImporter):
    def __init__(self, filepath ,sheet_name = "Daily", index_col=0, skip_rows=[1],
                 data_source='put_spread', drop_na=False, index_data = False):
        """
        Reads an excel file into a putspreadDataImporter object 

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
        putspreadDataImporter object

        """
        super().__init__(filepath, sheet_name, index_col, skip_rows,
                              data_source,drop_na, index_data)
        
        self.data_import.columns = ['99 Rep','Short Put','Put Spread']

    #TODO: Delete pass
    pass  
     
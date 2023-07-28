# -*- coding: utf-8 -*-
"""
Created on Fri July  7 2023

@author: Powis Forjoe
"""

import pandas as pd
# from ...analytics import summary
# from ...analytics import util
# from ...analytics.corr_stats import get_corr_rank_data
# from ...analytics.historical_selloffs import get_hist_sim_table
# from ...datamanager import data_manager as dm
from .import new_sheets
import os

def get_filepath(report_name, data_file=False):
    """
    Gets the file path where the report will be stored

    Parameters
    ----------
    report_name : String
        Name of report
    data_file : boolean, optional
        Boolean to determine if excel file belongs in data folder or not. The default is False.
    Returns
    -------
    string
        File path

    """
    
    cwd = os.getcwd()
    
    fp = '\\EquityHedging\\data\\returns_data\\' if data_file else '\\EquityHedging\\reports\\'
    file_name = report_name +'.xlsx'
    return cwd + fp + file_name

def print_report_info(report_name, file_path):
    """
    Print name of report and location

    Parameters
    ----------
    report_name : string
        Name of report.
    file_path : string
        File location.

    Returns
    -------
    None.

    """
    folder_location = file_path.replace(report_name+'.xlsx', '')
    print('"{}.xlsx" report generated in "{}" folder'.format(report_name,folder_location))

class setReport():
    def __init__(self, report_name, data_file=False):
        """
        Setup excel report

        Parameters
        ----------
        report_name : string
            Name of excel report.
        data_file : boolean, optional
            Boolean to determine if excel file belongs in data folder or not. The default is False.

        Returns
        -------
        None.

        """
        self.report_name = report_name
        self.data_file = data_file
        self.file_path = get_filepath(self.report_name, self.data_file)
        self.writer = pd.ExcelWriter(self.file_path, engine='xlsxwriter')

class getReturnsReport(setReport):
    def __init__(self, report_name, data_dict, data_file=True):
        """
        Generates excel file containing historical returns for different frequencies

        Parameters
        ----------
        report_name : string
            Name of report.
        data_dict : dict
            Dictionary containing returns of different frequencies.
        data_file : boolean, optional
            Boolean to determine if excel file belongs in data folder or reports folder. The default is True.

        Returns
        -------
        None. An excel report called [report_name].xlsx is created
        """
        setReport(self,report_name, data_file)
        setReport.__init__(self, report_name, data_file)
        self.data_dict = data_dict
        self.generate_report()
        print_report_info(self.report_name, self.file_path)
        self.writer.save()
        
    def generate_report(self):
        #loop through dictionary to create returns spreadsheets
        for key in self.data_dict:
            print("Writing {} Historical Returns sheet...".format(key))
            if len(key) > 31:
                diff = len(key) - 31
                new_sheets.setHistReturnSheet(self.writer, self.data_dict[key],key[:-diff])
                
            else:
                new_sheets.setHistReturnSheet(self.writer, self.data_dict[key],key)

class getRetMVReport(getReturnsReport):
    def __init__(self, report_name, data_dict, data_file=True):
        """
        Generates an excel file containing monthly returns and market values

        Parameters
        ----------
        report_name : string
            Name of report.
        data_dict : dict
            Dictionary containing returns and market_values.
        data_file : boolean, optional
            Boolean to determine if excel file belongs in data folder or reports folder. The default is True.

        Returns
        -------
        None. An excel report called [report_name].xlsx is created
        """
        getReturnsReport.__init__(self, report_name, data_dict, data_file)
                
    def generate_report(self):
        print("Writing Monthly Returns sheet...")
        new_sheets.setHistReturnSheet(self.writer, self.data_dict['returns'], 'returns')
        print("Writing Monthly Market Values sheet...")
        new_sheets.setMVSheet(self.writer, self.data_dict['market_values'], 'market_values')        
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 20:13:09 2022

@author: Powis Forjoe
"""
import os
from .import data_manager as dm
from .import data_xformer_new as dxf
import pandas as pd
from ..reporting.excel import new_reports as rp

CWD = os.getcwd()
RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\returns_data\\'
UPDATE_DATA_FP = CWD +'\\EquityHedging\\data\\update_data\\'
BMK_COL_LIST = ['SPTR', 'SX5T', 'M1WD', 'MIMUAWON', 'Long Corp', 'STRIPS',
                    'HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']
HF_COL_LIST = ['HFRX Macro/CTA', 'SG Trend','HFRX Absolute Return','DM Equity',
               'EM Equity','Gov Bonds','Agg Bonds','EM Bonds','High Yield','BCOM',
               'S&P GSCI TR','Equity Volatility','EM FX','FX Carry','Commo Carry',
               'CTAs','HFRX Systematic Macro','HFRX Rel Val Arb','HFRX Global',
               'HFRX Eq Hedge','HFRX Event driven','HFRX Convert Arb','HFRX EM',
               'HFRX Commodities','HFRX RV']
FREQ_LIST = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
EQ_HEGDE_COL_LIST = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                     'Vortex', 'VOLA I', 'VOLA II','Dynamic VOLA','Dynamic Put Spread',
                     'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)',
                     'Def Var (Wed)', 'Commodity Basket']


class mainUpdater():
    def __init__(self, filename, report_name):
        self.filename = filename
        self.report_name = report_name
        self.data_xform = self.xform_data() 
        self.data_dict = self.calc_data_dict()
        self.update_report()
    
    def xform_data(self):
        #TODO: Are you sure this is right?
        return self.xform_data
        #return dxf.dataXformer(self.filename)
    
    def calc_data_dict(self):
        return dxf.copy_data(self.data_xform)
    
    def update_report(self):
        pass
    
    def get_return_data(self, filename, sheet_list=[]):
        if sheet_list:
            return_dict = {}
            for sheet in sheet_list:
                temp_ret = pd.read_excel(RETURNS_DATA_FP+filename,sheet_name=sheet,index_col=0)
                temp_ret = get_real_cols(temp_ret)  
                return_dict[sheet] = temp_ret.copy()
            return return_dict
        else:
            return_df = pd.read_excel(RETURNS_DATA_FP+filename,sheet_name=sheet,index_col=0)
            return_df = get_real_cols(temp_ret)  
            return return_df
        
    def update_columns(self, df, old_col_list, new_col_list):
        df = df[old_col_list]
        df.columns = new_col_list
        return df

    def update_df_dict_columns(self, df_dict, old_col_list, new_col_list):
        for key in df_dict:
            df_dict[key] = self.update_columns(df_dict[key], old_col_list, new_col_list)
        return df_dict
     
    def update_data(self, main_dict, new_dict, freq_data = True):
        updated_dict = {}
        for key in main_dict:
            #create returns data frame
            new_ret_df = new_dict[key].copy()
            ret_df = main_dict[key].copy()
            
            #update current year returns 
            if key == 'Yearly':
                if ret_df.index[-1] == new_ret_df.index[-1]:
                    ret_df = ret_df[:-1]
            #get new returns df       
            new_ret_df = get_new_returns_df(new_ret_df, ret_df)
            updated_dict[key] = pd.concat([ret_df,new_ret_df])
        
        if freq_data:
            updated_dict = check_returns(updated_dict)
        return updated_dict
    

     
class nexenLiquidAltsDataUpdater(mainUpdater):
    """
    Class for updating Nexen Liquid Alternatives data.
    
    Args:
        filename (str, optional): Name of the input Excel file containing data. 
            Default is 'Monthly Returns Liquid Alts.xls'.
        report_name (str, optional): Name of the report to generate. 
            Default is 'nexen_liq_alts_data-new'.
    """
    def __init__(self, filename='Monthly Returns Liquid Alts.xls', report_name='nexen_liq_alts_data-new'):
        """
       Initializes the nexenLiquidAltsDataUpdater instance.

       Args:
           filename (str, optional): Name of the input Excel file containing data. 
               Default is 'Monthly Returns Liquid Alts.xls'.
           report_name (str, optional): Name of the report to generate. 
               Default is 'nexen_liq_alts_data-new'.
       """
        super().__init__(filename, report_name)
        
    def xform_data(self):
        """
       Transform the Nexen Liquid Alternatives data.

       Returns:
           transformed_data (DataFrame or Dict): Transformed Nexen Liquid Alternatives data.
       """
        return dxf.nexenDataXformer(UPDATE_DATA_FP+ self.filename).data_xform
    
    def update_report(self):
        """
        Update the report of Nexen Liquid Alternatives data.

        """
        rp.getRetMVReport(self.report_name, self.data_dict, True)
    

class innocapLiquidAltsDataUpdater(nexenLiquidAltsDataUpdater):
    """
    Class for updating Innocap Liquid Alternatives data.
    
    Args:
        filename (str, optional): Name of the input Excel file containing data. 
            Default is '1907_hf_data.xlsx'.
        report_name (str, optional): Name of the report to generate. 
            Default is 'innocap_liq_alts_data-new'.
    """
    def __init__(self, filename='1907_hf_data.xlsx', report_name= 'innocap_liq_alts_data-new'):
        """
        Initializes the innocapLiquidAltsDataUpdater instance.

        Args:
            filename (str, optional): Name of the input Excel file containing data. 
                Default is '1907_hf_data.xlsx'.
            report_name (str, optional): Name of the report to generate. 
                Default is 'innocap_liq_alts_data-new'.
        """
        super().__init__(filename, report_name)
        
    def xform_data(self):
        """
        Transform the Innocap Liquid Alternatives data.

        Returns:
            transformed_data (DataFrame or Dict): Transformed Innocap Liquid Alternatives data.
        """
        return dxf.innocapDataXformer(UPDATE_DATA_FP+self.filename).data_xform
        
    def calc_data_dict(self):
        """
       Calculate the data dictionary for Innocap Liquid Alternatives.

       Returns:
           data_dict (dict): Calculated data dictionary for Innocap Liquid Alternatives.
       """
        #self.innocap_dict = dxf.innocapDataXformer(UPDATE_DATA_FP+self.filename).data_xform
        self.old_col_list = ['1907 Campbell Trend Following LLC', '1907 III Class A','1907 Penso Class A',
                        '1907 Systematica Trend Following',
                        '1907 ARP Trend Following LLC_Class EM', '1907 III Fund Ltd _ Class CV', '1907 Kepos']
        self.new_col_list = ['1907 Campbell TF', '1907 III Class A', '1907 Penso Class A', '1907 Systematica TF'
                             , '1907 ARP EM', '1907 III CV','1907 Kepos RP']
        
        self.data_xform = self.update_df_dict_columns(self.data_xform, self.old_col_list, self.new_col_list)
        self.data_dict = self.get_return_data('innocap_liq_alts_data.xlsx', ['returns', 'market_values'])
        self.data_dict = self.update_data(self.data_dict, self.data_xform, False)  
        return self.data_dict
    
   
        

class bbgDataUpdater(mainUpdater):
    """
    Class for updating Bloomberg (BBG) data.
    
    This class inherits from mainUpdater and specializes in updating and transforming Bloomberg data.
    
    Args:
        filename (str): Name of the input Excel file containing data.
        report_name (str): Name of the report to generate.
        col_list (list, optional): List of column names to include in the data. Default is an empty list.
    """
    def __init__(self, filename,report_name, col_list=[]):
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
        return dxf.bbgDataXformer(UPDATE_DATA_FP+self.filename).data_xform
    
    def calc_data_dict(self):
        """
       Calculate the data dictionary for Bloomberg (BBG) data.

       Returns:
           data_dict (dict): Calculated data dictionary for Bloomberg data.
       """
        if self.col_list:
            for key in self.data_xform:
                self.data_xform[key] = self.data_xform[key][self.col_list]
        # self.data_dict = dxf.get_data_dict(self.data_xform)
        return dxf.copy_data(self.data_xform)

    def update_report(self): 
        """
        Update the report of Bloomberg (BBG) data.

        """
        rp.getReturnsReport(self.report_name, self.data_dict, True)

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
    def __init__(self, filename='liq_alts_bmk_data.xlsx',report_name='hf_bmks-new', col_list=[]):
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
        return dxf.bbgDataXformer(UPDATE_DATA_FP+self.filename,sheet_name='bbg_d',freq='1D', col_list=HF_COL_LIST).data_xform
   

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
    def __init__(self, filename='liq_alts_bmk_data.xlsx', report_name= 'liq_alts_bmks-new', col_list = ['HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']):
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
        return dxf.bbgDataXformer(UPDATE_DATA_FP+self.filename,sheet_name='bbg_d', freq = '1D', col_list=HF_COL_LIST).data_xform


class bmkDataUpdater(hfBmkDataUpdater):
    """
    Class for updating Benchmark data.
    
    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'bmk_data.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'bmk_returns-new'.
    """    
    def __init__(self, filename='bmk_data.xlsx', report_name = 'bmk_returns-new'):
        """
       Initializes the bmkDataUpdater instance.

       Args:
           filename (str, optional): Name of the input Excel file containing data.
               Default is 'bmk_data.xlsx'.
           report_name (str, optional): Name of the report to generate.
               Default is 'bmk_returns-new'.
       """
        super().__init__(filename, report_name)

    def xform_data(self):
        """
       Transform the Benchmark data.

       Returns:
           transformed_data (DataFrame or Dict): Transformed Benchmark data.
       """
        return dxf.bbgDataXformer(UPDATE_DATA_FP+self.filename,freq = '1D', col_list=BMK_COL_LIST).data_xform
    
    def calc_data_dict(self):
        """
        Calculate the data dictionary for Benchmark data.

        Returns:
            data_dict (dict): Calculated data dictionary for Benchmark data.
        """
        self.data_xform = dxf.copy_data(self.data_xform)
        self.returns_dict = self.get_return_data('bmk_returns.xlsx', FREQ_LIST)
        self.data_xform = match_dict_columns(self.returns_dict, self.data_xform)
        return self.update_data(self.returns_dict, self.data_xform)
        
   
class assetClassDataUpdater(nexenLiquidAltsDataUpdater):
    """
   Class for updating Asset Class Returns data.

   Args:
       filename (str, optional): Name of the input Excel file containing data.
           Default is 'Historical Asset Class Returns.xls'.
       report_name (str, optional): Name of the report to generate.
           Default is 'upsgt_returns-new'.
   """
    def __init__(self,filename = 'Historical Asset Class Returns.xls', report_name = 'upsgt_returns-new'):
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
        self.old_col_list = ['Total EQ w/o Derivatives','Total Fixed Income',
                        'Total Liquid Alts','Total Real Estate','Total Private Equity',
                        'Total Credit','LDI ONLY-TotUSPenMinus401H']
        self.new_col_list = ['Public Equity', 'Fixed Income', 'Liquid Alts','Real Estate',
                        'Private Equity', 'Credit', 'Total Group Trust']
        self.data_dict = self.update_df_dict_columns(self.data_xform, self.old_col_list, self.new_col_list)
        return self.data_dict

class equityHedgeReturnsUpdater(nexenLiquidAltsDataUpdater):
    """
    Class for updating Equity Hedge Returns data.
        
    Args:
        filename (str, optional): Name of the input Excel file containing data.
            Default is 'eq_hedge_returns.xlsx'.
        report_name (str, optional): Name of the report to generate.
            Default is 'eq_hedge_returns-new'.
    """
    def __init__(self, filename = 'eq_hedge_returns.xlsx', report_name='eq_hedge_returns-new'):
        """
        Initializes the equityHedgeReturnsUpdater instance.

        Args:
            filename (str, optional): Name of the input Excel file containing data.
                Default is 'eq_hedge_returns.xlsx'.
            report_name (str, optional): Name of the report to generate.
                Default is 'eq_hedge_returns-new'.
        """
        super().__init__(filename,report_name)
        
    def xform_data(self):
        """
        Transform the Equity Hedge Returns data.

        Returns:
            transformed_data (dict): Transformed Equity Hedge Returns data.
        """
        return self.get_return_data(self.filename,sheet_list=FREQ_LIST)
    
    def calc_data_dict(self):
        """
        Calculate the data dictionary for Equity Hedge Returns data.

        Returns:
            data_dict (dict): Calculated data dictionary for Equity Hedge Returns data.
        """
        new_data_dict = create_update_dict()
        return self.update_data(self.data_xform, new_data_dict)
    
    def update_report(self):
        """
        Update the report with Equity Hedge Returns data.

        """
        rp.getReturnsReport(self.report_name, self.data_dict, True)

class liquidAltsReturnsUpdater(mainUpdater):
    def __init__(self, filename="test", report_name="all_liquid_alts_data"):
        super().__init__(filename,report_name)
   

#TODO: Make this a class liquidAltsReturnsUpdater as well 
    def calc_data_dict(self):
        #TODO: Make this self.calc_data_dict
        #TODO: call the data_dicts in the respective dataupdater classes, nexenLiquidAltsDataUpdater and innocapLiquidAltsDataUpdater
        nexen_data = pd.read_excel(RETURNS_DATA_FP+'nexen_liq_alts_data-new.xlsx', sheet_name=None)
        innocap_data = pd.read_excel(RETURNS_DATA_FP+'innocap_liq_alts_data-new.xlsx', sheet_name=None)
    
        merged_data = {}
    
        # Loop through sheets in nexen_data
        for sheet_name, nexen_df in nexen_data.items():
            # Check if the sheet exists in innocap_data
            if sheet_name in innocap_data:
                innocap_df = innocap_data[sheet_name]
                
                # Use combine_first to merge DataFrames and replace values from nexen with innocap where they exist
                merged_df = nexen_df.set_index(nexen_df.columns[0]).combine_first(innocap_df.set_index(innocap_df.columns[0]))
    
                # Reset the index to move the date column back to its original position
                merged_df.reset_index(inplace=True)
    
                # Format the first column (dates) as short date format (mm/dd/yyyy)
                merged_df[merged_df.columns[0]] = merged_df[merged_df.columns[0]].dt.strftime('%m/%d/%Y')
                # Add the merged DataFrame to the dictionary
                merged_data[sheet_name] = merged_df
            else:
                # If sheet_name doesn't exist in innocap_data, add nexen_df as is
                merged_data[sheet_name] = nexen_df
        
        return merged_data
        #TODO: Make this self.update_report
        #TODO: use rp.getRetMVReport here
    def update_report(self):
            """
            Update the report of Nexen Liquid Alternatives data.

            """
            #rp.getRetMVReport(self.report_name, self.data_dict, True)
        
            output_path = RETURNS_DATA_FP+'all_liquid_alts_data.xlsx'
            with pd.ExcelWriter(output_path) as writer:
              for sheet_name, merged_df in self.data_dict.items():
                  merged_df.to_excel(writer, sheet_name=sheet_name, index=False)


      


    
def get_data_to_update(col_list, filename, sheet_name = 'data', put_spread=False):
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
    #read excel file to dataframe
    data = pd.read_excel(UPDATE_DATA_FP + filename, sheet_name= sheet_name, index_col=0)
    
    #rename column(s) in dataframe
    data.columns = col_list
    
    if put_spread:
        #remove the first row of dataframe
        data = data.iloc[1:,]
    
        #add column into dataframe
        data = data[['99%/90% Put Spread']]
    
        #add price into dataframe
        data = dxf.get_prices_df(data)
    
    data_dict = dxf.get_data_dict(data)
    return data_dict

def add_bps(vrr_dict, strat_name, add_back=.0025):
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
    #create empty dictionary
    temp_dict = {}
    
    #iterate through keys of a dictionary
    for key in vrr_dict:
        
        #set dataframe equal to dictionary's key
        temp_df = vrr_dict[key].copy()
        
        #set variable equaly to the frequency of key
        freq = dm.switch_string_freq(key)
        
        #add to dataframe
        temp_df[strat_name] += add_back/(dm.switch_freq_int(freq))
        
        #add value to the temp dictionary
        temp_dict[key] = temp_df
    return temp_dict

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
    
    #iterate through keys in dictionary
    for key in new_dict:
        
        #set column in the new dictionary equal to that of the main
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
    #iterate through keys in dictionary
    for key in new_dict:
        
        #add value from new_dict to main_dict
        main_dict[key] = main_dict[key].append(new_dict[key])
    return main_dict

#TODO: refactor function and rename to make it eq_hedge specific
def create_update_dict():
    '''
    Create a dictionary that updates returns data

    Returns
    -------
    new_data_dict : Dictionary
        Contains the updated information after adding new returns data

    '''
    #Import data from bloomberg into dataframe and create dictionary with different frequencies
    new_ups_data_dict = get_data_to_update(EQ_HEGDE_COL_LIST, 'ups_data.xlsx')
    
    #get vrr data
    vrr_dict = get_data_to_update(['VRR'], 'vrr_tracks_data.xlsx', sheet_name='VRR')
    vrr2_dict = get_data_to_update(['VRR 2'], 'vrr_tracks_data.xlsx', sheet_name='VRR2')
    vrr_trend_dict = get_data_to_update(['VRR Trend'], 'vrr_tracks_data.xlsx', sheet_name='VRR Trend')
    
    #add back 25 bps
    vrr_dict = add_bps(vrr_dict,'VRR')
    vrr2_dict = add_bps(vrr2_dict,'VRR 2', add_back= 0.005)
    vrr_trend_dict =add_bps(vrr_trend_dict, 'VRR Trend', add_back= 0.005)
    
    #get put spread data
    put_spread_dict = get_data_to_update(['99 Rep', 'Short Put', '99%/90% Put Spread'], 'put_spread_data.xlsx', 'Daily', put_spread = True)
    
    #merge vrr and put spread dicts to the new_data dict
    new_data_dict = dm.merge_dicts_list([new_ups_data_dict,put_spread_dict, vrr_dict, vrr2_dict, vrr_trend_dict], True)
    
    #get data from returns_data.xlsx into dictionary
    returns_dict = dm.get_equity_hedge_returns(all_data=True)
    
    #set columns in new_data_dict to be in the same order as returns_dict
    new_data_dict = match_dict_columns(returns_dict, new_data_dict)
        
    #return a dictionary
    return new_data_dict

def get_new_returns_df(new_returns_df,returns_df):
    #copy dataframes
    new_ret_df = new_returns_df.copy()
    ret_df = returns_df.copy()
    #reset both data frames index to make current index (dates) into a column
    new_ret_df.index.names = ['Date']
    ret_df.index.names = ['Date']
    new_ret_df.reset_index(inplace = True)
    ret_df.reset_index(inplace=True)
   
    #find difference in dates
    difference = set(new_ret_df.Date).difference(ret_df.Date)
    #find which dates in the new returns are not in the current returns data
    difference_dates = new_ret_df['Date'].isin(difference)
    
    #select only dates not included in original returns df
    new_ret_df = new_ret_df[difference_dates]
    
    #set 'Date' column as index for both data frames
    new_ret_df.set_index('Date', inplace = True)
    ret_df.set_index('Date', inplace = True)
    
    return new_ret_df

def check_returns(returns_dict):
    #if the last day of the month is earlier than the last row in weekly returns then drop last row of weekly returns
    if returns_dict['Monthly'].index[-1] < returns_dict['Weekly'].index[-1] :
        returns_dict['Weekly'] = returns_dict['Weekly'][:-1]
    
    
    if returns_dict['Monthly'].index[-1] < returns_dict['Quarterly'].index[-1] :
        returns_dict['Quarterly'] = returns_dict['Quarterly'][:-1]
        
    return returns_dict    


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


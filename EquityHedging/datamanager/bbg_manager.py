# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 14:37:05 2021

@author: Powis Forjoe
"""

from xbbg import blp
from . import data_xformer_new as dxf

UPS_BBG_TICKER_LIST = ['SPTR Index', 'SX5T Index', 'M1WD Index', 'LD07TRUU Index',
                       'BSTRTRUU Index', 'SGIXETRU Index', 'MLEIVT5H Index',
                       'BNPIVOLA Index', 'BNPXVO2A Index', 'CSEADP2E Index',
                       'SGBVVRRU Index', 'CSVPDSPG Index', 'JPOSCOSV Index',
                       'UBCSLSFB Index', 'UBCSLSMB Index', 'UBCSLSWB Index']


def switch_ticker(arg):
    """
    switch from bbg ticker to alias 
    
    Parameters:
    arg -- string
    
    Returns:
    alias of bbg ticker
    """
    switcher = {
        "SPTR Index": "SPTR", "SX5T Index": "SX5T", "M1WD Index": "M1WD",
        "LD07TRUU Index": "Long Corp", "BSTRTRUU Index": "STRIPS",
        "SGIXETRU Index": "Down Var",
        "MLEIVT5H Index": "Vortex",
        "BNPIVOLA Index": "VOLA I", "BNPXVO2A Index": "VOLA II",
        "CSEADP2E Index": "Dynamic Put Spread",
        "CSVPDSPG Index": "GW Dispersion",
        "JPOSCOSV Index": "Corr Hedge",
        "UBCSLSFB Index": "Def Var (Fri)", "UBCSLSMB Index": "Def Var (Mon)", "UBCSLSWB Index": "Def Var (Wed)",
        "SGBVVRRU Index": "VRR", "FEDL01 Index": "Fed Funds",
    }
    return switcher.get(arg, 1)


def get_price_data(tickers, start_date, end_date='today', freq='D'):
    df_index = get_data(tickers, 'PX_LAST', start_date, end_date, freq)
    df_index.columns = tickers
    return df_index


def get_ups_data(start_date, end_date='today'):
    ups_data = get_price_data(UPS_BBG_TICKER_LIST, start_date, end_date)
    ups_data.columns = [switch_ticker(col) for col in ups_data.columns]
    return dxf.get_data_dict(ups_data)


def get_data(tickers, flds=None, start_date=None, end_date='today', freq='D'):
    """
    Returns Historical data of tickers Bloomberg

    Parameters
    ----------
    tickers : list
        Bloomberg tickers.
    flds : list, optional
        list of fields. The default is None.
    start_date : string, optional
        start date. The default is None.
    end_date : string, optional
        today. The default is 'today'.
    freq : string, optional
        frequency of data. The default is 'D'.

    Returns
    -------
    df : dataframe
        dataframe containing data.

    """
    df = blp.bdh(tickers, flds, start_date, end_date, Per=freq, Fill='P', Days='T')
    df.dropna(inplace=True)
    return df

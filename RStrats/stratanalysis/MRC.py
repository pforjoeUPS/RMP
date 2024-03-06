# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 11:12:23 2024

@author: PCR7FJW
"""
import os
CWD = os.getcwd()
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import returns_stats as rs
import pandas as pd
import numpy as np


def calculate_covariance_matrix(correlation_matrix, volatility):
    return np.outer(volatility, volatility) * correlation_matrix


def get_MRC(returns, vol_weight, bmk_returns=None):
    """
    Marginal Risk Contribution
    
    Parameters:
    data -- DataFrame
    weight_list -- list
    price -- Boolean (is the data price or returns)

    Returns:
    Cov, MRisk, Beta, CRisk -- DataFrame
    """
    correlation_matrix = np.corrcoef(returns, rowvar=False)
    volatility = vol_weight['Vol']
    covariance_matrix = calculate_covariance_matrix(correlation_matrix, volatility)

    portfolio_variance = np.dot(vol_weight['Weight'].T, np.dot(covariance_matrix, vol_weight['Weight']))
    portfolio_sigma = np.sqrt(portfolio_variance)

    results = {}
    for i, asset_i in enumerate(vol_weight.index):
        cov_value = vol_weight['Weight'][asset_i] * np.square(vol_weight['Vol'][asset_i])
        for j, asset_j in enumerate(vol_weight.index):
            if asset_i != asset_j:
                cov_value += vol_weight['Weight'][asset_j] * covariance_matrix[i][j]
        results[asset_i] = cov_value

    df = pd.DataFrame.from_dict(results, orient='index', columns=['Covariance'])
    df['MRISK'] = [i / portfolio_sigma for i in df['Covariance']]
    df['BETA'] = [i / portfolio_variance for i in df['Covariance']]
    df['CRISK'] = vol_weight['Weight'] * df['MRISK']
    if bmk_returns is not None:
        df['Excess Ret'] = (returns.to_numpy() - bmk_returns.to_numpy()).sum(axis=0) * (12**0.5)
        df['Excess Ret/CRISK'] = df['Excess Ret'] / df['CRISK']
    return df
    
returns = pd.read_excel(dm.NEW_DATA + 'IMIP_TE_RET.xlsx', sheet_name = 'Returns', index_col=0)
bmk_returns = pd.read_excel(dm.NEW_DATA + 'IMIP_TE_RET.xlsx', sheet_name = 'BMKReturns', index_col=0)
vol_weight = pd.read_excel(dm.NEW_DATA + 'IMIP_TE_RET.xlsx', sheet_name = 'TEWeight', index_col=0)
df1 = get_MRC(returns, vol_weight, bmk_returns)
df1.to_excel(CWD +'\\RStrats\\MRC_IMIP.xlsx", index=True)

equity_bmk = 'SPTR'
strat_drop_list = ['SPTR', 'Vortex', 'VRR Trend']
include_fi = False
start_date = pd.to_datetime('2022-05-01')

returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list, only_equity=False)
daily_returns = returns['Daily'][returns['Daily'].index >= start_date]

daily_returns_vol = rs.get_ann_vol(daily_returns, freq='1D')
strat_notionals = [1,1.25,0.5,0.8,1,.25,1,1,1.05,1,0.5]
strat_weights = [i / sum(strat_notionals) for i in strat_notionals]

df_vol_weight = pd.DataFrame({'Vol': daily_returns_vol[0], 'Weight': strat_weights}, index=daily_returns_vol.index)
df1 = get_MRC(daily_returns, vol_weight=df_vol_weight)
df1.to_excel(CWD +'\\RStrats\\EqHedge MRC.xlsx', index=True)

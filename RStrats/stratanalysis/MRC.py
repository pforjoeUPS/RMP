# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 11:12:23 2024

@author: PCR7FJW
"""
from EquityHedging.datamanager import data_manager as dm
import pandas as pd
import numpy as np


def calculate_covariance_matrix(correlation_matrix, volatility):
    return np.outer(volatility, volatility) * correlation_matrix


def get_MRC(data, vol_weight, price = True):
    """
    Marginal Risk Contribution
    
    Parameters:
    data -- DataFrame
    weight_list -- list
    price -- Boolean (is the data price or returns)

    Returns:
    Cov, MRisk, Beta, CRisk -- DataFrame
    """
    if price == True:
        returns = data.pct_change().dropna()
    else:
        returns = data
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

    return df
    
data = pd.read_excel(dm.NEW_DATA + 'IMIP_TE_RET.xlsx', sheet_name = 'Returns', index_col=0)  
vol_weight = pd.read_excel(dm.NEW_DATA + 'IMIP_TE_RET.xlsx', sheet_name = 'TEWeight', index_col=0)
df1 = get_MRC(data, vol_weight, price = False)

# volatility = vol_weight['Vol']
#
#
#
#
#
#
#
# returns = data.pct_change().dropna()
# volatility = returns.std(axis=0) * np.sqrt(252)
# weight_list = []
# vol_weight_2 = pd.DataFrame(data = {'Vol': volatility.values,'Weight': weight_list}, index=returns.columns.tolist())
#
#
# returns = data.pct_change().dropna()
# returns = data
# correlation_matrix = np.corrcoef(returns, rowvar=False)
# volatility = returns.std(axis=0) * np.sqrt(252)
# covariance_matrix = calculate_covariance_matrix(correlation_matrix, volatility)
#
# vol_weight = pd.DataFrame(data = {'Vol': volatility.values,'Weight': weight_list}, index=returns.columns.tolist())
# portfolio_variance = np.dot(vol_weight['Weight'].T, np.dot(covariance_matrix, vol_weight['Weight']))
# portfolio_sigma = np.sqrt(portfolio_variance)
#
#
# results = {}
#
# # Iterate over each asset to calculate its covariance contribution
# for i, asset_i in enumerate(vol_weight.index):
#     # Start with the weighted variance of the asset
#     cov_value = vol_weight['Weight'][asset_i] * np.square(vol_weight['Vol'][asset_i])
#
#     # Add the weighted covariances with the other assets
#     for j, asset_j in enumerate(vol_weight.index):
#         if asset_i != asset_j:
#             cov_value += vol_weight['Weight'][asset_j] * covariance_matrix[i][j]
#
#     # Store the result in the dictionary
#     results[asset_i] = cov_value
#
# # Convert the results to a DataFrame for easy viewing
# df = pd.DataFrame.from_dict(results, orient='index', columns=['Covariance'])
#
#
# df['MRISK'] = [i / portfolio_sigma for i in df['Covariance']]
# df['BETA'] = [i / portfolio_variance for i in df['Covariance']]
# df['CRISK'] = vol_weight['Weight'] * df['MRISK']


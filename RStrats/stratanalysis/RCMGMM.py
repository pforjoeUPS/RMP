# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:07:58 2024

@author: PCR7FJW
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from scipy.stats import norm
from RStrats.stratanalysis import MVO as mvo
from RStrats.stratanalysis import rcm as rcm

import os
CWD = os.getcwd()


#MXWDIM DATA
bmk_index = pd.read_excel(CWD+'\\RStrats\\' + 'SPX&MXWDIM Historical Price.xlsx', sheet_name = 'MXWDIM', index_col=0)

#PROGRAM DATA
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'weighted hedgesSam.xlsx', sheet_name = 'Program', index_col=0)

# =============================================================================
# Using from MVO
#calculated returns off of price data
bmk = 'MXWDIM'
df_index_prices = pd.merge(df_index_prices, bmk_index, left_index=True, right_index=True, how='inner')
returns = df_index_prices.pct_change().dropna()
bmk_returns = pd.DataFrame({bmk: returns.pop(bmk)})

data = pd.merge(bmk_returns, returns, left_index=True, right_index=True, how='inner')
# Standardize the data
data_standardized = (data - data.mean()) / data.std()

# Fit the GMM (replace 'components' with the number of components you want)
components = 2  # Change this to the desired number of components
gmm = GaussianMixture(n_components=components, covariance_type='full', random_state=23)
gmm.fit(data_standardized)

# Predict the regime for each observation
regimes = gmm.predict(data_standardized)

# Create a scatter plot with different colors for each regime
for strat in data.columns:
    sns.scatterplot(data=data, x='MXWDIM', y=strat, hue=regimes, palette='viridis')
    plt.title('GMM Clustering')
    plt.xlabel('MXWDIM')
    plt.ylabel(strat)
    plt.legend(title='Regime')
    plt.show()
    
    
# Robust Covariance Matrix using GMM
# If using 2 components, regime 1 seems "normal" and 0 seems "sell-off" and "rally"
# If using 3 components, regime 2 seems "extreme sell-off", 1 seems "normal" and 0 seems "rally"/little "sell-off"
def get_robust_cov_matrix(benchmark_returns, strategy_returns, components=3, weight = .7):
    """
    GMM for regime based covariance matrices.
    
    Parameters:
    bmk_returns -- DataFrame
    strat_returns -- DataFrame
    components -- integer
    threshold -- float
    weight -- float
    upper_level -- boolean

    Returns:
    regime_cov_matrix -- dict
    """

    # Combine the benchmark and strategies into a single DataFrame
    data = pd.merge(benchmark_returns, strategy_returns, left_index=True, right_index=True, how='inner')

    # Standardize the data
    data_standardized = (data - data.mean()) / data.std()

    # Fit the GMM
    gmm = GaussianMixture(n_components=components, covariance_type='full', random_state=23)
    gmm.fit(data_standardized)

    # Predict the regime for each observation
    regimes = gmm.predict(data_standardized)
        
    # Identify indices for each regime
    crisis_indices = np.where((regimes == 0) | (regimes == 2))[0]
    normal_indices = np.where(regimes == 1)[0]

    # Take out bmk from data_standarized
    bmk_name = data_standardized.columns[0]  # Assuming first column is benchmark
    data_standardized_noBMK = data_standardized#.drop(bmk_name, axis=1)
    
    # Compute covariance matrices for each regime
    cov_crisis = np.cov(data_standardized_noBMK.iloc[crisis_indices].T)
    cov_normal = np.cov(data_standardized_noBMK.iloc[normal_indices].T)

    # Convert covariance matrices to DataFrames
    columns = list(data_standardized.columns)
    cov_matrices = {
        'crisis': pd.DataFrame(cov_crisis, index=columns, columns=columns),
        'normal': pd.DataFrame(cov_normal, index=columns, columns=columns),
    }
    
    # Combine covariance matrices
    combined_cov_matrix = cov_matrices['crisis']*weight + cov_matrices['normal']*(1-weight)
    
    return combined_cov_matrix



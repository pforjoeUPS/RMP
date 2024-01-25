# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 10:40:28 2024

@author: PCR7FJW
"""

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from scipy.stats import norm
import os
CWD = os.getcwd()

def run_gmm_and_get_covariances(benchmark_returns, strategy_returns, components=3, threshold = 0.1):
    """
    GMM for regime based covariance matrices.
    
    Parameters:
    bmk_returns -- DataFrame
    strat_returns -- DataFrame
    components -- integer
    threshold -- float

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

    # Define thresholds for sell-off and positive regimes
    lower_threshold = norm.ppf(threshold)
    upper_threshold = norm.ppf(1 - threshold)
    standardized_benchmark = data_standardized.iloc[:, 0]

    # Label each data point as per the regime
    regime_labels = pd.Series(1, index=standardized_benchmark.index)  # Default to 'normal' (label 1)
    regime_labels[standardized_benchmark < lower_threshold] = 0  # Label for 'sell-off'
    regime_labels[standardized_benchmark > upper_threshold] = 2  # Label for 'positive'
    
    # Identify indices for each regime
    sell_off_indices = np.where(regimes == 0)[0]
    normal_indices = np.where(regimes == 1)[0]
    positive_indices = np.where(regimes == 2)[0]

    # Compute covariance matrices for each regime
    cov_sell_off = np.cov(data_standardized.iloc[sell_off_indices].T)
    cov_normal = np.cov(data_standardized.iloc[normal_indices].T)
    cov_positive = np.cov(data_standardized.iloc[positive_indices].T)
    
# =============================================================================
#     # OR create "crisis" and "normal" regime
#     crisis_indices = np.where((standardized_benchmark < lower_threshold) | (standardized_benchmark > upper_threshold))[0]
#     normal_indices = np.where((standardized_benchmark >= lower_threshold) & (standardized_benchmark <= upper_threshold))[0]
#     
#     # Identify indices for regimes
#     sell_off_indices = np.where(regimes == 0)[0]
#     normal_indices = np.where(regimes == 1)[0]
#     
#     # Compute covariance matrices for each regime
#     cov_sell_off = np.cov(data_standardized.iloc[sell_off_indices].T)
#     cov_normal = np.cov(data_standardized.iloc[normal_indices].T)
# =============================================================================

    # Convert covariance matrices to DataFrames
    columns = ['Benchmark'] + list(strategy_returns.columns)
    cov_matrices = {
        'sell-off': pd.DataFrame(cov_sell_off, index=columns, columns=columns),
        'normal': pd.DataFrame(cov_normal, index=columns, columns=columns),
        'positive': pd.DataFrame(cov_positive, index=columns, columns=columns)
# =============================================================================
#         'crisis': pd.DataFrame(cov_crisis, index=columns, columns=columns),
#         'normal': pd.DataFrame(cov_normal, index=columns, columns=columns)
# =============================================================================
    }

    return cov_matrices




# =============================================================================
spx_index = pd.read_excel(CWD+'\\RStrats\\' + 'SPX&MXWDIM Historical Price.xlsx', sheet_name = 'SPX', index_col=0)
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'weighted hedgesSam.xlsx', sheet_name = 'Program Prices', index_col=0)
df_index_prices = df_index_prices.drop('Diversified Commodity Portfolio (noMacq)', axis=1)
spx_returns = spx_index.pct_change().dropna()
strat_returns = df_index_prices.pct_change().dropna()

test = run_gmm_and_get_covariances(benchmark_returns = spx_returns, strategy_returns = strat_returns)



# =============================================================================
# pca = PCA(n_components=2)  # or n_components=3 for 3D visualization
# data_reduced = pca.fit_transform(data_standardized)
# plt.figure(figsize=(10, 6))
# plt.scatter(data_reduced[:, 0], data_reduced[:, 1], c=regimes, cmap='viridis', marker='o')
# plt.title('GMM Clusters Visualization')
# plt.xlabel('PCA Component 1')
# plt.ylabel('PCA Component 2')
# plt.colorbar(label='Cluster')
# plt.show()
# 
# pca = PCA(n_components=3)  # or n_components=3 for 3D visualization
# data_reduced = pca.fit_transform(data_standardized)
# fig = plt.figure(figsize=(10, 7))
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(data_reduced[:, 0], data_reduced[:, 1], data_reduced[:, 2], c=regimes, cmap='viridis', marker='o')
# ax.set_title('GMM Clusters Visualization')
# ax.set_xlabel('PCA Component 1')
# ax.set_ylabel('PCA Component 2')
# ax.set_zlabel('PCA Component 3')
# plt.show()
# 
# =============================================================================

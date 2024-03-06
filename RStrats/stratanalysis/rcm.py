# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 10:40:28 2024

@author: PCR7FJW
"""

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from EquityHedging.analytics import returns_stats as rs
from RStrats.stratanalysis import MVO as mvo

from scipy.stats import norm
import os
CWD = os.getcwd()

def asset_class_bounds():
    asset_class_bounds = {
# =============================================================================
#         'Down Var': (.1063, .1065),
#         'VOLA': (0.1329, 0.1331),
#         'VRR 2': (.0903, .0905),
#         'GW Dispersion': (.1063, .1065),
#         'Corr Hedge': (0,.2),
#         'Def Var': (.1063, .1065),
#         'Macq Core': (.1063, .1065),
#         'ESPRSO': (0.1116, 0.1118),
#         'EVolCon': (0,.2),
#         'Moments': (0,.2)
# =============================================================================
        
    }
    return asset_class_bounds

# Robust Covariance Matrix using return distributions
def get_robust_cov_matrix(benchmark_returns, strategy_returns, threshold = 0.05, regime_weight = .7, two_tails = False):
    """
    Using percentiles for robust covariance matrix
    
    Parameters:
    bmk_returns -- DataFrame
    strat_returns -- DataFrame
    threshold -- float
    regime_weight -- float
    two_tails -- boolean

    Returns:
    regime_cov_matrix -- dict
    """

    # Combine the benchmark and strategies into a single DataFrame
    data = pd.merge(benchmark_returns, strategy_returns, left_index=True, right_index=True, how='inner')

    # Standardize the data
    data_standardized = (data - data.mean()) / data.std()

    # Establish percentile bounds
    lower_threshold = norm.ppf(threshold)
    upper_threshold = norm.ppf(1 - threshold)
    standardized_benchmark = data_standardized.iloc[:, 0]
    regime_labels = pd.Series(1, index=standardized_benchmark.index)  # Default to 'normal' (label 1)
    
    # Classify crisis period
    if two_tails == True:
        regime_labels[standardized_benchmark < lower_threshold] = 0  # Label for 'sell-off'
        regime_labels[standardized_benchmark > upper_threshold] = 2  # Label for 'positive'
    else:
        regime_labels[standardized_benchmark < lower_threshold] = 0  # Label for 'sell-off'
        
    # Identify indices for each regime
    crisis_indices = np.where((regime_labels == 0) | (regime_labels == 2))[0]
    normal_indices = np.where(regime_labels == 1)[0]

    # Take out bmk from data_standarized
    bmk_name = data_standardized.columns[0]  # Assuming first column is benchmark
    data_standardized_noBMK = data_standardized.drop(bmk_name, axis=1)
    
    # Compute covariance matrices for each regime
    cov_crisis = np.cov(data_standardized_noBMK.iloc[crisis_indices].T)
    cov_normal = np.cov(data_standardized_noBMK.iloc[normal_indices].T)

    # Convert covariance matrices to DataFrames
    columns = list(strategy_returns.columns)
    cov_matrices = {
        'crisis': pd.DataFrame(cov_crisis, index=columns, columns=columns),
        'normal': pd.DataFrame(cov_normal, index=columns, columns=columns),
    }
    
    # Combine covariance matrices
    combined_cov_matrix = cov_matrices['crisis']*regime_weight + cov_matrices['normal']*(1-regime_weight)
    
    return combined_cov_matrix


def mean_variance_optimization(returns, bmk_returns, optimization_type='sharpe'):
    """
    Mean-variance optimization.
    The objective can be based on either the Sharpe ratio or the Calmar ratio.

    Parameters:
    returns -- DataFrame
    num_iterations -- float
    optimization_type -- string
    bmk_returns -- DataFrame (for Calmar)

    Returns:
    Result of optimal weights and some statistics -- dict
    """

    # Calculate mean and volatility of returns
    ann_returns = rs.get_ann_return(returns, freq='1D')
    volatility = rs.get_ann_vol(returns, freq='1D')
    covariance_matrix = mvo.calculate_covariance_matrix(np.corrcoef(returns, rowvar=False), volatility)
    robust_covariance_matrix = get_robust_cov_matrix(bmk_returns, returns)

    # Define objective functions
    def sharpe_objective(weights, expected_returns, covariance_matrix):
        portfolio_return = np.dot(expected_returns, weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        return -portfolio_return / portfolio_volatility

    def calmar_objective(weights, expected_returns, covariance_matrix):
        portfolio_return = np.dot(expected_returns, weights)
        max_drawdown = mvo.calculate_max_drawdown(bmk_returns)
        calmar_ratio = portfolio_return / abs(max_drawdown)
        return -calmar_ratio

    # Define constraints and bounds
    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
    bounds = [asset_class_bounds().get(asset, (0, 0.5)) for asset in returns.columns.tolist()]

    # Initial guess
    initial_weights = np.ones(len(returns.columns)) / len(returns.columns)

        # Choose objective function based on optimization type
    if optimization_type == 'sharpe':
        objective = sharpe_objective
        args = (ann_returns, robust_covariance_matrix)
    elif optimization_type == 'calmar':
        objective = calmar_objective
        args = (ann_returns, robust_covariance_matrix)
    else:
        raise ValueError("Invalid optimization type. Choose 'sharpe' or 'calmar'.")

    # Perform optimization
    result = mvo.minimize(objective, initial_weights, args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    optimal_weights = result.x

    # Aggregate results
    final_optimal_weights = pd.DataFrame(optimal_weights,index=returns.columns.tolist(), columns=['Weights'])
    final_portfolio_return = np.sum(ann_returns * final_optimal_weights['Weights'])
    final_portfolio_volatility = np.sqrt(np.dot(final_optimal_weights.T, np.dot(covariance_matrix, final_optimal_weights)))
    final_portfolio_retvol = final_portfolio_return / final_portfolio_volatility

    # Create dictionary for results
    result_dict = {
        'final_optimal_weights': final_optimal_weights,
        'final_portfolio_return': final_portfolio_return,
        'final_portfolio_volatility': final_portfolio_volatility,
        'final_portfolio_ret/vol': final_portfolio_retvol
    }

    return result_dict
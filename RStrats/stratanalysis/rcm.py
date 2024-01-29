# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 10:40:28 2024

@author: PCR7FJW
"""

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
# =============================================================================
# from sklearn.decomposition import PCA
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# =============================================================================
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




def get_robust_cov_matrix(benchmark_returns, strategy_returns, components=3, threshold = 0.05, regime_weight = .7, upper_level = False):
    """
    GMM for regime based covariance matrices.
    
    Parameters:
    bmk_returns -- DataFrame
    strat_returns -- DataFrame
    components -- integer
    threshold -- float
    regime_weight -- float
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
    
        # Classify crisis period
    if upper_level == True:
        lower_threshold = norm.ppf(threshold)
        upper_threshold = norm.ppf(1 - threshold)
        standardized_benchmark = data_standardized.iloc[:, 0]
        regime_labels = pd.Series(1, index=standardized_benchmark.index)  # Default to 'normal' (label 1)
        regime_labels[standardized_benchmark < lower_threshold] = 0  # Label for 'sell-off'
        regime_labels[standardized_benchmark > upper_threshold] = 2  # Label for 'positive'
    elif upper_level == False:
        lower_threshold = norm.ppf(threshold)
        standardized_benchmark = data_standardized.iloc[:, 0]
        regime_labels = pd.Series(1, index=standardized_benchmark.index)  # Default to 'normal' (label 1)
        regime_labels[standardized_benchmark < lower_threshold] = 0  # Label for 'sell-off'
        
    # Identify indices for each regime
    crisis_indices = np.where((regimes == 0) | (regimes == 2))[0]
    normal_indices = np.where(regimes == 1)[0]

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
    mean_returns = returns.mean()*252
    volatility = returns.std(axis=0)*np.sqrt(252)
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
        args = (mean_returns, robust_covariance_matrix)
    elif optimization_type == 'calmar':
        objective = calmar_objective
        args = (mean_returns, robust_covariance_matrix)
    else:
        raise ValueError("Invalid optimization type. Choose 'sharpe' or 'calmar'.")

    # Perform optimization
    result = mvo.minimize(objective, initial_weights, args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    optimal_weights = result.x

    # Aggregate results
    final_optimal_weights = optimal_weights
    final_portfolio_return = np.sum(mean_returns * final_optimal_weights)
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




# =============================================================================
bmk_index = pd.read_excel(CWD+'\\RStrats\\' + 'SPX&MXWDIM Historical Price.xlsx', sheet_name = 'MXWDIM', index_col=0)
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'weighted hedgesSam.xlsx', sheet_name = 'Program', index_col=0)

#calculated returns off of price data
bmk = 'MXWDIM'
df_index_prices = pd.merge(df_index_prices, bmk_index, left_index=True, right_index=True, how='inner')
returns = df_index_prices.pct_change().dropna()
bmk_returns = pd.DataFrame({bmk: returns.pop(bmk)})
 
mvo_sh = mean_variance_optimization(returns, bmk_returns, optimization_type='sharpe')
mvo_ca = mean_variance_optimization(returns, bmk_returns, optimization_type='calmar')
 
mean_var_weights_sh = pd.concat([pd.DataFrame({'Optimal Weight: Sharpe': mvo_sh['final_optimal_weights'].tolist()}, index=returns.columns.tolist()), pd.DataFrame({'Optimal Weight: Sharpe': [mvo_sh['final_portfolio_return'], mvo_sh['final_portfolio_volatility'], mvo_sh['final_portfolio_ret/vol']]}, index=['Ret', 'Vol', 'Ret/Vol'])])
mean_var_weights_ca = pd.concat([pd.DataFrame({'Optimal Weight: Calmar': mvo_ca['final_optimal_weights'].tolist()}, index=returns.columns.tolist()), pd.DataFrame({'Optimal Weight: Calmar': [mvo_ca['final_portfolio_return'], mvo_ca['final_portfolio_volatility'], mvo_ca['final_portfolio_ret/vol']]}, index=['Ret', 'Vol', 'Ret/Vol'])])
 
program_mean_var_weights = pd.merge(mean_var_weights_sh, mean_var_weights_ca, left_index=True, right_index=True, how='inner')
 



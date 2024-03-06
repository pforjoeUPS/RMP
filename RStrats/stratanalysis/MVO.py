# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:05:57 2023

@author: PCR7FJW
"""
# TODO: Refactor and link different functions that we already have
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from EquityHedging.analytics import returns_stats as rs
from EquityHedging.analytics import hedge_metrics as hm
from EquityHedging.datamanager import data_manager as dm
# TODO: Use dm to transform returns to price data if needed
import os
CWD = os.getcwd()


def calculate_covariance_matrix(correlation_matrix, volatility):
    return np.outer(volatility, volatility) * correlation_matrix

    # Bootstrap resampling logic
def bootstrap_resample(data,sample_size, n):

    resample_indices = np.random.choice(n, sample_size, replace=True)
    return data.iloc[resample_indices]

    # Calculate CAGR
# def calculate_cagr(returns_series, years_lookback = 3):
#     years = returns_series.index.year.unique().tolist()[-years_lookback:]
#     returns = returns_series.loc[f'{years[0]}-01-01':f'{years[-1]}-12-31']
#     cum_returns = (1 + returns).cumprod() - 1
#     total_return = cum_returns.iloc[-1]
#     num_years = len(returns) / 252
#     cagr = (1 + total_return) ** (1 / num_years) - 1
#     return cagr

    # Calculate MAX DD
# def calculate_max_drawdown(returns_series):
#    cum_returns = (1 + returns_series).cumprod()
#    peak = cum_returns.cummax()
#    drawdown = (cum_returns/peak)-1
#    max_drawdown = drawdown.min()
#    return max_drawdown

    # Calculate AVERAGE DRAWDOWN -- WIP
# def calculate_average_annual_drawdowns(returns_series, years_lookback = 3):
#     avg_max_dd = 0
#     for year in returns_series.index.year.unique().tolist()[-years_lookback:]:
#         returns_year = returns_series.loc[f'{year}-01-01':f'{year}-12-31']
#         max_dd_year = calculate_max_drawdown(returns_year)
#         avg_max_dd += max_dd_year
#     avg_max_dd /= years_lookback
#     return avg_max_dd

    # Define BOUNDS
def asset_class_bounds():
    asset_class_bounds = {
# =============================================================================
        'Down Var': (0,1),
        'VOLA 3': (0,1),
        'Dynamic Put Spread': (0,1),
        'VRR 2': (0,1),
        'GW Dispersion': (0,1),
        'Corr Hedge': (0,1),
        'Def Var': (0,1),
        'ESPRSO': (0,1),
        'EVolCon': (0,1),
        'Moments': (0,1),
        "Total Commodity Portfolio": (0, 1)
# =============================================================================        
    }
    return asset_class_bounds



def mean_variance_optimization(returns, sample_size, bmk_returns=None, num_iterations=1000, optimization_type='sharpe'):
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
    # check difference of mean returns w Powis
    #mean_returns = returns.mean() * 252
    #volatility = returns.std(axis=0) * np.sqrt(252)
    ann_returns = rs.get_ann_return(returns, freq='1D')
    volatility = rs.get_ann_vol(returns, freq='1D')
    covariance_matrix = calculate_covariance_matrix(np.corrcoef(returns, rowvar=False), volatility)

    # Resample correlation matrices using bootstrap
    resampled = []
    
    for _ in range(num_iterations):
        resampled_returns = bootstrap_resample(returns, sample_size = sample_size, n = len(returns) )
        resampled_matrix = np.corrcoef(resampled_returns, rowvar=False)
        resampled.append({'resampled_matrix': resampled_matrix, 'resampled_returns': resampled_returns})

    # Define objective functions
    def sharpe_objective(weights, expected_returns, covariance_matrix):
        portfolio_return = np.dot(expected_returns, weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        return -portfolio_return / portfolio_volatility

    def calmar_objective(weights, expected_returns, sample_returns, covariance_matrix):
        portfolio_return = np.dot(expected_returns, weights)
        bmk_prices = dm.get_prices_df(bmk_returns.reindex(sample_returns.index))
        max_drawdown = rs.get_max_dd(bmk_prices)
        calmar_ratio = portfolio_return / abs(max_drawdown)
        return -calmar_ratio
    
    def convexity_cost_objective(weights,  sample_returns, covariance_matrix):

         # index = dm.get_prices_df(sample_returns)
         # weighted_index = dm.get_weighted_index(index, name = "Port Return",weight_ratio = weights)
         ret_df = pd.DataFrame()
         ret_df['Port Return'] = np.dot(sample_returns, weights)
         convexity = hm.get_convexity_stats(ret_df, 'Port Return')['cumulative']
         cost = hm.get_cost_stats(ret_df, 'Port Return')['cumulative']
         
         covex_cost = convexity / cost
         
         return covex_cost
     
    # Perform optimization for each sampled matrix
    all_optimal_weights = []

    for sample in resampled:
        covariance_matrix = calculate_covariance_matrix(sample['resampled_matrix'], volatility)

        # Define constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
        bounds = [asset_class_bounds().get(asset, (0, 1)) for asset in returns.columns.tolist()]

        # Initial guess
        initial_weights = np.ones(len(returns.columns)) / len(returns.columns)

        # Choose objective function based on optimization type
        if optimization_type == 'sharpe':
            objective = sharpe_objective
            args = (ann_returns, covariance_matrix)
        elif optimization_type == 'calmar':
            objective = calmar_objective
            args = (ann_returns, sample['resampled_returns'], covariance_matrix)
        elif optimization_type == 'convexity/cost':
            objective = convexity_cost_objective
            args = ( sample['resampled_returns'], covariance_matrix)
        else:
            raise ValueError("Invalid optimization type. Choose 'sharpe' or 'calmar'.")

        # Perform optimization
        result = minimize(objective, initial_weights, args=args, method='SLSQP', bounds=bounds, constraints=constraints)
        optimal_weights = result.x
        all_optimal_weights.append(optimal_weights)

    # Aggregate results
    #final_optimal_weights = np.mean(all_optimal_weights, axis=0)
    final_optimal_weights = pd.DataFrame(np.mean(all_optimal_weights, axis=0),index=returns.columns.tolist(), columns=['Weights'])
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

# =============================================================================
#     # Objective function using portoflio return divided by average annual maximum drawdown
#     def objective(weights, expected_returns, sample_returns, covariance_matrix):
#         portfolio_return = np.dot(expected_returns, weights)
#         avg_max_drawdown = calculate_average_annual_drawdowns(sample_returns @ weights, years_lookback)
#         sterling_ratio = portfolio_return / (abs(avg_max_drawdown))
#         return -sterling_ratio
# =============================================================================
















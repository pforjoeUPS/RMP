# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:05:57 2023

@author: PCR7FJW
"""
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from RStrats import SharpeVSCVar as SVC
import matplotlib.pyplot as plt
import os
CWD = os.getcwd()


def mean_variance_optimization_V1(returns):
    """
    Perform mean-variance optimization and return the optimal weights.
    
    Parameters:
    returns -- DataFrame

    Returns:
    optimal_weights -- array
    """
    
    # Calculate the mean and covariance of returns
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    # Define the objective function for mean-variance optimization - minimizing the negative sharpe ratio
    def objective(weights):
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -portfolio_return / portfolio_volatility

    # Define constraints (weights sum to 1)
    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})

    # Define bounds for weights (each weight is between 0 and 1)
    bounds = tuple((0, 0.5) for _ in range(len(returns.columns.tolist())))

    # Initialize equal weights for each asset
    initial_weights = np.ones(len(returns.columns.tolist())) / len(returns.columns.tolist())

    # Run the optimization
    result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

    # Get the optimal weights
    optimal_weights = result.x

    return optimal_weights


#including bootstraping resampling correlation
def mean_variance_optimization_V2(returns, num_iterations=1000):
    """
    Perform mean-variance optimization and return the optimal weights with resmapling correlation matrix
    
    Parameters:
    returns -- DataFrame
    num_iterations -- float

    Returns:
    final_optimal_weights -- array
    """
    
    # Calculate the mean and volatility of returns
    mean_returns = returns.mean()
    volatility = returns.std(axis=0)

    # Function to calculate the covariance matrix from the resampled correlation matrix
    def calculate_covariance_matrix(correlation_matrix, volatility):
        return np.outer(volatility, volatility) * correlation_matrix

    # Bootstrap resampling logic
    def bootstrap_resample(data):
        n = len(data)
        resample_indices = np.random.choice(n, n, replace=True)
        return data.iloc[resample_indices].reset_index(drop=True)

    # Resample correlation matrices using bootstrap
    resampled_matrices = []

    for _ in range(num_iterations):
        # Bootstrap resampling for returns data
        resampled_returns = bootstrap_resample(returns)

        # Calculate the correlation matrix for the resampled dataset
        resampled_matrix = np.corrcoef(resampled_returns, rowvar=False)
        
        # Append the resampled matrix to the list
        resampled_matrices.append(resampled_matrix)

    # Define the mean-variance optimization objective function
    def objective(weights, expected_returns, covariance_matrix):
        portfolio_return = np.dot(expected_returns, weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        return -portfolio_return / portfolio_volatility
    
    # Perform mean-variance optimization for each resampled matrix
    all_optimal_weights = []

    for correlation_matrix in resampled_matrices:
        covariance_matrix = calculate_covariance_matrix(correlation_matrix, volatility)
        
        # Define constraints
        constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})

        # Define bounds
        bounds = tuple((0, 0.5) for _ in range(len(returns.columns.tolist())))

        # Initial guess
        initial_weights = np.ones(len(returns.columns.tolist())) / len(returns.columns.tolist())

        # Perform optimization
        result = minimize(objective, initial_weights, args=(mean_returns, covariance_matrix),
                          method='SLSQP', bounds=bounds, constraints=constraints)

        # Collect optimal weights
        optimal_weights = result.x
        all_optimal_weights.append(optimal_weights)

    # Aggregate results (e.g., take the mean or median)
    final_optimal_weights = np.mean(all_optimal_weights, axis=0)

    return final_optimal_weights


#==================================================================================================================


df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'weighted hedgesSam.xlsx', sheet_name = 'Sheet2', index_col=0)
MXWDIM_index = pd.read_excel(CWD+'\\RStrats\\' + 'Commods Example.xlsx', sheet_name = 'Sheet2', index_col=0)['MXWDIM']

#calculated returns off of price data
returns = df_index_prices.pct_change().dropna()
mean_var_weights_V1 = pd.DataFrame({'Strategy': returns.columns.tolist(), 'Optimal Weight': mean_variance_optimization_V1(returns).tolist()})
mean_var_weights_V2 = pd.DataFrame({'Strategy': returns.columns.tolist(), 'Optimal Weight': mean_variance_optimization_V2(returns).tolist()})
# Example usage:


V1_notionals = mean_variance_optimization_V1(returns).tolist()
V2_notionals = mean_variance_optimization_V2(returns).tolist()
V1_index = SVC.get_weighted_index(df_index_prices, notional_weights = V1_notionals)
V2_index = SVC.get_weighted_index(df_index_prices, notional_weights = V2_notionals)
current_wei_index = SVC.get_weighted_index(df_index_prices, notional_weights = [1,1.25,1,1,1,.25,1,.55,1])

current_wei_index.name = 'Current_weights'
V1_index.name = 'V1_weights'
V2_index.name = 'V2_weights'

df = pd.merge(MXWDIM_index, current_wei_index, left_index=True, right_index=True, how='inner')
df = pd.merge(df, V1_index, left_index=True, right_index=True, how='inner')
df = pd.merge(df, V2_index, left_index=True, right_index=True, how='inner') 


BMK = 'MXWDIM'
strat_type = 'MeanVarTest'
strat_index = df.copy()
strat_list = strat_index.columns.tolist()
strat_list.remove('MXWDIM')

#Get Analysis Metrics
dict_strat_metrics = {}
for strat in strat_list:
    df_stratname = f'{strat}'
    dict_strat_metrics[df_stratname] = SVC.get_returns_analysis(strat_index, BMK = 'MXWDIM', Strat = strat)

#graphing against strategies
test_strat_list = list(dict_strat_metrics.keys())
plot_list = ['Ret', 'Vol', 'Sharpe', 'CVaR', 'Tracking Error', 'Corr', 'IR',]
for graph in plot_list:
    plt.figure(figsize=(8, 6))
    for strat in test_strat_list:
        ol_weights_index_list = dict_strat_metrics[strat].index.tolist()
        metrics_results_list = dict_strat_metrics[strat][graph]
        if graph == 'IR':
            ol_weights_index_list.pop(0)
            ol_weights_index_list = [float(x) for x in ol_weights_index_list]
            metrics_results_list = dict_strat_metrics[strat][graph].copy().tolist()
            metrics_results_list.pop(0)
        plt.scatter(ol_weights_index_list, metrics_results_list, label=strat, marker='o')
    plt.xticks(rotation=-45)
    plt.xlabel('Extended Weights')
    plt.ylabel(graph)
    plt.title(strat_type + ': ' + graph)
    if graph == 'IR':
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()


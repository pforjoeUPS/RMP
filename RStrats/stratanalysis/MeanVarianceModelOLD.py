# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:05:57 2023

@author: PCR7FJW
"""
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from RStrats.stratanalysis import SharpeVSCVar as SVC
import matplotlib.pyplot as plt
import os
CWD = os.getcwd()

#getting price data
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'weighted hedgesSam.xlsx', sheet_name = 'Sheet2', index_col=0)
MXWDIM_index = pd.read_excel(CWD+'\\RStrats\\' + 'Commods Example.xlsx', sheet_name = 'Sheet2', index_col=0)['MXWDIM']

#calculated returns off of price data
returns = df_index_prices.pct_change().dropna()

def mean_variance_optimization(returns):
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


mean_var_weights_test_df = pd.DataFrame({'Strategy': returns.columns.tolist(), 'Optimal Weight': mean_variance_optimization(returns)})
# Example usage:
# optimal_weights = mean_variance_optimization(returns)
# print(optimal_weights)



#===================================================================================================================
#MANUAL SCRIPT
# Calculate the mean and covariance of returns
mean_returns = returns.mean()
cov_matrix = returns.cov()

# Define the objective function for mean-variance optimization -  minimizing the negative sharpe ratio
def objective(weights):
    portfolio_return = np.sum(mean_returns * weights)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return -portfolio_return / portfolio_volatility

# Define constraints (weights sum to 1)
constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})

# Define bounds for weights (each weight is between 0 and 1)
bounds = tuple((0, 0.5) for asset in range(len(returns.columns.tolist())))

# Initialize equal weights for each asset
initial_weights = np.ones(len(returns.columns.tolist())) / len(returns.columns.tolist())

# Run the optimization
result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

# Get the optimal weights
optimal_weights = result.x

# Print the results
print("Optimal Weights:", optimal_weights)
print("Expected Portfolio Return:", -result.fun)
print("Portfolio Volatility:", np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights))))



mean_var_notionals = optimal_weights.tolist()
current_wei_index = SVC.get_weighted_index(df_index_prices, notional_weights = [1,1.25,1,1,1,.25,1,.55,1])
mean_var_index = SVC.get_weighted_index(df_index_prices, notional_weights = mean_var_notionals)
current_wei_index.name = 'Current_Weights'
mean_var_index.name = 'Mean_Var_Weights'

df = pd.merge(MXWDIM_index, current_wei_index, left_index=True, right_index=True, how='inner')
df = pd.merge(df, mean_var_index, left_index=True, right_index=True, how='inner')

 
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

#Graph plots
for strat in strat_list:
    df_stratname = f'{strat}'
    SVC.show_SharpeCVaR(dict_strat_metrics[df_stratname], Strat = strat)
    SVC.show_plots(dict_strat_metrics[df_stratname], Strat = strat)

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

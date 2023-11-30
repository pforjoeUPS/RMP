# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:05:57 2023

@author: PCR7FJW
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import skew, kurtosis
from RStrats import SharpeVSCVar as SVC
from EquityHedging.datamanager import data_manager as dm
import os
CWD = os.getcwd()


def calculate_covariance_matrix(correlation_matrix, volatility):
    return np.outer(volatility, volatility) * correlation_matrix

    # Bootstrap resampling logic
def bootstrap_resample(data):
    n = len(data)
    resample_indices = np.random.choice(n, n, replace=True)
    return data.iloc[resample_indices].reset_index(drop=True)

def mean_variance_optimization_V1(returns):
    """
    Perform mean-variance optimization and return the optimal weights
    Objective using sharpe
    
    Parameters:
    returns -- DataFrame

    Returns:
    optimal_weights -- array
    """
    
    # Calculate the mean and covariance of returns
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov()

    # Define the objective function for mean-variance optimization - minimizing the negative sharpe ratio
    def objective(weights):
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -portfolio_return / portfolio_volatility

    # Define constraints and bounds
    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
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
    Objective using sharpe
    
    Parameters:
    returns -- DataFrame
    num_iterations -- float

    Returns:
    final_optimal_weights -- array
    """
    
    # Calculate the mean and volatility of returns
    mean_returns = returns.mean() * 252
    volatility = returns.std(axis=0)

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


def calculate_max_drawdown(returns_series):
    cum_returns = np.cumprod(1 + returns_series) - 1
    peak = np.maximum.accumulate(cum_returns)
    drawdown = cum_returns - peak
    max_drawdown = np.min(drawdown)
    return max_drawdown


def mean_variance_optimization_V3(returns, num_iterations=1000):
    """
    Perform mean-variance optimizatio and return the optimal weights with resmapling correlation matrix
    Objective using calmar
    
    Parameters:
    returns -- DataFrame
    num_iterations -- float

    Returns:
    final_optimal_weights -- array
    """
    
    # Calculate the mean and volatility of returns
    mean_returns = returns.mean()*252
    volatility = returns.std(axis=0)

    # Resample correlation matrices using bootstrap
    resampled_matrices = []

    for _ in range(num_iterations):
        # Bootstrap resampling for returns data
        resampled_returns = bootstrap_resample(returns)

        # Calculate the correlation matrix for the resampled dataset
        resampled_matrix = np.corrcoef(resampled_returns, rowvar=False)
        
        # Append the resampled matrix to the list
        resampled_matrices.append(resampled_matrix)
    
    # objective function
    def objective(weights, expected_returns, covariance_matrix):
        portfolio_return = np.dot(expected_returns, weights)
        max_drawdown = calculate_max_drawdown(returns @ weights)
        calmar_ratio = portfolio_return / abs(max_drawdown)
        return -calmar_ratio

    # optimization for each sampled matrix
    all_optimal_weights = []

    for correlation_matrix in resampled_matrices:
        covariance_matrix = calculate_covariance_matrix(correlation_matrix, volatility)
        
        # constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
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


def mean_variance_optimization_V4(returns, num_iterations=1000):
    """
    Perform mean-variance optimizatio and return the optimal weights with resmapling correlation matrix
    Objective using calmar
    
    Parameters:
    returns -- DataFrame
    num_iterations -- float

    Returns:
    final_optimal_weights -- array
    """
    
    # Calculate the mean and volatility of returns
    mean_returns = returns.mean()*252
    volatility = returns.std(axis=0)

    # Resample correlation matrices using bootstrap
    resampled_matrices = []

    for _ in range(num_iterations):
        # Bootstrap resampling for returns data
        resampled_returns = bootstrap_resample(returns)

        # Calculate the correlation matrix for the resampled dataset
        resampled_matrix = np.corrcoef(resampled_returns, rowvar=False)
        
        # Append the resampled matrix to the list
        resampled_matrices.append(resampled_matrix)

    # define objective
    def composite_objective(weights, expected_returns, covariance_matrix, alpha=0.3):
        # Objective function that combines Sharpe ratio and Calmar ratio
        portfolio_return = np.dot(expected_returns, weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        max_drawdown = calculate_max_drawdown(returns @ weights)
        
        sharpe_ratio = portfolio_return / portfolio_volatility
        calmar_ratio = portfolio_return / abs(max_drawdown)
        
        # Combine Sharpe and Calmar ratios using a weighted sum
        composite_objective_value = alpha * sharpe_ratio + (1 - alpha) * calmar_ratio
        
        return -composite_objective_value  # Minimize negative composite objective


    # optimization for each sampled matrix
    all_optimal_weights = []

    for correlation_matrix in resampled_matrices:
        covariance_matrix = calculate_covariance_matrix(correlation_matrix, volatility)
        
        # constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
        bounds = tuple((0, 0.5) for _ in range(len(returns.columns.tolist())))

        # Initial guess
        initial_weights = np.ones(len(returns.columns.tolist())) / len(returns.columns.tolist())

        # Perform optimization
        result = minimize(composite_objective, initial_weights, args=(mean_returns, covariance_matrix),
                          method='SLSQP', bounds=bounds, constraints=constraints)

        # Collect optimal weights
        optimal_weights = result.x
        all_optimal_weights.append(optimal_weights)

    # Aggregate results (e.g., take the mean or median)
    final_optimal_weights = np.mean(all_optimal_weights, axis=0)

    return final_optimal_weights
#==================================================================================================================
#MXWDIM DATA
MXWDIM_index = pd.read_excel(CWD+'\\RStrats\\' + 'Commods Example.xlsx', sheet_name = 'Sheet2', index_col=0)
MXWDIM_index = MXWDIM_index[['MXWDIM']].copy()


#PROGRAM DATA
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'weighted hedgesSam.xlsx', sheet_name = 'Sheet2', index_col=0)
df_index_prices = df_index_prices.drop('Commodity Basket', axis=1)


#DISPERSION DATA
new_strat = pd.read_excel(dm.NEW_DATA + 'Copy of 231017 GN Dispersion Variations Time Series - UPS-NISA.xlsx',
                                           sheet_name = 'CS', index_col=0)
new_strat1 = pd.read_excel(dm.NEW_DATA + 'Copy of 231017 GN Dispersion Variations Time Series - UPS-NISA.xlsx',
                                           sheet_name = 'BNP', index_col=0)
new_strat2 = pd.read_excel(dm.NEW_DATA + 'Copy of 231017 GN Dispersion Variations Time Series - UPS-NISA.xlsx',
                                           sheet_name = 'CITINOMOD', index_col=0)
df_index_prices = pd.merge(new_strat, new_strat1, left_index=True, right_index=True, how='inner').merge(new_strat2, left_index=True, right_index=True, how='inner')


#GRIND LOWER HEDGES DATA
new_strat = pd.read_excel(dm.NEW_DATA + 'esprso.xlsx',
                                           sheet_name = 'Sheet2', index_col=0)
new_strat1 = new_strat = pd.read_excel(dm.NEW_DATA + 'Barclays Grind Lower Ts.xlsx',
                                           sheet_name = 'Sheet1', index_col=0)
new_strat2 = new_strat = pd.read_excel(dm.NEW_DATA + 'Barclays Grind Lower TS.xlsx',
                                           sheet_name = 'SG', index_col=0)
df_index_prices = df_index_prices = pd.merge(new_strat, new_strat1, left_index=True, right_index=True, how='inner').merge(new_strat2, left_index=True, right_index=True, how='inner')


#calculated returns off of price data
returns = df_index_prices.pct_change().dropna()

#mean_var_weights_V1 = pd.DataFrame({'Strategy': returns.columns.tolist(), 'Optimal Weight': mean_variance_optimization_V1(returns).tolist()})
mean_var_weights_V2 = pd.DataFrame({'Optimal Weight V2': mean_variance_optimization_V2(returns).tolist()}, index=returns.columns.tolist())
mean_var_weights_V3 = pd.DataFrame({'Optimal Weight V3': mean_variance_optimization_V3(returns).tolist()}, index=returns.columns.tolist())
mean_var_weights_V4 = pd.DataFrame({'Optimal Weight V4': mean_variance_optimization_V4(returns).tolist()}, index=returns.columns.tolist())

program_mean_var_weights = pd.merge(mean_var_weights_V2, mean_var_weights_V3, left_index=True, right_index=True, how='inner').merge(mean_var_weights_V4, left_index=True, right_index=True, how='inner')





#V1_index = SVC.get_weighted_index(df_index_prices, notional_weights = mean_var_weights_V1['Optimal Weight'].tolist())
V2_index = SVC.get_weighted_index(df_index_prices, notional_weights = program_mean_var_weights['Optimal Weight V2'].tolist())
V3_index = SVC.get_weighted_index(df_index_prices, notional_weights = program_mean_var_weights['Optimal Weight V3'].tolist())
V4_index = SVC.get_weighted_index(df_index_prices, notional_weights = program_mean_var_weights['Optimal Weight V4'].tolist())
current_wei_index = SVC.get_weighted_index(df_index_prices, notional_weights = [1,1.25,1,1,1,.25,1,.55,1])

#current_wei_index.name = 'Current_weights'
#V1_index.name = 'V1_weights'
V2_index.name = 'V2_weights'
V3_index.name = 'V3_weights'
V4_index.name = 'V4_weights'
current_wei_index.name = 'Current Program Weights'

df = pd.merge(MXWDIM_index, V2_index, left_index=True, right_index=True, how='inner').merge(V3_index, left_index=True, right_index=True, how='inner').merge(V4_index, left_index=True, right_index=True, how='inner').merge(current_wei_index, left_index=True, right_index=True, how='inner')

BMK = 'MXWDIM'
strat_type = 'MeanVarTest'
strat_index = df.copy()
strat_list = strat_index.columns.tolist()
strat_list.remove('MXWDIM')

#Get Analysis Metrics
dict_strat_metrics = {}
for strat in strat_list:
    df_stratname = f'{strat}'
    dict_strat_metrics[df_stratname] = SVC.get_returns_analysis(strat_index, BMK = 'MXWDIM', Strat = strat, weights = [.05,.1,.15,.2,.25,.3,.35,.4,.45,.5])

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


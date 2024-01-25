# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:05:57 2023

@author: PCR7FJW
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
#from scipy.stats import skew, kurtosis
#from RStrats import SharpeVSCVar as SVC
from EquityHedging.datamanager import data_manager as dm
import os
CWD = os.getcwd()


def calculate_covariance_matrix(correlation_matrix, volatility):
    return np.outer(volatility, volatility) * correlation_matrix

    # Bootstrap resampling logic
def bootstrap_resample(data):
    n = len(data)
    resample_indices = np.random.choice(n, n, replace=True)
    return data.iloc[resample_indices]

    # Calculate CAGR
def calculate_cagr(returns_series, years_lookback = 3):
    years = returns_series.index.year.unique().tolist()[-years_lookback:]
    returns = returns_series.loc[f'{years[0]}-01-01':f'{years[-1]}-12-31']
    cum_returns = (1 + returns).cumprod() - 1
    total_return = cum_returns.iloc[-1]
    num_years = len(returns) / 252
    cagr = (1 + total_return) ** (1 / num_years) - 1
    return cagr

    # Calculate MAX DD
def calculate_max_drawdown(returns_series):
    cum_returns = (1 + returns_series).cumprod()
    peak = cum_returns.cummax()
    drawdown = (cum_returns/peak)-1
    max_drawdown = drawdown.min()
    return max_drawdown

    # Calculate AVERAGE DRAWDOWN -- WIP
def calculate_average_annual_drawdowns(returns_series, years_lookback = 3):
    avg_max_dd = 0
    for year in returns_series.index.year.unique().tolist()[-years_lookback:]:
        returns_year = returns_series.loc[f'{year}-01-01':f'{year}-12-31']
        max_dd_year = calculate_max_drawdown(returns_year)
        avg_max_dd += max_dd_year
    avg_max_dd /= years_lookback
    return avg_max_dd

    # Define BOUNDS
def asset_class_bounds():
    asset_class_bounds = {
        #'CITIUVega': (0.0, 1),
    }
    return asset_class_bounds

    # Caclulate CVAR
def calculate_cvar(portfolio_returns, alpha=0.05):
    var = np.percentile(portfolio_returns, alpha * 100)
    cvar = portfolio_returns[portfolio_returns <= var].mean()
    return cvar


def mean_variance_optimization(returns, bmk_returns=None, num_iterations=1000, optimization_type='sharpe'):
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
    mean_returns = returns.mean() * 252
    volatility = returns.std(axis=0) * np.sqrt(252)

    # Resample correlation matrices using bootstrap
    resampled = []
    
    for _ in range(num_iterations):
        resampled_returns = bootstrap_resample(returns)
        resampled_matrix = np.corrcoef(resampled_returns, rowvar=False)
        resampled.append({'resampled_matrix': resampled_matrix, 'resampled_returns': resampled_returns})

    # Define objective functions
    def sharpe_objective(weights, expected_returns, covariance_matrix):
        portfolio_return = np.dot(expected_returns, weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        return -portfolio_return / portfolio_volatility

    def calmar_objective(weights, expected_returns, sample_returns, covariance_matrix):
        portfolio_return = np.dot(expected_returns, weights)
        max_drawdown = calculate_max_drawdown(bmk_returns.reindex(sample_returns.index))
        calmar_ratio = portfolio_return / abs(max_drawdown)
        return -calmar_ratio

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
            args = (mean_returns, covariance_matrix)
        elif optimization_type == 'calmar':
            objective = calmar_objective
            args = (mean_returns, sample['resampled_returns'], covariance_matrix)
        else:
            raise ValueError("Invalid optimization type. Choose 'sharpe' or 'calmar'.")

        # Perform optimization
        result = minimize(objective, initial_weights, args=args, method='SLSQP', bounds=bounds, constraints=constraints)
        optimal_weights = result.x
        all_optimal_weights.append(optimal_weights)

    # Aggregate results
    final_optimal_weights = np.mean(all_optimal_weights, axis=0)
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

def check_MAXDD(returns):
    df = pd.DataFrame(columns=['Max_DD'])
    for _ in range(1000):
        if _ == 0:
            maxdd=calculate_max_drawdown(returns)
        else:
            resampled_returns = bootstrap_resample(returns)
            maxdd = calculate_max_drawdown(resampled_returns)
        df.loc[_] = [maxdd[0]]
    return df

# =============================================================================
#     # Objective function using portoflio return divided by average annual maximum drawdown
#     def objective(weights, expected_returns, sample_returns, covariance_matrix):
#         portfolio_return = np.dot(expected_returns, weights)
#         avg_max_drawdown = calculate_average_annual_drawdowns(sample_returns @ weights, years_lookback)
#         sterling_ratio = portfolio_return / (abs(avg_max_drawdown))
#         return -sterling_ratio
# =============================================================================


#==================================================================================================================
#MXWDIM DATA
bmk_index = pd.read_excel(CWD+'\\RStrats\\' + 'SPX&MXWDIM Historical Price.xlsx', sheet_name = 'SPX', index_col=0)

#PROGRAM DATA
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'weighted hedgesSam.xlsx', sheet_name = 'Program Prices', index_col=0)
df_index_prices = df_index_prices.drop('Commodity Basket', axis=1)

#COMMODITIES
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'Commods Example.xlsx', sheet_name = 'Sheet4', index_col=0)

#RATES STRATEGIES
new_strat = pd.read_excel(CWD+'\\RStrats\\' + 'VRR Timeseries.xlsx',
                                           sheet_name = 'BASKETS', index_col=0)

#CITI Dispersion
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'CITIDispersionIndex.xlsx',
                                           sheet_name = 'Gamma', index_col=0)



#calculated returns off of price data
bmk = 'SPX'
df_index_prices = pd.merge(df_index_prices, bmk_index, left_index=True, right_index=True, how='inner')
returns = df_index_prices.pct_change().dropna()
bmk_returns = pd.DataFrame({bmk: returns.pop(bmk)})

mvo_sh = mean_variance_optimization(returns, num_iterations=1000, optimization_type='sharpe')
mvo_ca = mean_variance_optimization(returns, bmk_returns, num_iterations=1000, optimization_type='calmar')

mean_var_weights_sh = pd.concat([pd.DataFrame({'Optimal Weight: Sharpe': mvo_sh['final_optimal_weights'].tolist()}, index=returns.columns.tolist()), pd.DataFrame({'Optimal Weight: Sharpe': [mvo_sh['final_portfolio_return'], mvo_sh['final_portfolio_volatility'], mvo_sh['final_portfolio_ret/vol']]}, index=['Ret', 'Vol', 'Ret/Vol'])])
mean_var_weights_ca = pd.concat([pd.DataFrame({'Optimal Weight: Calmar': mvo_ca['final_optimal_weights'].tolist()}, index=returns.columns.tolist()), pd.DataFrame({'Optimal Weight: Calmar': [mvo_ca['final_portfolio_return'], mvo_ca['final_portfolio_volatility'], mvo_ca['final_portfolio_ret/vol']]}, index=['Ret', 'Vol', 'Ret/Vol'])])

program_mean_var_weights = pd.merge(mean_var_weights_sh, mean_var_weights_ca, left_index=True, right_index=True, how='inner')



















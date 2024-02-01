
import pandas as pd
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

# Using from MVO
mvo_sh = mvo.mean_variance_optimization(returns, num_iterations=10, optimization_type='sharpe')
mvo_ca = mvo.mean_variance_optimization(returns, bmk_returns, num_iterations=10, optimization_type='calmar')

# Using from RCM
rob_cov = rcm.get_robust_cov_matrix(bmk_returns, returns, components=2, threshold = 0.05, regime_weight = .7, upper_level = False)

mvo_sh = rcm.mean_variance_optimization(returns, bmk_returns, optimization_type='sharpe')
mvo_ca = rcm.mean_variance_optimization(returns, bmk_returns, optimization_type='calmar')

# =============================================================================
# mean_var_weights_sh = pd.concat(
#     [pd.DataFrame({'Optimal Weight: Sharpe': mvo_sh['final_optimal_weights'].tolist()}, index=returns.columns.tolist()),
#      pd.DataFrame({'Optimal Weight: Sharpe': [mvo_sh['final_portfolio_return'], mvo_sh['final_portfolio_volatility'],
#                                               mvo_sh['final_portfolio_ret/vol']]}, index=['Ret', 'Vol', 'Ret/Vol'])])
# mean_var_weights_ca = pd.concat(
#     [pd.DataFrame({'Optimal Weight: Calmar': mvo_ca['final_optimal_weights'].tolist()}, index=returns.columns.tolist()),
#      pd.DataFrame({'Optimal Weight: Calmar': [mvo_ca['final_portfolio_return'], mvo_ca['final_portfolio_volatility'],
#                                               mvo_ca['final_portfolio_ret/vol']]}, index=['Ret', 'Vol', 'Ret/Vol'])])
# 
# program_mean_var_weights = pd.merge(mean_var_weights_sh, mean_var_weights_ca, left_index=True, right_index=True, how='inner')
# =============================================================================






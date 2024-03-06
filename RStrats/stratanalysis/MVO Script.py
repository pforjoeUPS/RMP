
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
mvo_shar = mvo.mean_variance_optimization(returns, num_iterations=10, optimization_type='sharpe')
mvo_calm = mvo.mean_variance_optimization(returns, bmk_returns, num_iterations=1, optimization_type='calmar')
mvo_cvar = mvo.mean_variance_optimization(returns, bmk_returns, num_iterations=1, optimization_type='cvar')

# Using from MVO_basic
mvo_shar = mvo.mean_variance_optimization_basic(returns, optimization_type='sharpe')
mvo_calm = mvo.mean_variance_optimization_basic(returns, bmk_returns, optimization_type='calmar')
mvo_sort = mvo.mean_variance_optimization_basic(returns, optimization_type='sortino')
mvo_cvar = mvo.mean_variance_optimization_basic(returns, bmk_returns, optimization_type='cvar')
mvo_bene = mvo.mean_variance_optimization_basic(returns, optimization_type='benefit')
mvo_cone = mvo.mean_variance_optimization_basic(returns, optimization_type='convexity')
mvo_cost = mvo.mean_variance_optimization_basic(returns, optimization_type='cost')

optimization_types = ['sharpe', 'calmar', 'sortino', 'cvar', 'benefit', 'convexity', 'cost']
mvo_results_df = pd.DataFrame()

for opt_type in optimization_types:
    if opt_type in ['sharpe', 'sortino', 'convexity', 'cost']:
        result = mvo.mean_variance_optimization_basic(returns, optimization_type=opt_type)
    else:
        result = mvo.mean_variance_optimization_basic(returns, bmk_returns, optimization_type=opt_type)
    name = 'mvo_' + opt_type
    mvo_results_df[name] = result['final_optimal_weights']

print(mvo_results_df)



# Using from RCM
rob_cov = rcm.get_robust_cov_matrix(bmk_returns, returns, components=2, threshold = 0.05, regime_weight = .7, upper_level = False)

mvo_sh = rcm.mean_variance_optimization(returns, bmk_returns, optimization_type='sharpe')
mvo_ca = rcm.mean_variance_optimization(returns, bmk_returns, optimization_type='calmar')

optimization_types = ['sharpe', 'calmar']
mvo_results_df = pd.DataFrame()
for opt_type in optimization_types:
    result = rcm.mean_variance_optimization(returns, bmk_returns, optimization_type='sharpe')
    name = 'mvo_' + opt_type
    mvo_results_df[name] = result['final_optimal_weights']

mvo_results_df.to_excel(CWD +'\\RStrats\\RCM_MVO.xlsx', index=True)


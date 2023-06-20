from EquityHedging.datamanager import data_manager as dm
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from matplotlib.ticker import PercentFormatter

#import returns data
equity_bmk = 'SPTR'
returns = dm.get_equity_hedge_returns(equity_bmk)

comparison_strategy = 'Down Var'
frequency = 'Daily'

#load the returns data for SPTR and the selected strategy
sptr_returns = returns[frequency][equity_bmk]
comparison_returns = returns[frequency][comparison_strategy]

#creates a dataframe of the isolated returns
data = pd.concat([sptr_returns, comparison_returns], axis=1)
data.columns = [equity_bmk, comparison_strategy]

#splits the data accordingly
data_sptr_pos = data[data[equity_bmk] >= 0]
data_sptr_neg = data[data[equity_bmk] < 0]

#prepares the input features (SPTR) and target variable (selected strategy) for each subset
X_pos = data_sptr_pos[equity_bmk].values.reshape(-1, 1)
y_pos = data_sptr_pos[comparison_strategy].values
X_neg = data_sptr_neg[equity_bmk].values.reshape(-1, 1)
y_neg = data_sptr_neg[comparison_strategy].values
X_all = data[equity_bmk].values.reshape(-1, 1)
y_all = data[comparison_strategy].values

#fits separate linear regressions
regression_model_pos = LinearRegression()
regression_model_pos.fit(X_pos, y_pos)
regression_model_neg = LinearRegression()
regression_model_neg.fit(X_neg, y_neg)
regression_model_all = LinearRegression()
regression_model_all.fit(X_all, y_all)

#get the regression line coordinates
x_range_pos = np.linspace(min(X_pos), max(X_pos), 100)
y_pred_pos = regression_model_pos.predict(x_range_pos.reshape(-1, 1))
x_range_neg = np.linspace(min(X_neg), max(X_neg), 100)
y_pred_neg = regression_model_neg.predict(x_range_neg.reshape(-1, 1))

#prints seperate linear equations 
intercept_pos = regression_model_pos.intercept_
coefficient_pos = regression_model_pos.coef_[0]
intercept_neg = regression_model_neg.intercept_
coefficient_neg = regression_model_neg.coef_[0]
intercept_all = regression_model_all.intercept_
coefficient_all = regression_model_all.coef_[0]
print(f"Regression equation (SPTR >= 0): {comparison_strategy} = {coefficient_pos:.4f} * {equity_bmk} + {intercept_pos:.4f}")
print(f"Regression equation (SPTR < 0): {comparison_strategy} = {coefficient_neg:.4f} * {equity_bmk} + {intercept_neg:.4f}")
print(f"Regression equation (All Data): {comparison_strategy} = {coefficient_all:.4f} * {equity_bmk} + {intercept_all:.4f}")

#prints seperate bets for each condition
beta_pos = coefficient_pos
beta_neg = coefficient_neg
beta_all = coefficient_all
print(f"Beta (All Data): {beta_all:.4f}")
print(f"Beta (SPTR >= 0): {beta_pos:.4f}")
print(f"Beta (SPTR < 0): {beta_neg:.4f}")

#creates graph of points, line of best fit, etc.
plt.scatter(X_pos, y_pos, color='g', label='Data Points (SPTR >= 0)')
plt.scatter(X_neg, y_neg, color='b', label='Data Points (SPTR < 0)')
plt.plot(x_range_pos, y_pred_pos, color='r', label='Regression Line (SPTR >= 0)')
plt.plot(x_range_neg, y_pred_neg, color='orange', label='Regression Line (SPTR < 0)')
plt.xlabel(equity_bmk)
plt.ylabel(comparison_strategy)
plt.title(f'Regression Analysis: {equity_bmk} vs {comparison_strategy} ({frequency} Returns)')
#change axis labels into percentages
plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=1))
plt.gca().xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=1))
plt.plot

#create method in plots and bring that to script
from EquityHedging.datamanager import data_manager as dm

#for regressions
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

#import returns data
equity_bmk = 'SPTR'
strat_drop_list = []
returns= dm.get_equity_hedge_returns(equity_bmk)

comparison_strategy = 'Down Var'
#write in greater or less
comparison_direction = 'greater'
frequency = 'Daily'

#load the returns data for SPTR and the selected strategy
sptr_returns = returns[frequency]['SPTR']
comparison_returns = returns[frequency][comparison_strategy]

#create a DataFrame for the regression analysis
data = pd.concat([sptr_returns, comparison_returns], axis=1)
data.columns = ['SPTR', comparison_strategy]

#filter the data based on the selected direction
if comparison_direction == 'greater':
    data = data[data['SPTR'] >= 0]
else:
    data = data[data['SPTR'] < 0]

#prepare the input features (SPTR) and target variable (selected strategy)
X = data['SPTR'].values.reshape(-1, 1)
y = data[comparison_strategy].values

#fit the linear regression model
regression_model = LinearRegression()
regression_model.fit(X, y)

#get the regression line coordinates
x_range = np.linspace(min(X), max(X), 100)
y_pred = regression_model.predict(x_range.reshape(-1, 1))

#print the regression coefficients
intercept = regression_model.intercept_
coefficient = regression_model.coef_[0]
print(f"Regression equation: {comparison_strategy} = {coefficient:.4f} * SPTR + {intercept:.4f}")

#calculate beta as the coefficient of SPTR
beta = coefficient
print(f"Beta: {beta:.4f}")

#TODO : Great job on the plot. However, the chart shoud be a scatter plot of all returns
# with 2 different regression lines on it 
#one regression line fitting only returns when sptr<0 and another regression line when sptr>=0
# refer to the screen shot in the email for the proj descrription :)
#plot the scatter plot of the data points and the regression line
plt.scatter(X, y, color='b', label='Data Points')
plt.plot(x_range, y_pred, color='r', label='Regression Line')
plt.xlabel('SPTR')
plt.ylabel(comparison_strategy)
plt.title(f'Regression Analysis: SPTR vs {comparison_strategy} ({frequency} Returns)')
plt.legend()
plt.show()

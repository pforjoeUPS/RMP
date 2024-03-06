import os
CWD = os.getcwd()
from EquityHedging.datamanager import data_manager as dm
from RStrats.stratanalysis import MarginalAnalysis as marg
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np

equity_bmk = 'SPTR'
strat_drop_list = ['SPTR', 'Vortex', 'VRR Trend']
include_fi = False
strat = 'UBCSSKUE Index'
strat_weight = 1
start_date = pd.to_datetime('2019-12-31')

# bmk returns
bmk = pd.read_excel(dm.NEW_DATA + 'SPX&MXWDIM Historical Price.xlsx', sheet_name='MXWDIM', index_col=0)
bmk_dict = dm.get_data_dict(bmk)
for key, df in bmk_dict.items():
    # Filter to only include data from the start_date onwards
    filtered_df = df[df.index >= start_date]

    # Update the dictionary with the filtered DataFrame
    bmk_dict[key] = filtered_df

# new strat returns
new_strat = pd.read_excel(dm.NEW_DATA + 'LongSkewPutRatio CITI.xlsx', sheet_name='Sheet4', index_col=0)
new_strat_dict = dm.get_data_dict(new_strat)
for key, df in new_strat_dict.items():
    # Filter to only include data from the start_date onwards
    filtered_df = df[df.index >= start_date]

    # Update the dictionary with the filtered DataFrame
    new_strat_dict[key] = filtered_df

# eqhedge index returns
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list, only_equity=False)
df_index_prices = dm.get_prices_df(returns['Daily']) * 100
df_index_prices = df_index_prices[df_index_prices.index >= start_date]
eqhedge_index = marg.get_weighted_index(df_index_prices, name='EqHedge', notional_weights=[1,1.25,0.5,0.8,1,.25,1,1,1.05,1,0.5])
eqhedge_dict = dm.get_data_dict(eqhedge_index)

full_data_dict = dm.merge_dicts_list([bmk_dict, eqhedge_dict, new_strat_dict])
daily_index = dm.get_prices_df(full_data_dict['Daily'])*100
weighted_program_strat_index = marg.get_weighted_index(daily_index.iloc[:,1:], name='EqHedge Program w '+strat, notional_weights=[9.35,strat_weight]) / 100
daily_index['EqHedge Program w '+strat] = weighted_program_strat_index['EqHedge Program w '+strat]
daily_index = daily_index.drop(strat, axis=1)
rolling_monthly_returns = ((1 + (daily_index.pct_change())).rolling(window=20).apply(lambda x: x.prod()) - 1).dropna()


def create_convexity_fit(returns):
    """"
    Creates scatter plot

    Parameters:
    returns -- dataframe containing monthly rolling returns (bmk, EqHedge w Strat, EqHedge)
        assumes returns are in the order of bmk returns is first
    """
    # Get column names
    names = returns.columns.tolist()

    # Create scatter plot
    plt.figure(figsize=(13.5, 6))

    # Plot data
    plt.scatter(returns[names[0]], returns[names[1]], color='red', label=names[1])
    plt.scatter(returns[names[0]], returns[names[2]], color='blue', label=names[2])

    # Fit a 2nd order polynomial (quadratic curve) to 'Y1' and 'MXWDIM'
    coefficients_y1 = np.polyfit(returns['MXWDIM'], returns[names[1]], 2)
    poly_y1 = np.poly1d(coefficients_y1)

    # Fit a 2nd order polynomial to 'Y2' and 'MXWDIM'
    coefficients_y2 = np.polyfit(returns['MXWDIM'], returns[names[2]], 2)
    poly_y2 = np.poly1d(coefficients_y2)

    # Generate x values for plotting the trendline
    x_values = np.linspace(returns['MXWDIM'].min(), returns['MXWDIM'].max(), 100)

    # Plot the trendlines
    plt.plot(x_values, poly_y1(x_values), color='red', linestyle='dashed', label=f'{names[1]} Trendline')
    plt.plot(x_values, poly_y2(x_values), color='blue', linestyle='dashed', label=f'{names[2]} Trendline')

    # Plot the trendline equations
    formula_y1 = f'y = {coefficients_y1[0]:.4f}x² + {coefficients_y1[1]:.4f}x + {coefficients_y1[2]:.4f}'
    plt.text(1.0, 1.10, formula_y1, transform=plt.gca().transAxes, color='red', horizontalalignment='right', verticalalignment='top')
    formula_y2 = f'y = {coefficients_y2[0]:.4f}x² + {coefficients_y2[1]:.4f}x + {coefficients_y2[2]:.4f}'
    plt.text(1.0, 1.05, formula_y2, transform=plt.gca().transAxes, color='blue', horizontalalignment='right', verticalalignment='top')

    # Adding labels and title
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{100 * x:.0f}%'))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{100 * x:.0f}%'))
    plt.axhline(0, color='gray', linestyle='dotted', linewidth=0.5)
    plt.axvline(0, color='gray', linestyle='dotted', linewidth=0.5)
    plt.xlabel('MXWDIM Returns')
    plt.ylabel('Portfolio Returns')
    plt.legend()

    # Display the plot
    plt.show()

create_convexity_fit(rolling_monthly_returns)

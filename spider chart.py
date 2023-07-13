import numpy as np
import matplotlib.pyplot as plt
import EquityHedging.analytics.util as ut
import EquityHedging.analytics.hedge_metrics as hm
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import summary 


#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False

returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

#get notional weights

notional_weights = dm.get_notional_weights(returns['Monthly'])
returns = dm.create_vrr_portfolio(returns,notional_weights)
notional_weights[4:6] = [notional_weights[4] + notional_weights[5]]

df_weights = ut.get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)
returns_df = returns['Daily']

#get weighted strats and weighted hedges
r = summary.get_weighted_data(returns_df, notional_weights)

# Step 3: Compute hedge metrics, this line causes an error for some reason but the rest of it runs fine. 
df_hedge_metrics = hm.get_hedge_metrics(r,freq = "1D", full_list=True)

# Step 4: Select specific metrics for spider chart
metrics_to_plot = df_hedge_metrics.transpose()
metrics = metrics_to_plot[["Benefit Cum", "Convexity Cum", "Cost Cum", "Downside Reliability", "Decay Days (25% retrace)"]]

# Step 5: Normalize the hedge metrics
normalized_data = ut.get_normalized_data(metrics)

# Get the strategy names
strategies = normalized_data.index

# Get the values for each strategy
values = normalized_data.values

# Create a radar chart for each strategy
for i in range(len(strategies)):
    # Get the values for the current strategy
    strategy_values = values[i].tolist()
    strategy_values.append(strategy_values[0])  # Close the loop
    
    # Create a new figure and polar axis for the radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    
    # Set the angles and plot the strategy values
    angles = np.linspace(0, 2 * np.pi, len(metrics.columns), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    ax.plot(angles, strategy_values)
    
    # Set the labels for each angle
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics.columns)
    
    # Set the title as the strategy name
    ax.set_title(strategies[i])
    
    # Show the plot
    plt.show()
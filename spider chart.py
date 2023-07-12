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

# Step 3: Compute hedge metrics, ask to find where to find dataframe of the returns
df_hedge_metrics = hm.get_hedge_metrics(r,freq = "1D", full_list=True)

# Step 4: Select specific metrics for spider chart
metrics_to_plot = df_hedge_metrics.transpose()
metrics = metrics_to_plot[["Benefit Cum", "Convexity Cum", "Cost Cum", "Downside Reliability", "Decay Days (25% retrace)"]]

# Step 5: Normalize the hedge metrics
normalized_data = ut.get_normalized_data(metrics)

test = normalized_data.transpose()
x = test['SPTR']

# Step 6: Create a spider chart for each strategy
for strategy in normalized_data.index:
    values = normalized_data.loc[strategy].tolist()
    values.append(values[0])  # Close the loop
    labels = metrics_to_plot + [metrics_to_plot[0]]  # Add the first label at the end for closed loop
    
    # Plot the spider chart
    angles = [n / float(len(labels)) * 2 * np.pi for n in range(len(labels))]
    angles += angles[:1]  # Close the loop
    plt.polar(angles, values)
    plt.fill(angles, values, alpha=0.25)
    plt.xticks(angles[:-1], labels[:-1])
    plt.yticks([])
    plt.title(strategy)
    plt.show()

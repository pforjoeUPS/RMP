import pandas as pd
from RStrats.stratanalysis import MarginalAnalysis as marg
from EquityHedging.datamanager import data_manager as dm
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import os
CWD = os.getcwd()


#MXWDIM DATA
bmk_index = pd.read_excel(dm.NEW_DATA + 'Commods TICKERS.xlsx', sheet_name = 'MXWDIM', index_col=0)
#DATA
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'Commods TICKERS.xlsx', sheet_name = 'EqHedgePrices', index_col=0)
eqhedge_index = marg.get_weighted_index(df_index_prices, name = 'EqHedge', notional_weights = [1,0,1.25,0.5,0.8,0,1,.25,1,1,1.05,1,0.5]) #[1,1.25,0.5,0.85,1,.25,1,1,1.05,0.5,1])

dcp_strat_index = pd.read_excel(CWD+'\\RStrats\\' + 'Commods TICKERS.xlsx', sheet_name = 'DCP', index_col=0)
dcpineh_index = marg.get_weighted_index(data, name ='Program+DCP', notional_weights = [9.35,1])

data = dm.merge_data_frames(eqhedge_index, dcp_strat_index)

#========================
#FOR SINGULAR INDEX ANALYSIS
bmk = 'MXWDIM'
bmk_index = bmk_index
strat = 'DCP'
strat_index = dcp_strat_index#marg.get_weighted_index(df_index_prices, name = strat, notional_weights = [1,1,1,1,1,1]) #[1,1.25,0.5,0.85,1,.25,1,1,1.05,0.5,1])
overlay_weights = [0,.01,.02,.03,.04,.05,.06,.07,.08,.09,.1]

df_metrics = marg.get_returns_analysis(bmk_index, strat_index,eqhedge_index, bmk = bmk, strat = strat, weights = overlay_weights)
marg.show_SharpeCVaR(df_metrics, BMK = bmk, Strat = strat, weights = overlay_weights)
marg.show_plots(df_metrics, Strat = strat)
marg.transpose_export_excel_file(df_metrics, strat_type = 'DCPMODIFIED')


# WIP
# FOR MULTIPLE INDICIES ANALYSIS
BMK = 'MXWDIM'
strat_type = 'Program w and wo DCP'
strat_index = data
strat_list = data.columns.tolist()
strat_list.remove('MXWDIM')

# Get Analysis Metrics
dict_strat_metrics = {}
for strat in strat_list:
    df_stratname = f'{strat}'
    dict_strat_metrics[df_stratname] = marg.get_returns_analysis(strat_index[BMK], strat_index[strat], bmk= BMK, strat=strat)

# Graph plots
for strat in strat_list:
    df_stratname = f'{strat}'
    marg.show_SharpeCVaR(dict_strat_metrics[df_stratname], Strat=strat)
    marg.show_plots(dict_strat_metrics[df_stratname], Strat=strat)

# graphing against strategies
test_strat_list = list(dict_strat_metrics.keys())
plot_list = ['Ret', 'Vol', 'Sharpe', 'CVaR', 'Tracking Error', 'Corr', 'IR']
for graph in plot_list:
    for strat in test_strat_list:
        ol_weights_index_list = dict_strat_metrics[strat].index.tolist()
        bmk_name = ol_weights_index_list[0]  # Assuming this is the label you want at (0,0)
        metrics_results_list = dict_strat_metrics[strat][graph]

        # Plot
        plt.scatter(ol_weights_index_list, metrics_results_list, label=strat, marker='o')

    # Formatting the plot
    plt.xticks(rotation=-45)
    plt.xlabel('Extended Weights')
    plt.ylabel(graph)
    plt.title(strat_type + ': ' + graph)

    if graph in ['Tracking Error', 'CVaR', 'Ret', 'Vol']:
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

    # Set x-ticks. Assuming the first tick is at 0.0, replace it with `bmk_name`
    current_ticks = plt.gca().get_xticks()
    new_labels = [bmk_name if x == 0.0 else f'{x:.0f}%' for x in current_ticks]
    plt.xticks(current_ticks, new_labels)
    plt.tight_layout()

    plt.legend(loc='best')
    plt.show()


# get report
marg.transpose_export_excel_file(dict_strat_metrics, strat_type=strat_type, multiple=True)




import pandas as pd
from RStrats.stratanalysis import MarginalAnalysis as marg
import os
CWD = os.getcwd()


#MXWDIM DATA
bmk_index = pd.read_excel(CWD+'\\RStrats\\' + 'SPX&MXWDIM Historical Price.xlsx', sheet_name = 'MXWDIM', index_col=0)

#PROGRAM DATA
df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'weighted hedgesSam.xlsx', sheet_name = 'Program', index_col=0)

bmk = 'MXWDIM'
df_index_prices = pd.merge(df_index_prices, bmk_index, left_index=True, right_index=True, how='inner')

#========================
#FOR SINGULAR INDEX ANALYSIS
bmk = 'MXWDIM'
strat = 'EqHedge'
strat_index = marg.get_weighted_index(df_index_prices, name = strat, notional_weights = [1,1.25,0.5,0.85,1,.25,1,1,1.05,0.5,1])
overlay_weights = [.05,.1,.15,.2,.25,.3,.35,.4,.45,.5]

df_metrics = marg.get_returns_analysis(bmk_index, strat_index, bmk = bmk, strat = strat, weights = overlay_weights)
marg.show_SharpeCVaR(df_metrics, BMK = bmk, Strat = strat, weights = overlay_weights)
marg.show_plots(df_metrics, Strat = strat)
marg.transpose_export_excel_file(df_metrics, strat_type = strat)


# WIP
# =============================================================================
# # FOR MULTIPLE INDICIES ANALYSIS
# BMK = 'MXWDIM'
# filename = '../GrindLowerHedgesTS.xlsx'
# sheetname = 'Sheet1'
# strat_type = 'GrindLowHedges'
# strat_index = pd.read_excel(CWD + '\\RStrats\\' + filename, sheet_name=sheetname, index_col=0)
# strat_list = strat_index.columns.tolist()
# strat_list.remove('MXWDIM')
# 
# # Get Analysis Metrics
# dict_strat_metrics = {}
# for strat in strat_list:
#     df_stratname = f'{strat}'
#     dict_strat_metrics[df_stratname] = get_returns_analysis(strat_index, BMK='MXWDIM', Strat=strat)
# 
# # Graph plots
# for strat in strat_list:
#     df_stratname = f'{strat}'
#     show_SharpeCVaR(dict_strat_metrics[df_stratname], Strat=strat)
#     show_plots(dict_strat_metrics[df_stratname], Strat=strat)
# 
# # graphing against strategies
# test_strat_list = list(dict_strat_metrics.keys())
# plot_list = ['Ret', 'Vol', 'Sharpe', 'CVaR', 'Tracking Error', 'Corr', 'IR', ]
# for graph in plot_list:
#     plt.figure(figsize=(8, 6))
#     for strat in test_strat_list:
#         ol_weights_index_list = dict_strat_metrics[strat].index.tolist()
#         metrics_results_list = dict_strat_metrics[strat][graph]
#         if graph == 'IR':
#             ol_weights_index_list.pop(0)
#             ol_weights_index_list = [float(x) for x in ol_weights_index_list]
#             metrics_results_list = dict_strat_metrics[strat][graph].copy().tolist()
#             metrics_results_list.pop(0)
#         plt.scatter(ol_weights_index_list, metrics_results_list, label=strat, marker='o')
#     plt.xticks(rotation=-45)
#     plt.xlabel('Extended Weights')
#     plt.ylabel(graph)
#     plt.title(strat_type + ': ' + graph)
#     if graph == 'IR':
#         plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
# 
#     plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
#     plt.show()
# 
# # get report
# transpose_export_excel_file(dict_strat_metrics, strat_type=strat_type, multiple=True)
# =============================================================================




# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 15:45:57 2023

@author: pcr7fjw
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import returns_stats  as rs
from matplotlib.ticker import FuncFormatter
import os
CWD = os.getcwd()

def percent_formatter(x, pos):
    return f'{x * 100:.2f}%'

def get_max_dd_from_returns(df):
    # Calculate the cumulative returns
    df['Cumulative_Returns'] = (1 + df).cumprod()

    # Calculate the previous peaks
    df['Previous_Peaks'] = df['Cumulative_Returns'].cummax()

    # Calculate the drawdowns
    df['Drawdowns'] = (df['Cumulative_Returns'] / df['Previous_Peaks']) - 1
    
    # Calculate the Maximum Drawdown
    max_drawdown = df['Drawdowns'].min()
    return max_drawdown

#weighted index by notional weights
def get_weighted_index(df_index_prices, notional_weights = []):
    weight_ratio = [notional / sum(notional_weights) for notional in notional_weights]
    strat_list = df_index_prices.columns.tolist()
    weighted_index = 100 + pd.Series(0, index=df_index_prices.index) 
    for i in range(0,len(strat_list)):
        strat = strat_list[i]
        strat_weight = weight_ratio[i]
        StratStartLevel = df_index_prices[strat][0]
        StratShare = (strat_weight * 100 / StratStartLevel) * (df_index_prices[strat] - StratStartLevel)
        weighted_index += StratShare
    
    return weighted_index


def get_returns_analysis(df_index_prices, BMK = '', Strat = '', weights = [.01,.02,.03,.04,.05,.06,.07,.08,.09,.1,.11,.12,.13,.14,.15]):  
    df_weighted_prices = pd.DataFrame({BMK: df_index_prices[BMK],Strat: df_index_prices[Strat]})
    StratStartLevel = df_index_prices[Strat][0]
    MXWDIMStartLevel = df_index_prices[BMK][0]
    for i in weights:
        StratShare = i * 100.0 / StratStartLevel
        MXWDIMShare = 100.0 / MXWDIMStartLevel
        df_weighted_prices[str(i)] = 100.0 + StratShare * (df_index_prices[Strat] - StratStartLevel) + MXWDIMShare * (df_index_prices[BMK]  - MXWDIMStartLevel)
 
    returns_strat_only = dm.get_data_dict(df_weighted_prices)['Daily'].drop((Strat), axis=1)

    var_list = []
    cvar_list = []
    sharpe_list = []
    ret_list = []
    vol_list = []
    trackerror_list = []
    ir_list = []
    corr_list = []
    max_dd_list = []
    
    for col in returns_strat_only:
        ret = returns_strat_only[col].mean() * 252
        vol = returns_strat_only[col].std() * np.sqrt(252)
        sharpe = ret/vol
        bottom5pct = np.percentile(returns_strat_only[col].values[1:],q=5)
        cvar = returns_strat_only[col][returns_strat_only[col] < bottom5pct].mean()
        excess_return = (returns_strat_only[col]- returns_strat_only[BMK])
        track_error = np.std(excess_return) * np.sqrt(252)
        if track_error == 0:
            information_ratio = 0
        else:     
            information_ratio = excess_return.mean() * 252 / track_error
        correlation = returns_strat_only[BMK].corr(returns_strat_only[col])
        max_dd = get_max_dd_from_returns(returns_strat_only[col])
        
        var_list.append(bottom5pct)
        cvar_list.append(cvar)
        sharpe_list.append(sharpe)
        ret_list.append(ret)
        vol_list.append(vol)
        trackerror_list.append(track_error)
        ir_list.append(information_ratio)
        corr_list.append(correlation)
        max_dd_list.append(max_dd)
        
    df_metrics = pd.DataFrame()
    df_metrics['Ret'] = ret_list
    df_metrics['Vol'] = vol_list
    df_metrics['Sharpe'] = sharpe_list
    df_metrics['5%-ile'] = var_list
    df_metrics['CVaR'] = cvar_list
    df_metrics['Tracking Error'] = trackerror_list
    df_metrics['IR'] = ir_list
    df_metrics['Corr'] = corr_list
    df_metrics['Max DD'] = max_dd_list 
    df_metrics.set_index(returns_strat_only.columns,inplace=True)
    df_metrics['Rank'] = df_metrics['Tracking Error'].rank()
    df_metrics['Rank'] = df_metrics['Rank'] * 50
    
    return df_metrics

#plot SharpeVSCVaR
def show_SharpeCVaR(df_metrics, BMK = '', Strat = '', weights = []):
    fig, ax = plt.subplots(figsize=(23, 15))
    plt.scatter(df_metrics['CVaR'], df_metrics['Sharpe'], s= df_metrics['Rank'], c = 'blue', marker='o', label='')
    labels = [BMK + ' 0 weight'] + [f'{int(wei * 100)}%' for wei in weights]
    # Add labels to each data point
    for i, label in enumerate(labels):
        plt.annotate(label, (df_metrics['CVaR'][i], df_metrics['Sharpe'][i]), textcoords="offset points", xytext=(-5,20), ha='center')
    #Round x and y axes
    for i, (x, y) in enumerate(zip(df_metrics['CVaR'], df_metrics['Sharpe'])):
       x_rounded = round(x, 4)
       y_rounded = round(y, 3)
       label = f'({x_rounded}%, {y_rounded})'
       plt.text(x+0.00002, y, label, ha='left', va='bottom')
    # Customize the plot
    plt.xticks(rotation=-45)
    plt.gca().xaxis.set_major_formatter(FuncFormatter(percent_formatter))
    plt.xlabel('CVaR')
    plt.ylabel('Sharpe')
    plt.title('MXWDIM w ' + Strat)
    plt.show()

#plot for sharpe, cvar, tracking error, correlation, information ratio against extended weights of strategy
def show_plots(df_metrics, Strat = ''):
    plot_list = ['Sharpe', 'CVaR', 'Tracking Error', 'Corr', 'IR']
    ol_weight_index_list = df_metrics.index.tolist()
    for graph in plot_list:
        if graph == 'IR':
            ol_weight_index_list_IR = ol_weight_index_list.copy()
            ol_weight_index_list_IR.pop(0)
            ol_weight_index_list_IR_float = [float(x) for x in ol_weight_index_list_IR]
            df_metrics_IR = df_metrics[graph].copy().tolist()
            df_metrics_IR.pop(0)
            plt.scatter(ol_weight_index_list_IR_float, df_metrics_IR, c = 'blue', marker='o', label='')
            
            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    
            plt.xticks(rotation=-45)
            plt.xlabel('Extended ' + Strat + ' Weights')
            plt.ylabel(graph)
            plt.title('MXWDIM w ' + Strat + ': ' + 'Information Ratio')
            #plt.legend()
            plt.show()
        else:
            plt.scatter(ol_weight_index_list, df_metrics[graph], c = 'blue', marker='o', label='')
            plt.xticks(rotation=-45)
            plt.xlabel('Extended ' + Strat + ' Weights')
            plt.ylabel(graph)
            plt.title('MXWDIM w ' + Strat + ': ' + graph)
            #plt.legend()
            plt.show()

#Transpose dataframes and Create an ExcelWriter object and specify the file name
def transpose_export_excel_file(strat_metrics, strat_type = '', multiple = False):
    if multiple == True:
        for strat, df in strat_metrics.items():
            df = df.transpose()
            df.columns = [df.columns[0]] + [f'{float(col) * 100:.0f}%' for col in df.columns[1:]]
            dict_strat_metrics[strat] = df
        with pd.ExcelWriter(CWD+'\\RStrats\\' + strat_type + 'MetricsAnalysis.xlsx', engine='xlsxwriter') as writer:
            for sheet_name, df in dict_strat_metrics.items():
                df.to_excel(writer, sheet_name=sheet_name, index=True)
    else:
        strat_metrics = strat_metrics.transpose()
        file_path = CWD +'\\RStrats\\'+ Strat + 'Metrics.xlsx'
        # Export the DataFrame to an Excel file
        strat_metrics.to_excel(file_path, index=True)
        
    print(f"DataFrame exported to {file_path}")


df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'Performance Q3 2023.xlsx', sheet_name = 'Sheet2', index_col=0)
MXWDIM_index = pd.read_excel(CWD+'\\RStrats\\' + 'Commods Example.xlsx', sheet_name = 'Sheet2', index_col=0)['MXWDIM']

strats_weighted_index = get_weighted_index(df_index_prices, notional_weights = [1,1.25,1,1,1,.25,1,1,.55,1])

df_index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'Commods Example.xlsx', sheet_name = 'Sheet4', index_col=0)
MXWDIM_index = pd.read_excel(CWD+'\\RStrats\\' + 'Commods Example.xlsx', sheet_name = 'Sheet2', index_col=0)['MXWDIM']

commods_weighted_index = get_weighted_index(df_index_prices, notional_weights = [1.25, 0.167, 0.167, 0.167, 0.167, 0.167, 0.167])
df_index_prices = pd.concat([MXWDIM_index, commods_weighted_index], axis=1, keys=["MXWDIM", "Commods Weighted Index"], join='inner')




#FOR SINGULAR INDEX ANALYSIS
BMK = 'MXWDIM'
Strat = 'Commods Weighted Index'
weights = [.05,.1,.15,.2,.25,.3,.35,.4,.45,.5]

df_metrics = get_returns_analysis(df_index_prices, BMK = BMK, Strat = Strat, weights = weights)
show_SharpeCVaR(df_metrics, BMK = BMK, Strat = Strat, weights = weights)
show_plots(df_metrics, Strat = Strat)
transpose_export_excel_file(df_metrics, strat_type = Strat)



#FOR MULTIPLE INDICIES ANALYSIS
BMK = 'MXWDIM'
filename = 'Commods Example.xlsx'
sheetname = 'Sheet2'
strat_type = 'Commods Basket'
strat_index = pd.read_excel(CWD+'\\RStrats\\' + filename, sheet_name = sheetname, index_col = 0)
strat_list = strat_index.columns.tolist()
strat_list.remove('MXWDIM')

#Get Analysis Metrics
dict_strat_metrics = {}
for strat in strat_list:
    df_stratname = f'{strat}'
    dict_strat_metrics[df_stratname] = get_returns_analysis(strat_index, BMK = 'MXWDIM', Strat = strat)

#Graph plots
for strat in strat_list:
    df_stratname = f'{strat}'
    show_SharpeCVaR(dict_strat_metrics[df_stratname], Strat = strat)
    show_plots(dict_strat_metrics[df_stratname], Strat = strat)

#graphing against strategies
test_strat_list = list(dict_strat_metrics.keys())
plot_list = ['Ret', 'Vol', 'Sharpe', 'CVaR', 'Tracking Error', 'Corr', 'IR',]
for graph in plot_list:
    plt.figure(figsize=(8, 6))
    for strat in test_strat_list:
        ol_weights_index_list = dict_strat_metrics[strat].index.tolist()
        metrics_results_list = dict_strat_metrics[strat][graph]
        if graph == 'IR':
            ol_weights_index_list.pop(0)
            ol_weights_index_list = [float(x) for x in ol_weights_index_list]
            metrics_results_list = dict_strat_metrics[strat][graph].copy().tolist()
            metrics_results_list.pop(0)
        plt.scatter(ol_weights_index_list, metrics_results_list, label=strat, marker='o')
    plt.xticks(rotation=-45)
    plt.xlabel('Extended Weights')
    plt.ylabel(graph)
    plt.title(strat_type + ': ' + graph)
    if graph == 'IR':
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()

#get report
transpose_export_excel_file(dict_strat_metrics, strat_type = strat_type, multiple = True)











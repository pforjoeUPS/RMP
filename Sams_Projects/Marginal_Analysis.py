# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 15:45:57 2023

@author: pcr7fjw
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from EquityHedging.datamanager import data_xformer_new as dxf, data_manager_new as dm
from EquityHedging.analytics import returns_stats_new as rsn
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import PercentFormatter
import os

CWD = os.getcwd()

RET_STATS_DICT = {'ann_ret': 'get_ann_return', 'ann_vol': 'get_ann_vol', 'max_dd': 'get_max_dd',
                  'ret_vol': 'get_sharpe_ratio', 'sortino': 'get_sortino_ratio',
                  'ret_dd': 'get_ret_max_dd_ratio', 'var': 'get_var', 'cvar': 'get_cvar'}

# TODO: Two ways: keep where it is one ret_stats_dict or separate and combine later
ACTIVE_RET_STATS_DICT = {'correlation': 'get_correlation', 'tracking_error': 'get_tracking_error', 'information_ratio': 'get_information_ratio'}
                         # 'bmk_beta': 'get_beta', 'excess_ret': 'get_excess_return', 'te': 'get_tracking_error',
                         # 'downside_te': 'get_tracking_error', 'ir': 'get_information_ratio',
                         # 'ir_asym': 'get_information_ratio'}

def percent_formatter(x, pos):
    return f'{x * 100:.2f}%'

def get_method_data(returns_stats, ret_stat):
    method_name = RET_STATS_DICT.get(ret_stat)
    method = getattr(returns_stats, method_name)
    return method

def get_correlation(self, returns_series, bmk_series):
    return bmk_series.corr(returns_series)

def get_returns_stats_list(returns_stats, returns_df, stat):
    ret_stat_method = get_method_data(returns_stats, stat)
    if stat in ACTIVE_RET_STATS_DICT.keys():
        return [ret_stat_method(returns_df[x], returns_df.iloc[:, 0]) for x in returns_df]
    else:
        return [ret_stat_method(returns_df[x]) for x in returns_df]

#TODO: Make it adaptable to different frequencies
def get_returns_analysis(bmk_index, strat_index, bmk, strat, freq,
                         weights=[.01, .02, .03, .04, .05, .06, .07, .08, .09, .1, .11, .12, .13, .14, .15]):
    df_index_prices = dm.merge_dfs(bmk_index, strat_index, drop_na=False)
    strat_start_level = df_index_prices[strat].iloc[0]
    bmk_start_level = df_index_prices[bmk].iloc[0]
    weighted_prices = pd.DataFrame(data=df_index_prices[bmk], index=df_index_prices.index)

    for weight in weights:
        strat_share = weight * 100.0 / strat_start_level
        bmk_share = 100.0 / bmk_start_level
        weighted_prices[str(weight)] = 100.0 + strat_share * (strat_index[strat] - strat_start_level) + bmk_share * (bmk_index[bmk] - bmk_start_level)

    returns_df = dxf.format_df(weighted_prices, freq=freq, drop_na=False)
    returns_stats = rsn.ActiveReturnsStats(freq=freq)
    returns_stats.get_correlation = get_correlation.__get__(returns_stats)
    RET_STATS_DICT.update(ACTIVE_RET_STATS_DICT)

    df_metrics = pd.DataFrame()
    for ret_stat in RET_STATS_DICT:
        ret_stat_list = get_returns_stats_list(returns_stats, returns_df, stat=ret_stat)
        df_metrics[ret_stat] = ret_stat_list
    df_metrics.set_index(returns_df.columns, inplace=True)

    return df_metrics

def show_sharpe_cvar(df_metrics, bmk, strat, weights):

    fig, ax = plt.subplots(figsize=(23, 15))

    # Scatter plot
    plt.scatter(df_metrics['cvar'], df_metrics['ret_vol'], s=df_metrics['tracking_error']*500,
                c='blue', marker='o', label='')
    labels = [bmk + ' 0 weight'] + [f'{int(wei * 100)}%' for wei in weights]

    # Add labels to each data point
    for i, label in enumerate(labels):
        plt.annotate(label, (df_metrics['cvar'][i], df_metrics['ret_vol'][i]), textcoords="offset points",
                     xytext=(-5, 20), ha='center')

    # Round x and y axes
    for i, (x, y) in enumerate(zip(df_metrics['cvar'], df_metrics['ret_vol'])):
        x_rounded = round(x * 100, 4)
        y_rounded = round(y, 3)
        label = f'({x_rounded}%, {y_rounded})'
        plt.text(x + 0.0002, y, label, ha='left', va='bottom')

    # Label/Alter the plot
    plt.xticks(rotation=-45)
    plt.gca().xaxis.set_major_formatter(FuncFormatter(percent_formatter))
    plt.xlabel('CVaR')
    plt.ylabel('Sharpe')
    plt.title('MXWDIM w ' + strat)
    plt.tight_layout()
    plt.show()

def show_sharpe_cvar_sns(df_metrics, bmk, strat, weights):

    fig, ax = plt.subplots(figsize=(23, 15))

    # Scatter plot using Seaborn
    sns.scatterplot(x='cvar', y='ret_vol', size='tracking_error', sizes=(50, 200),
                    data=df_metrics, ax=ax, legend=False)

    labels = [bmk + ' 0 weight'] + [f'{int(wei * 100)}%' for wei in weights]

    # Add labels to each data point
    for i, label in enumerate(labels):
        ax.annotate(label, (df_metrics['cvar'][i], df_metrics['ret_vol'][i]), textcoords="offset points",
                     xytext=(-5, 20), ha='center')

    # Round x and y axes
    for i, (x, y) in enumerate(zip(df_metrics['cvar'], df_metrics['ret_vol'])):
        x_rounded = round(x * 100, 4)
        y_rounded = round(y, 3)
        label = f'({x_rounded}%, {y_rounded})'
        plt.text(x + 0.0002, y, label, ha='left', va='bottom')

    # Label/Alter the plot
    plt.xticks(rotation=-45)
    ax.xaxis.set_major_formatter(FuncFormatter(percent_formatter))
    plt.xlabel('CVaR')
    plt.ylabel('Sharpe')
    plt.title('MXWDIM w ' + strat)
    plt.tight_layout()
    plt.show()


# plot for sharpe, cvar, tracking error, correlation, information ratio against extended weights of strategy
def show_plots(df_metrics, strat=''):
    plot_list = ['Sharpe', 'CVaR', 'Tracking Error', 'Corr', 'IR']
    ol_weight_index_list = df_metrics.index.tolist()
    for graph in plot_list:
        if graph == 'IR':
            ol_weight_index_list_ir = ol_weight_index_list.copy()
            ol_weight_index_list_ir.pop(0)
            ol_weight_index_list_ir_float = [float(x) for x in ol_weight_index_list_ir]
            df_metrics_ir = df_metrics[graph].copy().tolist()
            df_metrics_ir.pop(0)
            plt.scatter(ol_weight_index_list_ir_float, df_metrics_ir, c='blue', marker='o', label='')

            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
        else:
            plt.scatter(ol_weight_index_list, df_metrics[graph], c='blue', marker='o', label='')

        if graph in ['Tracking Error', 'CVaR', 'Ret', 'Vol']:
            plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

        plt.xticks(rotation=-45)
        plt.xlabel('Extended ' + strat + ' Weights')
        plt.ylabel(graph)
        plt.title('MXWDIM w ' + strat + ': ' + graph)
        plt.tight_layout()
        plt.show()


# Transpose dataframes and Create an ExcelWriter object and specify the file name
def transpose_export_excel_file(strat_metrics, strat_type='', multiple=False):
    if multiple is True:
        for strat, df in strat_metrics.items():
            df = df.transpose()
            df.columns = [df.columns[0]] + [f'{float(col) * 100:.0f}%' for col in df.columns[1:]]
            strat_metrics[strat] = df
        with pd.ExcelWriter(CWD + '\\RStrats\\' + strat_type + 'MetricsAnalysis.xlsx', engine='xlsxwriter') as writer:
            for sheet_name, df in strat_metrics.items():
                df.to_excel(writer, sheet_name=sheet_name, index=True)
    else:
        strat_metrics = strat_metrics.transpose()
        file_path = CWD + '\\RStrats\\' + strat_type + 'Metrics.xlsx'
        # Export the DataFrame to an Excel file
        strat_metrics.to_excel(file_path, index=True)

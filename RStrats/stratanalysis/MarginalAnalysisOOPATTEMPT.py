# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 16:13:52 2024

@author: PCR7FJW
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import returns_stats as rs
from matplotlib.ticker import FuncFormatter
import os

class MarginalAnalysis:
    def __init__(self):
        self.CWD = os.getcwd()

    def percent_formatter(self, x, pos):
        return f'{x * 100:.2f}%'

    def get_weighted_index(self, df_index_prices, name='', notional_weights=[]):
        weight_ratio = [notional / sum(notional_weights) for notional in notional_weights]
        strat_list = df_index_prices.columns.tolist()
        weighted_index = pd.Series(100, index=df_index_prices.index)
        for i in range(len(strat_list)):
            strat = strat_list[i]
            strat_weight = weight_ratio[i]
            StratStartLevel = df_index_prices[strat][0]
            StratShare = (strat_weight * 100 / StratStartLevel) * (df_index_prices[strat] - StratStartLevel)
            weighted_index += StratShare
        weighted_index_df = weighted_index.to_frame(name=name)
        return weighted_index_df

    # TODO: Make some kind of filter to only have certain/additional metric (something like a checkbox of what metrics you'd like)
    def get_returns_analysis(self, bmk_index, strat_index, bmk='', strat='', weights=[]):
        df_index_prices = pd.merge(bmk_index, strat_index, left_index=True, right_index=True, how='inner')
        StratStartLevel = df_index_prices[strat][0]
        bmk_start_level = df_index_prices[bmk][0]
        df_weighted_prices = pd.DataFrame({bmk: df_index_prices[bmk], strat: df_index_prices[strat]})
        for i in weights:
            StratShare = i * 100.0 / StratStartLevel
            MXWDIMShare = 100.0 / bmk_start_level
            df_weighted_prices[str(i)] = 100.0 + StratShare * (df_index_prices[strat] - StratStartLevel) + MXWDIMShare * (df_index_prices[bmk] - bmk_start_level)

        returns_strat_only = dm.get_data_dict(df_weighted_prices)['Daily'].drop(columns=[strat])

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
            ret = rs.get_ann_return(returns_strat_only[col], freq='1D')
            vol = rs.get_ann_vol(returns_strat_only[col], freq='1D')
            sharpe = ret / vol
            bottom5pct = np.percentile(returns_strat_only[col].values[1:], q=5)
            cvar = returns_strat_only[col][returns_strat_only[col] < bottom5pct].mean()
            excess_return = (returns_strat_only[col] - returns_strat_only[bmk])
            track_error = np.std(excess_return) * np.sqrt(252)
            if track_error == 0:
                information_ratio = 0
            else:
                information_ratio = excess_return.mean() * 252 / track_error
            correlation = returns_strat_only[bmk].corr(returns_strat_only[col])
            max_dd = rs.get_max_dd(df_weighted_prices[col])

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
        df_metrics.set_index(returns_strat_only.columns, inplace=True)

        return df_metrics

    # TODO: Figure out a better way to graph the size of plots w Tracking Error
    # TODO: Make this function dynamic where so its not just Sharpe vs CVar, but could adjust for whatever metric to graph Y vs X
    def show_SharpeCVaR(self, df_metrics, BMK='', Strat='', weights=[]):
        fig, ax = plt.subplots(figsize=(25, 18))
        plt.scatter(df_metrics['CVaR'], df_metrics['Sharpe'], s=(df_metrics['Tracking Error']*10000)+100, c='blue', marker='o', label='')
        labels = [BMK + ' 0 weight'] + [f'{int(wei * 100)}%' for wei in weights]
        # Add labels to each data point
        for i, label in enumerate(labels):
            plt.annotate(label, (df_metrics['CVaR'][i], df_metrics['Sharpe'][i]), textcoords="offset points", xytext=(-5, 20), ha='center')
        # Round x and y axes
        for i, (x, y) in enumerate(zip(df_metrics['CVaR'], df_metrics['Sharpe'])):
            x_rounded = round(x, 4)
            y_rounded = round(y, 3)
            label = f'({x_rounded}%, {y_rounded})'
            plt.text(x + 0.00002, y, label, ha='left', va='bottom')
        # Customize the plot
        plt.xticks(rotation=-45)
        plt.gca().xaxis.set_major_formatter(FuncFormatter(self.percent_formatter))
        plt.xlabel('CVaR')
        plt.ylabel('Sharpe')
        plt.title('MXWDIM w ' + Strat)
        plt.show()

    def show_plots(self, df_metrics, Strat=''):
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

    def transpose_export_excel_file(self, strat_metrics, strat_type='', multiple=False):
        if multiple:
            for strat, df in strat_metrics.items():
                df = df.transpose()
                df.columns = [df.columns[0]] + [f'{float(col) * 100:.0f}%' for col in df.columns[1:]]
                strat_metrics[strat] = df
            with pd.ExcelWriter(self.CWD + '\\RStrats\\' + strat_type + 'MargAnalysis.xlsx', engine='xlsxwriter') as writer:
                for sheet_name, df in strat_metrics.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=True)
        else:
            strat_metrics = strat_metrics.transpose()
            file_path = self.CWD + '\\RStrats\\' + strat_type + 'Metrics.xlsx'
            strat_metrics.to_excel(file_path, index=True)


equity_analyzer = MarginalAnalysis()

#MXWDIM and Program DATA
bmk_index = pd.read_excel(equity_analyzer.CWD+'\\RStrats\\' + 'SPX&MXWDIM Historical Price.xlsx', sheet_name = 'MXWDIM', index_col=0)
df_index_prices = pd.read_excel(equity_analyzer.CWD+'\\RStrats\\' + 'weighted hedgesSam.xlsx', sheet_name = 'Program', index_col=0)
    
bmk = 'MXWDIM'
strat = 'EqHedge'
strat_index = equity_analyzer.get_weighted_index(df_index_prices, name = strat, notional_weights = [1,1.25,0.5,0.85,1,.25,1,1,1.05,0.5,1])
ol_weights = [.05,.1,.15,.2,.25,.3,.35,.4,.45,.5]

df_metrics = equity_analyzer.get_returns_analysis(bmk_index, strat_index, bmk, strat, ol_weights)
equity_analyzer.show_SharpeCVaR(df_metrics, bmk, strat, ol_weights)
equity_analyzer.show_plots(df_metrics, strat)
equity_analyzer.transpose_export_excel_file(df_metrics, strat, multiple=False)

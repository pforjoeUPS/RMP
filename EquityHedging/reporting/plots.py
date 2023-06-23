# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe
"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#from heatmap import corrplot
from ..analytics.corr_stats import get_corr_analysis
import pandas as pd


from EquityHedging.datamanager import data_manager as dm
from matplotlib.ticker import PercentFormatter
from EquityHedging.analytics import util


sns.set(color_codes=True, font_scale=1.2)

CMAP_DEFAULT = sns.diverging_palette(20, 220, as_cmap=True)

def draw_corrplot(corr_df,size_scale=1000):
    """
    """
    plt.figure(figsize=corr_df.shape)
    #corrplot(corr_df, size_scale)
    
def draw_heatmap(corr_df, half=True):
    """
    """
    sns.set(style="white")
    
    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr_df, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = half
    
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=corr_df.shape)
    #ax.set_xticklabels(corr_dict['corr'][0].columns, rotation = 45)
    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr_df
                ,mask=mask 
                ,cmap=CMAP_DEFAULT
                ,center=0
                ,square=True
                ,linewidths=1
                ,cbar_kws={"shrink": 1} 
                ,annot=True
                ,fmt=".2f"
                ,cbar=False
               )

def plot_heatmap(corr,filename,title='Correlation Analysis',cmap=CMAP_DEFAULT):
    """
    Return a half diagonal correlation matrix heat map

    Parameters:
    corr -- correlation matrix
    filename -- string
    title -- string
    cmap -- color map
    
    Returns:
    a half diagonal heatmap correlation matrix
    """
    sns.set(style="white")
    
    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=corr.shape)
    
    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap, center=0,square=True,
                linewidths=.5, cbar_kws={"shrink": .5}, annot=True)
    plt.title(title, fontsize=20)
    plt.tight_layout()
    plt.savefig(filename +'.png')
    return plt

def plot_corr(df_returns, notional_weights=[], include_fi=False):
    """"
    Plot crrelation matrices

    """
    
    corr_dict = get_corr_analysis(df_returns, notional_weights, include_fi)
    for key,value in corr_dict.items():
        plot_heatmap(value[0], key, value[1], cmap='coolwarm')
   
#TODO: rename variables in this method
def get_symbols(df_normal, unique= True):
    '''
    Obtains a list of symbols and index's the corresponding amount of strategies

    Parameters
    ----------
    df_normal : data frame
        data frame 
    weighted_hedge : boolean
        is weighted hedge included in your data

    Returns
    -------
    symbols : data frame
        data frame with strategy names assigned to a number that corresponds to a symbol

    '''
     #get length of columns
    n=len(df_normal.columns)
    
    #get column names of df_normal
    c=list(df_normal.columns)
    
    #creates a list of the corresponding number of the symbols we want
    a=list(range(1,33))
    b=list(range(46,52))
    
    #to get different symbol for each strategy
    if unique == True:
   
        for i in b: 
            a.append(i)
    
    
        if 'Weighted Hedges' in c:
            c.remove('Weighted Hedges')
            c.append('Weighted Hedges')
            df_normal = df_normal[c]
            c=list(df_normal.columns)
            symbol_list= a[0:n-1]
            #weighted hedge wil always be symbol 236
            symbol_list.append(224)
    
        else:
            symbol_list= a[0:n]
            
    else: 
        symbol_list = [201 for i in list(range(0,n))]
        
    #Creates a data frame that assigns each strategy with a symbol
    symbols=pd.DataFrame(columns=c,index=[0])
    
    symbols.iloc[0] = symbol_list
    
    return symbols



def get_colors(df_normal, grey=False):
    '''
    

    Parameters
    ----------
    df_normal : data frame
        Data Frame with Normalized Data
    grey : boolean
        True if you want strategies to only be grey. The default is False.

    Returns
    -------
    color_df : data fame
        

    '''
    #get column and row names
    col_names =list(df_normal.columns)
    row_names = list(df_normal.index)
    
    #get length of columns
    col_length = len(df_normal.columns)
    
    #get a list from 0 to the length of the columns
    col_length_list = list(range(0,col_length))
    
    #get a list from 0 to the length of the rows
    row_length_list = list(range(0,len(row_names)))
    
    #list of colors
    colors=["blue","pink","red","purple","green","yellow","orange","brown","teal","liver-colored",
            "grayish-blue", "rust", "light blue", "lime"]
    
    if grey == False:
        
        #if weighted hedges are calculated in df_normal
        if 'Weighted Hedges' in col_names:
            #place the weighted hedges column to the end of the data frame
            col_names.remove('Weighted Hedges')
            col_names.append('Weighted Hedges')
            df_normal = df_normal[col_names]
            
            #get new column names
            col_names=list(df_normal.columns)
            
            #get list of colors for strategies minus weighted hedge
            color_list= colors[0:col_length-1]
            
            #weighted hedge wil always be color "wheat"
            color_list.append("wheat")
    
        else:
            #get list of colors for strategies
            color_list= colors[0:col_length]
            
    else:
        #assign all strategies ro be color grey 
        color_list=["grey" for i in col_length_list]
    
    #create an empty data frame
    color_df = pd.DataFrame(columns=col_names,index=row_names)
    
    #assign color list to the empty data frame
    for i in row_length_list:
        color_df.iloc[i] = color_list
   
    return color_df


def get_regression_plot(frequency, strategy_y, strategy_x = 'SPTR'):
    returns = dm.get_equity_hedge_returns(strategy_x)
    comparison_strategy = strategy_y
    strategy_x_returns = returns[frequency][strategy_x]
    comparison_returns = returns[frequency][comparison_strategy]
    data = pd.concat([strategy_x_returns, comparison_returns], axis=1)
    data.columns = [strategy_x, comparison_strategy]
     #splits the data accordingly
     # add percentile notes
    #data_sptr_pos = data[data[strategy_x] >= 0]
    #data_sptr_neg = data[data[strategy_x] < 0]
    if(strategy_x == 'VIX' or strategy_x == 'UX3'):
        data_sptr_low = data[data[strategy_x] >= np.quantile(data[strategy_x],.025)]
        data_sptr_high = data[data[strategy_x] < np.quantile(data[strategy_x],.025)]
    else:
        data_sptr_low = data[data[strategy_x] < np.quantile(data[strategy_x],.025)]
        data_sptr_high = data[data[strategy_x] >= np.quantile(data[strategy_x],.025)]
    
    x_pos = data_sptr_high[strategy_x].values.reshape(-1, 1)
    y_pos = data_sptr_high[comparison_strategy].values
    x_neg = data_sptr_low[strategy_x].values.reshape(-1, 1)
    y_neg = data_sptr_low[comparison_strategy].values
    x_all = data[strategy_x].values.reshape(-1, 1)
    y_all = data[comparison_strategy].values
    
    positive_data = util.reg(x_pos,y_pos)
    negative_data = util.reg(x_neg, y_neg)
    all_data = util.reg(x_all,y_all)
    
    print(f"Regression equation (All Data): {comparison_strategy} = {all_data[3]:.4f} * {strategy_x} + {all_data[2]:.4f}")
    print(f"Regression equation (SPTR Highest 97.5%): {comparison_strategy} = {positive_data[3]:.4f} * {strategy_x} + {positive_data[2]:.4f}")
    print(f"Regression equation (SPTR Lowest 2.5%): {comparison_strategy} = {negative_data[3]:.4f} * {strategy_x} + {negative_data[2]:.4f}")
    
    print(f"Beta (All Data): {all_data[4]:.4f}")
    print(f"Beta (SPTR Highest 97.5%): {positive_data[4]:.4f}")
    print(f"Beta (SPTR Lowest 2.5%): {negative_data[4]:.4f}")

    #creates graph of points, line of best fit, etc.
    plt.scatter(x_pos, y_pos, color='g', label='Data Points (SPTR >= 0)')
    plt.scatter(x_neg, y_neg, color='b', label='Data Points (SPTR < 0)')
    plt.plot(positive_data[0], positive_data[1], color='r', label='Regression Line (SPTR >= 0)')
    plt.plot(negative_data[0], negative_data[1], color='orange', label='Regression Line (SPTR < 0)')
    plt.xlabel(strategy_x)
    plt.ylabel(comparison_strategy)
    plt.title(f'Regression Analysis: {strategy_x} vs {comparison_strategy} ({frequency} Returns)')
    #change axis labels into percentages
    plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=1))
    plt.gca().xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=1))
    plt.plot


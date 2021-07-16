# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe
"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from heatmap import corrplot
from ..analytics.corr_stats import get_corr_analysis
import pandas as pd


sns.set(color_codes=True, font_scale=1.2)

CMAP_DEFAULT = sns.diverging_palette(20, 220, as_cmap=True)

def draw_corrplot(corr_df,size_scale=1000):
    """
    """
    plt.figure(figsize=corr_df.shape)
    corrplot(corr_df, size_scale)
    
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

#plot
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

#plot
def plot_corr(df_returns, notional_weights=[], include_fi=False):
    """"
    Plot crrelation matrices

    """
    
    corr_dict = get_corr_analysis(df_returns, notional_weights, include_fi)
    for key,value in corr_dict.items():
        plot_heatmap(value[0], key, value[1], cmap='coolwarm')
   

def get_symbols(df_normal, weighted_hedge = True):
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
    a=list(range(0,33))
    b=list(range(46,52))
    for i in b: 
        a.append(i)
        
    if weighted_hedge == True:
        symbol_list= a[0:n-1]
        #weighted hedge wil always be symbol 236
        symbol_list.append(224)
    else:
        symbol_list= a[0:n]

    #Creates a data frame that assigns each strategy with a symbol
    symbols=pd.DataFrame(columns=c,index=[0])
    
    symbols.iloc[0] = symbol_list
    
    return symbols

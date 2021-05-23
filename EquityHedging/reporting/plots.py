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
   

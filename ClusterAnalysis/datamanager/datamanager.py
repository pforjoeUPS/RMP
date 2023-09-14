# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 17:34:11 2023

@author: RRQ1FYQ
"""

import pandas as pd
import numpy as np
import os

from EquityHedging.analytics import summary 
from EquityHedging.analytics import  util
from EquityHedging.datamanager import data_manager as dm
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster 

CWD = os.getcwd()
NORMALIZED_HM_FP = CWD + "\\ClusterAnalysis\\data\\Normalized_Hedge_Metrics.xlsx"
QIS_UNIVERSE_FP = CWD + '\\ClusterAnalysis\\data\\QIS Universe Returns.xlsx'

def get_qis_uni_dict():
    qis_uni = {}
    #Get Sheet Name
    sheet_names = util.get_sheetnames_xlsx(QIS_UNIVERSE_FP)
    for sheet in sheet_names:
        qis_uni[sheet] = pd.read_excel(QIS_UNIVERSE_FP, sheet_name = sheet, index_col=0,header = 0)
        #qis_uni[sheet] = format_data(index_price, freq = '1D')
    return qis_uni


def get_normalized_hm():
    normalized_hm = pd.read_excel(NORMALIZED_HM_FP, sheet_name = "Hedge_Metrics", index_col = 0)
    
    normalized_hm_df = normalized_hm[['Downside Reliability', 'Convexity', 'Cost', 'Decay']]
    
    
    return normalized_hm_df

def hierarchical_clustering_analysis(normalized_hm_df, n_clusters):
    
    # Calculate the pairwise distances between strategies
    distances = pdist(normalized_hm_df, metric = "euclidean")
    
    
    # Perform hierarchical clustering using linkage on the square distance matrix
    linked = linkage(distances, 'ward')
    num_clusters = 3
    
    clusters = fcluster(linked, t=num_clusters, criterion='maxclust')
    
    normalized_hm_df['Cluster'] = clusters
    
    return normalized_hm_df
    
def best_in_cluster(normalized_hm_df, n_clusters):
    best_in_cluster_strats = []
    #loop through each cluster and find top 2 strategies with the largest total score
    for i in list(range(1,n_clusters+1)):
         cluster_df = normalized_hm_df[normalized_hm_df["Cluster"]==i]
         top2 = cluster_df.nlargest(2,"Total")
         top2.reset_index(inplace = True)
         #add strat names to list
         best_in_cluster_strats = best_in_cluster_strats + (top2["index"].tolist())
    return best_in_cluster_strats

def best_in_metric(normalized_hm_df, decay_factor = "Total"):
    best_in_metric_strats= []
   #loop through each metric and find top 2 strategies with the largest score for that metric
    for i in list(normalized_hm_df.columns.drop(["Total","Cluster"])):
        if i == "Decay":
            #gets all strategies that rank highes in decay (i.e. 1) 
            decay = normalized_hm_df[normalized_hm_df["Decay"] ==1]
            #then select top 2 strats based on total score
            top2 = decay.nlargest(2,decay_factor)
        else:
             top2 = normalized_hm_df.nlargest(2,i)
        #add strat names to list
        top2.reset_index(inplace = True)
        best_in_metric_strats = best_in_metric_strats + (top2["index"].tolist())
    
    return best_in_metric_strats

def best_in_universe(normalized_hm_df, top_n_strats = 8):
    #find top n strats with largest total score within the QIS universe
    top_performing = normalized_hm_df.nlargest(top_n_strats,"Total")
    top_performing.reset_index(inplace = True)
    best_in_universe_strats = top_performing["index"].tolist()
    return  best_in_universe_strats


def get_best_returns_data(qis_uni_dict, best_list):
    returns_data = pd.DataFrame()
    #loop through each strategy in the list
    
    for i in best_list:
        #loop through each bank data in qis_uni_dict
        for key in qis_uni_dict:
            try:
                returns_data[i] = qis_uni_dict[key][i]
                #if error (i.e. strat not in the bank df move to next loop)
            except:
                pass
    return returns_data

def find_best_sharpe(results_df,weights_df):
    
   
    max_sharpe_idx = np.argmax(results_df.loc['Sharpe'])
    
    #create empty data frame with strategies as the row names
    weights_max_sharpe = pd.DataFrame(index = list(weights_df.index))
    results_max_sharpe = pd.DataFrame()
    
    #find weights tha match the max sharpe index
    weights_max_sharpe['Weights'] = weights_df[max_sharpe_idx]
    
    #find return stats that match the max sharpe index
    results_max_sharpe['Weighted_Portfolio'] = results_df[max_sharpe_idx]
    
    best_dict = {"Return Stats":results_max_sharpe, "Weights": weights_max_sharpe, }

    return best_dict


def get_efficient_frontier(best_strats_ret_df):

    num_assets = best_strats_ret_df.shape[1]
    num_portfolios = 10000
    
    #get mean returns and covariance matrix
    mean_returns = np.mean(best_strats_ret_df)
    mean_returns = np.array(mean_returns)
    cov_matrix = np.cov(best_strats_ret_df.transpose())
    
    # Initialize arrays to store portfolio results
    results_df = pd.DataFrame()
    weights_df = pd.DataFrame()
    for i in range(num_portfolios):
        # Generate random weights for each asset
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        
        # Calculate portfolio expected return and standard deviation
        portfolio_return = np.sum(weights * mean_returns)
        portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        results_df[i]= [portfolio_return,portfolio_stddev,(portfolio_return / portfolio_stddev)] # Return
        
        weights_df[i] =  weights  # Store weights
    
    

    results_df.index = ['Returns','StDev','Sharpe']
    
    
    weights_df.index = list(best_strats_ret_df.columns)
    
    top_sharpe_idx = np.argmax(results_df.loc['Sharpe'])
    
    efficient_frontier = {"Return Stats": results_df, "Weights": weights_df, 
                          "Weighted Portfolio Ret Stats": results_df[top_sharpe_idx],
                          "Weights for Portfolio": weights_df[top_sharpe_idx]}

    return efficient_frontier

def get_notional_weights(weights, total_notional, equity_notional):
    notional_weights = [equity_notional] +[i * total_notional for i in weights]
    return notional_weights





















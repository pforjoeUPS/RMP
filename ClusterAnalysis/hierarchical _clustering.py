# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 22:23:07 2023

@author: RRQ1FYQ
"""

from EquityHedging.datamanager import data_manager as dm
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as shc
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster 
from scipy.spatial.distance import pdist, squareform
from Cluster Analysis.datamanager import datamanager as dm
import matplotlib.pyplot as plt
import os


CWD = os.getcwd()

file_path = CWD + "\\Cluster Analysis\\data\\"

normalized_hm = pd.read_excel(dm.QIS_UNIVERSE +'Normalized_Hedge_Metrics.xlsx', sheet_name = "Hedge Metrics", index_col=(0))
features = ['Downside Reliability', 'Convexity', 'Cost', 'Decay']
normalized_hm = normalized_hm[features]
# Calculate the sum of features for each strategy (row-wise sum)
normalized_hm['Total'] = normalized_hm.sum(axis=1)




pca = PCA(n_components = 2)
X_principal = pca.fit_transform(normalized_hm[features])
X_principal = pd.DataFrame(X_principal, index = normalized_hm.index)
X_principal.columns = ['P1', 'P2']
inertia = []
K = range(1,6)
for k in K:
    kmeanModel = KMeans(n_clusters=k).fit(normalized_hm)
    kmeanModel.fit(normalized_hm)
    inertia.append(kmeanModel.inertia_)
    
    # Plot the elbow
plt.plot(K, inertia, 'bx-')
plt.xlabel('k')
plt.ylabel('Inertia')
plt.show()



#top 2 in cluster
# Call the function to get the two best-performing strategies in each cluster
best_in_cluster = get_two_best_performing_strategies_per_cluster(normalized_hm,3)

def get_two_best_performing_strategies_per_metric(df):
    best_in_metric = []
    col_list = ["Cost","Decay","Convexity","Downside Reliability"]
    
    for i in col_list:
        if i == "Decay":
            decay = df[df["Decay"] ==1]
            top2 = decay.nlargest(2,"Total")
        else:
             top2 = df.nlargest(2,i)
        top2.reset_index(inplace = True)
        best_in_metric = best_in_metric + (top2["index"].tolist())
    return best_in_metric

best_in_metric = get_two_best_performing_strategies_per_metric(normalized_hm)

def get_best_in_universe(df, n):
    top_performing = df.nlargest(n,"Total")
    top_performing.reset_index(inplace = True)
    best_in_universe = top_performing["index"].tolist()
    return  best_in_universe

best_in_universe = get_best_in_universe(normalized_hm, 6)


qis_uni = dm.get_qis_uni_dict()

def get_best_returns_data(qis_uni, best_list):
    returns_data = pd.DataFrame()
    for i in best_list:
        for key in qis_uni:
            try:
                returns_data[i] = qis_uni[key][i]
            except:
                pass
    return returns_data


best_cluster_data = get_best_returns_data(qis_uni, best_in_cluster)

import numpy as np
import matplotlib.pyplot as plt

# Example data: asset returns and covariances


# Generate random returns for each asset

def get_efficient_frontier(best_data):

    num_assets = best_data.shape[1]
    num_portfolios = 10000
    
    # Generate random returns for each asset
    
    mean_returns = np.mean(best_data)
    mean_returns = np.array(mean_returns)
    cov_matrix = np.cov(best_data.transpose())
    
    # Initialize arrays to store portfolio results
    results = np.zeros((3, num_portfolios))
    weights_df=pd.DataFrame()
    for i in range(num_portfolios):
        # Generate random weights for each asset
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        
        # Calculate portfolio expected return and standard deviation
        portfolio_return = np.sum(weights * mean_returns)
        portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        results[0, i] = portfolio_return  # Return
        results[1, i] = portfolio_stddev  # Standard Deviation
        results[2, i] = portfolio_return / portfolio_stddev  # Sharpe Ratio
        weights_df[i] =  weights  # Store weights
    
   
    results_df.columns = ['Returns','stdev','Sharpe']
    
    
    weights_df.set_index(pd.Index(best_data.columns), inplace = True)
    
    efficient_frontier = {}
    efficient_frontier['Results'] = results_df
    efficient_frontier['Weights'] = weights_df
    
    return efficient_frontier

z = get_efficient_frontier(best_cluster_data)
    
def find_best_sharpe(efficient_frontier):
    results = efficient_frontier["Results"]
    weights_df = efficient_frontier["Weights"]
    # Find the index of the portfolio with the highest Sharpe ratio
    max_sharpe_idx = np.argmax(results['Sharpe'])
    weights_max_sharpe = pd.DataFrame(index = list(weights_df.index))
        
    weights_max_sharpe['Weights'] = weights_df[max_sharpe_idx]
    results_max_sharpe = results.iloc[max_sharpe_idx]
    
    best_dict = {"Weights": weights_max_sharpe, "Results":results_max_sharpe}

    return best_dict

y = find_best_sharpe(z)

# Plot the efficient frontier
plt.scatter(stddevs, returns, c=sharpe_ratios, marker='o')
plt.scatter(optimal_stddev, optimal_return, marker='x', color='r', label='Optimal Portfolio')
plt.title('Efficient Frontier')
plt.xlabel('Standard Deviation')
plt.ylabel('Expected Return')
plt.colorbar(label='Sharpe Ratio')
plt.legend()
plt.show()

print("Optimal Portfolio:")
print("Expected Return:", optimal_return)
print("Standard Deviation:", optimal_stddev)
print("Asset Weights:", optimal_weights)




















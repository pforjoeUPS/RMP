# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 22:23:07 2023

@author: RRQ1FYQ
"""

from EquityHedging.datamanager import data_manager as dm
from ClusterAnalysis.datamanager import datamanager as cdm
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as shc
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster 
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import os


normalized_hm = cdm.get_normalized_hm()
qis_uni = cdm.get_qis_uni_dict()


pca = PCA(n_components = 2)
X_principal = pca.fit_transform(normalized_hm[['Downside Reliability', 'Convexity','Cost','Decay']])
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

n_cluster = 3
cluster_analysis = cdm.hierarchical_clustering_analysis(normalized_hm, n_cluster)

#top 2 in cluster
# Call the function to get the two best-performing strategies in each cluster
best_in_cluster = cdm.best_in_cluster(cluster_analysis, n_cluster)
best_in_metric = cdm.best_in_metric(cluster_analysis)
best_in_uni =  cdm.best_in_universe(cluster_analysis)

best_in_cluster_ret = cdm.get_best_returns_data(qis_uni, best_in_cluster)
best_in_metric_ret = cdm.get_best_returns_data(qis_uni, best_in_metric)
best_in_universe_ret = cdm.get_best_returns_data(qis_uni, best_in_uni)


best_in_cluster_ef = cdm.get_efficient_frontier(best_in_cluster_ret)
weights = cdm.find_best_sharpe(best_in_cluster_ef)

stddevs = best_in_cluster_ef['Return Stats'].loc['StDev']
returns = best_in_cluster_ef['Return Stats'].loc['Returns']
sharpe_ratios = best_in_cluster_ef['Return Stats'].loc['Sharpe']

optimal_stddev = weights['Return Stats'].loc['StDev']
optimal_return = weights['Return Stats'].loc['Returns']
# Plot the efficient frontier
plt.scatter(stddevs, returns, c=sharpe_ratios, marker='o')
plt.scatter(optimal_stddev, optimal_return, marker='x', color='r', label='Optimal Portfolio')
plt.title('Efficient Frontier')
plt.xlabel('Standard Deviation')
plt.ylabel('Expected Return')
plt.colorbar(label='Sharpe Ratio')
plt.legend()
plt.show()



























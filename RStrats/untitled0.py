# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:21:50 2024

@author: PCR7FJW
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from scipy.optimize import minimize
from EquityHedging.datamanager import data_manager as dm
import os
CWD = os.getcwd()

MXWDIM_index = pd.read_excel(CWD+'\\RStrats\\' + 'SPX&MXWDIM Historical Price.xlsx', sheet_name = 'SPX', index_col=0)

returns = MXWDIM_index.pct_change().dropna().values.reshape(-1,1)

# Choose the number of Gaussian components (clusters) for the GMM
num_components = 2

# Fit the Gaussian Mixture Model
gmm = GaussianMixture(n_components=num_components, random_state=0)
gmm.fit(returns)

# Predict the component (cluster) assignments for each data point
cluster_assignments = gmm.predict(returns)

# Get the parameters of the fitted GMM (e.g., means, covariances, weights)
means = gmm.means_
covariances = gmm.covariances_
weights = gmm.weights_

# Print the results
for i in range(num_components):
    print(f"Component {i + 1}:")
    print(f"Mean: {means[i][0]}")
    print(f"Covariance Matrix: \n{covariances[i][0]}")
    print(f"Weight: {weights[i]}\n")

#Histogram of Component Weights
plt.hist(cluster_assignments, bins=num_components, edgecolor='k', alpha=0.7)
plt.xlabel('Component')
plt.ylabel('Count')
plt.title('Histogram of Component Assignments')
plt.xticks(range(num_components))
plt.show()

#Density  PLot
x = np.linspace(returns.min(), returns.max(), 1000)
for i in range(num_components):
    pdf_values = np.exp(gmm.score_samples(x.reshape(-1, 1)) * weights[i])
    plt.plot(x, pdf_values, label=f'Component {i + 1}')

plt.xlabel('Returns')
plt.ylabel('Probability Density')
plt.title('Probability Density Functions of Components')
plt.legend()
plt.show()


component_returns = [returns[cluster_assignments == i] for i in range(num_components)]

plt.figure(figsize=(12, 6))
for i in range(num_components):
    plt.plot(np.arange(1, len(component_returns[i]) + 1), component_returns[i], label=f'Component {i + 1}')

plt.xlabel('Data Point')
plt.ylabel('Returns')
plt.title('Component-Specific Returns Over Time')
plt.legend()
plt.show()


# Visualize the clusters if you have 2D data (e.g., time series)
if returns.shape[1] == 2:
    plt.scatter(returns[:, 0], returns[:, 1], c=cluster_assignments, cmap='viridis')
    plt.xlabel('Return 1')
    plt.ylabel('Return 2')
    plt.title('GMM Clustering of Returns')
    plt.show()
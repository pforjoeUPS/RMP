# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 11:12:23 2024

@author: PCR7FJW
"""
import pandas as pd
import numpy as np

test = pd.DataFrame(data = {'Vol': [0.0833,0.1010,0.2006],'Weight': [.4,.35,.25]}, index=['S','B','C'])


def calculate_covariance_matrix(correlation_matrix, volatility):
    return np.outer(volatility, volatility) * correlation_matrix


correlation_matrix = np.corrcoef(resampled_returns, rowvar=False)
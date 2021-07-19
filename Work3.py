# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 15:05:18 2021

@author: gcz5chn
"""
import numpy as np
import pandas as pd
housing = pd.read_csv("/context/sample_data/california_housing_train.csv")

from sklearn import preprocessing
x_array = np.array(housing['total_bedrooms'])
normalized_arr = preprocessing.normalize([x_array])
print(normalized_arr)
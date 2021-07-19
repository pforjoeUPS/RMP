# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 15:01:52 2021

@author: gcz5chn
"""

from sklearn import preprocessing

import numpy as np
x_array = np.array([2,3,5,6,7,4,8,7,6])

normalized_arr = preprocessing.normalize([x_array])
print(normalized_arr)
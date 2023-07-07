# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 22:35:26 2021

@author: Maddie Choi
"""
import os
os.chdir("..\..")
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp

returns_dict = dm.update_returns_data()

#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)

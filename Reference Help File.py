# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 15:17:41 2023

@author: pcr7fjw
"""

from EquityHedging.datamanager import data_manager as dm

from EquityHedging.datamanager import data_importer as di

from EquityHedging.datamanager import data_xformer_new as dxf

from EquityHedging.datamanager import data_handler as dh

y = dxf.putSpreadDataXformer(filepath = dm.UPDATE_DATA+'put_spread_data.xlsx').data_import

x = dxf.putSpreadDataXformer(filepath = dm.UPDATE_DATA+'put_spread_data.xlsx').data_xform
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 03:43:47 2023

@author: NVG9HXP
"""
from EquityHedging.datamanager import data_transformer as dt
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.datamanager import data_updater as du
from EquityHedging.reporting.excel import reports as rp

sma_data = dt.transform_innocap_data(du.UPDATE_DATA_FP+'1907_hf_data.xlsx')
arpem_data = dt.transform_innocap_data(du.UPDATE_DATA_FP+'1907_arp_em_data.xlsx')
arptf_data = dt.transform_innocap_data(du.UPDATE_DATA_FP+'1907_arp_tf_data.xlsx')
iiicv_data = dt.transform_innocap_data(du.UPDATE_DATA_FP+'1907_iii_cv_data.xlsx')
kepos_data = dt.transform_innocap_data(du.UPDATE_DATA_FP+'1907_kepos_data.xlsx')
sma_dict = dm.merge_dicts(sma_data, arptf_data)
sma_dict = dm.merge_dicts(sma_dict, arpem_data)
sma_dict = dm.merge_dicts(sma_dict, iiicv_data)
sma_dict = dm.merge_dicts(sma_dict, kepos_data)
sma_dict['returns'].columns = ['1907 Campbell TF', '1907 III Class A',
       '1907 Penso Class A', '1907 Systematica TF',
       'UPS 1907 ARP TF',
       '1907 ARP EM', '1907 III CV',
       '1907 Kepos RP']
sma_dict['mv'].columns = ['1907 Campbell TF', '1907 III Class A',
       '1907 Penso Class A', '1907 Systematica TF',
       'UPS 1907 ARP TF',
       '1907 ARP EM', '1907 III CV',
       '1907 Kepos RP']
rp.get_ret_mv_report('innocap_liq_alts_data',sma_dict, data_file=True)
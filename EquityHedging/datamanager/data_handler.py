# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 22:18:15 2022

@author: NVG9HXP
"""

import os
from .import data_manager as dm
import pandas as pd

CWD = os.getcwd()
RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\'
BMK_DATA_FP = RETURNS_DATA_FP+'bmk_returns.xlsx'
LIQ_ALTS_BMK_DATA_FP = RETURNS_DATA_FP+'liq_alts_bmks.xlsx'
LIQ_ALTS_PORT_DATA_FP = RETURNS_DATA_FP+'liq_alts_data.xlsx'
LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A','Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital'],
                     'Trend Following': ['1907 ARP TF','1907 Campbell TF', '1907 Systematica TF',
                                         'One River Trend'],
                     'Absolute Return':['1907 ARP EM',  '1907 III CV', '1907 III Class A',
                                        'ABC Reversion','Acadian Commodity AR',
                                        'Blueshift', 'Duality', 'Elliott']
                     }
EQ_HEDGE_DATA_FP = RETURNS_DATA_FP+'eq_hedge_returns.xlsx'
EQ_HEDGE_STRAT_DICT = {'99%/90% Put Spread':0.0, 'Down Var':1.0, 'Vortex':0.0, 'VOLA':1.25,'Dynamic Put Spread':1.0,
                       'VRR':1.0, 'GW Dispersion':1.0, 'Corr Hedge':0.25,'Def Var':1.0}
FREQ_LIST = ['1D', '1W', '1M', '1Q', '1Y']


def read_ret_data(fp, sheet_name):
    ret_data = pd.read_excel(fp, sheet_name, index_col=0)
    return dm.get_real_cols(ret_data)

class bmkHandler():
    def __init__(self, equity_bmk = 'M1WD',include_fi = True, all_data=False):
        self.equity_bmk = equity_bmk
        self.include_fi = include_fi
        self.all_data = all_data
        self.bmk_returns = self.get_bmk_returns()
        
    def get_bmk_returns(self):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            temp_ret = read_ret_data(BMK_DATA_FP, freq_string)
            if self.all_data:
                returns_dict[freq_string] = temp_ret.copy()
            else:    
                if freq != '1D':
                    if self.include_fi:
                        temp_ret['FI Benchmark'] = (temp_ret['Long Corp'] + temp_ret['STRIPS'])/2
                        returns_dict[freq_string] = temp_ret[[self.equity_bmk, 'FI Benchmark']]
                    else:
                        returns_dict[freq_string] = temp_ret[[self.equity_bmk]]
                else:
                    returns_dict[freq_string] = temp_ret[[self.equity_bmk]]
                returns_dict[freq_string].index.names = ['Date']
        
        return returns_dict
        
class liqAltsBmkHandler(bmkHandler):
    def __init__(self, equity_bmk = 'M1WD',include_fi = True, all_data=False):
        bmkHandler.__init__(self, equity_bmk, include_fi)
        self.equity_bmk = equity_bmk
        self.include_fi = include_fi
        self.all_data = all_data
        self.returns = self.get_returns()
        
    def get_returns(self):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            temp_ret = read_ret_data(LIQ_ALTS_BMK_DATA_FP, freq_string)
            if not self.all_data:
                temp_ret['Liquid Alts Bmk'] = 0.5*temp_ret['HFRX Macro/CTA'] + 0.3*temp_ret['HFRX Absolute Return'] + 0.2*temp_ret['SG Trend']
            returns_dict[freq_string] = temp_ret.copy()
        return returns_dict

class liqAltsPortHandler(bmkHandler):
    def __init__(self, equity_bmk = 'M1WD',include_fi = True):
        bmkHandler.__init__(self, equity_bmk, include_fi)
        self.equity_bmk = equity_bmk
        self.include_fi = include_fi
        self.sub_ports = self.get_sub_port_data()
        self.returns = self.get_full_port_data()
        self.mvs = self.get_full_port_data(False)
        
    def get_sub_port_data(self):
        liq_alts_ret = read_ret_data(LIQ_ALTS_PORT_DATA_FP, 'returns')
        liq_alts_mv = read_ret_data(LIQ_ALTS_PORT_DATA_FP, 'market_values')
        liq_alts_dict = {}
        total_ret = pd.DataFrame(index = liq_alts_ret.index)
        total_mv = pd.DataFrame(index = liq_alts_mv.index)
        for key in LIQ_ALTS_MGR_DICT:
            temp_dict = {}
            temp_ret = liq_alts_ret[LIQ_ALTS_MGR_DICT[key]].copy()
            temp_mv = liq_alts_mv[LIQ_ALTS_MGR_DICT[key]].copy()
            temp_dict = dm.get_agg_data(temp_ret, temp_mv, key)
            if key == 'Trend Following':
                tf_list = self.get_sub_mgrs(key)
                temp_dict = {'returns': liq_alts_ret[tf_list], 
                                  'mv':liq_alts_mv[tf_list]}
            total_ret = dm.merge_data_frames(total_ret, temp_ret[[key]], False)
            total_mv = dm.merge_data_frames(total_mv, temp_mv[[key]], False)
            liq_alts_dict[key] = temp_dict
        liq_alts_dict['Total Liquid Alts'] = self.get_total(total_ret, total_mv)
        return liq_alts_dict
    
    def get_total(self, total_ret, total_mv):
        total_dict = dm.get_agg_data(total_ret, total_mv, 'Total Liquid Alts')
        return {'returns': total_dict['returns'][['Total Liquid Alts']],
                'mv':total_dict['mv'][['Total Liquid Alts']]}
    
    def get_full_port_data(self, return_data = True):
        data = 'returns' if return_data else 'mv'
        liq_alts_port = pd.DataFrame()
        for key in LIQ_ALTS_MGR_DICT:
            liq_alts_port = dm.merge_data_frames(liq_alts_port, self.sub_ports[key][data], False)
            
        liq_alts_port = dm.merge_data_frames(liq_alts_port, self.sub_ports['Total Liquid Alts'][data], False)
        return liq_alts_port
    
    def get_sub_mgrs(self,sub_port = 'Global Macro'):
        mgr_list = []
        mgr_list = mgr_list + LIQ_ALTS_MGR_DICT[sub_port]
        mgr_list.append(sub_port)
        return mgr_list

#TODO: add weighted strats logic
class eqHedgeHandler(bmkHandler):
    def __init__(self, equity_bmk = 'M1WD',include_fi = True, all_data=False, strat_drop_list=[]):
        bmkHandler.__init__(self, equity_bmk, include_fi)
        self.equity_bmk = equity_bmk
        self.include_fi = include_fi
        self.all_data = all_data
        self.strat_drop_list = strat_drop_list
        self.returns = dm.merge_dicts(self.bmk_returns, self.get_returns())
        
    def get_returns(self):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            temp_ret = read_ret_data(EQ_HEDGE_DATA_FP, freq_string)
            if not self.all_data:
                temp_ret['VOLA'] = temp_ret['Dynamic VOLA']
                temp_ret['Def Var']=temp_ret['Def Var (Fri)']*.4 + temp_ret['Def Var (Mon)']*.3+temp_ret['Def Var (Wed)']*.3
                temp_ret = temp_ret[list(EQ_HEDGE_STRAT_DICT.keys())]
            if self.strat_drop_list:
                temp_ret.drop(self.strat_drop_list, axis=1, inplace=True)
            returns_dict[freq_string] = temp_ret.copy()
        return returns_dict
        

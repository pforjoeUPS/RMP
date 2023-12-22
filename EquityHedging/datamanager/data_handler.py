# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 22:18:15 2022

@author: NVG9HXP
"""

import os
from .import data_manager as dm
import pandas as pd

CWD = os.getcwd()
RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\returns_data\\'
BMK_DATA_FP = RETURNS_DATA_FP+'bmk_returns_1.xlsx'
HF_BMK_DATA_FP = RETURNS_DATA_FP+'hf_bmks.xlsx'
LIQ_ALTS_BMK_DATA_FP = RETURNS_DATA_FP+'liq_alts_bmks.xlsx'
LIQ_ALTS_PORT_DATA_FP = RETURNS_DATA_FP+'nexen_liq_alts_data.xlsx'
LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A','Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital', 'JSC Vantage', 'Capula TM Fund', 'KAF'],
                     'Trend Following': ['1907 Campbell TF', '1907 Systematica TF',
                                         'One River Trend'],
                     'Absolute Return':['1907 ARP EM',  '1907 III CV', '1907 III Class A','1907 Kepos RP',
                                        'Blueshift','Acadian Commodity AR','Duality', 'Elliott']
                     }
EQ_HEDGE_DATA_FP = RETURNS_DATA_FP+'eq_hedge_returns.xlsx'
EQ_HEDGE_STRAT_DICT = {'99%/90% Put Spread':0.0, 'Down Var':1.0, 'Vortex':0.0, 'VOLA':1.25,'Dynamic Put Spread':1.0,
                       'VRR':1.0, 'GW Dispersion':1.0, 'Corr Hedge':0.25,'Def Var':1.0}
FREQ_LIST = ['1D', '1W', '1M', '1Q', '1Y']


def read_ret_data(fp, sheet_name):
    ret_data = pd.read_excel(fp, sheet_name, index_col=0)
    return dm.get_real_cols(ret_data)

class mktHandler():
    def __init__(self, eq_bmk = 'MSCI ACWI',include_fi = True, fi_bmk = 'FI Benchmark',
                 include_cm = False, cm_bmk = 'Commodities (BCOM)', include_fx=False,
                 fx_bmk = 'U.S. Dollar Index', all_data=False):
        self.eq_bmk = eq_bmk
        self.include_fi = include_fi
        self.fi_bmk = fi_bmk if self.include_fi else None
        self.include_cm = include_cm
        self.cm_bmk = cm_bmk if self.include_cm else None
        self.include_fx = include_fx
        self.fx_bmk = fx_bmk if self.include_fx else None
        self.all_data = all_data
        self.mkt_key = self.get_mkt_key()
        self.mkt_returns = self.get_mkt_returns_new()
        
    
    def get_mkt_key(self):
        if self.all_data:
            return {}
        else:
            return {'Equity': self.eq_bmk, 'Fixed Income': self.fi_bmk,
                    'Commodities': self.cm_bmk, 'FX': self.fx_bmk}
            
    def get_mkt_returns_new(self):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            temp_ret = read_ret_data(BMK_DATA_FP, freq_string)
            if self.all_data:
                returns_dict[freq_string] = temp_ret.copy()
            else:    
                returns_dict[freq_string] = pd.DataFrame(index=temp_ret.index)
                for key in self.mkt_key:
                    try:
                        if freq != '1D' and self.fi_bmk=='FI Benchmark':
                            temp_ret[self.fi_bmk] = temp_ret['Long Corp']*0.6 + temp_ret['STRIPS']*0.4
                        returns_dict[freq_string] = dm.merge_data_frames(returns_dict[freq_string], temp_ret[[self.mkt_key[key]]])
                    except KeyError:
                        pass
                returns_dict[freq_string].index.names = ['Date']
        
        return returns_dict
    
    
        
        
class liqAltsBmkHandler(mktHandler):
    def __init__(self, equity_bmk = 'M1WD',include_fi = True, all_data=False):
        super().__init__(self, equity_bmk, include_fi)
        self.equity_bmk = equity_bmk
        self.include_fi = include_fi
        self.all_data = all_data
        self.hf_returns = self.get_returns(False)
        self.bmk_returns = self.get_returns()
        self.bmk_key = {'Global Macro': 'HFRX Macro/CTA', 'Trend Following':'SG Trend',
                        'Absolute Return':'HFRX Absolute Return', 'Total Liquid Alts':'Liquid Alts Bmk'}
        
        
    def get_returns(self, bmk_data = True):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            if bmk_data:
                temp_ret = read_ret_data(LIQ_ALTS_BMK_DATA_FP, freq_string)
                if not self.all_data:
                    temp_ret['Liquid Alts Bmk'] = 0.5*temp_ret['HFRX Macro/CTA'] + 0.3*temp_ret['HFRX Absolute Return'] + 0.2*temp_ret['SG Trend']
            else:
                temp_ret = read_ret_data(HF_BMK_DATA_FP, freq_string)
            returns_dict[freq_string] = temp_ret.copy()
        return returns_dict

class liqAltsBmkHandler1(mktHandler):
    def __init__(self, equity_bmk = 'MSCI ACWI',include_fi = True, fi_bmk = 'FI Benchmark',
                 include_cm = True, cm_bmk = 'Commodities (BCOM)', include_fx=True,
                 fx_bmk = 'U.S. Dollar Index', all_data=False):
        super().__init__(equity_bmk ,include_fi, fi_bmk,include_cm, cm_bmk,
                            include_fx,fx_bmk, all_data)
        
        self.hf_returns = self.get_returns(False)
        self.bmk_returns = self.get_returns()
        self.bmk_key = {'Global Macro': 'HFRX Macro/CTA', 'Trend Following':'SG Trend',
                        'Absolute Return':'HFRX Absolute Return', 'Total Liquid Alts':'Liquid Alts Bmk'}
        
        
    def get_returns(self, bmk_data = True):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            if bmk_data:
                temp_ret = read_ret_data(LIQ_ALTS_BMK_DATA_FP, freq_string)
                if not self.all_data:
                    temp_ret['Liquid Alts Bmk'] = 0.5*temp_ret['HFRX Macro/CTA'] + 0.3*temp_ret['HFRX Absolute Return'] + 0.2*temp_ret['SG Trend']
            else:
                temp_ret = read_ret_data(HF_BMK_DATA_FP, freq_string)
            returns_dict[freq_string] = temp_ret.copy()
        return returns_dict


#TODO: Add returns from new managers that we just allocated to
#TODO: Add functionality to pull raw data    
class liqAltsPortHandler(liqAltsBmkHandler1):
    def __init__(self, equity_bmk = 'MSCI ACWI',include_fi = True, fi_bmk = 'FI Benchmark',
                 include_cm = True, cm_bmk = 'Commodities (BCOM)', include_fx=True,
                 fx_bmk = 'U.S. Dollar Index'):
        super().__init__(equity_bmk ,include_fi, fi_bmk,include_cm, cm_bmk,
                            include_fx,fx_bmk)
        
        self.hf_returns = self.hf_returns['Monthly']
        self.bmk_returns = self.bmk_returns['Monthly']
        self.mkt_returns = self.mkt_returns['Monthly'].iloc[11:,]
        self.sub_ports = self.get_sub_port_data()
        self.returns = self.get_full_port_data()
        self.mvs = self.get_full_port_data(False)
        self.mgr_bmk_dict = self.get_mgr_bmk_data()
        #TODO: add get_bmk_returns
        
    def get_sub_port_data(self):
        #pull all returns and mvs
        liq_alts_ret = read_ret_data(LIQ_ALTS_PORT_DATA_FP, 'returns')
        liq_alts_mv = read_ret_data(LIQ_ALTS_PORT_DATA_FP, 'market_values')
        #define dicts and dataframes
        liq_alts_dict = {}
        total_ret = pd.DataFrame(index = liq_alts_ret.index)
        total_mv = pd.DataFrame(index = liq_alts_mv.index)
        #loop through to creat sub_ports dict
        for key in LIQ_ALTS_MGR_DICT:
            temp_dict = {}
            temp_ret = liq_alts_ret[LIQ_ALTS_MGR_DICT[key]].copy()
            temp_mv = liq_alts_mv[LIQ_ALTS_MGR_DICT[key]].copy()
            temp_bmk = self.bmk_returns[[self.bmk_key[key]]].copy()
            temp_dict = dm.get_agg_data(temp_ret, temp_mv, key)
            if key == 'Trend Following':
                temp_dict = {'returns': liq_alts_ret[[key]], 'mv':liq_alts_mv[[key]], 'bmk': temp_bmk}
            # temp_ret =  dm.merge_data_frames(temp_ret, temp_dict['returns'], False)
            # temp_mv = dm.merge_data_frames(temp_mv, temp_dict['mv'], False)
            liq_alts_dict[key] = {'returns': temp_ret, 'mv': temp_mv, 'bmk': temp_bmk}
            total_ret = dm.merge_data_frames(total_ret, temp_dict['returns'], False)
            total_mv = dm.merge_data_frames(total_mv, temp_dict['mv'], False)
        total_dict = dm.get_agg_data(total_ret, total_mv, 'Total Liquid Alts')
        total_ret = dm.merge_data_frames(total_ret, total_dict['returns'], False)
        total_mv = dm.merge_data_frames(total_mv, total_dict['mv'], False)
        liq_alts_dict['Total Liquid Alts'] = {'returns': total_ret, 'mv':total_mv, 'bmk': self.bmk_returns.copy()}
        
        return liq_alts_dict
    
    
    def get_full_port_data(self, return_data = True):
        data = 'returns' if return_data else 'mv'
        liq_alts_port = pd.DataFrame()
        for key in self.sub_ports:
            liq_alts_port = dm.merge_data_frames(liq_alts_port, self.sub_ports[key][data], False)
        return liq_alts_port
    
    def get_mgr_bmk_data(self):
        bmk_data_dict = {}
        for key in self.sub_ports:
            bmk_name = self.bmk_key[key]
            for mgr in self.sub_ports[key]['returns'].columns:
                if key == 'Total Liquid Alts':
                    bmk_name = self.bmk_key[mgr]
                bmk_data_dict[mgr] = bmk_name
        return bmk_data_dict

    def add_mgr(self, df_mgr_ret, sub_port_key, mv_amt=100000000):
        self.sub_ports[sub_port_key]['returns'] = dm.merge_data_frames(self.sub_ports[sub_port_key]['returns'], df_mgr_ret,drop_na=False)
        col_list = list(self.sub_ports[sub_port_key]['returns'].columns)
        self.sub_ports[sub_port_key]['mv'][col_list[len(col_list)-1]] = dm.get_prices_df(df_mgr_ret,mv_amt)

        sub_port_dict = dm.get_agg_data(self.sub_ports[sub_port_key]['returns'],self.sub_ports[sub_port_key]['mv'], sub_port_key)
        self.sub_ports['Total Liquid Alts']['returns'][sub_port_key] = sub_port_dict['returns'][sub_port_key]
        self.sub_ports['Total Liquid Alts']['mv'][sub_port_key] = sub_port_dict['mv'][sub_port_key]
        self.update_total()
        self.returns = self.get_full_port_data()
        self.mvs = self.get_full_port_data(False)
        self.mgr_bmk_dict = self.get_mgr_bmk_data()
        
    #TODO
    def remove_mgr(self):
        pass
    
    #TODO
    def update_total(self):
        total_ret = self.sub_ports['Total Liquid Alts']['returns'][list(LIQ_ALTS_MGR_DICT.keys())]
        total_mv = self.sub_ports['Total Liquid Alts']['mv'][list(LIQ_ALTS_MGR_DICT.keys())]
        total_dict = dm.get_agg_data(total_ret, total_mv, 'Total Liquid Alts')
        self.sub_ports['Total Liquid Alts']['returns']['Total Liquid Alts'] = total_dict['returns']['Total Liquid Alts']
        self.sub_ports['Total Liquid Alts']['mv']['Total Liquid Alts'] = total_dict['mv']['Total Liquid Alts']
        
    def get_sub_mgrs(self,sub_port = 'Global Macro'):
        mgr_list = []
        mgr_list = mgr_list + LIQ_ALTS_MGR_DICT[sub_port]
        mgr_list.append(sub_port)
        return mgr_list

#TODO: add weighted strats logic
class eqHedgeHandler(mktHandler):
    def __init__(self, equity_bmk = 'M1WD',include_fi = True, all_data=False, strat_drop_list=[]):
        mktHandler.__init__(self, equity_bmk, include_fi)
        self.equity_bmk = equity_bmk
        self.include_fi = include_fi
        self.all_data = all_data
        self.strat_drop_list = strat_drop_list
        self.returns = dm.merge_dicts(self.mkt_returns, self.get_returns())
        
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
        

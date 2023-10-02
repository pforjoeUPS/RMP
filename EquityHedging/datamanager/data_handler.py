# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 22:18:15 2022

@author: NVG9HXP
"""

import os
from .import data_manager as dm
from .data_importer import read_data
import pandas as pd

CWD = os.getcwd()
RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\returns_data\\'
NEW_STRAT_DATA_FP = CWD +'\\EquityHedging\\data\\new_strats\\'

BMK_DATA_FP = RETURNS_DATA_FP+'bmk_returns.xlsx'
HF_BMK_DATA_FP = RETURNS_DATA_FP+'hf_bmks.xlsx'
UPSGT_DATA_FP = RETURNS_DATA_FP+'upsgt_returns.xlsx'
LIQ_ALTS_BMK_DATA_FP = RETURNS_DATA_FP+'liq_alts_bmks.xlsx'
LIQ_ALTS_PORT_DATA_FP = RETURNS_DATA_FP+'nexen_liq_alts_data.xlsx'


LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A','Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital', 'JSC Vantage'],
                     'Trend Following': ['1907 ARP TF','1907 Campbell TF', '1907 Systematica TF',
                                         'One River Trend'],
                     'Absolute Return':['1907 ARP EM',  '1907 III CV', '1907 III Class A',
                                        'Acadian Commodity AR','Blueshift', 'Duality', 'Elliott']
                     }
EQ_HEDGE_DATA_FP = RETURNS_DATA_FP+'eq_hedge_returns.xlsx'
EQ_HEDGE_STRAT_DICT = {'99%/90% Put Spread':0.0, 'Down Var':1.0, 'Vortex':0.0, 'VOLA 3':1.25,'Dynamic Put Spread':1.0,
                       'VRR Portfolio':1.0, 'GW Dispersion':1.0, 'Corr Hedge':0.25,'Def Var':1.0,'Commodity Basket':1.0}
FREQ_LIST = ['1D', '1W', '1M', '1Q', '1Y']

class mktHandler():
    def __init__(self, equity_bmk = 'M1WD',include_fi = True, all_data=False):
        self.equity_bmk = equity_bmk
        self.include_fi = include_fi
        if include_fi:
            self.fi_bmk = 'FI Benchmark'
        self.all_data = all_data
        self.mkt_returns = self.get_mkt_returns()
        
    def get_mkt_returns(self):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            temp_ret = read_data(BMK_DATA_FP, freq_string)
            if self.all_data:
                returns_dict[freq_string] = temp_ret.copy()
            else:    
                if freq != '1D':
                    if self.include_fi:
                        temp_ret[self.fi_bmk] = temp_ret['Long Corp']*0.6 + temp_ret['STRIPS']*0.4
                        returns_dict[freq_string] = temp_ret[[self.equity_bmk, self.fi_bmk]]
                    else:
                        returns_dict[freq_string] = temp_ret[[self.equity_bmk]]
                else:
                    returns_dict[freq_string] = temp_ret[[self.equity_bmk]]
                returns_dict[freq_string].index.names = ['Date']
        
        return returns_dict
        
class upsGTPortHandler(mktHandler):
    def __init__(self, equity_bmk = 'M1WD', include_fi=True):
        super().__init__(equity_bmk, include_fi)
        self.mkt_returns = self.mkt_returns['Monthly']
        self.returns = read_data(UPSGT_DATA_FP, 'returns')
        self.mvs = read_data(UPSGT_DATA_FP, 'market_values')
        
        
class liqAltsBmkHandler(mktHandler):
    def __init__(self, equity_bmk = 'M1WD',include_fi = True):
        super().__init__(equity_bmk, include_fi)
        self.hf_returns = self.get_returns(False)
        self.bmk_returns = self.get_returns()
        
    def get_returns(self, bmk_data = True):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            if bmk_data:
                temp_ret = read_data(LIQ_ALTS_BMK_DATA_FP, freq_string)
                if not self.all_data:
                    temp_ret['Liquid Alts Bmk'] = 0.5*temp_ret['HFRX Macro/CTA'] + 0.3*temp_ret['HFRX Absolute Return'] + 0.2*temp_ret['SG Trend']
            else:
                temp_ret = read_data(HF_BMK_DATA_FP, freq_string)
            returns_dict[freq_string] = temp_ret.copy()
        return returns_dict

class liqAltsPortHandler(liqAltsBmkHandler):
    def __init__(self, equity_bmk = 'M1WD',include_fi = True):
        super().__init__(equity_bmk, include_fi)
        self.sub_ports = self.get_sub_port_data()
        self.returns = self.get_full_port_data()
        self.mvs = self.get_full_port_data(False)
        self.hf_returns = self.hf_returns['Monthly']
        self.bmk_returns = self.bmk_returns['Monthly']
        self.mkt_returns = self.mkt_returns['Monthly']
        
    def get_sub_port_data(self):
        #pull all returns and mvs
        liq_alts_ret = read_data(LIQ_ALTS_PORT_DATA_FP, 'returns')
        liq_alts_mv = read_data(LIQ_ALTS_PORT_DATA_FP, 'market_values')
        #define dicts and dataframes
        liq_alts_dict = {}
        total_ret = pd.DataFrame(index = liq_alts_ret.index)
        total_mv = pd.DataFrame(index = liq_alts_mv.index)
        #loop through to creat sub_ports dict
        for key in LIQ_ALTS_MGR_DICT:
            temp_dict = {}
            temp_ret = liq_alts_ret[LIQ_ALTS_MGR_DICT[key]].copy()
            temp_mv = liq_alts_mv[LIQ_ALTS_MGR_DICT[key]].copy()
            temp_dict = dm.get_agg_data(temp_ret, temp_mv, key)
            if key == 'Trend Following':
                temp_dict = {'returns': liq_alts_ret[[key]], 'market_values':liq_alts_mv[[key]]}
            temp_ret =  temp_ret.join( temp_dict['returns'])
            temp_mv = temp_mv.join(temp_dict['market_values'])
            liq_alts_dict[key] = {'returns': temp_ret, 'market_values': temp_mv}
            total_ret = total_ret.join(temp_dict['returns'])
            total_mv = total_mv.join(temp_dict['market_values'])
        total_dict = dm.get_agg_data(total_ret, total_mv, 'Total Liquid Alts')
        total_ret = total_ret.join(total_dict['returns'])
        total_mv = total_mv.join(total_dict['market_values'])
        liq_alts_dict['Total Liquid Alts'] = {'returns': total_ret, 'market_values':total_mv}
        
        return liq_alts_dict
    
    def get_full_port_data(self, return_data = True):
        data = 'returns' if return_data else 'market_values'
        liq_alts_port = pd.DataFrame()
        for key in LIQ_ALTS_MGR_DICT:
            liq_alts_port = dm.merge_data_frames(liq_alts_port, self.sub_ports[key][data], drop_na=False)
        return liq_alts_port
    
    def add_new_mgr(self, df_mgr_ret, sub_port_key, mv_amt):
        self.sub_ports[sub_port_key]['returns'] = dm.merge_data_frames(self.sub_ports[sub_port_key]['returns'], df_mgr_ret,drop_na=False)
        col_list = list(self.sub_ports[sub_port_key]['returns'].columns)
        self.sub_ports[sub_port_key]['market_values'][col_list[len(col_list)-1]] = mv_amt

        js_dict = dm.get_agg_data(self.sub_ports[sub_port_key]['returns'],self.sub_ports[sub_port_key]['mv'], sub_port_key)
        self.sub_ports['Total Liquid Alts']['returns'][sub_port_key] = js_dict['returns'][sub_port_key]
        self.sub_ports['Total Liquid Alts']['market_values'][sub_port_key] = js_dict['market_values'][sub_port_key]

        self.returns = self.get_full_port_data()
        self.mvs = self.get_full_port_data(False)
        
    def get_sub_mgrs(self,sub_port = 'Global Macro'):
        mgr_list = []
        mgr_list = mgr_list + LIQ_ALTS_MGR_DICT[sub_port]
        mgr_list.append(sub_port)
        return mgr_list


#TODO: make strat_drop_list default to an empty list now
class eqHedgeHandler(mktHandler):
    def __init__(self, equity_bmk = 'SPTR',include_fi = False, all_data=False, strat_drop_list=['99%/90% Put Spread', 'Vortex']):
        super().__init__(equity_bmk, include_fi, all_data)
        self.strat_drop_list = strat_drop_list
        self.returns = dm.merge_dicts(self.mkt_returns, self.get_returns())
        #TODO: work on functional to overwrite the nmtionals in EQ_HEDGE_STRAT_DICT
        self.notional_dict = self.get_notional_weights()
        
    def get_returns(self):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            temp_ret = dm.get_real_cols(read_data(EQ_HEDGE_DATA_FP, freq_string))
            if not self.all_data:
                temp_ret['VOLA 3'] = temp_ret['Dynamic VOLA']
                temp_ret['Def Var'] = temp_ret['Def Var (Fri)']*.4 + temp_ret['Def Var (Mon)']*.3+temp_ret['Def Var (Wed)']*.3
                
                #Check with documents to know exact weights for VRR Portfolio*?
                temp_ret['VRR Portfolio'] = temp_ret['VRR 2']*0.75 + temp_ret['VRR Trend']*0.25
                
                temp_ret = temp_ret[list(EQ_HEDGE_STRAT_DICT.keys())]
            if self.strat_drop_list:
                temp_ret.drop(self.strat_drop_list, axis=1, inplace=True)
            returns_dict[freq_string] = temp_ret.copy()
        return returns_dict
    
    def get_new_strategy_returns_data(self, filename, sheet_name, strategy_list):
        df_strategy = pd.read_excel(NEW_STRAT_DATA_FP+filename, sheet_name=sheet_name, index_col=0)
        df_strategy = dm.get_real_cols(df_strategy)
        if strategy_list:
            df_strategy.columns = strategy_list
        try:
            df_strategy.index = pd.to_datetime(df_strategy.index)
        except TypeError:
            pass
        df_strategy = df_strategy.resample('1D').ffill()
        new_strategy_returns = df_strategy.copy()
        if 'Index' in sheet_name:
            new_strategy_returns = df_strategy.pct_change(1)
        new_strategy_returns.dropna(inplace=True)
        return new_strategy_returns
    
    def add_new_strat(self, filename, sheet_name, strategy_list, notional_list):
        #TODO: not sure if this will be used plus there may be some bugs in here
        if isinstance(filename, list):
            new_strat_dict = {}
            for i in range(0,len(filename)):
                new_strat = self.get_new_strategy_returns_data(filename[i], sheet_name[i], strategy_list[i:i+1])
                new_strat_dict_temp = dm.get_data_dict(new_strat, data_type='index')
                if i == 0:
                    new_strat_dict = new_strat_dict_temp
                else:
                    new_strat_dict = dm.merge_dicts(new_strat_dict, new_strat_dict_temp)
        else:
            new_strat = self.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
            new_strat_dict = dm.get_data_dict(new_strat, data_type='index')
            
        self.returns = dm.merge_dicts(self.returns, new_strat_dict)
        self.update_notional(strategy_list, notional_list)

    def update_notional(self, strategy_list, notional_list):
        notional_list = [float(x) for x in notional_list]
        self.notional_dict.update(dict(zip(strategy_list, notional_list)))
    
    def get_notional_weights(self):
        notional_dict = EQ_HEDGE_STRAT_DICT.copy()
        for key in self.strat_drop_list:
            notional_dict.pop(key)
        return notional_dict
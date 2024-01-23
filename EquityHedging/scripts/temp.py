# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 13:58:51 2023

@author: NVG9HXP
"""
from copy import deepcopy
import pandas as pd
from EquityHedging.analytics import returns_analytics as rsa
from EquityHedging.analytics import returns_stats as rs
from EquityHedging.analytics import util
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm

mkt_dh = dh.mktHandler()


liq_alts_p = dh.liqAltsPortHandler('MSCI ACWI')
# C:\Users\nvg9hxp\Documents\Projects\RMP\EquityHedging\datamanager\data_handler.py:165: SettingWithCopyWarning:
# A value is trying to be set on a copy of a slice from a DataFrame.
# Try using .loc[row_indexer,col_indexer] = value instead
# See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
#   self.bmk_returns[freq_string]['Liquid Alts Bmk'] = self.bmk_returns[freq_string].dot([0.5, 0.3, 0.2])#*returns_df['HFRX Macro/CTA'] + 0.3*returns_df['HFRX Absolute Return'] + 0.2*returns_df['SG Trend']
# C:\Users\nvg9hxp\Documents\Projects\RMP\EquityHedging\datamanager\data_handler.py:165: SettingWithCopyWarning:
# A value is trying to be set on a copy of a slice from a DataFrame.
# Try using .loc[row_indexer,col_indexer] = value instead
penso = dm.get_new_strat_data('liq_alts\\penso_returns.xlsx')
jsc = dm.get_new_strat_data('liq_alts\\jsc.xlsx')
tmf = dm.get_new_strat_data('liq_alts\\tmf.xlsx')
kaf = dm.get_new_strat_data('liq_alts\\kaf.xlsx')
edl_c = dm.get_new_strat_data('liq_alts\\edl.xlsx')
edl_c.columns = ['EDL GOF']

drop_mgr = '1907 Penso Class A'
liq_alts_p.remove_mgr(drop_mgr)
liq_alts_p.update_mgr('JSC Vantage', jsc)
liq_alts_p.update_mgr('Capula TM Fund', tmf)
liq_alts_p.update_mgr('KAF', kaf)
liq_alts_p.add_mgr(edl_c, 'Global Macro',125000000)
returns_df = liq_alts_p.sub_ports['Global Macro']['returns'].copy()

mkt_df=liq_alts_p.mkt_returns.copy()
mkt_key=deepcopy(liq_alts_p.mkt_key)
bmk_df=liq_alts_p.bmk_returns.copy()
bmk_key=deepcopy(liq_alts_p.mgr_bmk_dict)
bmk_key['EDL GOF'] = 'HFRX Macro/CTA'
ret_dict = dm.get_period_dict(returns_df)
analytics_dict = {}
for key in ret_dict:
    temp_rsa = rsa.liquidAltsAnalytic(ret_dict[key],mkt_df=mkt_df, mkt_key=mkt_key,include_eq=True, freq='1M',
                                   rfr=0.0, target=0.0, include_bmk=True, bmk_df=bmk_df, 
                                   bmk_dict=bmk_dict, include_fi=True, include_cm=True, include_fx=True)
    analytics_dict[key] = temp_rsa.returns_stats_data.copy()


rsa_basic = rsa.returnsAnalytic(returns_df,include_bmk=True, bmk_df=bmk_df,bmk_dict=bmk_dict,
                               include_eq=True,include_fi=True, mkt_df=mkt_df, mkt_key=mkt_key)
    
class ClassA:
    def method1(self):
        print("Method 1 of ClassA")

    def method2(self):
        print("Method 2 of ClassA")

class ClassB:
    def __init__(self, instance_of_a):
        self.instance_of_a = instance_of_a

    def call_method(self, method_name):
        # Check if the method exists in ClassA
        if hasattr(self.instance_of_a, method_name) and callable(getattr(self.instance_of_a, method_name)):
            # Call the method dynamically
            getattr(self.instance_of_a, method_name)()
        else:
            print(f"Method '{method_name}' does not exist in ClassA.")

# Create an instance of ClassA
obj_a = ClassA()

# Create an instance of ClassB and pass the instance of ClassA
obj_b = ClassB(obj_a)

# Dynamically call methods of ClassA from ClassB
obj_b.call_method("method1")
obj_b.call_method("method2")
obj_b.call_method("nonexistent_method")

corr_matrix = {}
for asset in rsa_la.mkt_key:
    asset_id = rsa_la.mkt_key[asset]
    asset_up = (df_returns[df_returns[asset_id] > 0])
    asset_down = (df_returns[df_returns[asset_id] < 0])
    asset_dict = {"full": df_returns.corr(),
    "up": asset_up.corr(),
    "down": asset_down.corr()}
    corr_matrix[asset] = asset_dict
    
a=pd.np.triu(x_up.corr().values)
b=pd.np.tril(x_dwn.corr().values)
c = a+b
for i in range(0,len(c)):
    print(i)
    
for i in range(0,len(c)):
    c[i][i] = 1
    
c = pd.DataFrame(c, index=x_up.columns, columns=x_up.columns)

mkt_ret_df_1 = pd.DataFrame(index=mkt_df.index)
for key in rsa_la_1.mkt_key:
    print(key)
    if rsa_la_1.bool_dict[key]:
        print(rsa_la_1.bool_dict[key])
        try:
            print('try')
            mkt_ret_df_1 = dm.merge_data_frames(mkt_ret_df_1, rsa.add_mkt_data(mkt_df, rsa_la_1.mkt_key, key))
        except KeyError:
            print(f'No {key} market data...')
            rsa_la_1.bool_dict[key] = False
            pass
            
rsa_la_1.mkt_ret_data = mkt_ret_df_1.copy()

empty=False
empty_analytics = {'alpha':None, 'beta':None, 'up_beta':None, 'dwn_beta':None,
                    'corr': None,'up_corr': None,'dwn_corr': None }

returns_stats_dict = {}
for col in rsa_la_1.returns_df.columns:
    return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
    time_frame = rsa_la_1.period[col]
    obs = len(return_series)
    active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
    port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
    mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsa_la_1.returns_df[[col]])
    mkt_ret_df.dropna(inplace=True)
    mkt_analytics={}
    for key in rsa_la_1.mkt_key:
        if empty:
            mkt_analytics[key]= empty_analytics
        else:
            try:
                strat = return_series.name
                mkt_id = rsa_la_1.mkt_key[key]
                mkt_strat = mkt_ret_df[mkt_id]
                mkt_up_df = (mkt_ret_df[mkt_strat > 0])
                mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])

                mkt_alpha = 0 if strat == mkt_id else rs.get_alpha(return_series,mkt_strat,rsa_la_1.freq,rsa_la_1.rfr)
                mkt_beta = 1 if strat == mkt_id else rs.get_beta(return_series,mkt_strat,rsa_la_1.freq)
                mkt_up_beta = 1 if strat == mkt_id else rs.get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],rsa_la_1.freq)
                mkt_dwn_beta = 1 if strat == mkt_id else rs.get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],rsa_la_1.freq)
                mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
                mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
                mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
                mkt_analytics[key] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                        'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
            except KeyError:
                mkt_analytics[key] = empty_analytics
                
    returns_stats_dict[col] = [time_frame, obs] + list(port_analytics.values()) + list(active_analytics.values()) + rsa_la_1.get_mkt_analytics_list(mkt_analytics)

df_returns_stats = util.convert_dict_to_df(returns_stats_dict, 
                                           ['Time Frame',f'No. of {rsa_la_1.freq_string} Observations']+list(rsa.PORT_COL_DICT.values())+list(rsa.ACTIVE_COL_DICT.values())+ rsa.get_mkt_index_list())
df_returns_stats = df_returns_stats.reindex(rsa_la_1.index)

for key in rsa_la_1.bool_dict:
    if not rsa_la_1.bool_dict[key]:
        try:
            df_returns_stats.drop(rsa_la_1.drop_list_dict[key], inplace = True)
        except KeyError:
            pass
            
rsa_la_1.bool_dict
######################################################################################################################################
x=0

col = rsa_la_1.returns_df.columns[x]
return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
time_frame = rsa_la_1.period[col]
obs = len(return_series)
active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsa_la_1.returns_df[[col]])
# mkt_ret_df.dropna(inplace=True)
mkt_analytics={}
for key in rsa_la_1.mkt_key:
    print(key)
    if empty:
        mkt_analytics[key]= empty_analytics
    else:
        try:
            strat = return_series.name
            mkt_id = rsa_la_1.mkt_key[key]
            mkt_strat = mkt_ret_df[mkt_id]
            mkt_up_df = (mkt_ret_df[mkt_strat > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])

            mkt_alpha = 0 if strat == mkt_id else rs.get_alpha(return_series,mkt_strat,rsa_la_1.freq,rsa_la_1.rfr)
            mkt_beta = 1 if strat == mkt_id else rs.get_beta(return_series,mkt_strat,rsa_la_1.freq)
            mkt_up_beta = 1 if strat == mkt_id else rs.get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],rsa_la_1.freq)
            mkt_dwn_beta = 1 if strat == mkt_id else rs.get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],rsa_la_1.freq)
            mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
            mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
            mkt_analytics[key] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                    'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
        except KeyError:
            mkt_analytics[key] = empty_analytics
            
returns_stats_dict[col] = [time_frame, obs] + list(port_analytics.values()) + list(active_analytics.values()) + rsa_la_1.get_mkt_analytics_list(mkt_analytics)




rsa_la_1.bool_dict
returns_stats_dict = {}
for col in rsa_la_1.returns_df.columns:
    return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
    time_frame = rsa_la_1.period[col]
    obs = len(return_series)
    active_analytics = rsa_la_1.get_active_analytics(col) if a_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
    port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
    
returns_stats_dict = {}
for col in rsa_la_1.returns_df.columns:
    return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
    time_frame = rsa_la_1.period[col]
    obs = len(return_series)
    active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
    port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
    
col = 'Bridgewater Alpha'
returns_stats_dict = {}

return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
time_frame = rsa_la_1.period[col]
obs = len(return_series)
active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
    
mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsala_1.returns_df[[col]])
mkt_ret_df.dropna(inplace=True)
mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsa_la_1.returns_df[[col]])
mkt_ret_df.dropna(inplace=True)
empty_analytics = {'alpha':None, 'beta':None, 'up_beta':None, 'dwn_beta':None,
                    'corr': None,'up_corr': None,'dwn_corr': None }
mkt_analytics = {}
empty=False
for key in rsa_la_1.mkt_key:
    if empty:
        mkt_analytics[key]= empty_analytics
    else:
        try:
            strat = return_series.name
            mkt_id = rsa_la_1.mkt_key[key]
            mkt_strat = mkt_ret_df[mkt_id]
            mkt_up_df = (mkt_ret_df[mkt_strat > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])

            mkt_alpha = 0 if strat == mkt_id else rs.get_alpha(return_series,mkt_strat,rsa_la_1.freq,rsa_la_1.rfr)
            mkt_beta = 1 if strat == mkt_id else rs.get_beta(return_series,mkt_strat,rsa_la_1.freq)
            mkt_up_beta = 1 if strat == mkt_id else rs.get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],rsa_la_1.freq)
            mkt_dwn_beta = 1 if strat == mkt_id else rs.get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],rsa_la_1.freq)
            mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
            mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
            mkt_analytics[key] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                    'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
        except KeyError:
            mkt_analytics[key] = empty_analytics
            
returns_stats_dict[col] = [time_frame, obs] + list(port_analytics.values()) + list(active_analytics.values()) + rsa_la_1.get_mkt_analytics_list(mkt_analytics)
rsa_la_1.returns_df.columns
col = rsa_la_1.returns_df.columns[0]
col
return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
time_frame = rsa_la_1.period[col]
obs = len(return_series)
active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsa_la_1.returns_df[[col]])
mkt_ret_df.dropna(inplace=True)
mkt_analytics={}
for key in rsa_la_1.mkt_key:
    if empty:
        mkt_analytics[key]= empty_analytics
    else:
        try:
            strat = return_series.name
            mkt_id = rsa_la_1.mkt_key[key]
            mkt_strat = mkt_ret_df[mkt_id]
            mkt_up_df = (mkt_ret_df[mkt_strat > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])

            mkt_alpha = 0 if strat == mkt_id else rs.get_alpha(return_series,mkt_strat,rsa_la_1.freq,rsa_la_1.rfr)
            mkt_beta = 1 if strat == mkt_id else rs.get_beta(return_series,mkt_strat,rsa_la_1.freq)
            mkt_up_beta = 1 if strat == mkt_id else rs.get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],rsa_la_1.freq)
            mkt_dwn_beta = 1 if strat == mkt_id else rs.get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],rsa_la_1.freq)
            mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
            mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
            mkt_analytics[key] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                    'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
        except KeyError:
            mkt_analytics[key] = empty_analytics
            
returns_stats_dict[col] = [time_frame, obs] + list(port_analytics.values()) + list(active_analytics.values()) + rsa_la_1.get_mkt_analytics_list(mkt_analytics)
col = rsa_la_1.returns_df.columns[1]
col
col = rsa_la_1.returns_df.columns[2]
col
return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
time_frame = rsa_la_1.period[col]
obs = len(return_series)
active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsa_la_1.returns_df[[col]])
mkt_ret_df.dropna(inplace=True)
mkt_analytics={}
for key in rsa_la_1.mkt_key:
    if empty:
        mkt_analytics[key]= empty_analytics
    else:
        try:
            strat = return_series.name
            mkt_id = rsa_la_1.mkt_key[key]
            mkt_strat = mkt_ret_df[mkt_id]
            mkt_up_df = (mkt_ret_df[mkt_strat > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])

            mkt_alpha = 0 if strat == mkt_id else rs.get_alpha(return_series,mkt_strat,rsa_la_1.freq,rsa_la_1.rfr)
            mkt_beta = 1 if strat == mkt_id else rs.get_beta(return_series,mkt_strat,rsa_la_1.freq)
            mkt_up_beta = 1 if strat == mkt_id else rs.get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],rsa_la_1.freq)
            mkt_dwn_beta = 1 if strat == mkt_id else rs.get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],rsa_la_1.freq)
            mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
            mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
            mkt_analytics[key] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                    'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
        except KeyError:
            mkt_analytics[key] = empty_analytics
            
returns_stats_dict[col] = [time_frame, obs] + list(port_analytics.values()) + list(active_analytics.values()) + rsa_la_1.get_mkt_analytics_list(mkt_analytics)
x=3
col = rsa_la_1.returns_df.columns[x]
return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
time_frame = rsa_la_1.period[col]
obs = len(return_series)
active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsa_la_1.returns_df[[col]])
mkt_ret_df.dropna(inplace=True)
mkt_analytics={}
for key in rsa_la_1.mkt_key:
    if empty:
        mkt_analytics[key]= empty_analytics
    else:
        try:
            strat = return_series.name
            mkt_id = rsa_la_1.mkt_key[key]
            mkt_strat = mkt_ret_df[mkt_id]
            mkt_up_df = (mkt_ret_df[mkt_strat > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])
            
            mkt_alpha = 0 if strat == mkt_id else rs.get_alpha(return_series,mkt_strat,rsa_la_1.freq,rsa_la_1.rfr)
            mkt_beta = 1 if strat == mkt_id else rs.get_beta(return_series,mkt_strat,rsa_la_1.freq)
            mkt_up_beta = 1 if strat == mkt_id else rs.get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],rsa_la_1.freq)
            mkt_dwn_beta = 1 if strat == mkt_id else rs.get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],rsa_la_1.freq)
            mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
            mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
            mkt_analytics[key] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                    'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
        except KeyError:
            mkt_analytics[key] = empty_analytics

returns_stats_dict[col] = [time_frame, obs] + list(port_analytics.values()) + list(active_analytics.values()) + rsa_la_1.get_mkt_analytics_list(mkt_analytics)
x=4
col = rsa_la_1.returns_df.columns[x]
return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
time_frame = rsa_la_1.period[col]
obs = len(return_series)
active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsa_la_1.returns_df[[col]])
mkt_ret_df.dropna(inplace=True)
mkt_analytics={}
for key in rsa_la_1.mkt_key:
    if empty:
        mkt_analytics[key]= empty_analytics
    else:
        try:
            strat = return_series.name
            mkt_id = rsa_la_1.mkt_key[key]
            mkt_strat = mkt_ret_df[mkt_id]
            mkt_up_df = (mkt_ret_df[mkt_strat > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])
            
            mkt_alpha = 0 if strat == mkt_id else rs.get_alpha(return_series,mkt_strat,rsa_la_1.freq,rsa_la_1.rfr)
            mkt_beta = 1 if strat == mkt_id else rs.get_beta(return_series,mkt_strat,rsa_la_1.freq)
            mkt_up_beta = 1 if strat == mkt_id else rs.get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],rsa_la_1.freq)
            mkt_dwn_beta = 1 if strat == mkt_id else rs.get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],rsa_la_1.freq)
            mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
            mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
            mkt_analytics[key] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                    'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
        except KeyError:
            mkt_analytics[key] = empty_analytics

returns_stats_dict[col] = [time_frame, obs] + list(port_analytics.values()) + list(active_analytics.values()) + rsa_la_1.get_mkt_analytics_list(mkt_analytics)
x=5
col = rsa_la_1.returns_df.columns[x]
return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
time_frame = rsa_la_1.period[col]
obs = len(return_series)
active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsa_la_1.returns_df[[col]])
mkt_ret_df.dropna(inplace=True)
mkt_analytics={}
for key in rsa_la_1.mkt_key:
    if empty:
        mkt_analytics[key]= empty_analytics
    else:
        try:
            strat = return_series.name
            mkt_id = rsa_la_1.mkt_key[key]
            mkt_strat = mkt_ret_df[mkt_id]
            mkt_up_df = (mkt_ret_df[mkt_strat > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])
            
            mkt_alpha = 0 if strat == mkt_id else rs.get_alpha(return_series,mkt_strat,rsa_la_1.freq,rsa_la_1.rfr)
            mkt_beta = 1 if strat == mkt_id else rs.get_beta(return_series,mkt_strat,rsa_la_1.freq)
            mkt_up_beta = 1 if strat == mkt_id else rs.get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],rsa_la_1.freq)
            mkt_dwn_beta = 1 if strat == mkt_id else rs.get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],rsa_la_1.freq)
            mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
            mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
            mkt_analytics[key] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                    'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
        except KeyError:
            mkt_analytics[key] = empty_analytics

returns_stats_dict[col] = [time_frame, obs] + list(port_analytics.values()) + list(active_analytics.values()) + rsa_la_1.get_mkt_analytics_list(mkt_analytics)
x=6
col = rsa_la_1.returns_df.columns[x]
return_series = dm.remove_na(rsa_la_1.returns_df, col)[col]
time_frame = rsa_la_1.period[col]
obs = len(return_series)
active_analytics = rsa_la_1.get_active_analytics(col) if rsa_la_1.include_bmk else rsa_la_1.get_active_analytics(col, True)
port_analytics = rs.get_port_analytics(return_series, col, rsa_la_1.freq)
mkt_ret_df = dm.merge_data_frames(rsa_la_1.mkt_ret_data, rsa_la_1.returns_df[[col]])
mkt_ret_df.dropna(inplace=True)
mkt_analytics={}
for key in rsa_la_1.mkt_key:
    if empty:
        mkt_analytics[key]= empty_analytics
    else:
        try:
            strat = return_series.name
            mkt_id = rsa_la_1.mkt_key[key]
            mkt_strat = mkt_ret_df[mkt_id]
            mkt_up_df = (mkt_ret_df[mkt_strat > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])
            
            mkt_alpha = 0 if strat == mkt_id else rs.get_alpha(return_series,mkt_strat,rsa_la_1.freq,rsa_la_1.rfr)
            mkt_beta = 1 if strat == mkt_id else rs.get_beta(return_series,mkt_strat,rsa_la_1.freq)
            mkt_up_beta = 1 if strat == mkt_id else rs.get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],rsa_la_1.freq)
            mkt_dwn_beta = 1 if strat == mkt_id else rs.get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],rsa_la_1.freq)
            mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
            mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
            mkt_analytics[key] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                    'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
        except KeyError:
            mkt_analytics[key] = empty_analytics

returns_stats_dict[col] = [time_frame, obs] + list(port_analytics.values()) + list(active_analytics.values()) + rsa_la_1.get_mkt_analytics_list(mkt_analytics)
df_returns_stats = util.convert_dict_to_df(returns_stats_dict, 
                                           ['Time Frame',f'No. of {rsa_la_1.freq_string} Observations']+list(PORT_COL_DICT.values())+list(ACTIVE_COL_DICT.values())+ rsa.get_mkt_index_list())
df_returns_stats = df_returns_stats.reindex(rsa_la_1.index)
for key in rsa_la_1.bool_dict:
    if not rsa_la_1.bool_dict[key]:
        try:
            df_returns_stats.drop(rsa_la_1.drop_list_dict[key], inplace = True)
        except KeyError:
            pass
            
rsa_la_1.bool_dict




file_path = rp.get_filepath_path('test_corr')
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_corr_sheet(writer,corr_stats,sheet_name='Correlation Analysis')
rp.print_report_info('test_corr', file_path)
writer.save()



dates_df = returns_df.index()
dates_df = returns_df.index
date_rng = pd.to_datetime(dates_df) # DatetimeIndex
print(pd.infer_freq(date_rng))
liq_alts_b = dh.liqAltsBmkHandler1()
dates = liq_alts_b.bmk_returns['Daily'].index
date_rng = pd.to_datetime(dates) # DatetimeIndex
print(pd.infer_freq(date_rng))
date_freq_dict_bmk = {}
for key in liq_alts_b.bmk_returns:
    dates = liq_alts_b.bmk_returns[key].index
    date_rng = pd.to_datetime(dates) # DatetimeIndex
    date_freq_dict_bmk[key] = pd.infer_freq(date_rng)
    
date_freq_dict_hf = {}
for key in liq_alts_b.hf_returns:
    dates = liq_alts_b.bmk_returns[key].index
    date_rng = pd.to_datetime(dates) # DatetimeIndex
    date_freq_dict_hf[key] = pd.infer_freq(date_rng)
    
date_freq_dict_mkt = {}
for key in liq_alts_b.mkt_returns:
    dates = liq_alts_b.bmk_returns[key].index
    date_rng = pd.to_datetime(dates) # DatetimeIndex
    date_freq_dict_mkt[key] = pd.infer_freq(date_rng)
    
pd.infer_freq(liq_alts_b.bmk_returns['Monthly'].index)
pd.infer_freq(liq_alts_b.bmk_returns['Daily'].index)
pd.infer_freq(liq_alts_b.bmk_returns['Yearly'].index)
pd.infer_freq(liq_alts_b.bmk_returns['Weekly'].index)
pd.infer_freq(liq_alts_b.bmk_returns['Quarterly'].index)
liq_alts_b.bmk_returns['Weekly'].index.freq
liq_alts_b.bmk_returns['Weekly'].index.inferred_freq
liq_alts_b.bmk_returns['Daily'].index.inferred_freq
temp_df = liq_alts_b.bmk_returns['Daily'].copy()
a = temp_df.resample('A')ffill()
a = temp_df.resample('A').ffill()
a = temp_df.resample('Y').ffill()
b = temp_df.resample('A').ffill()
liq_alts_b.bmk_returns['Daily'].index.inferred_freq
liq_alts_b.bmk_returns['Weekly'].index.inferred_freq
liq_alts_b.bmk_returns['Weekly'].index.inferred_freq[0]
dm.switch_freq_int('P')
dm.switch_freq_string('P')
dm.switch_freq_int('P')
dm.switch_freq_string('P')
dm.switch_freq_int('A')
dm.switch_freq_string('P')
a
from EquityHedging.analytics import summary
c = summary.all_strat_month_ret_table(liq_alts_p.sub_ports['Global Macro']['returns'], include_fi=False)
d = dm.month_ret_table(liq_alts_p.sub_ports['Global Macro']['returns'], 'EDL GOF')
type(d)
type(c)
e = a['SG Trend']
type(e)
d.index
d.index.name

## ---(Fri Dec 29 03:39:35 2023)---
from EquityHedging.datamanager import data_handler as dh
mkt_dh = dh.mktHandler()
from EquityHedging.datamanager import data_handler as dh
mkt_dh = dh.mktHandler()
for freq in dh.FREQ_LIST:
    print(freq)
    
for freq in dh.FREQ_LIST:
    print(f'{freq}: {dh.dm.switch_freq_string(freq)})
for freq in dh.FREQ_LIST:
    print(f'{freq}: {dh.dm.switch_freq_string(freq)}')
    
from EquityHedging.datamanager import data_handler as dh
for freq in dh.FREQ_LIST:
    print(f'{freq}: {dh.dm.switch_freq_string(freq)}')
    
from EquityHedging.datamanager import data_handler as dh
for freq in dh.FREQ_LIST:
    print(f'{freq}: {dh.dm.switch_freq_string(freq)}')
    
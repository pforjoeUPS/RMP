# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 13:58:51 2023

@author: NVG9HXP
"""
from EquityHedging.analytics import return_stats as rsa
from EquityHedging.analytics import returns_stats as rs
from EquityHedging.analytics import rolling_stats as roll
from EquityHedging.analytics import corr_stats as cs
from EquityHedging.analytics import util
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
import pandas as pd
import copy

liq_alts_p = dh.liqAltsPortHandler()
returns_df = liq_alts_p.sub_ports['Global Macro']['returns'].copy()
returns_df.drop(['1907 Penso Class A','JSC Vantage', 'Capula TM Fund', 'KAF'], axis=1, inplace=True)
penso = dm.get_new_strat_data('liq_alts\\penso_returns.xlsx')
jsc = dm.get_new_strat_data('liq_alts\\jsc.xlsx')
tmf = dm.get_new_strat_data('liq_alts\\tmf.xlsx')
kaf = dm.get_new_strat_data('liq_alts\\kaf.xlsx')
edl_c = dm.get_new_strat_data('liq_alts\\edl.xlsx')
returns_df = dm.merge_data_frames(returns_df,penso, False)
returns_df = dm.merge_data_frames(returns_df,jsc, False)
returns_df = dm.merge_data_frames(returns_df,tmf, False)
returns_df = dm.merge_data_frames(returns_df,kaf, False)
returns_df = dm.merge_data_frames(returns_df,edl_c, False)

returns_df = returns_df[['Bridgewater Alpha', 'DE Shaw Oculus Fund',
                               'Element Capital',  'JSC Vantage','Capula TM Fund', 'KAF','EDL-C']]
mkt_df=liq_alts_p.mkt_returns.copy()
mkt_key=copy.deepcopy(liq_alts_p.mkt_key)
bmk_df=liq_alts_p.bmk_returns.copy()
bmk_dict=copy.deepcopy(liq_alts_p.mgr_bmk_dict)
bmk_dict['EDL-C'] = 'HFRX Macro/CTA'
ret_dict = dm.get_period_dict(returns_df)
analytics_dict = {}
for key in ret_dict:
    temp_rsa = rsa.liquidAltsAnalytic(ret_dict[key],mkt_df=mkt_df, mkt_key=mkt_key,include_eq=True, freq='1M',
                                   rfr=0.0, target=0.0, include_bmk=True, bmk_df=bmk_df, 
                                   bmk_dict=bmk_dict, include_fi=True, include_cm=True, include_fx=True)
    analytics_dict[key] = temp_rsa.returns_stats_data.copy()


rsa_basic = rsa.returnsAnalytic(returns_df,include_bmk=True, bmk_df=bmk_df,bmk_dict=bmk_dict,
                               include_eq=True,include_fi=True, mkt_df=mkt_df, mkt_key=mkt_key)
    
rsa_la = rsa.liquidAltsAnalytic(returns_df,include_bmk=True, bmk_df=bmk_df, bmk_dict=bmk_dict,
                               include_eq=True,include_fi=True, include_cm=True, include_fx=True,
                               mkt_df=mkt_df, mkt_key=mkt_key)


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

def get
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

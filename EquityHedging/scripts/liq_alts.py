# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 01:31:53 2022

@author: NVG9HXP
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
beta_m =  dm.get_equity_hedge_returns(equity='M1WD', include_fi=True)['Monthly'][['M1WD', 'FI Benchmark']]
liq_alts_m = dm.pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\new_constr.xlsx', index_col=0, sheet_name='data')
gm = dm.pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\new_constr.xlsx', index_col=0, sheet_name='gm')
caygan = dm.pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\caygan.xlsx', index_col=0, sheet_name='caygan')
caygan_p = dm.get_prices_df(caygan)
caygan_m = dm.format_data(caygan_p)
caygan_m = dm.merge_data_frames(beta_m,caygan_m, drop_na=False)
total = dm.merge_data_frames(caygan_m, liq_alts_m, drop_na=False)
sub = dm.merge_data_frames(caygan_m,gm, drop_na=False)
rp.get_alts_report('caygan_total_1', {'Monthly':total},include_fi=True)
rp.get_alts_report('caygan_gm_1', {'Monthly':sub},include_fi=True)
df_return_stats = summary.get_return_stats(sub)
df_returns = sub
df_returns = sub.copy()
df_prices = dm.get_prices_df(df_returns)
mkt = df_returns.columns[0]
if include_fi:
    fi = df_returns.columns[1]
include_fi=True
if include_fi:
    fi = df_returns.columns[1]
    
df_strat = df_returns[[mkt,col]].copy()
col = 'M1WD'
df_strat = df_returns[[mkt,col]].copy()
if include_fi:
    df_strat = df_returns[[mkt,fi,col]]
df_strat.dropna(inplace=True)
df_prices = dm.pd.DataFrame(dm.get_price_series(df_strat[col]))
df_prices = dm.get_price_series(df_strat[col])
return_series = df_strat[col].copy()
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots
df_prices = dm.get_prices_df(df_returns)
returns_stats_dict = {}
mkt_strat = df_returns[df_returns.columns[0]]
if include_fi:
    fi_mkt_strat = df_returns[df_returns.columns[1]]
df_strat = dm.remove_na(df_returns, col)
df_prices = dm.get_prices_df(df_strat)
ann_ret = get_ann_return(df_strat[col], freq)
alpha = get_alpha(df_strat[col],mkt_strat,freq,rfr)
beta = get_beta(df_strat[col],mkt_strat,freq)
if include_fi:
    alpha_fi = get_alpha(df_strat[col],fi_mkt_strat,freq,rfr)
    beta_fi = get_beta(df_strat[col],fi_mkt_strat,freq)
med_ret = df_strat[col].median()
avg_ret = df_strat[col].mean()
avg_up_ret = get_avg_pos_neg(df_strat[col])
avg_down_ret = get_avg_pos_neg(df_strat[col],False)
avg_pos_neg = get_avg_pos_neg_ratio(df_strat[col])
best_period = df_strat[col].max()
worst_period = df_strat[col].min()
pct_pos_periods = get_pct_pos_neg_periods(df_strat[col])
pct_neg_periods = get_pct_pos_neg_periods(df_strat[col], False)
ann_vol = get_ann_vol(df_strat[col], freq)
up_dev = get_updown_dev(df_strat[col], freq,up=True)
down_dev = get_updown_dev(df_strat[col], freq)
updev_downdev_ratio = get_up_down_dev_ratio(df_strat[col],freq)
skew = get_skew(df_strat[col])
kurt = get_kurtosis(df_strat[col])
max_dd = get_max_dd(df_prices[col])
ret_vol = get_ret_vol_ratio(df_strat[col],freq)
sortino = get_sortino_ratio(df_strat[col], freq)
ret_dd = get_ret_max_dd_ratio(df_strat[col],df_prices[col],freq)
returns_stats_dict[col] = [ann_ret, alpha, beta, med_ret, avg_ret, avg_up_ret, avg_down_ret,
                           avg_pos_neg, best_period, worst_period, pct_pos_periods,
                           pct_neg_periods, ann_vol, up_dev, down_dev, updev_downdev_ratio,
                           skew, kurt, max_dd,ret_vol,sortino, ret_dd]
if include_fi:
    returns_stats_dict[col] = [ann_ret, alpha, alpha_fi, beta, beta_fi, med_ret, avg_ret, avg_up_ret, avg_down_ret,
                               avg_pos_neg, best_period, worst_period, pct_pos_periods,
                               pct_neg_periods, ann_vol, up_dev, down_dev, updev_downdev_ratio,
                               skew, kurt, max_dd,ret_vol,sortino, ret_dd]
df_returns.columns
col = 'Caygan'
df_strat = dm.remove_na(df_returns, col)
df_prices = dm.get_prices_df(df_strat)
mkt = df_returns.columns[0]
if include_fi:
    fi_mkt = df_returns.columns[1]
mkt_list = [mkt]
mkt_list.append(fi_mkt)
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots
df_return_stats = summary.get_return_stats(sub)
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots
df_return_stats = summary.get_return_stats(sub)
mkt_list = [df_returns.columns[0]]
if include_fi:
    mkt_list.append(df_returns.columns[1])
df_strat = dm.remove_na(df_returns, col)
df_prices = dm.get_prices_df(df_strat)
temp_df = df_returns[mkt_list.append(col)]
mkt_list.append(col)
mkt_list = [df_returns.columns[0]]
if include_fi:
    mkt_list.append(df_returns.columns[1])
mkt_list.append(col)
mkt_list = [df_returns.columns[0]]
if include_fi:
    mkt_list.append(df_returns.columns[1])
    
temp_list = mkt_list.copy()
mkt_list+[col]
df_strat = dm.remove_na(df_returns, col)
df_prices = dm.get_prices_df(df_strat)
temp_df = df_returns[mkt_list + [col]]
t
df_strat = dm.remove_na(df_returns, col)
df_prices = dm.get_prices_df(df_strat)
temp_df = df_returns[mkt_list + [col]]
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
df_return_stats = summary.get_return_stats(sub)
temp_df.dropna(inplace=True)
mkt_strat = temp_df[mkt_list[0]]
df_prices = dm.get_prices_df(df_strat)
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
df_return_stats = summary.get_return_stats(sub)
df_strat = dm.remove_na(df_returns, col)
df_prices = dm.get_prices_df(df_strat)
temp_df = df_returns[mkt_list + [col]].copy()
temp_df.dropna(inplace=True)
mkt_strat = temp_df[mkt_list[0]]
fi_mkt_strat = temp_df[mkt_list[1]]


from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots
liq_ret = dm.transform_nexen_data('liq_alts\\Monthly Returns Liquid Alts.xls')
liq_ret.columns
LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A','Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital'],
                     'Trend Following': ['1907 ARP TF','1907 Campbell TF', '1907 Systematica TF',
                                         'One River Trend'],
                     'Absolute Return':['1907 ARP EM', '1907 CFM ISE Risk Premia', '1907 III CV', '1907 III Class A',
                                        '1907 Kepos RP', 'ABC Reversion','Acadian Commodity AR','Black Pearl RP',
                                        'Blueshift', 'Duality', 'Elliott'],
                     'Total Liquid Alts':['Global Macro', 'Trend Following', 'Absolute Return']}
LIQ_ALTS_MGR_DICT.keys()
LIQ_ALTS_MGR_DICT.keys().aslist()
list(LIQ_ALTS_MGR_DICT.keys())
lq_ret = lq_ret[list(LIQ_ALTS_MGR_DICT)]
bmks.columns
bmks = bmks[['M1WD', 'FI Benchmark', 'HFRX Macro/CTA Index', 'SG Trend Index',
       'HFRX Absolute Return Index', 'Liquid Alts Bmk']]
bmks = bmks[:-1]
bmks = dm.merge_data_frames(bmks, lq_ret, drop_na=False)
bmks.columns
bmks = bmks[['M1WD', 'FI Benchmark','Global Macro', 'HFRX Macro/CTA Index', 'Trend Following', 'SG Trend Index','Absolute Return','HFRX Absolute Return Index','Total Liquid Alts', 'Liquid Alts Bmk']]
bmks['Active Global Macro'] = bmks['Global Macro'] - bmks['HFRX Macro/CTA Index']
bmks['Active Trend Following'] = bmks['Trend Following'] - bmks['SG Trend Index']
bmks['Active Absolute Return'] = bmks['Absolute Return'] - bmks['HFRX Absolute Return Index']
bmks.columns
bmks = bmks[['M1WD', 'FI Benchmark','Global Macro', 'HFRX Macro/CTA Index','Active Global Macro', 'Trend Following', 'SG Trend Index','Active Trend Following','Absolute Return','HFRX Absolute Return Index','Active Absolute Return','Total Liquid Alts', 'Liquid Alts Bmk']]
bmks['Active Liquid Alts'] = bmks['Total Liquid Alts'] - bmks['Liquid Alts Bmk']
bmks = bmks[['M1WD', 'FI Benchmark','Global Macro', 'HFRX Macro/CTA Index','Active Global Macro', 'Trend Following', 'SG Trend Index','Active Trend Following','Absolute Return','HFRX Absolute Return Index','Active Absolute Return','Total Liquid Alts', 'Liquid Alts Bmk', 'Active Liquid Alts']]
rp.get_alts_report('liq_alts_full', {'Monthly':bmks},include_fi=True)
runfile('C:/Users/nvg9hxp/Documents/Projects/Return based analysis_python/returnAnalysis.py', wdir='C:/Users/nvg9hxp/Documents/Projects/Return based analysis_python')
files = np.array(['portfolio','selection'])
for a in files:
    globals()[a] = pd.read_excel(r"C:\Users\nvg9hxp\Documents\Projects\Return based analysis_python\%s.xlsx"%a, index_col=0)
selection = selection[['portfolio','benchmark','marketValue']].dropna(axis=0)
reset
runfile('C:/Users/nvg9hxp/Documents/Projects/Return based analysis_python/returnAnalysis.py', wdir='C:/Users/nvg9hxp/Documents/Projects/Return based analysis_python')

## ---(Thu Aug  4 21:36:34 2022)---
runfile('C:/Users/nvg9hxp/Documents/Projects/Return based analysis_python/returnAnalysis.py', wdir='C:/Users/nvg9hxp/Documents/Projects/Return based analysis_python')

maxx2 = pd.Series(dtype='float64')
beta_all.concat([beta_all]*(len(port)-1))

beta_m =  dm.get_equity_hedge_returns(equity='M1WD', include_fi=True)['Monthly'][['M1WD', 'FI Benchmark']]
welton = dm.get_new_strat_data('liq_alts\\welton.xlsx')
js_data = dm.get_new_strat_data('liq_alts\\Johns Street.xlsx')



for key in monthly_dict:
    rp.get_alts_report('johns_street_{}'.format(key), {'Monthly':monthly_dict[key]},include_fi=True)
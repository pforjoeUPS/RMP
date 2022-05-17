# -*- coding: utf-8 -*-
"""
Created on Sun May 15 21:50:52 2022

@author: nvg9hxp
"""

import pandas as pd
import numpy as np
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp


asset_df = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\Historical Returns.xls', sheet_name='Historical Returns')
asset_df.columns = ['Name', 'Account Id', 'Return Type', 'Date',
       'Market Value', 'Return']
asset_ret = asset_df.pivot_table(values='Return', index='Date', columns='Name')
asset_ret /= 100
eq_fi_df = asset_ret[['Total EQ w/o Derivatives', 'Total Fixed Income']]

report_name = 'asset_return_data'
file_path = rp.get_report_path(report_name)
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
rp.sheets.set_hist_return_sheet(writer,asset_ret, 'data')

bmk_df = pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\bmk_data.xlsx', sheet_name='data_m', index_col=0)
bmk_df = bmk_df[['LBUSTRUU Index', 'NDUEACWF Index', 'SPGSCITR Index', 'HFRXM Index','HFRIMI Index',
                 'SGSLRPEW Index', 'SGSLRPWH Index', 'SGIXTFXA Index', 'NEIXCTAT Index',
                 'HFRXAR Index', 'HFRXEH Index', 'HFRXEW Index', 'HFRXED Index',
                 'HFRXCA Index', 'HFRXEMC Index', 'HFRXCOM Index',
                 'SECTGLMA Index', 'SECTNEUT Index','SECTMSTR Index',
                 'HEDGGLMA Index', 'HEDGNAV Index','HEDGNEUT Index','HEDGCONV Index',
                 'CSLAB Index', 'CSLABED Index', 'CSLABGS Index']]
bmk_df.columns = ['US Agg Bond', 'MSCI ACWI TR','S&P GSCI TR', 'HFRX Macro/CTA', 'HFRI Macro Total Index',
                  'Eqty Risk Prem', 'Eqty Risk Prem-Hedged','SGI Cross Asset Trend', 'SG Trend Index',
                  'HFRX Abs Ret', 'HFRX Eqty Hedge', 'HFRX Equal Wgtd', 'HFRX Event Driven',
                  'HFRX RV FI Conv Arb', 'HFRX EM', 'HFRX Macro Comdty',
                  'CS AllHedge Global Macro', 'CS AllHedge Eqty Mkt Neutral','CS AllHedge Multi_Strat',
                  'CS Global Macro', 'CS Hedge Fund', 'CS Eqty Mkt Neutral', 'CS Conv Arb',
                 'CS Liq Alt Beta', 'CS Event Driven', 'CS Global Strat']
bmk_df = dm.format_data(bmk_df)

liq_alts_df = dm.get_real_cols(pd.read_excel(dm.RETURNS_DATA_FP + 'liq_alts\\mgr_data_m.xlsx', sheet_name='bny',index_col=0))
liq_alts_sp = liq_alts_df[['Total Liquid Alts',  'Global Macro',  'Trend Following','Alt Risk Premia']]
liq_alts_mgr = liq_alts_df[['1907 ARP EM', '1907 ARP TF', '1907 CFM ISE Risk Premia',
       '1907 Campbell TF', '1907 III CV', '1907 III Class A', '1907 Kepos RP',
       '1907 Penso Class A', '1907 Systematica TF', 'ABC Reversion',
       'Acadian Commodity AR', 'Black Pearl RP',
       'Blueshift', 'Bridgewater Alpha', 'DE Shaw Oculus Fund', 'Duality',
       'Element Capital', 'Elliott', 'One River Trend']]

#Multiple Linear Regression With scikit-learn
from sklearn.linear_model import LinearRegression
x = bmk_df.copy()
x = x.iloc[24:,]
x = x.to_numpy()

y = liq_alts_df[['Total Liquid Alts']].copy()
y.dropna(inplace=True)
y = np.array(list(y['Total Liquid Alts']))

model = LinearRegression().fit(x, y)
print('coefficient of determination:', model.score(x,y))
print('intercept:', model.intercept_)
print('slope:', model.coef_)

#Multiple Linear Regression With statsmodels
import statsmodels.api as sm
x = bmk_df.copy()
x = x.iloc[24:,]
x = x.to_numpy()

y = liq_alts_df[['Total Liquid Alts']].copy()
y.dropna(inplace=True)
y = np.array(list(y['Total Liquid Alts']))

x, y = np.array(x), np.array(y)
x = sm.add_constant(x)
print(x)
model = sm.OLS(y, x)
results = model.fit()
print(results.summary())
bmk_df.columns[9]

sp_results_dict = {}

for col in liq_alts_sp.columns:
    
    data = dm.merge_data_frames(liq_alts_sp[[col]].copy(),bmk_df)
    x = data[list(bmk_df.columns)].copy()
    x = x.to_numpy()
   
    y = data[[col]].copy()
    y.dropna(inplace=True)
    y = np.array(list(y[col]))
    
    x, y = np.array(x), np.array(y)
    x = sm.add_constant(x)
    
    model = sm.OLS(y, x)
    sp_results_dict[col] = model.fit()
    
selloffs = False
include_fi = True
rp.generate_strat_report('macro', {'Monthly': data}, selloffs, ['Monthly'],include_fi)
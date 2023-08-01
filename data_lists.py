# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 11:52:24 2023

@author: NVG9HXP
"""

BMK_COL_LIST = ['SPTR', 'SX5T', 'M1WD', 'MIMUAWON', 'Long Corp', 'STRIPS',
                    'HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']

FREQ_LIST = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']

#Risk
EQ_HEGDE_COL_LIST = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                     'Vortex', 'VOLA I', 'VOLA II','Dynamic VOLA','Dynamic Put Spread',
                     'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)',
                     'Def Var (Wed)', 'Commodity Basket']

EQ_HEDGE_STRAT_DICT = {'99%/90% Put Spread':0.0, 'Down Var':1.0, 'Vortex':0.0, 'VOLA':1.25,'Dynamic Put Spread':1.0,
                       'VRR':1.0, 'GW Dispersion':1.0, 'Corr Hedge':0.25,'Def Var':1.0}

#Liq Alts
HF_COL_LIST = ['HFRX Macro/CTA', 'SG Trend','HFRX Absolute Return','DM Equity',
               'EM Equity','Gov Bonds','Agg Bonds','EM Bonds','High Yield','BCOM',
               'S&P GSCI TR','Equity Volatility','EM FX','FX Carry','Commo Carry',
               'CTAs','HFRX Systematic Macro','HFRX Rel Val Arb','HFRX Global',
               'HFRX Eq Hedge','HFRX Event driven','HFRX Convert Arb','HFRX EM',
               'HFRX Commodities','HFRX RV']

LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A','Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital', 'JSC Vantage'],
                     'Trend Following': ['1907 ARP TF','1907 Campbell TF', '1907 Systematica TF',
                                         'One River Trend'],
                     'Absolute Return':['1907 ARP EM',  '1907 III CV', '1907 III Class A',
                                        'Acadian Commodity AR','Blueshift', 'Duality', 'Elliott']
                     }

#UPSGT


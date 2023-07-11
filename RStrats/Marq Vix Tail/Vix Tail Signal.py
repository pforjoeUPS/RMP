# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 09:16:03 2023

@author: Sam Park
"""

import pandas as pd
import numpy as np
import math as ma
from datetime import datetime as dt
from math import prod
from EquityHedging.analytics import summary 


#vix futures calendar
futures_calendar = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='vix_futures_calendar',names=['Dates'])
futures_calendar_dates = list(futures_calendar['Dates'])
underlying_data=pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='Inverted Curve z-score', usecols=['Date','VIX','Intraday VIX'])


#reading in data
dataF = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='Replicating Portfolio')
dataF = dataF.drop(columns=['dr', 'dt','1M Replicating', '2M Replicating', '3M Replicating', '4M Replicating'])
dataF.rename({"Unnamed: 20":"a"}, axis="columns", inplace=True)
dataF.drop(['a'], axis=1, inplace=True)
dataI = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='Intraday Replicating Portfolio')
dataI = dataI.drop(columns=['dr', 'dt','1M Replicating', '2M Replicating', '3M Replicating', '4M Replicating'])
dataI.rename({"Unnamed: 20":"a"}, axis="columns", inplace=True)
dataI.drop(['a'], axis=1, inplace=True)


#replicate futures/portfolio
def replicate_portfolio(data):
    timestamps=[]
    OneMRep=[]
    TwoMRep = []
    ThreeMRep = []
    FourMRep = []
    for index, row in data.iterrows():
        timestamps.append(row['Date'])
        x = futures_calendar_dates.index(row['Front Contract Exp']) - futures_calendar_dates.index(row['Date'])
        y = futures_calendar_dates.index(row['Front Contract Exp']) - futures_calendar_dates.index(row['Prev Contract Exp'])
        z = x/y
        if x == y:
            OneMRep.append(row['Front Price'])
            TwoMRep.append(row['Second Price'])
            ThreeMRep.append(row['Third Price'])
            FourMRep.append(row['Fourth Price'])
        else:
            OneMRep.append((z*row['Front Price'])+((1-z)*row['Second Price']))
            TwoMRep.append((z*row['Second Price'])+((1-z)*row['Third Price']))        
            ThreeMRep.append((z*row['Third Price'])+((1-z)*row['Fourth Price']))    
            FourMRep.append((z*row['Fourth Price'])+((1-z)*row['Fifth Price']))    
            
    replicated_data = {'1M Replicating': OneMRep, '2M Replicating': TwoMRep, '3M Replicating': ThreeMRep, '4M Replicating': FourMRep}
    Portfolio = pd.DataFrame(replicated_data, index=timestamps)
    
    return Portfolio

rep_port = replicate_portfolio(dataF)
rep_intra_port = replicate_portfolio(dataI)

#calculating inverted z score (ratio z)
def calculating_ratio_z (data):
    inverted_z = []
    timestamps=[]
    prev_rolling_mean = 0
    prev_debiasing_factor = 0
    prev_rolling_vol = 0
    
    rolling_mean = 0
    rolling_var = 0
    debiasing_factor = 1
    rolling_vol = 0
    
    intraday_rolling_mean = 0
    intraday_rolling_vol = 0
    
    z_score_lambda = ma.exp(-2/364)
    
    for index, row in underlying_data.iterrows():
        
        timestamps.append(row['Date'])
        VixD1M = row['VIX'] / rep_port.loc[str(row['Date'])]['1M Replicating']
        Intraday_VixD1M = row['Intraday VIX'] / rep_intra_port.loc[str(row['Date'])]['1M Replicating']
        
        if prev_rolling_mean != 0:
            #for close prices
            prev_rolling_mean = rolling_mean
            rolling_mean = prev_rolling_mean*z_score_lambda + (1-z_score_lambda)*VixD1M
            rolling_var = z_score_lambda*((rolling_var)+(prev_rolling_mean-rolling_mean)**2)+((1-z_score_lambda)*(VixD1M-rolling_mean)**2)
            prev_debiasing_factor = debiasing_factor
            debiasing_factor = prev_debiasing_factor*z_score_lambda**2 + (1-z_score_lambda)**2
            
            prev_rolling_vol = rolling_vol
            rolling_vol = ma.sqrt((rolling_var/(1-debiasing_factor)))
            
            #for snap prices
            intraday_rolling_mean = prev_rolling_mean*z_score_lambda + (1-z_score_lambda)*Intraday_VixD1M
            intraday_rolling_vol = ((prev_rolling_vol**2+(prev_rolling_mean-intraday_rolling_mean)**2)*z_score_lambda + (1-z_score_lambda)*(Intraday_VixD1M-intraday_rolling_mean)**2)**0.5
                 
        else:
            prev_rolling_mean = VixD1M
            rolling_mean = prev_rolling_mean*z_score_lambda + (1-z_score_lambda)*VixD1M
            rolling_var = (VixD1M-rolling_mean)**2
            
        #calculating z-score
        z_score = (Intraday_VixD1M-intraday_rolling_mean)/intraday_rolling_vol
        
        inverted_z.append(z_score)
        data = {'inverted_z_score': inverted_z}
        inverted_z_scores = pd.DataFrame(data, index=timestamps)
        
    return inverted_z_scores

VIXtoVIXFutures_z = calculating_ratio_z(underlying_data)

#calculating differnce between Imp(vix) and Hist(SPX) Vol z score








        



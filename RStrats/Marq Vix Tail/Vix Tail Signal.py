# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 09:16:03 2023

@author: Sam Park
"""

import pandas as pd
import math as ma
from datetime import datetime
from EquityHedging.datamanager import data_manager as dm


#vix futures calendar
futures_calendar = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='vix_futures_calendar',names=['Dates'])
futures_calendar_dates = list(futures_calendar['Dates'])
fc = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='futures', index_col=(0))
underlier_lambda = ma.exp(-2/27)
z_score_lambda = ma.exp(-2/364)


#reading in data
dataF = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='Replicating Portfolio')
dataF = dataF.drop(columns=['dr', 'dt','1M Replicating', '2M Replicating', '3M Replicating', '4M Replicating'])
dataF.drop(columns=['Unnamed: 20'], inplace=True)
dataI = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='Intraday Replicating Portfolio')
dataI = dataI.drop(columns=['dr', 'dt','1M Replicating', '2M Replicating', '3M Replicating', '4M Replicating'])
dataI.drop(columns=['Unnamed: 20'], inplace=True)


# replicate futures/portfolio
def replicate_portfolio(data):
    timestamps = data['Date'].tolist()
    OneMRep = []
    TwoMRep = []
    ThreeMRep = []
    FourMRep = []
    
    for _, row in data.iterrows():
        x = futures_calendar_dates.index(row['Front Contract Exp']) - futures_calendar_dates.index(row['Date'])
        y = futures_calendar_dates.index(row['Front Contract Exp']) - futures_calendar_dates.index(row['Prev Contract Exp'])
        z = x / y
        
        if x == y:
            OneMRep.append(row['Front Price'])
            TwoMRep.append(row['Second Price'])
            ThreeMRep.append(row['Third Price'])
            FourMRep.append(row['Fourth Price'])
        else:
            OneMRep.append((z * row['Front Price']) + ((1 - z) * row['Second Price']))
            TwoMRep.append((z * row['Second Price']) + ((1 - z) * row['Third Price']))
            ThreeMRep.append((z * row['Third Price']) + ((1 - z) * row['Fourth Price']))
            FourMRep.append((z * row['Fourth Price']) + ((1 - z) * row['Fifth Price']))
            
    replicated_data = {
        '1M Replicating': OneMRep,
        '2M Replicating': TwoMRep,
        '3M Replicating': ThreeMRep,
        '4M Replicating': FourMRep
    }
    
    Portfolio = pd.DataFrame(replicated_data, index=timestamps)
    return Portfolio

def VIX_Futures_Calendar_Day_weights(data):
    timestamps = []
    fut_cal_weights = []
    for _, row in data.iterrows():
        timestamps.append(row['Date'])
        x = futures_calendar_dates.index(row['Front Contract Exp']) - futures_calendar_dates.index(row['Date'])
        y = futures_calendar_dates.index(row['Front Contract Exp']) - futures_calendar_dates.index(row['Prev Contract Exp'])
        fut_cal_weights.append(x/y)  
    weights = pd.DataFrame(fut_cal_weights, index=timestamps)
        
    return weights
test = VIX_Futures_Calendar_Day_weights(dataF)
x = replicate_portfolio(dataF)

underlying_data_inv = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='Inverted Curve z-score', usecols=['Date','VIX','Intraday VIX'])
#calculating inverted z score (ratio z)
def calculating_ratio_z(data, rep_port, rep_intra_port, z_score_lambda):
    inverted_z = []
    timestamps = []
    rolling_mean = 0
    rolling_var = 0
    debiasing_factor = 1
    rolling_vol = 0
    intraday_rolling_mean = 0
    intraday_rolling_vol = 0

    for index, row in underlying_data_inv.iterrows():
        timestamps.append(row['Date'])
        VixD1M = row['VIX'] / rep_port.loc[str(row['Date'])]['1M Replicating']
        Intraday_VixD1M = row['Intraday VIX'] / rep_intra_port.loc[str(row['Date'])]['1M Replicating']

        if rolling_mean != 0:
            #for close prices
            prev_rolling_mean = rolling_mean
            rolling_mean = prev_rolling_mean * z_score_lambda + (1 - z_score_lambda) * VixD1M
            rolling_var = z_score_lambda * (rolling_var + (prev_rolling_mean - rolling_mean) ** 2) + (
                        1 - z_score_lambda) * (VixD1M - rolling_mean) ** 2
            prev_debiasing_factor = debiasing_factor
            debiasing_factor = prev_debiasing_factor * z_score_lambda ** 2 + (1 - z_score_lambda) ** 2
            prev_rolling_vol = rolling_vol
            rolling_vol = ma.sqrt(rolling_var / (1 - debiasing_factor))
            
            #for snap prices
            intraday_rolling_mean = prev_rolling_mean * z_score_lambda + (1 - z_score_lambda) * Intraday_VixD1M
            intraday_rolling_vol = ma.sqrt(
                (prev_rolling_vol ** 2 + (prev_rolling_mean - intraday_rolling_mean) ** 2) * z_score_lambda + (
                            1 - z_score_lambda) * (Intraday_VixD1M - intraday_rolling_mean) ** 2)

        else:
            rolling_mean = VixD1M
            rolling_var = (VixD1M - rolling_mean) ** 2

        z_score = (Intraday_VixD1M - intraday_rolling_mean) / intraday_rolling_vol
        inverted_z.append(z_score)

    inverted_z_scores = pd.DataFrame({'inverted_z_score': inverted_z}, index=timestamps)
    return inverted_z_scores

VIXtoVIXFutures_z = calculating_ratio_z(underlying_data_inv, replicate_portfolio(dataF), replicate_portfolio(dataI), z_score_lambda)


underlying_data_SPX_VIX = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\Construct Vix Strategies.xlsx', sheet_name='Hist vs Imp Vol z score', usecols=['Date','SPX','VIX','Intraday SPX','Intraday VIX'])
#calculating differnce between Imp(vix) and Hist(SPX) Vol z score
def calculating_diff_z_score(data,underlier_lambda,z_score_lambda):
    diff_z = []
    timestamps = []
    prev_spx = underlying_data_SPX_VIX['SPX'][0]
    prev_iSPX = underlying_data_SPX_VIX['Intraday SPX'][0]
    skip_first = True
    
    prev_ret_roll_mean = prev_ret_roll_var = prev_hist_vol = 0
    ret_roll_mean = ret_roll_var = hist_vol = 0
    u_debiasing_factor = 1
    
    prev_diff_roll_mean = prev_diff_roll_var = prev_diff_roll_stdev = 0
    diff = diff_roll_mean = diff_roll_var = diff_roll_stdev = 0
    z_debiasing_factor = 1
    
    iret_roll_mean = ihist_vol = 0
    
    idiff = idiff_roll_mean = idiff_roll_stdev = 0
    
    for index, row in underlying_data_SPX_VIX.iterrows():
        
        timestamps.append(row['Date'])
        
        if skip_first:
            skip_first = False
            continue
        elif prev_ret_roll_mean == 0 and prev_spx == row['SPX']:
            daily_ret = (row['SPX'] / prev_spx) - 1
            ret_roll_mean = daily_ret
            ret_roll_var = (daily_ret - ret_roll_mean) ** 2
            prev_spx = row['SPX']
            
            intrdaily_ret = (row['Intraday SPX'] / prev_iSPX) - 1
            iret_roll_mean = intrdaily_ret
            prev_iSPX = row['Intraday SPX']

        else:
            daily_ret = (row['SPX'] / prev_spx) - 1
            ret_roll_mean = underlier_lambda * prev_ret_roll_mean + (1-underlier_lambda) * daily_ret
            ret_roll_var = underlier_lambda * (prev_ret_roll_var + (ret_roll_mean - prev_ret_roll_mean) ** 2) \
                            + (1 - underlier_lambda) * (daily_ret-ret_roll_mean) ** 2
            u_debiasing_factor = u_debiasing_factor * underlier_lambda ** 2 + (1 - underlier_lambda) ** 2
            hist_vol = ((ret_roll_var / (1 - u_debiasing_factor)) ** 0.5) * (252 ** 0.5) * 100
            
            intrdaily_ret = (row['Intraday SPX'] / prev_spx) - 1
            iret_roll_mean = underlier_lambda * prev_ret_roll_mean + (1 - underlier_lambda) * intrdaily_ret
            if hist_vol < 0:    
                pass
            else:
                ihist_vol =(((prev_hist_vol / (100 * 252 ** 0.5)) ** 2 + (prev_ret_roll_mean-iret_roll_mean) ** 2) \
                            * underlier_lambda + (1 - underlier_lambda) * (intrdaily_ret - iret_roll_mean) ** 2) ** \
                            0.5 * 252 ** 0.5 * 100
            #return
            prev_spx = row['SPX']        
            prev_ret_roll_mean = ret_roll_mean
            prev_ret_roll_var = ret_roll_var
            prev_iSPX = row['Intraday SPX']
            prev_hist_vol = hist_vol
    
            diff = hist_vol - row['VIX']
            idiff = ihist_vol - row['Intraday VIX']
            if prev_diff_roll_mean == 0:
                diff_roll_mean = diff
                diff_roll_var = (diff - diff_roll_mean)**2
                prev_diff_roll_mean = ret_roll_mean
                prev_diff_roll_var = ret_roll_var

                idiff_roll_mean = idiff

                prev_diff_roll_mean = ret_roll_mean
                prev_diff_roll_var = ret_roll_var
            else:
                diff_roll_mean = z_score_lambda*prev_diff_roll_mean + (1-z_score_lambda)*diff
                diff_roll_var = z_score_lambda*(prev_diff_roll_var+(diff_roll_mean-prev_diff_roll_mean)**2) + \
                            (1-z_score_lambda)*(diff-diff_roll_mean)**2
                z_debiasing_factor = z_debiasing_factor*z_score_lambda**2 + (1-z_score_lambda)**2
                diff_roll_stdev = ma.sqrt(diff_roll_var/(1-z_debiasing_factor))
                
                idiff_roll_mean = prev_diff_roll_mean*z_score_lambda+(1-z_score_lambda)*idiff
                idiff_roll_stdev =((prev_diff_roll_stdev**2+(prev_diff_roll_mean-idiff_roll_mean)**2)*z_score_lambda \
                                   + (1-z_score_lambda)*(idiff-idiff_roll_mean)**2)**0.5
                
                prev_diff_roll_mean = diff_roll_mean
                prev_diff_roll_var = diff_roll_var
                prev_diff_roll_stdev = diff_roll_stdev
                
        z_score = (idiff-idiff_roll_mean)/idiff_roll_stdev
        diff_z.append(z_score)
    del timestamps[:4]
    del diff_z[:3]
    hist_imp_z_scores = pd.DataFrame({'diff_z_score': diff_z}, index=timestamps)
    return hist_imp_z_scores


diff_z_score = calculating_diff_z_score(underlying_data_SPX_VIX,underlier_lambda,z_score_lambda)

def calculating_combined_signals (inverted_z, diff_z):
    comb = dm.merge_data_frames(VIXtoVIXFutures_z, diff_z_score)
    combined_signal = []
    for index, row in comb.iterrows():
        comb_z = 0.5*row['inverted_z_score'] + 0.5*row['diff_z_score']
        combined_signal.append(comb_z)
    comb['Signal'] = combined_signal
    comb = comb.drop(columns = ['inverted_z_score', 'diff_z_score'])
    return comb

#Nextsteps:
    #Make code more dynamic by beging able to do adjusted z-scores, change signal weights g_(num)
    #Calculate cost/returns and create index
combined_signals = calculating_combined_signals(VIXtoVIXFutures_z, diff_z_score)


#when futures had four continous contracts
Y = datetime.strptime('2006-10-31 00:00:00', '%Y-%m-%d %H:%M:%S')
#when VMARTRHG index began
start_date = datetime.strptime('2007-01-03 00:00:00', '%Y-%m-%d %H:%M:%S')
rows_to_delete = combined_signals.index.get_loc(start_date)
combined_signals = combined_signals.iloc[rows_to_delete:]

vix_close_1d = pd.read_excel('C:\\Users\\PCR7FJW\\Desktop\\SPX and VIX.xlsx', sheet_name='Sheet1',names=['VIX'])





#Calculates weights for dR/dT
timestamps = []
z_weights = []
for _, row in dataF.iterrows():
    timestamps.append(row['Date'])
    x = futures_calendar_dates.index(row['Front Contract Exp']) - futures_calendar_dates.index(row['Date'])
    y = futures_calendar_dates.index(row['Front Contract Exp']) - futures_calendar_dates.index(row['Prev Contract Exp'])
    z = x / y
    z_weights.append(z)
    dr_dt_weights = pd.DataFrame({'dr/dt': z_weights}, index=timestamps)

    
g_1 = 0.5
g_2 = g_1 + 1/6
g_3 = g_2 + 1/6
g_4 = g_3 + 1/6

minvolcharge = 0.025
slope = 0.05
basevol = 20


index_price = 100
skip_first = True  


for index, row in combined_signals.iterrows():
    for i in range(1,7):
        next_futures_date = index + pd.Timedelta(days=i)
        if next_futures_date in combined_signals.index:
            dr_dt = dr_dt_weights.loc[next_futures_date, 'dr/dt']
            break

    if skip_first:
        skip_first = False
        prev_date_index = index
        prev_turnover = 0
        continue
    else:
        thrM_w = (max(0, min(1/3, (1/3)*((row['Signal']-g_1)/(g_2 - g_1)))))
        twoM_w = (max(0, min(1/3, (1/3)*((row['Signal']-g_2)/(g_3 - g_2)))))
        oneM_w = (max(0, min(1/3, (1/3)*((row['Signal']-g_3)/(g_4 - g_3)))))
        
        prev_col_index = fc.loc[prev_date_index].first_valid_index()
        col_index = fc.loc[index].first_valid_index()
        col_index_2 = fc.columns.get_loc(col_index) + 1
        col_index_fir, col_index_sec, col_index_thi, col_index_fou = col_index, fc.columns[col_index_2], \
                    fc.columns[col_index_2 + 1], fc.columns[col_index_2 + 2]
            
        fir_Price_Diff = fc.loc[index,col_index_fir] - fc.loc[prev_date_index,col_index_fir]
        sec_Price_Diff = fc.loc[index,col_index_sec] - fc.loc[prev_date_index,col_index_sec]
        thi_Price_Diff = fc.loc[index,col_index_thi] - fc.loc[prev_date_index,col_index_thi]
        fou_Price_Diff = fc.loc[index,col_index_fou] - fc.loc[prev_date_index,col_index_fou]
        
        
        fro_weight = oneM_w * dr_dt
        sec_weight = oneM_w * (1 - dr_dt) + twoM_w * (dr_dt)
        thi_weight = twoM_w * (1 - dr_dt) + thrM_w * (dr_dt)
        fou_weight = thrM_w * (1 - dr_dt)
    
        fro_Unit = fro_weight * (index_price / fc.loc[prev_date_index,col_index_fir])
        sec_Unit = sec_weight * (index_price / fc.loc[prev_date_index,col_index_sec])
        thi_Unit = thi_weight * (index_price / fc.loc[prev_date_index,col_index_thi])
        fou_Unit = fou_weight * (index_price / fc.loc[prev_date_index,col_index_fou])
        
        prev_fro_Unit, prev_sec_Unit, prev_thi_Unit, prev_fou_Unit = fro_Unit, sec_Unit, thi_Unit, fou_Unit
        
                
        if col_index == prev_col_index:
            turnover = abs(fro_Unit - prev_fro_Unit)* fc.loc[prev_date_index, col_index_fir] + \
                       abs(sec_Unit - prev_sec_Unit)* fc.loc[prev_date_index, col_index_sec] + \
                       abs(thi_Unit - prev_thi_Unit)* fc.loc[prev_date_index, col_index_thi] + \
                       abs(fou_Unit - prev_fou_Unit)* fc.loc[prev_date_index, col_index_fou]
        else:
            turnover = abs(prev_fro_Unit)*fc.loc[prev_date_index, col_index_fir] + \
                       abs(fro_Unit - prev_sec_Unit)*fc.loc[prev_date_index, col_index_sec] + \
                       abs(sec_Unit - prev_thi_Unit)*fc.loc[prev_date_index, col_index_thi] + \
                       abs(thi_Unit - prev_fou_Unit)*fc.loc[prev_date_index, col_index_fou]
        
        vol_charge = minvolcharge + slope * max(vix_close_1d.loc[prev_date_index, 'VIX']/basevol-1,0)
        cost = (max(prev_turnover*(vol_charge/vix_close_1d.loc[prev_date_index, 'VIX']), prev_turnover*(max(vix_close_1d.loc[prev_date_index, 'VIX'],20)/10000)))

        prev_date_index = index
        prev_turnover = turnover


    index_price = index_price + (fro_Unit*fir_Price_Diff) + (sec_Unit*sec_Price_Diff) + \
        (thi_Unit*thi_Price_Diff) + (fou_Unit*fou_Price_Diff) - cost
        
    print(index_price)
    
    








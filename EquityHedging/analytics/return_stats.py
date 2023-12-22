# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 21:23:33 2022

@author: NVG9HXP
"""

from ..datamanager import data_manager as dm
from EquityHedging.analytics import  util
from .import  returns_stats as rs
from .import  rolling_stats as roll
from .import  drawdowns as dd
from .import  corr_stats as cs

import pandas as pd
from itertools import compress
# global 

ACTIVE_COL_DICT = {'bmk_name':'Bmk Name',' bmk_beta':'Bmk Beta','excess_ret':'Excess Return (Ann)',
                   'te':'Tracking Error (TE)', 'dwnside_te':'Downside TE','te_dwnside_te':'TE to Downside TE Ratio', 'ir':'Informatio Ratio (IR)', 'ir_asym':'Asymmetric IR'}

PORT_COL_DICT = {'ann_ret':'Annualized Return', 'median_ret':'Median Period Return','avg_ret':'Avg. Period Return',
                 'avg_pos_ret':'Avg. Period Up Return', 'avg_neg_ret':'Avg. Period Down Return', 'avg_pos_neg_ret':'Avg Pos Return/Avg Neg Return', 
                 'best_period':'Best Period','worst_period': 'Worst Period', 'pct_pos_periods':'% Positive Periods',
                 'pct_neg_periods':'% Negative Periods', 'ann_vol':'Annualized Volatility','up_dev':'Upside Deviation',
                 'down_dev':'Downside Deviation','up_down_dev':'Upside to Downside Deviation Ratio','vol_down_dev':'Vol to Downside Deviation Ratio', 
                 'skew':'Skewness','kurt':'Kurtosis','max_dd':'Max DD', 'ret_vol':'Return/Volatility', 'sortino':'Sortino Ratio', 'ret_dd':'Return/Max DD'}

MKT_COL_DICT = {'asset_id':{'Equity': 'EQ', 'Fixed Income':'FI','Commodities':'CM', 'FX':'FX'}, 
                'analytics': {'alpha':'Alpha', 'beta':'Beta', 'up_beta':'Upside Beta', 'dwn_beta':'Downside Beta',
                              'corr': 'Correlation', 'up_corr':'Upside Correlation', 'dwn_corr':'Downside Correlation'}
                }

def get_time_frame(returns_df):
    start = []
    end = []
    for i in range (len(returns_df.columns)):
        sta = returns_df.iloc[:,i].first_valid_index()
        en = returns_df.iloc[:,i].last_valid_index()
        start.append(sta)
        end.append(en)
    
    period = []
    for i in range (len(start)):
        per = start[i].strftime('%m/%d/%Y')+'-'+end[i].strftime('%m/%d/%Y')
        period.append(per)
    period = pd.Series(period,index=returns_df.columns)
    return period

def add_mkt_data(mkt_df,mkt_key, asset_class):
    return mkt_df[[mkt_key[asset_class]]]

class returnsAnalytic():
    def __init__(self,returns_df, freq='1M', rfr = 0.0, target = 0.0,
                 include_bmk = False, bmk_df = dm.pd.DataFrame(), bmk_dict={},
                 include_eq = True,include_fi=False,mkt_df=pd.DataFrame(), mkt_key={}):
        
        self.returns_df = returns_df
        self.period = get_time_frame(self.returns_df)
        self.freq = freq
        self.freq_int = dm.switch_freq_int(self.freq)
        self.freq_string = dm.switch_freq_string(self.freq)
        self.rfr = rfr
        self.target = target
        self.include_bmk = include_bmk
        self.bmk_df = bmk_df
        self.bmk_dict = bmk_dict
        self.include_eq = include_eq
        self.include_fi = include_fi
        self.mkt_bool_dict = self.get_mkt_bool_data()
        self.mkt_key = mkt_key
        self.mkt_ret_data = self.get_mkt_ret_data(mkt_df)
        
        self.dd_data = self.get_dd_data()
        self.corr_data = self.get_corr_data()
        self.mkt_stats_data = None if self.mkt_ret_data.empty else self.get_mkt_stats()
        self.returns_stats_data = self.get_returns_stats()
        self.roll_data = None
        
    def get_roll_stats(self, years):
        self.roll_stats_data = roll.get_rolling_data(self.returns_df, years, self.freq, self.rfr,
                                                     self.include_bmk, self.bmk_df, self.bmk_dict,
                                                     any(self.mkt_bool_dict.values()), self.mkt_ret_data)
        
    def get_mkt_bool_data(self):
        return {'Equity':self.include_eq, 'Fixed Income':self.include_fi}
    
    def get_mkt_ret_data(self, mkt_df):
        mkt_ret_df = pd.DataFrame(index=mkt_df.index)
        for asset_class in self.mkt_bool_dict:
            if self.mkt_bool_dict[asset_class]:
                try:
                    mkt_ret_df = dm.merge_data_frames(mkt_ret_df, add_mkt_data(mkt_df, self.mkt_key, asset_class))
                except KeyError:
                    self.mkt_bool_dict[asset_class] = False
                    pass
        mkt_ret_df.columns = list(compress(list(self.mkt_bool_dict.keys()), list(self.mkt_bool_dict.values())))
        return mkt_ret_df
    
    def get_dd_data(self):
        print('Computing Drawdown analytics...')
        if self.mkt_ret_data.empty:
            return {'dd_matrix':dd.get_dd_matrix(self.returns_df),
                    'co_dd_dict': dd.get_co_drawdown_data(self.returns_df),
                    'dd_dict': dd.get_drawdown_data(self.returns_df, recovery=True)
                    }
        else:
            return {'dd_matrix':dd.get_dd_matrix(dm.merge_data_frames(self.mkt_ret_data,self.returns_df, False)),
                    'mkt_co_dd_dict': dd.get_co_drawdown_data(self.mkt_ret_data, self.returns_df),
                    'co_dd_dict': dd.get_co_drawdown_data(self.returns_df),
                    'dd_dict': dd.get_drawdown_data(self.returns_df, recovery=True)
                    }
        
    def get_corr_data(self):
        print('Computing Correlation analytics...')
        corr_dict = cs.get_corr_analysis1(self.returns_df)
        if not self.mkt_ret_data.empty:
            corr_df = dm.merge_data_frames(self.mkt_ret_data, self.returns_df)
            for asset_class in self.mkt_bool_dict:
                if self.mkt_bool_dict[asset_class]:
                    corr_dict[asset_class] = cs.get_conditional_corr(corr_df, asset_class)
        return corr_dict
    
    def get_mkt_index_list(self):
        mkt_list = []
        for asset_class in self.mkt_bool_dict:
            mkt_list = mkt_list + [MKT_COL_DICT['asset_id'][asset_class] + ' ' + value for value in list(MKT_COL_DICT['analytics'].values())]
        return mkt_list
    
    def get_mkt_stats(self):
        print('Computing Market analytics...')
        mkt_stats_dict = {}
        for strat in self.returns_df:
            return_series = self.returns_df[strat]
            mkt_ret_df = dm.merge_data_frames(self.mkt_ret_data, return_series)
            
            mkt_analytics = {}
            for asset_class in self.mkt_bool_dict:
                if self.mkt_bool_dict[asset_class]:
                    mkt_analytics[asset_class] = rs.get_mkt_analytics(mkt_ret_df, self.mkt_key[asset_class], strat, self.freq, self.rfr)
                else:
                    mkt_analytics[asset_class] = rs.get_mkt_analytics(mkt_ret_df, self.mkt_key[asset_class], strat, empty=True)
            
            mkt_stats_dict[strat] = rs.get_mkt_analytics_list(mkt_analytics)
            
        df_mkt_stats = util.convert_dict_to_df(mkt_stats_dict, self.get_mkt_index_list())
        
        for asset_class in self.mkt_bool_dict:
            if not self.mkt_bool_dict[asset_class]:
                try:
                    droplist = [asset_class + ' ' + value for value in list(MKT_COL_DICT['analytics'].values())]
                    df_mkt_stats.drop(droplist, inplace = True)
                except KeyError:
                    pass
        return df_mkt_stats
    
    def get_returns_stats(self, drop_active=False):
        print('Computing Returns analytics...')
        returns_stats_dict = {}
        for strat in self.returns_df:
            return_series = self.returns_df[strat]
            time_frame = self.period[strat]
            obs = len(return_series)
            
            port_analytics = rs.get_port_analytics(return_series, self.freq)
        
            if self.include_bmk:
                try:
                    bmk_series = self.bmk_df[self.bmk_dict[strat]]
                    active_analytics = rs.get_active_analytics(return_series, bmk_series, self.freq)
                except KeyError:
                    active_analytics = rs.get_active_analytics(return_series, empty=True)
            else:
                active_analytics = rs.get_active_analytics(return_series, empty=True)
            
            returns_stats_dict[strat] = [*list(active_analytics.values())[0:1], *[time_frame, obs], *list(port_analytics.values()),
                                         *list(active_analytics.values())[1:]]
            
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, 
                                                   [*list(ACTIVE_COL_DICT.values())[0:1], *['Time Frame',f'No. of {self.freq_string} Observations'], 
                                                    *list(PORT_COL_DICT.values()), *list(ACTIVE_COL_DICT.values())[1:]])
        
        if not self.include_bmk:
            df_returns_stats.drop(list(ACTIVE_COL_DICT.values()), inplace = True)
        if drop_active:
            try:
                df_returns_stats.drop(list(ACTIVE_COL_DICT.values()), inplace = True)
            except KeyError:
                pass
        return df_returns_stats


class liquidAltsAnalytic(returnsAnalytic):
    def __init__(self,returns_df, freq='1M',rfr = 0.0, target = 0.0,
                 include_bmk = False, bmk_df = dm.pd.DataFrame(), bmk_dict={},
                 include_eq = True,include_fi=False, include_cm=False, include_fx=False,
                 mkt_df=pd.DataFrame(), mkt_key={}):
        
        self.include_cm = include_cm
        self.include_fx = include_fx
        
        super().__init__(returns_df, freq, rfr, target, include_bmk, bmk_df, bmk_dict, 
                         include_eq, include_fi, mkt_df, mkt_key)
        
    def get_mkt_bool_data(self):
        return {'Equity':self.include_eq, 'Fixed Income':self.include_fi,
                'Commodities':self.include_cm, 'FX':self.include_fx}

class eqHedgeAnalytic(returnsAnalytic):
    def __init__(self,returns_df, freq='1M',rfr = 0.0, target = 0.0,
                 include_bmk = False, bmk_df = dm.pd.DataFrame(), bmk_dict={},
                 include_eq = True,include_fi=False, 
                 mkt_df=pd.DataFrame(), mkt_key={}):
              
        super().__init__(returns_df, freq, rfr, target, include_bmk, bmk_df, bmk_dict, 
                         include_eq, include_fi, mkt_df, mkt_key)
        self.hedge_metrics_data = self.get_hedge_metrics()

    def get_hedge_metrics(self):
        pass
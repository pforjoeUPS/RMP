# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 21:23:33 2022

@author: NVG9HXP
"""

import numpy as np
from ..datamanager import data_manager as dm
from EquityHedging.analytics import  util


RETURNS_STATS_INDEX = ['Annualized Ret','Annualized Vol','Ret/Vol', 
                       'Max DD','Ret/Max DD',
                       'Max 1M DD','Max 1M DD Date', 'Ret/Max 1M DD',
                       'Max 3M DD','Max 3M DD Date','Ret/Max 3M DD',
                       'Skew','Avg Pos Ret/Avg Neg Ret',
                       'Downside Deviation','Sortino Ratio']

def get_ann_return(return_series, freq='1M'):
    """
    Return annualized return for a return series.

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    double
        Annualized return.

    """
    #compute the annualized return
    d = len(return_series)
    return return_series.add(1).prod()**(dm.switch_freq_int(freq)/d)-1

def get_ann_vol(return_series, freq='1M'):
    """
    Return annualized volatility for a return series.

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    double
        Annualized volatility.

    """
    #compute the annualized volatility
    return np.std(return_series, ddof=1)*np.sqrt(dm.switch_freq_int(freq))

def get_return_stats(df_returns, freq='1M'):
    """
    Return a dict of return analytics

    Parameters
    ----------
    df_returns : dataframe
        returns dataframe.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    df_returns_stats : dataframe

    """
    
    #generate return stats for each strategy
    ret_stats_dict = {}
    for col in df_returns.columns:
        rs = returnStats(df_returns[col])
        
        ret_stats_dict[col] = [rs.ann_ret, rs.ann_vol, rs.ret_vol, rs.max_dd, rs.ret_dd,
                               rs.max_1m_dd, rs.max_1m_dd_date, rs.ret_1m_dd,
                               rs.max_3m_dd, rs.max_3m_dd_date, rs.ret_3m_dd,
                               rs.skew, rs.avg_pos_neg, rs.down_dev, rs.sortino]
        
    #Converts ret_stats_dict to a data grame
    df_ret_stats = util.convert_dict_to_df(ret_stats_dict, RETURNS_STATS_INDEX)
    return df_ret_stats
    
class returnStats():
    
    def __init__(self,return_series, freq='1M', rfr = 0.0, target = 0.0):
        """
        

        Parameters
        ----------
        return_series : TYPE
            DESCRIPTION.
        freq : TYPE, optional
            DESCRIPTION. The default is '1M'.
        rfr : TYPE, optional
            DESCRIPTION. The default is 0.0.
        target : TYPE, optional
            DESCRIPTION. The default is 0.0.

        Returns
        -------
        None.

        """
        self.return_series = return_series
        self.price_series = dm.get_price_series(self.return_series)
        self.freq = freq
        self.freq_int = dm.switch_freq_int(self.freq)
        self.rfr = rfr
        self.target = target
        
        self.ann_ret = get_ann_return(self.return_series, self.freq)
        self.ann_vol = self.get_ann_vol(self.return_series, self.freq)
        self.ret_vol = self.ann_ret / self.ann_vol
        self.max_dd = self.get_max_dd()
        self.ret_dd = self.ann_ret / abs(self.max_dd)
        self.max_1m_dd = self.get_max_dd_freq()['max_dd']
        self.max_1m_dd_date = self.get_max_dd_freq()['index']
        self.ret_1m_dd = self.ann_ret / abs(self.max_1m_dd)
        self.max_3m_dd = self.get_max_dd_freq(True)['max_dd']
        self.max_3m_dd_date = self.get_max_dd_freq(True)['index']
        self.ret_3m_dd = self.ann_ret / abs(self.max_3m_dd)
        self.skew = self.return_series.skew()
        self.avg_pos_neg = self.get_avg_pos_neg()
        self.down_dev = self.get_up_down_dev()
        self.up_dev = self.get_up_down_dev(True)
        self.sortino = (self.ann_ret - self.rfr) / self.down_dev
        
    def get_ann_return(self):
        """
        Return annualized return for a return series.
    
        Parameters
        ----------
        return_series : series
            returns series.
        
        Returns
        -------
        double
            Annualized return.
    
        """
        #compute the annualized return
        d = len(self.return_series)
        return self.return_series.add(1).prod()**(self.freq_int/d)-1

    def get_ann_vol(self):
        """
        Return annualized volatility for a return series.
    
        Parameters
        ----------
        self.return_series : series
            returns series.
        Returns
        -------
        double
            Annualized volatility.
    
        """
        #compute the annualized volatility
        return np.std(self.return_series, ddof=1)*np.sqrt(self.freq_int)
    
    def get_max_dd(self):
        """
        Return maximum draw down (Max DD) for a price series.
    
        Parameters
        ----------
        
        Returns
        -------
        double
            Max DD.
    
        """
        
        #we are going to use the length of the series as the window
        window = len(self.price_series)
        
        #calculate the max drawdown in the past window periods for each period in the series.
        roll_max = self.price_series.rolling(window, min_periods=1).max()
        drawdown = self.price_series/roll_max - 1.0
        
        return drawdown.min()
    
    def get_max_dd_freq(self, max_3m_dd=False):
        """
        Return dictionary (value and date) of either Max 1M DD or Max 3M DD
    
        Parameters
        ----------
        max_3m_dd : boolean, optional
            Compute Max 3M DD. The default is False.
    
        Returns
        -------
        dictionary
        """
        ret_series = self.price_series.copy()
        ret_series = ret_series.resample(self.freq).ffill()
        
        #compute 3M or 1M returns
        if max_3m_dd:
            periods = round((3/12) * self.freq_int)
            ret_series = ret_series.pct_change(periods)
        else:
            periods = round((1/12) * self.freq_int)
            ret_series = ret_series.pct_change(periods)
        ret_series.dropna(inplace=True)
        
        #compute Max 1M/3M DD
        max_dd_freq = min(ret_series)
        
        #get Max 1M/3M DD date
        index_list = ret_series.index[ret_series==max_dd_freq].tolist()
        
        #return dictionary
        return {'max_dd': max_dd_freq, 'index': index_list[0]}
    
    def get_avg_pos_neg(self):
        """
        Return Average positve returns/ Average negative returns
        of a strategy
    
        Returns
        -------
        double
        
        """
        
        #filter positive and negative returns
        pos_ret = util.get_pos_neg_df(self.return_series,True)
        neg_ret = util.get_pos_neg_df(self.return_series,False)
        
        #compute means
        avg_pos = pos_ret.mean()
        avg_neg = neg_ret.mean()
        
        return avg_pos/abs(avg_neg)
    
    def get_up_down_dev(self, up = False):
        """
        Compute annualized upside/downside std dev
    
        Parameters
        ----------
        up : boolean, optional
            The default is False.
    
        Returns
        -------
        double
            upside/downside std deviation.
    
        """
        #create a upside/downside return series
        if up:
            upside_returns = self.return_series.loc[self.return_series >= self.target]
            return get_ann_vol(upside_returns, self.freq)
        else:
            downside_returns = self.return_series.loc[self.return_series < self.target]
            return np.std(downside_returns, ddof=1)*np.sqrt(self.freq_int)
        
    def get_cum_ret(self):
        return self.return_series.add(1).prod(axis=0) - 1
    
    
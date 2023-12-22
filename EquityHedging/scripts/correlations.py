
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 09:47:11 2020

@author: PMN2DBW
"""

import pandas as pd
import numpy as np
from DataHandler.DataHandler import DataHandler as dh
from statsmodels.regression.rolling import RollingOLS
import seaborn as sns
import os
try:
    #try importing cufflinks
    import cufflinks as cf
    import plotly.graph_objs as go
    #set as offline
    cf.go_offline()
    cuff = True
except:
    print('No Cufflinks package. There may be some issues displaying charts using plotly.')
    try:
        pd.options.plotting.backend = 'plotly'
        plotly_backend = True
    except:
        print('No Plotly integration for Pandas')

# pd.set_option('display.max_rows', None)

cwd = os.getcwd()
manager_fp = '\\data\\ManagerData\\'
#manager weekly returns filepath
manager_weekly_pct_fp = cwd + manager_fp + 'ManagerWeeklyPct.csv'

dh = dh()

class Correlations:
    
    def __init__(self, per=None, lookback=None):
        self.per = per
        self.lookback = lookback
    
    def rolling_vol(self, returns, figure=True, return_df=True):
        roll = returns.rolling(self.lookback).std() * np.sqrt(self.per)
        if figure:
            self._df_plot(roll, 'Rolling '+str(self.lookback)+' Period Volatility', 'Date', 'Volatility')
        if return_df:
            return roll
        
    
    def manager_correlations(self, x, match_data=True,
                             graphic=False, per=None,
                             return_corr_matrix=True,):
        """
        Get the correlation matrix of the thing we are comparing against our
        manager data.
        The manager data can be funky with missing data
        
        Parameters
        ----------
        x : Pandas DataFrame
            index is datetime, data are returns, column names are names of
            managers, or whatever it is we are looking at
        match_data : bool
            if True, then match data to good data for managers
        """
        try:
            if per == None:
                per = self.per
            if per == 52 or per == 'weekly':
                manager_returns = dh.read_weekly_manager_pct()
            
            data = pd.concat([x, manager_returns], axis=1)
            c = data.corr()
            
            if graphic=='seaborn' or graphic=='sns' or graphic=='clustermap':
                sns.clustermap(c, vmin=-1, vmax=1)
            elif graphic=='plotly' or graphic=='plty':
                """
                #commenting out does not work
                fig = go(data=go.heatmap(z=c))
                fig.show()
                """
                print('Plotly not implemented for manager_correlation function')
                
            if return_corr_matrix:
                return c
        except:
            print("Failed")
    
    def correlations_fig(self, x, lookback=None, graphic='sns', per=None,
                         markets='all', match_dates=True, make_pct=True,
                         invert=False, return_corr_matrix=True,
                         yticklabels=True):
        """
        Get the correlation matrix of the thing we are comparing against our
        manager data.
        The manager data can be funky with missing data
        
        Parameters
        ----------
        x : Pandas DataFrame
            index is datetime, data are returns, column names are names of
            managers, or whatever it is we are looking at
        match_data : bool
            if True, then match data to good data for managers
        """
        if per == None:
            per = self.per
        y = dh.read_market_data(markets=markets, invert=invert)
        if match_dates:
            idx = y.index.intersection(x.index)
            y = y.loc[idx]
            x = x.loc[idx]
        if make_pct:
            y = y.pct_change()
        c = pd.concat([y,x],axis=1)
        c = c.corr()
        if graphic=='seaborn' or graphic=='sns' or graphic=='clustermap':
            sns.clustermap(c, vmin=-1, vmax=1, yticklabels=yticklabels)
        if return_corr_matrix:
            return c
    
    def manager_roll_corr(self, x, lookback=None, graphic='plot', per=None):
        try:
            if per == None:
                per = self.per
            if per == 52 or per == 'weekly':
                y = dh.read_weekly_manager_pct()
            if lookback == None:
                lookback = self.lookback
            collect = self.roll_corr(x, y, lookback=lookback)
            x_names = list(x.columns)
            if graphic=='plot':
                for x_name in x_names:
                    title = 'Rolling '+str(lookback)+' Period Correlations of '+x_name+' Against Managers'
                    self._df_plot(collect[x_name], title, 'Date',
                                         'Correlation', yrange=[-1.0, 1.0])
        except:
            print("Failed")
    
    def market_roll_corr(self, x, lookback=None, graphic='plot', per=None,
                         markets='all', match_dates=True, make_pct=True,
                         invert=False):
        """
        Parameters
        ----------
        match_dates: bool
            If True, then will match the dates of the market data to the dates
            of x
        make_pct: bool
            If True, then make y data pct change
        invert: bool
            set to True if you want to invert the data
            This is needed for rates data if the data are yields, so we can
            look at correlations and whatnot against inverse change in yields
        """
        if per == None:
            per = self.per
        y = dh.read_market_data(markets=markets, invert=invert)
        if match_dates:
            idx = y.index.intersection(x.index)
            y = y.loc[idx]
            x = x.loc[idx]
        if make_pct:
            y = y.pct_change()
        if lookback == None:
            lookback = self.lookback
        collect = self.roll_corr(x, y, lookback=lookback)
        x_names = list(x.columns)
        if graphic=='plot':
            for x_name in x_names:
                title = title='Rolling '+str(lookback)+' Period Correlations of '+x_name+' Against '+markets+' Markets'
                self._df_plot(collect[x_name], title, 'Date', 
                                     'Correlation', yrange=[-1.0, 1.0])
    
    def manager_roll_beta(self, x, lookback=None, graphic='plot', per=None):
        if per == None:
            per = self.per
        if per == 52 or per == 'weekly':
            y = dh.read_weekly_manager_pct()
        if lookback == None:
            lookback = self.lookback
        collect = self.roll_corr(x, y, lookback=lookback)
        x_names = list(x.columns)
        if graphic=='plot':
            for x_name in x_names:
                title = 'Rolling '+str(lookback)+' Period Betas of '+x_name+' Against Managers'
                self._df_plot(collect[x_name], title, 'Date', 'Beta')
    
    def market_roll_beta(self, x, lookback=None, graphic='plot', per=None,
                         markets='all', match_dates=True, make_pct=True,
                         invert=False):
        """
        Parameters
        ----------
        match_dates: bool
            If True, then will match the dates of the market data to the dates
            of x
        make_pct: bool
            If True, then make y data pct change
        invert: bool
            set to True if you want to invert the data
            This is needed for rates data if the data are yields, so we can
            look at correlations and whatnot against inverse change in yields
        """
        if per == None:
            per = self.per
        y = dh.read_market_data(markets=markets, invert=invert)
        if match_dates:
            idx = y.index.intersection(x.index)
            y = y.loc[idx]
            x = x.loc[idx]
        if make_pct:
            y = y.pct_change()
        if lookback == None:
            lookback = self.lookback
        collect = self.roll_corr(x, y, lookback=lookback)
        x_names = list(x.columns)
        if graphic=='plot':
            for x_name in x_names:
                title = 'Rolling '+str(lookback)+' Period Betas of '+x_name+' Against '+markets+' Markets'
                self._df_plot(collect[x_name], title, 'Date', 'Beta')
                
    def market_roll_alpha(self, x, lookback=None, graphic='plot', per=None,
                         markets='all', match_dates=True, make_pct=True,
                         invert=False):
        """
        Parameters
        ----------
        match_dates: bool
            If True, then will match the dates of the market data to the dates
            of x
        make_pct: bool
            If True, then make y data pct change
        invert: bool
            set to True if you want to invert the data
            This is needed for rates data if the data are yields, so we can
            look at correlations and whatnot against inverse change in yields
        """
        if per == None:
            per = self.per
        y = dh.read_market_data(markets=markets, invert=invert)
        if match_dates:
            idx = y.index.intersection(x.index)
            y = y.loc[idx]
            x = x.loc[idx]
        if make_pct:
            y = y.pct_change()
        if lookback == None:
            lookback = self.lookback
        collect = self.roll_corr(x, y, lookback=lookback)
        x_names = list(x.columns)
        if graphic=='plot':
            for x_name in x_names:
                title = 'Rolling '+str(lookback)+' Period Alpha of '+x_name+' Against '+markets+' Markets'
                self._df_plot(collect[x_name], title, 'Date', 'Alpha')
    
    def rolling_reg(self, x, y, lookback=None):
        if lookback==None:
            lookback = self.lookback
        y_names = list(y.columns)
        x_names = list(x.columns)
        #make a dict to collect the data
        collect = {}
        #iterate through items
        for x_name in x_names:
            collect[x_name] = pd.DataFrame()
            for y_name in y_names:
                #print(pd.concat([data[x_name],m[y_name]]).rolling(lookback).corr(pairwise=True))
                #remove nan's, the data needs to match for rolling correlation to work properly
                dependent = x[x_name]
                independent = y[y_name]
                #combine them and remove NaNs
                comb = pd.concat([dependent,independent], axis=1)
                comb = comb[~comb.isna().any(axis=1)]
                #pull out the dependent and independent again
                dependent = comb[x_name]
                independent = comb[y_name]
                #comb = comb[~comb.isna().any()]
                df = pd.DataFrame(dependent.rolling(lookback).corr(independent))
                df.columns = [y_name]
                collect[x_name] = pd.concat([collect[x_name], df], axis=1)
        return collect
    
    def cluster_corr(self, x, match_data=True):
        data = self.manager_correlations(x, match_data=match_data)
        return data.corr()
    
    def _df_plot(self, df, title, xax, yax, yrange=None,
                 rangeslider_visible=False, kind='line'):
        """
        Parameters
        ----------
        yrange: list
            list giving y range for axis
        """
        if kind=='line':
            if cuff:
                #do this if Cufflinks package is installed
                layout = go.Layout(yaxis=dict(range=yrange), title=title)
                df.iplot(layout=layout)
            elif plotly_backend:
                fig = df.plot(title=title)
                fig.update_layout(xaxis_title=xax,
                                  yaxis_title=yax)
                if yrange is not None:
                    fig.update_yaxes(range=yrange,)
                fig.update_xaxes(rangeslider_visible=rangeslider_visible)
                fig.show()
            else:
                df.plot(title=title).legend(bbox_to_anchor=(1, 1))
        if kind=='bar':
            if cuff:
                df.iplot(kind='bar', )
    
    def roll_corr(self, x, y, lookback=None):
        """
        Parameters
        ----------
        x : Pandas DataFrame
        y : Pandas DataFrame
        
        Returns
        -------
        collect: Dict
            Dictionary of DataFrames where each key is the item in x and the
            dataframe columns are the items in y
        """
        if lookback==None:
            lookback = self.lookback
        y_names = list(y.columns)
        x_names = list(x.columns)
        #make a dict to collect the data
        collect = {}
        #iterate through items
        for x_name in x_names:
            collect[x_name] = pd.DataFrame()
            for y_name in y_names:
                #print(pd.concat([data[x_name],m[y_name]]).rolling(lookback).corr(pairwise=True))
                #remove nan's, the data needs to match for rolling correlation to work properly
                dependent = x[x_name]
                independent = y[y_name]
                #combine them and remove NaNs
                comb = pd.concat([dependent,independent], axis=1)
                comb = comb[~comb.isna().any(axis=1)]
                #pull out the dependent and independent again
                dependent = comb[x_name]
                independent = comb[y_name]
                #comb = comb[~comb.isna().any()]
                df = pd.DataFrame(dependent.rolling(lookback).corr(independent))
                df.columns = [y_name]
                collect[x_name] = pd.concat([collect[x_name], df], axis=1)
        return collect
    
    def cum_ret(self, x, return_df=False):
        df = (1 + x).cumprod()
        self._df_plot(df, "Cumulative Returns", "Index", "Dates")
        if return_df:
            return df
    
    def plot_drawdowns(self, x, return_df=False):
        df = self.run_drawdown(x)
        self._df_plot(df, "Peak to Trough Drawdowns", "Drawdown", "Dates")
        if return_df:
            return df
    
    def roll_beta(self, x, y, lookback=None):
        """
        Parameters
        ----------
        x : Pandas DataFrame
        y : Pandas DataFrame
        
        Returns
        -------
        collect: Dict
            Dictionary of DataFrames where each key is the item in x and the
            dataframe columns are the items in y
        """
        if lookback==None:
            lookback = self.lookback
        y_names = list(y.columns)
        x_names = list(x.columns)
        #make a dict to collect the data
        collect = {}
        #iterate through items
        for x_name in x_names:
            collect[x_name] = pd.DataFrame()
            for y_name in y_names:
                #print(pd.concat([data[x_name],m[y_name]]).rolling(lookback).corr(pairwise=True))
                #remove nan's, the data needs to match for rolling correlation to work properly
                dependent = x[x_name]
                independent = y[y_name]
                #combine them and remove NaNs
                comb = pd.concat([dependent,independent], axis=1)
                comb = comb[~comb.isna().any(axis=1)]
                #pull out the dependent and independent again
                independent = comb[x_name]
                dependent = comb[y_name]
                roll_cov = pd.DataFrame(dependent.rolling(lookback).cov(independent))
                roll_var_x = pd.DataFrame(independent.rolling(lookback).var())
                df = roll_cov / roll_var_x #rolling beta
                df.columns = [y_name]
                collect[x_name] = pd.concat([collect[x_name], df], axis=1)
        return collect
        
    def run_drawdown(self, returns):
        """
        Parameters
        ----------
        returns: Pandas DataFrame
            dataframe with returns as values and index is dates

        Returns
        -------
        drawdown: Pandas DataFrame
            Dataframe with index values of dates and values of drawdown from
            running maximum

        """
        cum = (1+returns).cumprod()
        runmax = cum.cummax()
        drawdown = (cum / runmax) - 1
        # self._df_plot(drawdown, 'drawdown',None,None)
        return drawdown
    
    def get_worst_drawdowns(self, returns, num_worst=5):
        """

        Parameters
        ----------
        returns : TYPE
            DESCRIPTION.
        num_worst : TYPE, optional
            DESCRIPTION. The default is 5.

        Returns
        -------
        worst_drawdowns : Pandas DataFrame
            Dataframe with num_worst rows. Has beginning date of drawdown,
            ending date, and drawdown amount

        """
        #first get the drawdowns with all of the data
        drawdowns = self.run_drawdown(returns)
        worst_drawdowns = []
        #get the worst drawdown
        draw = self._get_drawdown_dates(drawdowns)
        #collect
        worst_drawdowns.append(draw)
        #set i to 1, because we will be starting from 1 for the number of
        #drawdowns desired from num_worst
        i = 1
        while i < num_worst:
            i+=1
            try:
                #remove data from last drawdown from the returns data
                mask = (returns.index>=draw['peak']) & (returns.index<=draw['trough'])
                returns = returns.loc[~mask]
                drawdowns = self.run_drawdown(returns)
                draw = self._get_drawdown_dates(drawdowns)
                #collect
                worst_drawdowns.append(draw)
            except:
                print("No more drawdowns...")
        return pd.DataFrame(worst_drawdowns)
    
    def get_co_drawdowns(self, base_return, compare_return, num_worst=5,
                         graphic='plot', return_df=True):
        """
        

        Parameters
        ----------
        base_return : TYPE
            DESCRIPTION.
        compare_return : TYPE
            DESCRIPTION.
        num_worst : TYPE, optional
            DESCRIPTION. The default is 5.

        Returns
        -------
        co_drawdowns : TYPE
            DESCRIPTION.

        """
        #use collect to collect the drawdowns for compare_return items
        collect = pd.DataFrame(columns=compare_return.columns)
        #get the drawdowns of the base return item
        drawdowns = self.get_worst_drawdowns(base_return, num_worst=num_worst)
        for i in drawdowns.index:
            pull = drawdowns.loc[i]
            #get the peak date and trough date
            peak = pull['peak']
            trough = pull['trough']
            #now get the returns over this period for the things we are
            #comparing against
            mask = (compare_return.index>peak) & (compare_return.index<=trough)
            compare_pull = compare_return.loc[mask]
            #get the cumulative product over this period
            compare_pull = (1 + compare_pull).cumprod()
            compare_pull = compare_pull.iloc[-1] - 1
            #transpose compare_pull to where the compare_return columns become
            #the index, and the date becomes the columns
            #we will change the column names to compare_returns column names
            #and change index to match i, so it is compatible with drawdowns
            #df
            compare_pull = pd.DataFrame(compare_pull).T
            compare_pull.columns = compare_return.columns
            compare_pull.index = [i]
            #concatenate
            collect = pd.concat([collect,compare_pull], axis=0)
        co_drawdowns = pd.concat([drawdowns,collect], axis=1)
        if graphic=='plot':
            title = 'Worst Drawdowns'
            #make a df to be plotted
            #the index will be the dates added together (make them strings)
            idx = co_drawdowns['peak'].dt.strftime('%Y-%m-%d') + ' - ' + co_drawdowns['trough'].dt.strftime('%Y-%m-%d')
            #drop peak and trough and just keep actual drawdowns
            data = co_drawdowns.drop(['peak','trough'], axis=1)
            #maek the df
            df = data.copy()
            df.index = idx
            self._df_plot(df, title, 'date', 'drawdown', kind='bar')
        if return_df:
            return co_drawdowns
    
    def _get_drawdown_dates(self, drawdowns):
        """
        

        Parameters
        ----------
        drawdowns : TYPE
            DESCRIPTION.

        Returns
        -------
        draw_dates : dict
            DESCRIPTION.

        """
        #get the min value
        worst_val = drawdowns.min()[0]
        #get the date of the drawdown trough
        trough_date = drawdowns.idxmin()[0]
        #get the last time the value was 0 (meaning the peak before drawdown)
        peak_date = drawdowns[drawdowns.index <= trough_date]
        peak_date = peak_date[peak_date>=0].dropna().index[-1]
        draw_dates = {'peak':peak_date, 'trough':trough_date, 
                      'drawdown':worst_val}
        return draw_dates
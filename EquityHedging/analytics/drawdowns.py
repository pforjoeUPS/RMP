# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 23:27:30 2022

@author: Phill Moran, Powis Forjoe
"""
import pandas as pd

def run_drawdown(returns):
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
    
def get_worst_drawdowns(returns, num_worst=5):
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
    drawdowns = run_drawdown(returns)
    worst_drawdowns = []
    #get the worst drawdown
    draw = get_drawdown_dates(drawdowns)
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
            drawdowns = run_drawdown(returns)
            draw = get_drawdown_dates(drawdowns)
            #collect
            worst_drawdowns.append(draw)
        except:
            print("No more drawdowns...")
    return pd.DataFrame(worst_drawdowns)
    
def get_co_drawdowns(base_return, compare_return, num_worst=5,
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
    drawdowns = get_worst_drawdowns(base_return, num_worst=num_worst)
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
        # _df_plot(df, title, 'date', 'drawdown', kind='bar')
    if return_df:
        return co_drawdowns
    
def get_drawdown_dates(drawdowns):
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
    # peak_date_1 = drawdowns[drawdowns.index >= trough_date]
    # peak_date_1 = peak_date_1[peak_date_1>=0].dropna().index[1]
    draw_dates = {'peak':peak_date, 'trough':trough_date, 
                  # 'end':peak_date_1,
                  'drawdown':worst_val}
    return draw_dates
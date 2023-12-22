# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 23:27:30 2022

@author: Phill Moran, Powis Forjoe
"""

#TODO: Make it Start, Trough, End, DD, Lenght, Recovery
import pandas as pd
from ..datamanager import data_manager as dm
from .historical_selloffs import compute_event_ret
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
    # self._df_plot(drawdown, 'Drawdown',None,None)
    return drawdown
    
def get_worst_drawdowns(returns, num_worst=5, recovery=False):
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
    returns_dd = returns.copy()
    #first get the drawdowns with all of the data
    drawdowns = run_drawdown(returns_dd)
    worst_drawdowns = []
    #get the worst drawdown
    draw = get_drawdown_dates(drawdowns)
    #add recovery data
    if recovery:
        draw = get_recovery_data(returns, draw)
    #collect
    worst_drawdowns.append(draw)
    #set i to 1, because we will be starting from 1 for the number of
    #drawdowns desired from num_worst
    for i in range(1,num_worst):
        try:
            #remove data from last drawdown from the returns data
            mask = (returns_dd.index>=draw['Peak']) & (returns_dd.index<=draw['Trough'])
            returns_dd = returns_dd.loc[~mask]
            drawdowns = run_drawdown(returns_dd)
            draw = get_drawdown_dates(drawdowns)
            #add recovery data
            if recovery:
                draw = get_recovery_data(returns, draw)
            #collect
            worst_drawdowns.append(draw)
        except:
            print("No more drawdowns...")
    
    return pd.DataFrame(worst_drawdowns)
    
#TODO: Review
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
    #get the drawdowns of the base return item
    drawdowns = get_worst_drawdowns(base_return, num_worst=num_worst)
    #use collect to collect the drawdowns for compare_return items
    compare_index = dm.get_prices_df(compare_return)
    collect = pd.DataFrame(columns=compare_index.columns, index=drawdowns.index)
    strat_name = base_return.columns[0]
    for i in drawdowns.index:
        pull = drawdowns.loc[i]
        #get the peak date and trough date
        peak = pull['Peak']
        trough = pull['Trough']
        for col in compare_index.columns:
            strat_df = dm.remove_na(compare_index,col)
            try:
                collect[col][i]=compute_event_ret(strat_df, col, peak, trough)
            except KeyError:
                # print(f'for {strat_name}, skipping {col}')
                collect[col][i]=float("nan")
    co_drawdowns = pd.concat([drawdowns,collect], axis=1)
    if graphic=='plot':
        pass
        # title = 'Worst Drawdowns'
        # #make a df to be plotted
        # #the index will be the dates added together (make them strings)
        # idx = co_drawdowns['Peak'].dt.strftime('%Y-%m-%d') + ' - ' + co_drawdowns['Trough'].dt.strftime('%Y-%m-%d')
        # #drop peak and trough and just keep actual drawdowns
        # data = co_drawdowns.drop(['Peak','Trough'], axis=1)
        # #maek the df
        # df = data.copy()
        # df.index = idx
        # df_plot(df, title, 'date', 'Drawdown', kind='bar')
    if return_df:
        return co_drawdowns
    
#TODO: Clean comments
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
    draw_dates = {'Peak':peak_date, 'Trough':trough_date, 
                  'Drawdown':worst_val}
    return draw_dates

#TODO: Add docstring
def get_recovery_data(returns, draw):
    #get strat name
    strat=returns.columns[0]
    #get index/price data
    ret_idx = dm.get_prices_df(returns)
    
    #remove data before drawdown
    mask_rec = (ret_idx.index>=draw['Trough'])
    ret_idx_1 = ret_idx.iloc[mask_rec]
    
    #find end of dd date
    peak_idx = ret_idx[ret_idx.index==draw['Peak']]
    try:
        draw['End'] = ret_idx_1[ret_idx_1[strat].gt(peak_idx[strat][0])].index[0]
        end_date = draw['End']
    except IndexError:
        #if recover not done, pick last period as end date
        draw['End'] = float("nan")
        end_date = ret_idx_1.last_valid_index()
    
    
    #get dd length
    mask_dd = (returns.index>=draw['Peak']) & (returns.index<=end_date )
    draw['Length'] = len(returns.iloc[mask_dd])-1
    
    #get recovery lenth    
    mask_recov=(returns.index>=draw['Trough']) & (returns.index<=end_date)
    draw['Recovery'] = len(returns.iloc[mask_recov])-1
    
    #reorder draw dict
    desired_order_list = ['Peak', 'Trough', 'End','Drawdown', 'Length', 'Recovery']
    return {key: draw[key] for key in desired_order_list}

#TODO: Add docstring and comments
def get_dd_matrix(returns):
    dd_matrix_df = pd.DataFrame()

    co_dd_dict = get_co_drawdown_data(returns, num_worst=1)
    for strat in returns:
        dd_matrix_df = pd.concat([dd_matrix_df,co_dd_dict[strat]])

    dd_matrix_df = dd_matrix_df.set_index(returns.columns, drop=False).rename_axis(None)
    dd_matrix_df.rename(columns={'Peak':'Start Date','Trough':'End Date','Drawdown':'Strategy Max DD'}, inplace=True)
    return dd_matrix_df

#TODO: Add docstring and comments
def get_drawdown_data(returns, num_worst=5, recovery=False):
    dd_dict = {}
    for strat in returns:
        dd_dict[strat] = get_worst_drawdowns(returns[[strat]],num_worst,recovery)
    return dd_dict

#TODO: Add docstring and comments
def get_co_drawdown_data(returns, compare_returns=pd.DataFrame(), num_worst=5):
    co_dd_dict = {}

    for strat in returns:
        if compare_returns.empty:
            co_dd_dict[strat] = get_co_drawdowns(returns[[strat]],returns.drop([strat], axis=1),num_worst)
        else:
            co_dd_dict[strat] = get_co_drawdowns(returns[[strat]],compare_returns,num_worst)
    return co_dd_dict


#TODO: Add docstring and comments
def get_dd_data(returns, include_fi=True):
    
    mgr = returns.columns[2] if include_fi else returns.columns[1]

    dd_data_dict = {}
    for strat in returns:
        if strat == mgr:
            dd_data_dict[f'{strat} Drawdown Statistics'] = get_worst_drawdowns(returns[[strat]],recovery=True)
        else:
            dd_data_dict[f'{mgr} vs {strat} Drawdowns'] = get_co_drawdowns(returns[[strat]], returns[[mgr]])
    return dd_data_dict


#TODO: Add docstring and comments
def df_plot(df, title, xax, yax, yrange=None,
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
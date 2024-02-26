# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 23:27:30 2022

@author: Phill Moran, Powis Forjoe
"""

# TODO: Make it Start, Trough, End, DD, Length, Recovery
# TODO: change to return series

import pandas as pd

from .historical_selloffs_new import compute_event_ret
from .returns_stats_new import ReturnsStats
from ..datamanager import data_manager_new as dm
from ..datamanager.data_xformer_new import PriceData

try:
    # try importing cufflinks
    import cufflinks as cf
    import plotly.graph_objs as go

    # set as offline
    cf.go_offline()
    cuff = True
except:
    print('No Cufflinks package. There may be some issues displaying charts using plotly.')
    try:
        pd.options.plotting.backend = 'plotly'
        plotly_backend = True
    except:
        print('No Plotly integration for Pandas')

DD_COL_DICT = {'Peak': 'Start Date', 'Trough': 'End Date', 'Drawdown': 'Strategy Max DD'}


def run_drawdown(returns_series):
    """
    Parameters
    ----------
    returns_series: series
        Series with returns as values and index is dates
    
    Returns
    -------
    drawdown: series
        Series with index values of dates and values of drawdown from
        running maximum
    
    """

    price_series = PriceData(returns_series).price_data
    window = len(price_series)

    # calculate the max drawdown in the past window periods for each period in the series.
    roll_max = price_series.rolling(window, min_periods=1).max()
    drawdown = price_series / roll_max - 1.0
    # cum = (1+return_series).cumprod()
    # runmax = cum.cummax()
    # drawdown = (cum / runmax) - 1
    # self._df_plot(drawdown, 'Drawdown',None,None)
    return drawdown


def get_worst_drawdowns(return_series, num_worst=5, recovery=False):
    """

    Parameters
    ----------
    return_series : series
        DESCRIPTION.
    num_worst : TYPE, optional
        DESCRIPTION. The default is 5.
    recovery: bool
    Returns
    -------
    worst_drawdowns : Pandas DataFrame
        Dataframe with num_worst rows. Has beginning date of drawdown,
        ending date, and drawdown amount

    """
    ret_dd_series = return_series.copy()
    # first get the drawdowns with all the data
    drawdowns = run_drawdown(ret_dd_series)
    worst_drawdowns = []
    # get the worst drawdown
    draw = get_drawdown_dates(drawdowns)
    # add recovery data
    if recovery:
        draw = get_recovery_data(return_series, draw)
    # collect
    worst_drawdowns.append(draw)
    # set i to 1, because we will be starting from 1 for the number of
    # drawdowns desired from num_worst
    for i in range(1, num_worst):
        try:
            # remove data from last drawdown from the returns data
            mask = (ret_dd_series.index >= draw['Peak']) & (ret_dd_series.index <= draw['Trough'])
            ret_dd_series = ret_dd_series.loc[~mask]
            drawdowns = run_drawdown(ret_dd_series)
            draw = get_drawdown_dates(drawdowns)
            # add recovery data
            if recovery:
                draw = get_recovery_data(return_series, draw)
            # collect
            worst_drawdowns.append(draw)
        except:
            print("No more drawdowns...")

    return pd.DataFrame(worst_drawdowns)


# TODO: Review
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
    # get the drawdowns of the base return item
    drawdowns = get_worst_drawdowns(base_return, num_worst=num_worst)
    # use collect to collect the drawdowns for compare_return items
    compare_index = PriceData(compare_return).price_data
    collect = pd.DataFrame(columns=compare_index.columns, index=drawdowns.index)
    # strat_name = base_return.columns[0]
    strat_name = base_return.name
    for i in drawdowns.index:
        pull = drawdowns.loc[i]
        # get the peak date and trough date
        peak = pull['Peak']
        trough = pull['Trough']
        for col in compare_index:
            strat_df = dm.remove_na(compare_index, col)
            try:
                collect[col][i] = compute_event_ret(strat_df, col, peak, trough)
            except KeyError:
                # print(f'for {strat_name}, skipping {col}')
                collect[col][i] = float("nan")
    co_drawdowns = pd.concat([drawdowns, collect], axis=1)
    if graphic == 'plot':
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
        return dm.rename_columns(co_drawdowns, DD_COL_DICT)


# TODO: Clean comments
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
    # get the min value
    # worst_val = drawdowns.min()[0]
    worst_val = drawdowns.min()
    # get the date of the drawdown trough
    # trough_date = drawdowns.idxmin()[0]
    trough_date = drawdowns.idxmin()
    # get the last time the value was 0 (meaning the peak before drawdown)
    peak_date = drawdowns[drawdowns.index <= trough_date]
    peak_date = peak_date[peak_date >= 0].dropna().index[-1]
    # peak_date_1 = drawdowns[drawdowns.index >= trough_date]
    # peak_date_1 = peak_date_1[peak_date_1>=0].drop_na().index[1]
    draw_dates = {'Peak': peak_date, 'Trough': trough_date,
                  'Drawdown': worst_val}
    return draw_dates


# TODO: Add docstring
def get_recovery_data(returns_data, draw):
    return_index = PriceData(returns_data).price_data

    # remove data before drawdown
    mask_rec = (return_index.index >= draw['Trough'])
    return_index_1 = return_index.iloc[mask_rec]

    # find end of dd date
    peak_index = return_index[return_index.index == draw['Peak']]
    try:
        draw['End'] = return_index_1[return_index_1.gt(peak_index[0])].index[0]
        end_date = draw['End']
    except IndexError:
        # if recover not done, pick last period as end date
        draw['End'] = float("nan")
        end_date = return_index_1.last_valid_index()

    # get dd length
    mask_dd = (returns_data.index >= draw['Peak']) & (returns_data.index <= end_date)
    draw['Length'] = len(returns_data.iloc[mask_dd]) - 1

    # get recovery length
    mask_recovery = (returns_data.index >= draw['Trough']) & (returns_data.index <= end_date)
    draw['Recovery'] = len(returns_data.iloc[mask_recovery]) - 1

    # reorder draw dict
    desired_order_list = ['Peak', 'Trough', 'End', 'Drawdown', 'Length', 'Recovery']
    return {key: draw[key] for key in desired_order_list}


# TODO: Add docstring and comments
def get_dd_matrix(returns_df):
    dd_matrix_df = pd.DataFrame()

    co_dd_dict = get_co_drawdown_data(returns_df, num_worst=1)
    for strat in returns_df:
        dd_matrix_df = pd.concat([dd_matrix_df, co_dd_dict[strat]])

    dd_matrix_df = dd_matrix_df.set_index(returns_df.columns, drop=False).rename_axis(None)
    return dd_matrix_df[[*DD_COL_DICT.values(), *returns_df.columns]]


# TODO: Add docstring and comments
def get_drawdown_data(returns_df, num_worst=5, recovery=False):
    dd_dict = {}
    for strat in returns_df:
        dd_dict[strat] = get_worst_drawdowns(returns_df[strat], num_worst, recovery)
    return dd_dict


# TODO: Add docstring and comments
def get_co_drawdown_data(returns_df, compare_returns=pd.DataFrame(), num_worst=5):
    co_dd_dict = {}

    for strat in returns_df:
        if compare_returns.empty:
            co_dd_dict[strat] = get_co_drawdowns(returns_df[strat], returns_df.drop([strat], axis=1), num_worst)
        else:
            co_dd_dict[strat] = get_co_drawdowns(returns_df[strat], compare_returns, num_worst)
            co_dd_dict[strat] = dm.rename_columns(co_dd_dict[strat], {'Strategy Max DD': f'{strat} Max DD'})
    return co_dd_dict


# TODO: Add docstring and comments
def get_dd_data(returns_df, include_fi=True):
    mgr = returns_df.columns[2] if include_fi else returns_df.columns[1]

    dd_data_dict = {}
    for strat in returns_df:
        if strat == mgr:
            dd_data_dict[f'{strat} Drawdown Statistics'] = get_worst_drawdowns(returns_df[strat], recovery=True)
        else:
            dd_data_dict[f'{mgr} vs {strat} Drawdowns'] = get_co_drawdowns(returns_df[strat], returns_df[[mgr]])
    return dd_data_dict


# TODO: Add docstring and comments
# Old code from Phil...need to review and decide ask Devang
def df_plot(df, title, xax, yax, yrange=None,
            rangeslider_visible=False, kind='line'):
    """
        Parameters
        ----------
        yrange: list
            list giving y range for axis
        """
    if kind == 'line':
        if cuff:
            # do this if Cufflinks package is installed
            layout = go.Layout(yaxis=dict(range=yrange), title=title)
            df.iplot(layout=layout)
        elif plotly_backend:
            fig = df.plot(title=title)
            fig.update_layout(xaxis_title=xax,
                              yaxis_title=yax)
            if yrange is not None:
                fig.update_yaxes(range=yrange, )
            fig.update_xaxes(rangeslider_visible=rangeslider_visible)
            fig.show()
        else:
            df.plot(title=title).legend(bbox_to_anchor=(1, 1))
    if kind == 'bar':
        if cuff:
            df.iplot(kind='bar', )


# from old rs, need to refactor
def get_drawdown_series(returns_series):
    """
    Calculate drawdown series (from calculation of MaxDD)

    Parameters
    ----------
    returns_series : pandas.series

    Returns
    -------
    Drawdown series

    """
    price_series = PriceData(returns_series).price_data
    window = len(price_series)
    roll_max = price_series.rolling(window, min_periods=1).max()
    drawdown = price_series / roll_max - 1.0
    return drawdown


# from old rs, need to refactor
def find_dd_date(returns_series):
    """
    Finds the date where Max DD occurs

    Parameters
    ----------
    returns_series : pandas.series

    Returns
    -------
    Date of MaxDD in dataframe

    """
    max_dd = ReturnsStats(returns_series=returns_series).get_max_dd()
    drawdown = get_drawdown_series(returns_series)
    dd_date = drawdown.index[drawdown == float(max_dd)]

    return dd_date


# from old rs, need to refactor
def find_zero_dd_date(price_series):
    """
    Finds the date where drawdown was at zero before Max DD

    Parameters
    ----------
    price_series : series
        price series.

    Returns
    -------
    Date of where drawdown was at zero before MaxDD in dataframe

    """
    drawdown = get_drawdown_series(price_series)
    drawdown_reverse = drawdown[::-1]
    x = (find_dd_date(price_series)[0])
    strat_drawdown = drawdown_reverse.loc[x:]

    for dd_index, dd_value in enumerate(strat_drawdown):
        if dd_value == 0:
            zero_dd_date = strat_drawdown.index[dd_index]
            break
    return zero_dd_date


# from old rs, need to refactor
def get_recovery(price_series):
    """
    Finds the recovery timeline from where MaxDD occured and when strategy recoverd

    Parameters
    ----------
    price_series : series
        price series.

    Returns
    -------
    The number of "days" it took for strategy to return back to 'recovery'

    """
    zero_dd_date = find_zero_dd_date(price_series)
    zero_dd_date_price = price_series.loc[zero_dd_date]
    dd_date = find_dd_date(price_series)
    count_price_series = price_series.loc[dd_date[0]:]
    recovery_days = 0

    for price in count_price_series:
        if price < zero_dd_date_price:
            recovery_days += 1
        else:
            break
    return recovery_days

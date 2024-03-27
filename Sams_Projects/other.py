import pandas as pd

def get_weighted_index_from_p(df_index_prices, name='', notional_weights=[]):
    total_notional = sum(notional_weights)
    weight_ratio = [notional / total_notional for notional in notional_weights]
    strat_list = df_index_prices.columns.tolist()

    # Create weighted index series
    weighted_index = pd.Series(1, index=df_index_prices.index)

    # Calculate weighted index
    for i, strat in enumerate(strat_list):
        strat_weight = weight_ratio[i]
        StratStartLevel = df_index_prices[strat].iloc[0]  # Using iloc[0] to access the first element
        StratShare = (strat_weight * 1 / StratStartLevel) * (df_index_prices[strat] - StratStartLevel)
        weighted_index += StratShare

    # Convert weighted index series to dataframe
    weighted_index_df = weighted_index.to_frame(name=name)

    return weighted_index_df

def get_weighted_index_from_r(df_index_returns, name='', notional_weights=[]):
    # Calculate weight ratios
    total_notional = sum(notional_weights)
    weight_ratio = [notional / total_notional for notional in notional_weights]
    strat_list = df_index_returns.columns.tolist()

    # Create weighted index series
    weighted_index = pd.Series(0, index=df_index_returns.index)

    # Calculate weighted index
    for i, strat in enumerate(strat_list):
        strat_weight = weight_ratio[i]
        StratShare = strat_weight * (1 + df_index_returns[strat]).cumprod() # Calculate cumulative returns
        weighted_index += (StratShare*1)

    # Convert weighted index series to DataFrame
    weighted_index_df = weighted_index.to_frame(name=name)

    return weighted_index_df
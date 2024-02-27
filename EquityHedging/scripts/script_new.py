# import os
#
# os.chdir('..\..')

# import libraries
from EquityHedging.datamanager import data_manager_new as dm
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_lists as dl
from EquityHedging.datamanager import data_xformer_new as dxf
from EquityHedging.analytics import returns_analytics as ra
from EquityHedging.reporting.excel import new_reports as rp

# import returns data
eq_bmk = 'S&P 500'
include_fi = False
weighted = True
strat_drop_list = []
new_strat = False

eq_hedge_dh = dh.EQHedgeDataHandler(eq_bmk=eq_bmk, eq_mv=11.0, include_fi=include_fi, fi_mv=20.0, strat_drop_list=[])

# Add new strat
new_strat = True
if new_strat:
    strategy_list = ['esprso']
    file_path = dl.NEW_STRATS_FP + 'esprso.xlsx'
    sheet_name = 'Sheet1'
    notional_list = [1]
    new_strategy = dxf.get_new_strategy_returns_data(file_path=file_path, sheet_name=sheet_name,
                                                     return_data=False, strategy_list=strategy_list)
    new_strategy_dict = dxf.get_data_dict(new_strategy, index_data=False)

    eq_hedge_dh.add_strategy(new_strategy_dict, notional_list)

eq_hedge_dh.get_weighted_returns(new_strat=new_strat)

returns_dict = eq_hedge_dh.weighted_returns if weighted else eq_hedge_dh.returns
mkt_data = eq_hedge_dh.mkt_returns
mkt_key = eq_hedge_dh.mkt_key
include_fi = eq_hedge_dh.include_fi

eq_hedge_analytics = ra.EqHedgeReturnsDictAnalytic(returns_dict, include_fi=include_fi,
                                                   mkt_data=mkt_data, mkt_key=mkt_key)

# compute correlations
check_corr = False
if check_corr:
    corr_freq_list = ['Daily', 'Weekly', 'Monthly']
    eq_hedge_analytics.get_corr_stats_dict(corr_freq_list)
    corr_dict = dm.copy_data(eq_hedge_analytics.corr_stats_dict)

# compute analytics
check_analysis = True
if check_analysis:
    analytics_freq_list = ['Weekly', 'Monthly']
    eq_hedge_analytics.get_returns_stats_dict(analytics_freq_list)
    eq_hedge_analytics.get_hedge_metrics_dict(analytics_freq_list)
    analytics_dict = {
        'return_stats':dm.copy_data(eq_hedge_analytics.returns_stats_dict),
        'hedge_metrics': dm.copy_data(eq_hedge_analytics.hedge_metrics_dict)
    }

# compute historical selloffs
check_hs = False
if check_hs:
    eq_hedge_analytics.get_hist_selloff()
    hist_df = dm.copy_data(eq_hedge_analytics.historical_selloff_data)

# get quantile dataframe
check_quantile = False
if check_quantile:
    eq_hedge_analytics.get_quantile_stats()
    quantile_dict = dm.copy_data(eq_hedge_analytics.quantile_stats_data)

# run report
report_name = 'equity_hedge_analysis_testNew'
selloffs = True
rp.EquityHedgeReport(report_name=report_name, data_handler=eq_hedge_dh, weighted=weighted,
                     new_strat=new_strat, selloffs=selloffs).run_report()

hs_report = 'historical_selloff_test'
rp.HistSelloffReport(report_name=hs_report, data_handler=eq_hedge_dh, weighted=weighted,
                     new_strat=new_strat).run_report()

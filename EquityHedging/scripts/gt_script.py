from EquityHedging.datamanager import data_handler as dh, data_manager_new as dm, data_xformer_new as dxf
from EquityHedging.analytics import returns_analytics as ra, period_stats as ps
from EquityHedging.reporting.excel import new_reports as rp, new_sheets

# GT Data
# GT DataHandler
filepath = dh.UPSGT_DATA_FP
gt_dh = dh.GTPortDataHandler()
w_la_list = ['Public Equity', 'Fixed Income', 'Liquid Alts', 'Credit', 'Private Equity', 'Real Estate', 'Cash']
wo_la_list = ['Public Equity', 'Fixed Income', 'Credit', 'Private Equity', 'Real Estate', 'Cash']

gt_w_la_returns = gt_dh.returns[w_la_list]
gt_w_la_mvs = gt_dh.mvs[w_la_list]
gt_w_la_data = dm.get_agg_data(returns_df=gt_w_la_returns, mvs_df=gt_w_la_mvs, agg_col='GT-Composite', merge_agg=True)

gt_wo_la_returns = gt_dh.returns[wo_la_list]
gt_wo_la_mvs_eq = gt_dh.mvs[wo_la_list]
gt_wo_la_mvs_eq['Public Equity'] += gt_dh.mvs['Liquid Alts']
gt_wo_la_data_eq = dm.get_agg_data(returns_df=gt_wo_la_returns, mvs_df=gt_wo_la_mvs_eq,
                                   agg_col='GT-Composite wo Liquid Alts', merge_agg=True)

gt_wo_la_mvs_cash = gt_dh.mvs[wo_la_list]
gt_wo_la_mvs_cash['Public Equity'] += gt_dh.mvs['Liquid Alts']
gt_wo_la_data_cash = dm.get_agg_data(returns_df=gt_wo_la_returns, mvs_df=gt_wo_la_mvs_cash,
                                     agg_col='GT-Composite wo Liquid Alts', merge_agg=True)

gt_dh.custom_returns_data = {'returns': dm.merge_df_lists([gt_dh.returns[w_la_list], gt_w_la_data['returns'],
                                                           gt_wo_la_data['returns']], drop_na=False),
                             'mv': dm.merge_df_lists([gt_dh.mvs, gt_w_la_data['mv'], gt_wo_la_data['mv']],
                                                     drop_na=False)}

returns_dict = dxf.get_data_dict(gt_dh.custom_returns_data['returns'], drop_na=False)
period_dict = dm.get_period_dict(gt_dh.custom_returns_data['returns'])

# GT Returns Analytic
gt_ra = ra.LiquidAltsPeriodAnalytic(returns_dict=period_dict, include_cm=False, include_fx=False,
                                    mkt_data=gt_dh.mkt_returns, mkt_key=gt_dh.mkt_key)
gt_ra.get_returns_stats_dict(list(period_dict.keys()))

best_worst_pds_dict = ps.BestWorstDictPeriods(dxf.get_data_dict(gt_dh.custom_returns_data['returns']),
                                              dxf.get_data_dict(gt_dh.mkt_returns)).best_worst_pds_dict

# GT Reports
gt_rp = rp.DataReport('Group Trust_with_and_wo_Liquid Alts (Public Equity increased)',
                      gt_ra.returns_stats_dict, False)
gt_rp.writer = gt_rp.get_writer()
ret_stats_idx_list = ['Time Frame', 'No. of Monthly Observations', 'Annualized Return', 'Median Period Return',
                      'Avg. Period Return', 'Avg. Period Up Return', 'Avg. Period Down Return',
                      'Avg Pos Return/Avg Neg Return', 'Best Period', 'Worst Period', '% Positive Periods',
                      '% Negative Periods', 'Annualized Volatility', 'Upside Deviation', 'Downside Deviation',
                      'Upside to Downside Deviation Ratio', 'Vol to Downside Deviation Ratio', 'Skewness', 'Kurtosis',
                      'Max DD', 'Return/Volatility', 'Sortino Ratio', 'Return/Max DD']
for freq, data_df in gt_rp.data.items():
    gt_rp.data[freq] = data_df.reindex(index=ret_stats_idx_list)
    new_sheets.LiquidAltsReturnsStatsSheet(writer=gt_rp.writer, data=gt_rp.data[freq],
                                           sheet_name=f'Returns Statistics ({freq})', include_bmk=False).create_sheet()
for freq, returns_df in returns_dict.items():
    new_sheets.HistReturnSheet(writer=gt_rp.writer, data=returns_df,
                               sheet_name=f'{freq} Historical Returns').create_sheet()
new_sheets.MktValueSheet(writer=gt_rp.writer, data=gt_dh.custom_returns_data['mv']).create_sheet()
gt_rp.writer.close()

gt_q_rp = rp.DataReport('EQ_FI_worst_qtrs_vs_GT-Composite',
                        best_worst_pds_dict['Quarterly']['worst_periods']['returns_data'])
gt_q_rp.writer = gt_q_rp.get_writer()
for x in ['Public Equity', 'Fixed Income']:
    new_sheets.DataFrameSheet(gt_q_rp.writer, gt_q_rp.data[x], sheet_name=f'{x} Worst Quarters').create_sheet()

gt_q_rp.writer.close()

gt_weights_rp = rp.DataReport('GT_Composite-weights',
                              {'GT-Composite': gt_w_la_data['weights'],
                               'GT wo LA (Cash)': gt_wo_la_data_cash['weights'],
                               'GT wo LA (Equity)': gt_wo_la_data_eq['weights']})
gt_weights_rp.writer = gt_weights_rp.get_writer()
for key, weights_df in gt_weights_rp.data.items():
    new_sheets.DataFrameSheet(gt_weights_rp.writer, weights_df, sheet_name=f'{key} Weights')
gt_weights_rp.writer.close()
# Liquid Alts Data
# Liquid Alts DataHandler
la_dh = dh.LiqAltsPortHandler()
la_q_returns = dm.merge_dfs(gt_dh.returns[['Public Equity', 'Fixed Income', 'Liquid Alts', 'Group Trust']],
                            la_dh.bmk_returns, drop_na=False)
la_q_returns = dxf.format_data(dxf.get_price_data(la_q_returns), freq='Q', drop_na=False)

# Liquid Alts Best-Worst Quarters
la_q_ps = ps.BestWorstPeriods(la_q_returns)
worst_quarters = la_q_ps.worst_periods_data

# Liquid Alts report
la_rp = rp.DataReport('EQ_FI_worst_qtrs_vs_LA', worst_quarters)
la_rp.writer = la_rp.get_writer()
for x in ['Public Equity', 'Fixed Income']:
    new_sheets.DataFrameSheet(la_rp.writer, la_rp.data['returns_data'][x],
                              sheet_name=f'{x} Worst Quarters').create_sheet()
la_rp.writer.close()

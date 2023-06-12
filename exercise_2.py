import os

os.chdir('..\..')

#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp


#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [False]
strat_drop_list = []
new_strat = False
sptr_dict= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list,True,False)

#Add new strat
new_strat = True
if new_strat:
    strategy_list1 = ['CS_Defensive_Skew']
    filename = 'CS_SG_Data.xlsx'
    sheet_name1 = 'CS Defensive Skew'
    new_strategy1 = dm.get_new_strategy_returns_data(filename, sheet_name1, strategy_list1)
    new_strategy_dict1 = dm.get_data_dict(new_strategy1, data_type='index')
    ret_dict = dm.merge_dicts(sptr_dict, new_strategy_dict1)

strat_report = rp.generate_strat_report('strat_report_Justin', ret_dict, False)
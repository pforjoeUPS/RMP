# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 22:20:15 2022

@author: rrq1fyq
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp
import pandas as pd



# Steps:
# 1. Get the dictionary of returns for the SPTR index using the get_equity_hedge_returns function from datamanager (dm). Name this dictionary sptr_dict
# 	Hint: import the data_manager (dm) library using:
# 		from EquityHedging.datamanager import datamanager as dm

sptr_dict = dm.get_equity_hedge_returns(equity = 'SPTR', include_fi = False,  only_equity=True)

# 2. Import the Credit Suisse stratgies from the "Credit Suisse Systematic Defensive Skew_Index_20220305_out.xlsx" file into a dataframe called cs_data:
# 	Hint: copy the data into a new sheet so it's easier to import without reformatting (we did this already, the data is in the data sheet file)

cs_data = pd.read_excel('C:/Users/RRQ1FYQ/Documents/RMP/Exercises/exercise_2/Credit Suisse Systematic Defensive Skew_Index_20220305_out.xlsx', sheet_name = 'Sheet1', index_col = 0)

# 3. Create cs_dict which should be a dictionary of frequency of returns of the cs_data
cs_dict = dm.get_data_dict(cs_data)

# 4. Merge the sptr_dict and cs_dict dictionaries with the merge_dicts function from data_manager (dm). Call this new dictionary ret_dict.
# 	Note: Make sure sptris the first column in all the dataframes in the ret_dict dictionery created

ret_dict = dm.merge_dicts(sptr_dict, cs_dict)


# 5. Generate the excel strat report ('strat_report_[first_name]') using the generate_strat_report function from reports (rp)
# 	Hint: import the reports (rp) library using:
# 		from EquityHedging.reporting.excel import reports as rp


rp.generate_strat_report("strat_report_Maddie.xlsx", ret_dict)



# 6. Save a copy of the lines of code you used to generate the report as well as the excel report ("strat_report_[first_name].xlsx").
# 7. Push to the exercise_2 folder in the repository.
#import returns data






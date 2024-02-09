# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 00:00:57 2023

@author: NVG9HXP
"""

# from EquityHedging.datamanager import data_updater as du
#
# du.update_nexen_liq_alts_data()
# du.update_liq_alts_bmk_data()
# du.update_innocap_liq_alts_data()
# du.update_hf_bmk_data()
# du.update_bmk_data()
# du.update_asset_class_data()
# du.update_eq_hedge_returns()

from EquityHedging.datamanager import data_updater_new as du
du.NexenDataUpdater().update_report() #nexen_liq_alts_data-new.xlsx
du.InnocapLiquidAltsDataUpdater().update_report() #innocap_liq_alts_data-new.xlsx
du.HFBmkDataUpdater().update_report() #hf_bmks-new.xlsx
du.BmkDataUpdater().update_report() #bmk_returns-new.xlsx
du.LiquidAltsBmkDataUpdater().update_report()
du.GTPortDataUpdater().update_report()
du.GTBmkDataUpdater().update_report()
du.EquityHedgeReturnsUpdater().update_report()
du.LiquidAltsReturnsUpdater().update_report()


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
du.nexenDataUpdater().update_report() #nexen_liq_alts_data-new.xlsx
# du.innocapLiquidAltsDataUpdater().update_report() #innocap_liq_alts_data-new.xlsx
du.hfBmkDataUpdater().update_report() #hf_bmks-new.xlsx
du.bmkDataUpdater().update_report() #bmk_returns-new.xlsx
du.liqAltsBmkDataUpdater().update_report()
# du.gtPortDataUpdater().update_report()
# du.gtBmkDataUpdater().update_report()
du.equityHedgeReturnsUpdater().update_report()
# du.liquidAltsReturnsUpdater().update_report()


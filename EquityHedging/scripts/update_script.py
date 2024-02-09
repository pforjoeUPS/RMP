# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 00:00:57 2023

@author: NVG9HXP
"""

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


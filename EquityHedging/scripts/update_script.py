# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 00:00:57 2023

@author: NVG9HXP
"""

from EquityHedging.datamanager import data_updater as du

du.update_nexen_liq_alts_data()
du.update_liq_alts_bmk_data()
du.update_innocap_liq_alts_data()
du.update_hf_bmk_data()
du.update_bmk_data()
du.update_asset_class_data()
du.update_eq_hedge_returns()

from EquityHedging.datamanager import data_updater_new as du
du.nexenDataUpdater().update_report()
du.innocapLiquidAltsDataUpdater().update_report()
du.hfBmkDataUpdater().update_report()
du.bmkDataUpdater().update_report()
du.liqAltsBmkDataUpdater().update_report()
du.assetClassDataUpdater().update_report()
du.equityHedgeReturnsUpdater().update_report()
du.liquidAltsReturnsUpdater().update_report()


# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 00:00:57 2023

@author: NVG9HXP
"""

from EquityHedging.datamanager import data_updater_new as du, data_xformer_new as dxf, data_lists as dl

du.NexenDataUpdater().update_report()  # nexen_liq_alts_data-new.xlsx
du.InnocapLiquidAltsDataUpdater().update_report()  # innocap_liq_alts_data-new.xlsx
du.HFBmkDataUpdater().update_report()  # hf_bmks-new.xlsx
du.BmkDataUpdater().update_report()  # bmk_returns-new.xlsx
du.LiquidAltsBmkDataUpdater().update_report()
du.GTPortDataUpdater().update_report()
du.GTBmkDataUpdater().update_report()
du.EquityHedgeReturnsUpdater().update_report()
du.LiquidAltsReturnsUpdater().update_report()

moments = dxf.BbgDataXformer(file_path=dl.NEW_STRATS_FP + 'moments.xlsx')
eq_hedge_du = du.EquityHedgeReturnsUpdater()
eq_hedge_du.add_new_index(moments.data_xform)
eq_hedge_du.update_report()

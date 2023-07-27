# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 07:35:12 2023

@author: NVG9HXP
"""
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.datamanager import data_transformer as dt
from EquityHedging.analytics import drawdowns as dd
from EquityHedging.analytics import summary
liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler()

# Import Penso, JSC, TMF
penso = dm.get_new_strat_data('liq_alts\\penso_returns.xlsx')
welwing = dm.get_new_strat_data('liq_alts\\welwing.xlsx')
gemini = dm.get_new_strat_data('liq_alts\\gemini.xlsx')
jsc = dm.get_new_strat_data('liq_alts\\jsc.xlsx')
tmf = dm.get_new_strat_data('liq_alts\\tmf.xlsx')
kaf = dm.get_new_strat_data('liq_alts\\kaf.xlsx')
eof = dm.get_new_strat_data('liq_alts\\eof.xlsx')
br_sys = dm.get_new_strat_data('liq_alts\\br_explorer.xlsx')
br_disc = dm.get_new_strat_data('liq_alts\\br_master.xlsx')
eg = dm.get_new_strat_data('liq_alts\\eg.xlsx')
campbell_ar = dm.get_new_strat_data('liq_alts\\campbell_ar.xlsx')
campbell_ar_strats = dm.get_new_strat_data('liq_alts\\campbell_ar_strats.xlsx')
welton_gm = dm.get_new_strat_data('liq_alts\\welton_gm.xlsx')
welton_gm_strats = dm.get_new_strat_data('liq_alts\\welton_gm.xlsx', sheet_name='strats')
welton_gm_hypo = dm.get_new_strat_data('liq_alts\\welton_gm.xlsx', sheet_name='hypo')
welton_tf = dm.get_new_strat_data('liq_alts\\welton_tf.xlsx')
welton_tf_strats = dm.get_new_strat_data('liq_alts\\welton_tf.xlsx', sheet_name='strats')
welton_tf_hypo = dm.get_new_strat_data('liq_alts\\welton_tf.xlsx', sheet_name='hypo')
haidar = dm.get_new_strat_data('liq_alts\\welton_tf.xlsx')
voleon = dm.get_new_strat_data('liq_alts\\voleon.xlsx')
rokos = dm.get_new_strat_data('liq_alts\\rokos.xlsx')
modular = dm.get_new_strat_data('liq_alts\\modular.xlsx')
discus = dm.get_new_strat_data('liq_alts\\discus.xlsx')[['Discus']]
stratus = dm.get_new_strat_data('liq_alts\\discus.xlsx')[['Stratus']]
sspf = dm.get_new_strat_data('liq_alts\\sspf.xlsx')
gm_qm_a = dm.get_new_strat_data('liq_alts\\graham.xlsx', sheet_name='quant_macro')[['Graham Quant Macro-A']]
gm_qm_b = dm.get_new_strat_data('liq_alts\\graham.xlsx', sheet_name='quant_macro')[['Graham Quant Macro-B']]
gm_qm = dm.get_new_strat_data('liq_alts\\graham.xlsx', sheet_name='quant_macro')
gm_qm_hypo = dm.get_new_strat_data('liq_alts\\graham.xlsx', sheet_name='hypo')
adapt = dm.get_new_strat_data('liq_alts\\adapt.xlsx')
aqr_gm = dm.get_new_strat_data('liq_alts\\aqr_gm.xlsx')
aqr_tf = dm.get_new_strat_data('liq_alts\\aqr_tf.xlsx')
aspect= dm.get_new_strat_data('liq_alts\\aspect.xlsx')
# aspect_alt = dm.get_new_strat_data('liq_alts\\aspect.xlsx')[['Aspect-Alt TF']]
# aspect_alt_chn = dm.get_new_strat_data('liq_alts\\aspect.xlsx')[['Aspect-Alt/China TF']]
# aspect_alt_man = dm.get_new_strat_data('liq_alts\\aspect.xlsx')[['Aspect-Alt TF Mandate']]
hbk = dm.get_new_strat_data('liq_alts\\hbk.xlsx')
centiva = dm.get_new_strat_data('liq_alts\\centiva.xlsx')
hypo = dm.get_new_strat_data('liq_alts\\demo_port.xlsx')
astignes = dm.get_new_strat_data('liq_alts\\astignes.xlsx')
east_one = dm.get_new_strat_data('liq_alts\\east_one.xlsx')
east_value = dm.get_new_strat_data('liq_alts\\east_value.xlsx')
magnetar = dm.get_new_strat_data('liq_alts\\magnetar.xlsx')
edl = dm.get_new_strat_data('liq_alts\\edl.xlsx', sheet_name='data_a')
gmo_sys = dm.get_new_strat_data('liq_alts\\gmo_sys.xlsx')
voloridge = dm.get_new_strat_data('liq_alts\\voloridge.xlsx')
gp_data = dm.get_new_strat_data('returns_data\\group_trust_returns.xlsx',sheet_name='returns')

#GM
#Penso
gm = dm.merge_data_frames(liq_alts_p.mkt_returns, br_disc, False)
gm = dm.merge_data_frames(gm, liq_alts_p.bmk_returns[['HFRX Macro/CTA']])
gm_dict = dm.get_period_dict(gm)
rp.get_strat_alts_report('br_disc_strats', gm_dict)

#GM
gm_list = ['1907 Penso Class A', 'Bridgewater Alpha', 'DE Shaw Oculus Fund','Element Capital']
gm_strat = gm_list[0]
gm = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Global Macro']['returns'][[gm_strat]], False)
gm = dm.merge_data_frames(gm, liq_alts_b.returns['Monthly'][['HFRX Macro/CTA']])
gm_dict = dm.get_period_dict(gm)
rp.get_strat_alts_report('{}_strat'.format(gm_strat), gm_dict)

#AR
ar_list = ['1907 ARP EM', '1907 III CV', '1907 III Class A','Acadian Commodity AR', 'Blueshift', 'Duality', 'Elliott']
ar_strat = ar_list[3]
ar = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Absolute Return']['returns'][[ar_strat]], False)
ar = dm.merge_data_frames(ar, liq_alts_b.returns['Monthly'][['HFRX Absolute Return']])
ar_dict = dm.get_period_dict(ar)
rp.get_strat_alts_report('{}_strat'.format(ar_strat), ar_dict)

#TF
tf_list = ['1907 ARP TF', '1907 Campbell TF', '1907 Systematica TF', 'One River Trend']
tf_strat = tf_list[0]
tf = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Trend Following']['returns'][[tf_strat]], False)
tf = dm.merge_data_frames(tf, liq_alts_b.returns['Monthly'][['SG Trend']])
tf_dict = dm.get_period_dict(tf)
rp.get_strat_alts_report('{}_strat'.format(tf_strat), tf_dict)

#Agg
liq_alts_list = ['Total Liquid Alts', 'Global Macro', 'Absolute Return', 'Trend Following']
liq_alts_strat = liq_alts_list[0]
liq_alts = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_p.sub_ports['Total Liquid Alts']['returns'][[liq_alts_strat]], False)
liq_alts = dm.merge_data_frames(liq_alts, liq_alts_b.returns['Monthly'][['Liquid Alts Bmk']])
liq_alts_dict = dm.get_period_dict(liq_alts)
rp.get_strat_alts_report('{}_strat'.format(liq_alts_strat), liq_alts_dict)


liq_alts_ret = dh.read_ret_data(dh.LIQ_ALTS_PORT_DATA_FP, 'returns')
arp_strat = 'Total Liquid Alts'
arp = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_ret[[arp_strat]], False)
arp = dm.merge_data_frames(arp, liq_alts_b.returns['Monthly'][['Liquid Alts Bmk']])
arp_dict = dm.get_period_dict(arp)
rp.get_strat_alts_report('{}-2_strat'.format(arp_strat), arp_dict)




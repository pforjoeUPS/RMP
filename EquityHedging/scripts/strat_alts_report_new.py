# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 07:35:12 2023

@author: NVG9HXP
"""

from EquityHedging.datamanager import data_handler as dh, data_manager_new as dm, data_xformer_new as dxf
from EquityHedging.datamanager import data_lists as dl
from EquityHedging.reporting.excel import new_reports as rp

LIQ_ALTS_FP = dl.DATA_FP + 'liq_alts\\'
la_dh = dh.LiqAltsPortHandler()
la_bmk_dh = dh.LiqAltsBmkDataHandler()

# AR strats
# fixed income rv
welwing = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'welwing.xlsx')
lmr_rates = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'lmr_rates.xlsx')
wb_rv = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'whitebox.xlsx', sheet_name='rv')
grv = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'capula_grv.xlsx')

# Quant/ML
eg = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'eg.xlsx')
voleon = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'voleon.xlsx')
east_one = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'east_one.xlsx')
east_value = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'east_value.xlsx')
voloridge = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'voloridge.xlsx')
fora = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'fora.xlsx')
two_sigma = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'two_sigma.xlsx')  # Two Sigma AR, Two Sigma AR Enhanced

# Systematic
gemini = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'gemini.xlsx')
magnetar = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'magnetar.xlsx')
newton_dfp = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'newton.xlsx', sheet_name='dfp')

# Discretionary
hbk = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'hbk.xlsx')
lmr_multi = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'lmr_multi.xlsx')
tcc = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'tcc.xlsx')
wb_ms = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'whitebox.xlsx', sheet_name='ms')
kawa = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'kawa.xlsx')
lab = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'LAB.xlsx')
taf = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'taf.xlsx')
lab_live = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'LAB.xlsx', sheet_name='live')
rathmore = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'rathmore.xlsx')
dymon_asia = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'dymon_asia.xlsx')

# EQ L/S
eof = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'eof.xlsx')
aleyska = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'aleyska.xlsx')

sub_port = 'Absolute Return'
ar_prelims_list = [aleyska, eof, gemini, grv, kawa, lab, lab_live, lmr_multi, lmr_rates, taf, tcc, two_sigma, voleon,
                   voloridge, wb_rv, wb_ms, welwing, dymon_asia]

ar_prelims_df = dm.merge_df_lists(ar_prelims_list, drop_na=False)
ar_prelims_df = ar_prelims_df.iloc[100:, ]
ar_prelims_df = ar_prelims_df[:-1]
for col in ar_prelims_df:
    if col not in la_dh.bmk_key.values():
        la_dh.bmk_key[col] = la_dh.sub_ports_bmk_key[sub_port]
ar_prelims_df = dm.merge_dfs(la_dh.sub_ports[sub_port]['returns'], ar_prelims_df, drop_na=False)

la_dh.sub_ports[sub_port]['returns'] = dm.copy_data(ar_prelims_df)
ar_prelims_rp = rp.AltsReport('ar_analysis', la_dh, sub_port=sub_port, add_composite_data=False,
                              include_dd=True, include_quantile=True, include_best_worst_pd=True)
ar_prelims_rp.run_report()

# GM strats
# discretionary
haidar = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'haidar.xlsx')
rokos = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'rokos.xlsx')
alphadyne = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'alphadyne.xlsx')
caygan = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'caygan.xlsx')
edl = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'edl.xlsx')

# systematic
gqm = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'graham.xlsx')[['GQM-A', 'GQM-B', 'GQM-15 vol']]
gmo_sys = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'gmo_sys.xlsx')
campbell_ar = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'campbell_ar.xlsx')
campbell_ar_ex_mkt = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'campbell_ar.xlsx', sheet_name='ex_mkt')
campbell_ar_no_tf = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'campbell_ar.xlsx', sheet_name='ex_trend')

# em
astignes = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'astignes.xlsx')
dymon_asia = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'dymon_asia.xlsx')
complus = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'complus.xlsx')
enko = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'enko.xlsx')
modular = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'modular.xlsx')
br_disc = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'br_master.xlsx')
kirkos = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'kirkos.xlsx')

sub_port = 'Global Macro'

gm_prelims_list = [edl, haidar, rokos, alphadyne, caygan, gqm, gmo_sys, campbell_ar, campbell_ar_no_tf, astignes,
                   dymon_asia, complus, enko, modular, br_disc, kirkos]

gm_prelims_df = dm.merge_df_lists(gm_prelims_list, drop_na=False)
for col in gm_prelims_df:
    if col not in la_dh.bmk_key.values():
        la_dh.bmk_key[col] = la_dh.sub_ports_bmk_key[sub_port]
gm_prelims_df = dm.merge_dfs(la_dh.sub_ports[sub_port]['returns'], gm_prelims_df, drop_na=False)

la_dh.sub_ports[sub_port]['returns'] = dm.copy_data(gm_prelims_df)
gm_prelims_rp = rp.AltsReport('gm_analysis', la_dh, sub_port=sub_port, add_composite_data=False,
                              include_quantile=True, include_dd=True, include_best_worst_pd=True)
gm_prelims_rp.run_report()
# TF strats
# Pure Trend
welton_tf = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'welton_tf.xlsx')
welton_tf_strats = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'welton_tf.xlsx', sheet_name='strats')
welton_tf_hypo = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'welton_tf.xlsx', sheet_name='hypo')
aqr_tf = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'aqr_tf.xlsx')
aspect = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'aspect.xlsx')
# aspect_alt = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'aspect.xlsx')[['Aspect-Alt TF']]
# aspect_alt_chn = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'aspect.xlsx')[['Aspect-Alt/China TF']]
# aspect_alt_man = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'aspect.xlsx')[['Aspect-Alt TF Mandate']]
newton_tf = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'newton.xlsx')[['Newton Trend']]
one_river_alt = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'one_river_alt.xlsx', sheet_name='data-alt')
transtrend = dxf.get_new_strat_data(file_path=LIQ_ALTS_FP+'transtrend.xlsx')

# hfrxsvd_aifa= pd.read_excel(dmo.DATA_FP + 'liq_alts\\aifa.xlsx', sheet_name='hfrxsvd', index_col=0)
# hfrxsvd_aifa= dxf.get_data_dict(hfrxsvd_aifa)

# custom_bmks = dxf.transform_bbg_data(dmo.DATA_FP + 'liq_alts\\custom_bmk.xlsx', sheet_name='data', freq='1D')
# custom_bmks = dmo.get_data_dict(custom_bmks)

# bmk_analysis = dmo.merge_dicts(hfrxsvd_aifa, custom_bmks)
# bmk_analysis = dmo.merge_dicts(liq_alts_b.mkt_returns, custom_bmks, True)

# for key in bmk_analysis:
#     print(key)
#     include_fi = False if key=='Daily' else True
#     rpo.get_alts_report('Bmk-analysis-{}'.format(key), dmo.get_period_dict(bmk_analysis[key], freq=dmo.switch_string_freq(key)), include_fi=include_fi)


# EDL
file_path = LIQ_ALTS_FP+'welton_tf.xlsx'
sheet_name = 'data'
strat_dh = dh.LiquidAltsStratDataHandler(file_path=file_path, sheet_name=sheet_name, bmk_name='SG Trend')
strat_rp = rp.StratAltsReport('welton_tf-test', data_handler=strat_dh, include_hf=False)
strat_rp.run_report()

# GM
# gm_list = ['Bridgewater Alpha', 'DE Shaw Oculus Fund', 'Element Capital', 'JSC Vantage', 'Capula TM Fund', 'KAF',
#            'Global Macro']
# gm_strat = gm_list[1]
# gm_dh = dh.DataHandler()
# gm = dmo.merge_dfs(la_p_dh.mkt_returns, la_p_dh.returns[[gm_strat]], False)
# gm = dmo.merge_dfs(gm, la_p_dh.bmk_returns[['HFRX Macro/CTA']])
# gm_dict = dmo.get_period_dict(gm)
# rpo.get_strat_alts_report('{}_strat'.format(gm_strat), gm_dict)
#
# # AR
# ar_list = ['1907 ARP EM', '1907 III CV', '1907 III Class A', 'Acadian Commodity AR', 'Blueshift', 'Duality', 'Elliott']
# ar_strat = ar_list[3]
# ar = dmo.merge_dfs(la_p_dh.mkt_returns[['MSCI ACWI', 'FI Benchmark']],
#                    la_p_dh.sub_ports['Absolute Return']['bmk_returns'][[ar_strat]], False)
# ar = dmo.merge_dfs(ar, la_p_dh.bmk_returns[['HFRX Absolute Return']])
# ar_dict = dmo.get_period_dict(ar)
# rpo.get_strat_alts_report('{}_strat-Nov2023'.format(ar_strat), ar_dict)
#
# # TF
# tf_list = ['1907 Campbell TF', '1907 Systematica TF', 'One River Trend']
# tf_strat = tf_list[0]
# tf = dmo.merge_dfs(la_p_dh.mkt_returns['MSCI ACWI', 'FI Benchmark'], la_p_dh.returns[[tf_strat]], False)
# tf = dmo.merge_dfs(tf, la_p_dh.bmk_returns[['SG Trend']])
# tf_dict = dmo.get_period_dict(tf)
# rpo.get_strat_alts_report('{}_strat'.format(tf_strat), tf_dict)
#
# # Agg
# liq_alts_list = ['Total Liquid Alts', 'Global Macro', 'Absolute Return', 'Trend Following']
# liq_alts_strat = liq_alts_list[0]
# liq_alts = dmo.merge_dfs(la_p_dh.mkt_returns,
#                          la_p_dh.sub_ports['Total Liquid Alts']['bmk_returns'][[liq_alts_strat]], False)
# liq_alts = dmo.merge_dfs(liq_alts, la_p_dh.bmk_returns[['Liquid Alts Bmk']])
# liq_alts = liq_alts.iloc[(165 - 86):, ]
# liq_alts_dict = dmo.get_period_dict(liq_alts)
# rpo.get_strat_alts_report('{}_strat'.format(liq_alts_strat), liq_alts_dict)

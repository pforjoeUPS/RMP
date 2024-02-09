# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 07:35:12 2023

@author: NVG9HXP
"""

from EquityHedging.datamanager import data_handler as dh, data_manager_new as dm, data_xformer_new as dxf
from EquityHedging.datamanager import data_manager as dmo
from EquityHedging.reporting.excel import new_reports as rp, reports as rpo

LIQ_ALTS_FP = dh.DATA_FP + 'liq_alts\\'
la_p_dh = dh.LiqAltsPortHandler()
la_b_dh = dh.LiqAltsBmkDataHandler()

penso = {'filename': 'penso_returns.xlsx', 'sheet_name': 'data'}
welwing = {'filename': 'welwing.xlsx', 'sheet_name': 'data'}
gemini = {'filename': 'gemini.xlsx', 'sheet_name': 'data'}
jsc = {'filename': 'jsc.xlsx', 'sheet_name': 'data'}
tmf = {'filename': 'tmf.xlsx', 'sheet_name': 'data'}
kaf = {'filename': 'kaf.xlsx', 'sheet_name': 'data'}
eof = {'filename': 'eof.xlsx', 'sheet_name': 'data'}
br_sys = {'filename': 'br_explorer.xlsx', 'sheet_name': 'data'}
br_disc = {'filename': 'br_master.xlsx', 'sheet_name': 'data'}
eg = {'filename': 'eg.xlsx', 'sheet_name': 'data'}
campbell_ar = {'filename': 'campbell_ar.xlsx', 'sheet_name': 'data'}
campbell_ar_ex_mkt = {'filename': 'campbell_ar.xlsx', 'sheet_name': 'ex_mkt'}
campbell_ar_strats = {'filename': 'campbell_ar_strats.xlsx', 'sheet_name': 'data'}
castle_hook = {'filename': 'castle_hook.xlsx', 'sheet_name': 'data'}
welton_gm = {'filename': 'welton_gm.xlsx', 'sheet_name': 'data'}
welton_gm_strats = {'filename': 'welton_gm.xlsx', 'sheet_name': 'strats'}
welton_gm_hypo = {'filename': 'welton_gm.xlsx', 'sheet_name': 'hypo'}
welton_tf = {'filename': 'welton_tf.xlsx', 'sheet_name': 'data'}
welton_tf_strats = {'filename': 'welton_tf.xlsx', 'sheet_name': 'strats'}
welton_tf_hypo = {'filename': 'welton_tf.xlsx', 'sheet_name': 'hypo'}
haidar = {'filename': 'welton_tf.xlsx', 'sheet_name': 'data'}
voleon = {'filename': 'voleon.xlsx', 'sheet_name': 'data'}
rokos = {'filename': 'rokos.xlsx', 'sheet_name': 'data'}
modular = {'filename': 'modular.xlsx', 'sheet_name': 'data'}
discus = {'filename': 'cfm.xlsx', 'sheet_name': 'discus'}
stratus = {'filename': 'cfm.xlsx', 'sheet_name': 'stratus'}
sgm = {'filename': 'cfm.xlsx', 'sheet_name': 'sgm'}
sspf = {'filename': 'sspf.xlsx', 'sheet_name': 'data'}
gm_qm_a = {'filename': 'graham.xlsx', 'sheet_name': 'quant_macro'}  # [['Graham Quant Macro-A']]
gm_qm_b = {'filename': 'graham.xlsx', 'sheet_name': 'quant_macro'}  # [['Graham Quant Macro-B']]
gm_qm = {'filename': 'graham.xlsx', 'sheet_name': 'quant_macro'}
gm_qm_hypo = {'filename': 'graham.xlsx', 'sheet_name': 'hypo'}
adapt = {'filename': 'adapt.xlsx', 'sheet_name': 'data'}
aqr_gm = {'filename': 'aqr_gm.xlsx', 'sheet_name': 'data'}
aqr_tf = {'filename': 'aqr_tf.xlsx', 'sheet_name': 'data'}
aspect = {'filename': 'aspect.xlsx', 'sheet_name': 'data'}
# aspect_alt = dm.get_new_strat_data('liq_alts\\aspect.xlsx'[['Aspect-Alt TF']]
# aspect_alt_chn = dm.get_new_strat_data('liq_alts\\aspect.xlsx'[['Aspect-Alt/China TF']]
# aspect_alt_man = dm.get_new_strat_data('liq_alts\\aspect.xlsx'[['Aspect-Alt TF Mandate']]
hbk = {'filename': 'hbk.xlsx', 'sheet_name': 'data'}
centiva = {'filename': 'centiva.xlsx', 'sheet_name': 'data'}
hypo = {'filename': 'demo_port.xlsx', 'sheet_name': 'data'}
astignes = {'filename': 'astignes.xlsx', 'sheet_name': 'data'}
east_one = {'filename': 'east_one.xlsx', 'sheet_name': 'data'}
east_value = {'filename': 'east_value.xlsx', 'sheet_name': 'data'}
magnetar = {'filename': 'magnetar.xlsx', 'sheet_name': 'data'}
edl = {'filename': 'edl.xlsx', 'sheet_name': 'data_a'}
edl_c = {'filename': 'edl.xlsx', 'sheet_name': 'data'}
gmo_sys = {'filename': 'gmo_sys.xlsx', 'sheet_name': 'data'}
voloridge = {'filename': 'voloridge.xlsx', 'sheet_name': 'data'}
wellington = {'filename': 'wellington.xlsx', 'sheet_name': 0}
lmr_rates = {'filename': 'lmr_rates.xlsx', 'sheet_name': 'data'}
lmr_multi = {'filename': 'lmr_multi.xlsx', 'sheet_name': 'data'}
newton_tf = {'filename': 'newton.xlsx', 'sheet_name': 'data'}  # [['Newton Trend']]
newton_gm = {'filename': 'newton.xlsx', 'sheet_name': 'data'}  # [['Newton Macro']]
newton_dfp = {'filename': 'newton.xlsx', 'sheet_name': 'dfp'}
newton_carry = {'filename': 'newton.xlsx', 'sheet_name': 'carry'}
tcc = {'filename': 'tcc.xlsx', 'sheet_name': 'data'}
one_river_alt = {'filename': 'one_river_alt.xlsx', 'sheet_name': 'data-alt'}
transtrend = {'filename': 'transtrend.xlsx', 'sheet_name': 'data'}
rathmore = {'filename': 'rathmore.xlsx', 'sheet_name': 'data'}
dymon_asia = {'filename': 'dymon_asia.xlsx', 'sheet_name': 'data'}
rv_3x = {'filename': 'rv_capital.xlsx', 'sheet_name': '3x'}
rv = {'filename': 'rv_capital.xlsx', 'sheet_name': 'data'}
aleyska = {'filename': 'aleyska.xlsx', 'sheet_name': 'data'}
fora = {'filename': 'fora.xlsx', 'sheet_name': 'data'}
gresham = {'filename': 'gresham.xlsx', 'sheet_name': 'data'}
wb_rv = {'filename': 'whitebox.xlsx', 'sheet_name': 'rv'}
wb_ms = {'filename': 'whitebox.xlsx', 'sheet_name': 'ms'}
hfrx_ew = {'filename': 'hfrxew.xlsx', 'sheet_name': 'data'}
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
filepath = LIQ_ALTS_FP + edl_c['filename']
sheet_name = edl_c['sheet_name']
strat_dh = dh.LiquidAltsStratDataHandler(filepath=filepath, sheet_name=sheet_name, bmk_name='HFRX Macro/CTA')
strat_rp = rp.StratAltsReport('edl-test', data_handler=strat_dh, include_hf=True)
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

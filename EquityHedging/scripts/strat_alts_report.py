# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 07:35:12 2023

@author: NVG9HXP
"""
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.datamanager import data_xformer as dt
from EquityHedging.datamanager import data_xformer_new as dxf
from EquityHedging.analytics import drawdowns as dd
from EquityHedging.analytics import summary
from EquityHedging.analytics import returns_stats as rs
import pandas as pd
import copy
liq_alts_p = dh.liqAltsPortHandler(include_cm=False, include_fx=False)
liq_alts_b = dh.liqAltsBmkHandler1()

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
campbell_ar_ex_mkt = dm.get_new_strat_data('liq_alts\\campbell_ar.xlsx', sheet_name='ex_mkt')
campbell_ar_strats = dm.get_new_strat_data('liq_alts\\campbell_ar_strats.xlsx')
castle_hook = dm.get_new_strat_data('liq_alts\\castle_hook.xlsx')
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
discus = dm.get_new_strat_data('liq_alts\\cfm.xlsx',sheet_name='discus')
stratus = dm.get_new_strat_data('liq_alts\\cfm.xlsx', sheet_name='stratus')
sgm = dm.get_new_strat_data('liq_alts\\cfm.xlsx',sheet_name='sgm')
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
edl_c = dm.get_new_strat_data('liq_alts\\edl.xlsx')
gmo_sys = dm.get_new_strat_data('liq_alts\\gmo_sys.xlsx')
voloridge = dm.get_new_strat_data('liq_alts\\voloridge.xlsx')
wellington = dm.get_new_strat_data('liq_alts\\wellington.xlsx', 0)
lmr_rates = dm.get_new_strat_data('liq_alts\\lmr_rates.xlsx')
lmr_multi = dm.get_new_strat_data('liq_alts\\lmr_multi.xlsx')
newton_tf = dm.get_new_strat_data('liq_alts\\newton.xlsx')[['Newton Trend']]
newton_gm = dm.get_new_strat_data('liq_alts\\newton.xlsx')[['Newton Macro']]
newton_dfp = dm.get_new_strat_data('liq_alts\\newton.xlsx', sheet_name='dfp')
tcc = dm.get_new_strat_data('liq_alts\\tcc.xlsx')
one_river_alt = dm.get_new_strat_data('liq_alts\\one_river_alt.xlsx', sheet_name='data-alt')
transtrend = dm.get_new_strat_data('liq_alts\\transtrend.xlsx')
rathmore = dm.get_new_strat_data('liq_alts\\rathmore.xlsx')
dymon_asia = dm.get_new_strat_data('liq_alts\\dymon_asia.xlsx')
rv_3x = dm.get_new_strat_data('liq_alts\\rv_capital.xlsx', sheet_name='3x')
rv = dm.get_new_strat_data('liq_alts\\rv_capital.xlsx')
aleyska = dm.get_new_strat_data('liq_alts\\aleyska.xlsx')
fora = dm.get_new_strat_data('liq_alts\\fora.xlsx')
wb_rv = dm.get_new_strat_data('liq_alts\\whitebox.xlsx', sheet_name='rv')
wb_ms = dm.get_new_strat_data('liq_alts\\whitebox.xlsx', sheet_name='ms')

hfrxsvd_aifa= dm.pd.read_excel(dm.DATA_FP+'liq_alts\\aifa.xlsx', sheet_name='hfrxsvd', index_col=0)
hfrxsvd_aifa= dm.get_data_dict(hfrxsvd_aifa)

custom_bmks = dxf.transform_bbg_data(dm.DATA_FP+'liq_alts\\custom_bmk.xlsx', sheet_name='data', freq='1D')
custom_bmks = dm.get_data_dict(custom_bmks)

bmk_analysis = dm.merge_dicts(hfrxsvd_aifa, custom_bmks)
bmk_analysis = dm.merge_dicts(liq_alts_b.mkt_returns, custom_bmks, True)

for key in bmk_analysis:
    print(key)
    include_fi = False if key=='Daily' else True
    rp.get_alts_report('Bmk-analysis-{}'.format(key),dm.get_period_dict(bmk_analysis[key], freq=dm.switch_string_freq(key)), include_fi=include_fi)

#GM
#Penso
gm = dm.merge_data_frames(liq_alts_p.mkt_returns, wb_ms, False)
gm = dm.merge_data_frames(gm, liq_alts_p.bmk_returns[['HFRX Absolute Return']])
gm_dict = dm.get_period_dict(gm)
rp.get_strat_alts_report('whitebox_ms_strat', gm_dict)

#GM
gm_list = ['1907 Penso Class A', 'Bridgewater Alpha', 'DE Shaw Oculus Fund','Element Capital', 'Global Macro']
gm_strat = gm_list[1]
gm = dm.merge_data_frames(liq_alts_p_1.mkt_returns, liq_alts_p.returns[[gm_strat]], False)
gm = dm.merge_data_frames(gm, liq_alts_p.bmk_returns[['HFRX Macro/CTA']])
gm_dict = dm.get_period_dict(gm)
rp.get_strat_alts_re
port('{}_strat'.format(gm_strat), gm_dict)

#AR
ar_list = ['1907 ARP EM', '1907 III CV', '1907 III Class A','Acadian Commodity AR', 'Blueshift', 'Duality', 'Elliott']
ar_strat = ar_list[3]
ar = dm.merge_data_frames(liq_alts_p.mkt_returns, liq_alts_p.sub_ports['Absolute Return']['returns'][[ar_strat]], False)
ar = dm.merge_data_frames(ar, liq_alts_p.bmk_returns[['HFRX Absolute Return']])
ar_dict = dm.get_period_dict(ar)
rp.get_strat_alts_report('{}_strat'.format(ar_strat), ar_dict)

#TF
tf_list = ['1907 Campbell TF', '1907 Systematica TF', 'One River Trend']
tf_strat = tf_list[0]
tf = dm.merge_data_frames(liq_alts_p.mkt_returns, liq_alts_p.returns[[tf_strat]], False)
tf = dm.merge_data_frames(tf, liq_alts_p.bmk_returns[['SG Trend']])
tf_dict = dm.get_period_dict(tf)
rp.get_strat_alts_report('{}_strat'.format(tf_strat), tf_dict)

#Agg
liq_alts_list = ['Total Liquid Alts', 'Global Macro', 'Absolute Return', 'Trend Following']
liq_alts_strat = liq_alts_list[0]
liq_alts = dm.merge_data_frames(liq_alts_p.mkt_returns, liq_alts_p.sub_ports['Total Liquid Alts']['returns'][[liq_alts_strat]], False)
liq_alts = dm.merge_data_frames(liq_alts, liq_alts_p.bmk_returns[['Liquid Alts Bmk']])
liq_alts = liq_alts.iloc[(165-86):,]
liq_alts_dict = dm.get_period_dict(liq_alts)
rp.get_strat_alts_report('{}_strat'.format(liq_alts_strat), liq_alts_dict)

import copy
strat_dict = copy.deepcopy(gm_dict)
mgr = strat_dict['Full'].columns[2]

dd_dict = {}
for strat in strat_dict['Full']:
    if strat == mgr:
        dd_dict['{} Drawdown Statistics'.format(strat)] = dd.get_worst_drawdowns(strat_dict['Full'][[strat]],recovery=True)
    else:
        dd_dict['{} vs {} Drawdowns'.format(mgr, strat)] = dd.get_co_drawdowns(strat_dict['Full'][[strat]], strat_dict['Full'][[mgr]])


liq_alts_ret = dh.read_ret_data(dh.LIQ_ALTS_PORT_DATA_FP, 'returns')
arp_strat = 'Total Liquid Alts'
arp = dm.merge_data_frames(liq_alts_p.bmk_returns['Monthly'], liq_alts_ret[[arp_strat]], False)
arp = dm.merge_data_frames(arp, liq_alts_b.returns['Monthly'][['Liquid Alts Bmk']])
arp_dict = dm.get_period_dict(arp)
rp.get_strat_alts_report('{}-2_strat'.format(arp_strat), arp_dict)

returns=edl_c.copy()
returns_dd = returns.copy()
recovery=True
drawdowns = dd.run_drawdown(returns_dd)
worst_drawdowns = []
#get the worst drawdown
draw = dd.get_drawdown_dates(drawdowns)
#add recovery data
if recovery:
    draw = dd.get_recovery_data(returns, draw)
#collect
worst_drawdowns.append(draw)
#set i to 1, because we will be starting from 1 for the number of
#drawdowns desired from num_worst
for i in range(1,):
    try:
        #remove data from last drawdown from the returns data
        mask = (returns_dd.index>=draw['Peak']) & (returns_dd.index<=draw['Trough'])
        returns_dd = returns_dd.loc[~mask]
        drawdowns = dd.run_drawdown(returns_dd)
        draw = dd.get_drawdown_dates(drawdowns)
        #add recovery data
        if recovery:
            draw = dd.get_recovery_data(returns, draw)
        #collect
        worst_drawdowns.append(draw)
    except:
        print("No more drawdowns...")

drawdowns = dd.run_drawdown(returns)
worst_drawdowns = []
#get the worst drawdown
draw = dd.get_drawdown_dates(drawdowns)
#collect
worst_drawdowns.append(draw)

def get_recovery_data(returns, draw):
    #get strat name
    strat=returns.columns[0]
    #get index/price data
    ret_idx = dm.get_prices_df(returns)
    
    #remove data before drawdown
    mask_rec = (ret_idx.index>=draw['Trough'])
    ret_idx_1 = ret_idx.iloc[mask_rec]
    
    #find end of dd date
    peak_idx = ret_idx[ret_idx.index==draw['Peak']]
    try:
        draw['End'] = ret_idx_1[ret_idx_1[strat].gt(peak_idx[strat][0])].index[0]
        end_date = draw['End']
    except IndexError:
        #if recover not done, pick last period as end date
        draw['End'] = float("nan")
        end_date = ret_idx_1.last_valid_index()
    
    
    #get dd length
    mask_dd = (returns.index>=draw['Peak']) & (returns.index<=end_date )
    draw['Length'] = len(returns.iloc[mask_dd])-1
    
    #get recovery lenth    
    mask_recov=(returns.index>=draw['Trough']) & (returns.index<=end_date)
    draw['Recovery'] = len(returns.iloc[mask_recov])-1
    
    #reorder draw dict
    desired_order_list = ['Peak', 'Trough', 'End','Drawdown', 'Length', 'Recovery']
    return draw = {key: draw[key] for key in desired_order_list}    


#recovery

returns = edl_c.copy()
strat=returns.columns[0]
ret_idx = dm.get_prices_df(returns)
drawdowns = dd.run_drawdown(returns)
worst_drawdowns = []
draw = dd.get_drawdown_dates(drawdowns)
draw = get_recovery_data(returns, draw)

mask_rec = (ret_idx.index>=draw['trough'])
ret_idx_1 = ret_idx.iloc[mask_rec]
peak_idx = ret_idx[ret_idx.index==draw['peak']]
try:
    draw['end'] = ret_idx_1[ret_idx_1[strat].gt(peak_idx[strat][0])].index[0]
    end_date = draw['end']
except IndexError:
    #if recover not done, pick last period as end date
    draw['end'] = float("nan")
    end_date = ret_idx_1.last_valid_index()
    
draw['end'] = ret_idx_1[ret_idx_1[strat].gt(peak_idx[strat][0])].index[0]

# recov_date = ret_idx_1[ret_idx_1[strat].gt(peak_idx[strat][0])].index[0]

mask_dd = (returns.index>=draw['peak']) & (returns.index<=end_date )

mask_recov=(returns.index>=draw['trough']) & (returns.index<=end_date)
dd_periods = returns.iloc[mask_dd]

recov_periods=returns.iloc[mask_recov]
draw['recovery'] = len(recov_periods)-1
draw['length'] = len(dd_periods)-1
desired_order_list = ['peak', 'trough', 'end','drawdown', 'length', 'recovery']
draw = {k: draw[k] for k in desired_order_list}

worst_drawdowns.append(draw)

num_worst=5
for i in range(1,num_worst):
    try:
        #remove data from last drawdown from the returns data
        mask = (returns.index>=draw['Peak']) & (returns.index<=draw['Trough'])
        returns_dd = returns.loc[~mask]
        drawdowns = dd.run_drawdown(returns)
        draw = dd.get_drawdown_dates(drawdowns)
        draw = dd.get_recovery_data(returns, draw)
        worst_drawdowns.append(draw)
    except:
        print("No more drawdowns...")
pd.DataFrame(worst_drawdowns)
        
        
        
        mask_rec = (ret_idx.index>=draw['trough'])
        ret_idx_1 = ret_idx.iloc[mask_rec]
        peak_idx = ret_idx[ret_idx.index==draw['peak']]
        draw['end'] = ret_idx_1[ret_idx_1[strat].gt(peak_idx[strat][0])].index[0]
        worst_drawdowns.append(draw)
        # recov_date = ret_idx_1[ret_idx_1[strat].gt(peak_idx[strat][0])].index[0]

        mask_dd = (returns.index>=draw['peak']) & (returns.index<=draw['end'] )

        mask_recov=(returns.index>=draw['trough']) & (returns.index<=draw['end'] )
        dd_periods = returns.iloc[mask_dd]

        recov_periods=returns.iloc[mask_recov]
        draw['recovery'] = len(recov_periods)-1
        draw['length'] = len(dd_periods)-1
        draw = {k: draw[k] for k in desired_order_list}
        #collect
        worst_drawdowns.append(draw)
    except:
        print("No more drawdowns...")
pd.DataFrame(worst_drawdowns)

drawdowns.idxmin()[0]
peak_date = drawdowns[drawdowns.index <= trough_date]
peak_date = peak_date[peak_date>=0].dropna().index[-1]
num_worst=5
worst_dd = dd.get_worst_drawdowns(returns,num_worst)

end_list = []
recov_list = []
length_list = []
ret_idx = dm.get_prices_df(returns)

for i in range(0, num_worst):
    peak_date = worst_dd['peak'][i]
    trough_date = worst_dd['trough'][i]
    mask_rec = (ret_idx.index>=trough_date)
    ret_idx_1 = ret_idx.iloc[mask_rec]
    peak_idx = ret_idx[ret_idx.index==peak_date]
    recov_date = ret_idx_1[ret_idx_1[strat].gt(peak_idx[strat][0])].index[0]

    mask_recov=(returns.index>=trough_date) & (returns.index<=recov_date)
    mask_dd = (returns.index>=peak_date) & (returns.index<=recov_date)

    dd_periods = returns.iloc[mask_dd]
    recov_periods=returns.iloc[mask_recov]
    
    end_list.append(recov_date)
    recov_list.append(len(recov_periods)-1)
    length_list.append(len(dd_periods)-1)


worst_dd['end'] = end_list
worst_dd['recovery'] = recov_list
worst_dd['length'] = length_list
worst_dd = worst_dd[['peak', 'trough', 'end','drawdown', 'length', 'recovery']]
worst_dd

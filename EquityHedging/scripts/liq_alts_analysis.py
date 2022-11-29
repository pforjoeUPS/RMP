# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 23:50:46 2022

@author: NVG9HXP
"""

from EquityHedging.reporting.excel import reports as rp
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import returns_stats as rs
from EquityHedging.analytics import util

LIQ_ALTS_BMK_DICT = {'Global Macro': 'HFRX Macro/CTA',
                     'Trend Following': 'SG Trend',
                     'Absolute Return':'HFRX Absolute Return',
                     'Total Liquid Alts':'Liquid Alts Bmk'
                     }
include_fi = True
freq = '1M'
rfr = 0

liq_alts_p = dh.liqAltsPortHandler()
liq_alts_b = dh.liqAltsBmkHandler()

liq_alts_dict = {}

for key in liq_alts_p.sub_ports:
    for mgr in liq_alts_p.sub_ports[key]['mv'].columns:
        liq_alts_dict[mgr] = LIQ_ALTS_BMK_DICT[key]

returns_stats_dict = {}
for key in liq_alts_dict:
    print(key)
    temp_df = dm.merge_data_frames(liq_alts_b.bmk_returns['Monthly'],liq_alts_p.returns[[key]])
    bmk = liq_alts_dict[key]
    temp_df = dm.merge_data_frames(temp_df, liq_alts_b.returns['Monthly'][[bmk]])
    temp_df['Active'] = temp_df[key] - temp_df[bmk]
    eq_u_df = (temp_df[temp_df[liq_alts_p.equity_bmk] > 0])
    eq_d_df = (temp_df[temp_df[liq_alts_p.equity_bmk] <= 0])
    mkt_value = liq_alts_p.mvs[key][-1]
    obs = len(liq_alts_p.returns[key])
    port_strat = temp_df[key]
    port_index = dm.get_price_series(port_strat)
    bmk_strat = temp_df[bmk]
    bmk_index = dm.get_price_series(bmk_strat)
    mkt_strat = temp_df[liq_alts_p.equity_bmk]
    if include_fi:
        fi_mkt_strat = temp_df['FI Benchmark']
        fi_u_df = (temp_df[temp_df[liq_alts_p.fi_bmk] > 0])
        fi_d_df = (temp_df[temp_df[liq_alts_p.fi_bmk] <= 0])
        
    active_strat = temp_df['Active']
    
    ann_ret = rs.get_ann_return(port_strat, freq)
    ann_ret_b = rs.get_ann_return(bmk_strat, freq)
    ann_ret_e = rs.get_ann_return(active_strat, freq)
    
    ann_vol = rs.get_ann_vol(port_strat, freq)
    ann_vol_b = rs.get_ann_vol(bmk_strat, freq)
    ann_vol_te = rs.get_ann_vol(active_strat, freq)
    
    down_dev = rs.get_updown_dev(port_strat, freq)
    down_dev_b = rs.get_updown_dev(bmk_strat, freq)
    down_dev_b = down_dev - down_dev_b
    
    max_dd = rs.get_max_dd(port_index)
    max_dd_b = rs.get_max_dd(bmk_index)
    max_dd_e = max_dd-max_dd_b
    
    skew = rs.get_skew(port_strat)
    skew_b = rs.get_skew(bmk_strat)
    skew_e = skew - skew_b
    
    kurt = rs.get_kurtosis(port_strat)
    kurt_b = rs.get_kurtosis(bmk_strat)
    kurt_e = kurt - kurt_b
    
    
    
    #var
    
    alpha = rs.get_alpha(port_strat,mkt_strat,freq,rfr)
    alpha_b = rs.get_alpha(bmk_strat,mkt_strat,freq,rfr)
    
    if include_fi:
        fi_alpha = rs.get_alpha(port_strat,fi_mkt_strat,freq,rfr)
        fi_alpha_b = rs.get_alpha(bmk_strat,fi_mkt_strat,freq,rfr)
    
    beta = rs.get_beta(port_strat,mkt_strat,freq)
    beta_b = rs.get_beta(bmk_strat,mkt_strat,freq)
    
    bull_beta = rs.get_beta(eq_u_df[key],eq_u_df[liq_alts_p.equity_bmk],freq)
    bull_beta_b = rs.get_beta(eq_u_df[bmk],eq_u_df[liq_alts_p.equity_bmk],freq)
    
    bear_beta = rs.get_beta(eq_d_df[key],eq_d_df[liq_alts_p.equity_bmk],freq)
    bear_beta_b = rs.get_beta(eq_d_df[bmk],eq_d_df[liq_alts_p.equity_bmk],freq)
    
    if include_fi:
        fi_mkt_strat = temp_df['FI Benchmark']
        fi_beta = rs.get_beta(port_strat,fi_mkt_strat,freq)
        fi_beta_b = rs.get_beta(bmk_strat,fi_mkt_strat,freq)
        
        fi_bull_beta = rs.get_beta(fi_u_df[key],fi_u_df[liq_alts_p.equity_bmk],freq)
        fi_bull_beta_b = rs.get_beta(fi_u_df[bmk],fi_u_df[liq_alts_p.equity_bmk],freq)
        
        fi_bear_beta = rs.get_beta(fi_d_df[key],fi_d_df[liq_alts_p.equity_bmk],freq)
        fi_bear_beta_b = rs.get_beta(fi_d_df[bmk],fi_d_df[liq_alts_p.equity_bmk],freq)
    
        fi_alpha = rs.get_alpha(port_strat,fi_mkt_strat,freq,rfr)
        fi_alpha_b = rs.get_alpha(bmk_strat,fi_mkt_strat,freq,rfr)
        
        
        
    ret_vol = rs.get_ret_vol_ratio(port_strat,freq)
    ret_vol_b = rs.get_ret_vol_ratio(bmk_strat,freq)
    
    sortino = rs.get_sortino_ratio(port_strat, freq)
    sortino_b = rs.get_sortino_ratio(bmk_strat, freq)
    
    ret_dd = rs.get_ret_max_dd_ratio(port_strat,port_index,freq)
    ret_dd_b = rs.get_ret_max_dd_ratio(bmk_strat,bmk_index,freq)
    
    #upside capture
    #downside capture
    #mar
    #cont to risk
    #%cont to risk
    
    returns_stats_dict[key] = [bmk,mkt_value, obs,
                               ann_ret, ann_ret_b, ann_ret_e,
                               ann_vol,ann_vol_b, ann_vol_te,
                               down_dev,down_dev_b,
                               max_dd,max_dd_b,max_dd_e,
                               skew, skew_b, skew_e,
                               kurt, kurt_b, kurt_e,
                               alpha, alpha_b,beta,beta_b,
                               bull_beta, bull_beta_b,bear_beta, bear_beta_b,
                               ret_vol,ret_vol_b,sortino, sortino_b,ret_dd, ret_dd_b]
    
    if include_fi:
        returns_stats_dict[key] = [bmk,mkt_value, obs,
                                   ann_ret,ann_ret_b,ann_ret_e,
                                   ann_vol,ann_vol_b,ann_vol_te,
                                   down_dev,down_dev_b,
                                   max_dd,max_dd_b,max_dd_e,
                                   skew,skew_b,skew_e,kurt,kurt_b,kurt_e,
                                   alpha,alpha_b,fi_alpha,fi_alpha_b,
                                   beta,beta_b,bull_beta,bull_beta_b,bear_beta,bear_beta_b,
                                   fi_beta,fi_beta_b,fi_bull_beta,fi_bull_beta_b,fi_bear_beta,fi_bear_beta_b,
                                   ret_vol,ret_vol_b,sortino,sortino_b,ret_dd,ret_dd_b]
dates = dm.get_min_max_dates(liq_alts_p.returns)


headers = ['Benchmark','Market Value as of {}'.format(str(dates['end']).split()[0]),'No. of Observations',
           'Port Return (Annualized)','Bmrk Return (Annualized)','Excess Return (Annualized)',
           'Port Vol (Annualized)','Bmrk Vol (Annualized)','Tracking Error (Annualized)',
           'Port Semideviation (Annualized, Minimum Acceptable Return = 0)',
           'Bmrk Semideviation (Annualized, Minimum Acceptable Return = 0)',
           'Port Maximum Drawdown','Bmrk Maximum Drawdown','Excess Maximum Drawdown',
           'Port Skewness','Bmrk Skewness','Excess Skewness',
           'Port Excess Kurtosis','Bmrk Excess Kurtosis','Difference in Excess Kurtosis (the definition here is port-bmrk)',
           # 'Port VaR95%','Bmrk VaR95%','Excess VaR95%','Port VaR95% in Dollar Amount','Port VaR95% in Dollar Amount as percentage of All Combined Portfolio Market Value',
           'Port Alpha','Bmrk Alpha','Port Beta', 'Bmrk Beta',
           'Port Bull Beta', 'Bmrk Bull Beta','Port Bear Beta', 'Bmrk Bear Beta',
           'Port Return/Vol Ratio (Annualized)','Bmrk Return/Vol Ratio (Annualized)',
           'Port Sortino Ratio (Annualized)','Bmrk Sortino Ratio (Annualized)',
           'Port Return/ Max Drawdown Ratio (Annualized)','Bmrk Return/ Max Drawdown Ratio (Annualized)']

fi_headers = ['Benchmark','Market Value as of {}'.format(str(dates['end']).split()[0]),'No. of Observations',
              'Port Return (Annualized)','Bmrk Return (Annualized)','Excess Return (Annualized)',
              'Port Vol (Annualized)','Bmrk Vol (Annualized)','Tracking Error (Annualized)',
              'Port Semideviation (Annualized, Minimum Acceptable Return = 0)',
              'Bmrk Semideviation (Annualized, Minimum Acceptable Return = 0)',
              'Port Maximum Drawdown','Bmrk Maximum Drawdown','Excess Maximum Drawdown',
              'Port Skewness','Bmrk Skewness','Excess Skewness',
              'Port Excess Kurtosis','Bmrk Excess Kurtosis',
              'Difference in Excess Kurtosis (the definition here is port-bmrk)',
              'Port Alpha','Bmrk Alpha','Port FI Alpha','Bmrk FI Alpha','Port Beta',
              'Bmrk Beta','Port Bull Beta', 'Bmrk Bull Beta','Port Bear Beta', 'Bmrk Bear Beta',
               'Port FI Beta', 'Bmrk FI Beta','Port FI Bull Beta', 'Bmrk FI Bull Beta',
               'Port FI Bear Beta', 'Bmrk FI Bear Beta',
               'Port Return/Vol Ratio (Annualized)','Bmrk Return/Vol Ratio (Annualized)',
               'Port Sortino Ratio (Annualized)','Bmrk Sortino Ratio (Annualized)',
               'Port Return/ Max Drawdown Ratio (Annualized)','Bmrk Return/ Max Drawdown Ratio (Annualized)']
        
if include_fi:
    df_returns_stats = util.convert_dict_to_df(returns_stats_dict, fi_headers)
else:
    df_returns_stats = util.convert_dict_to_df(returns_stats_dict, headers)   
    
    
writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')
workbook = writer.book
format1 = workbook.add_format()
format1.set_align('center')
format1.set_align('top')
format1.set_text_wrap('True')
format1.set_bold('True')
format1.set_font_size(9)
format2 = workbook.add_format({'num_format': '0.00%','font_size':'9','text_wrap':'True','align':'top'})
format3 = workbook.add_format({'num_format': '0.00','font_size':'9','text_wrap':'True','align':'top'})
format4 = workbook.add_format({'num_format': '0,00','font_size':'9','text_wrap':'True','align':'top'})
format5 = workbook.add_format({'num_format': '0','font_size':'9','text_wrap':'True','align':'top'})
format6 = workbook.add_format({'num_format': '0.0000','font_size':'9','text_wrap':'True','align':'top'})

table = df_returns_stats_t.copy()
table.index.rename = ['Portfolio']
table.reset_index(inplace=True)

# Output Statistics tab
table.to_excel(writer,sheet_name = 'Statistics',startcol=0, index=False)
statistics = writer.sheets['Statistics']
statistics.write_row('A1',list(table.columns), format1)
# statistics.write(0,0,'Portfolio',format1)
# statistics.write(0,1,'Benchmark',format1)
statistics.set_column('A:B', 18, format1)
statistics.set_column('C:D', 10, format4)
statistics.set_column('E:O', 11, format2)
statistics.set_column('P:U', 11, format3)
statistics.set_column('V:Y', 11, format2)
statistics.set_column('Z:AQ', 11, format3)
writer.save()
# -*- coding: utf-8 -*-
"""
This is a model for return-based analysis. An output example is available at 
X:\PUBLIC MARKETS\Analyst Research\Scripts\Return based analysis\output example.xlsx

Follow the instructions below for running the model:
(1) In the portfolio.xlsx file, fill 'date' and 'rf'(risk-free rate) columns, 
and add any number of portfolios and their benchmarks that you'd like to analyze starting from column C. Note that the
return types supported are daily, weekly, monthly, or quarterly. 
(2) In the selection.xlsx file, enter any number of portfolios for analysis. Note that the portfolio and benchmark names
have to match the ones in the portfolio.xlsx file, and marketValue needs to be assigned in Column C. 
(3) Open returnAnalysis.py file, hit F5 to execute the model.
(4) Select return type and rolling basis in the IPython Console. 
(5) Once the execution is complete, an Excel file should open up with outputs. Note that the return distribution
charts will be showing up in the IPython Console, not the Excel file.  
(6) For models that include Fama French factor analysis, talk to Grace. An output example is available at
X:\PUBLIC MARKETS\Analyst Research\Scripts\Return based analysis\output example - fama french factors.xlsx
The additions to this model include Factor Decomposition Chart in the bottom of the Statistics Visualization tab,
and an additional Rolling Factor Decomposition tab that visualizes factors on the user-selected rolling basis.   

"""

# Import modules
import pandas as pd
import numpy as np
# import statsmodels.formula.api as sm
import statsmodels.api as sm
import statsmodels.tools.tools as st
from scipy.stats import norm
import scipy.stats as s
from EquityHedging.analytics import returns_stats as rs

# Interactive User Input
print ('\nYou have entered a return-based analytical model. Please provide inputs below.')

frequency = ['DAILY','WEEKLY','MONTHLY','QUARTERLY']
while True:
    target = input("Return data(" + ', '.join(frequency) +'):')
    target = str.upper(target)
    if target in frequency:
        break
    else:
        print ('Sorry, the input is not valid. Please enter one of the options provided in the list.')

while True:
    try:
        rol_year = int(input('Number of years for rolling analysis:'))
        break
    except ValueError:
        print ('Sorry,the input is not valid. Please make sure the formats are correct and the start date is in the specified range.')

target = 'MONTHLY'
rol_year=3
inputs = {'DAILY':[252],'WEEKLY':[52],'MONTHLY':[12],'QUARTERLY':[4]}
inputsdf = pd.DataFrame(inputs)

annualize = int(inputsdf[target])
no_bins = 60

# Read excel files - portfolios, benchmakrs, risk-free rate, reference
files = np.array(['portfolio','selection'])
for a in files:
    globals()[a] = pd.read_excel(r"C:\Users\nvg9hxp\Documents\Projects\Return based analysis_python\%s.xlsx"%a)
selection = selection[['portfolio','benchmark','marketValue']].dropna(axis=0)

# Select portfolios, benchmarks and risk-free rate for analysis
portfolio = portfolio.set_index('date')
returns = np.array(['port', 'bmrk'])
names = np.array(['portfolio','benchmark'])
for a,b in zip(returns,names):
    globals()[a] = portfolio[selection[b]]
rf = portfolio['rf']

# Periods
ix = port.index
start = []
end = []
bmrk1 = pd.DataFrame()
port1 = pd.DataFrame()
rf1 = pd.DataFrame()

for i in range (len(selection['portfolio'])):
    sta = port.iloc[:,i].first_valid_index()
    en = port.iloc[:,i].last_valid_index()
    bm = pd.DataFrame(bmrk.iloc[:,i][sta:en])
    po = pd.DataFrame(port.iloc[:,i][sta:en])
    r = pd.DataFrame(rf)
    start.append(sta)
    end.append(en)
    bmrk1=pd.concat([bmrk1,bm],axis=1)
    port1=pd.concat([port1,po],axis=1)
    rf1 = pd.concat([rf1,r],axis=1)
    
bmrk = bmrk1
port = port1
rf = rf1
  
period = []
for i in range (len(start)):
    per = start[i].strftime('%m/%d/%Y')+'-'+end[i].strftime('%m/%d/%Y')
    period.append(per)
period = pd.Series(period,index=selection['portfolio'])

"""Analysis on Returns"""
# simple returns series
returns3 = np.array(['port', 'bmrk','rf'])
bmrk.columns = selection['portfolio']
rf.columns = selection['portfolio']
ups = np.array(['port_up','bmrk_up','rf_up'])
downs = np.array(['port_d','bmrk_d','rf_d'])
for a,b,c in zip(ups,downs,returns3):
    globals()[a] = np.where(bmrk>=0,globals()[c],np.nan)
    globals()[b] = np.where(bmrk<0,globals()[c],np.nan)
    globals()[a] = pd.DataFrame(globals()[a],index=port.index,columns=port.columns)    
    globals()[b] = pd.DataFrame(globals()[b],index=port.index,columns=port.columns)

# log returns series
returns2 = np.array(['port','bmrk','port_up','bmrk_up','port_d','bmrk_d','rf','rf_up','rf_d'])
logs = np.array(['port_log','bmrk_log','port_up_log','bmrk_up_log','port_d_log','bmrk_d_log','rf_log','rf_up_log','rf_d_log'])
for a,b in zip(logs,returns2):
    globals()[a] = np.log(1+globals()[b])

rfs = np.array(['rf_up','rf_d'])
rfs_log = np.array(['rf_up_log','rf_d_log'])
for a,b in zip(rfs_log,rfs):
    globals()[a] = np.log(1+globals()[b])

# geometric mean returns
returns_plus_1 = np.array(['port1','bmrk1','port_up1','bmrk_up1','port_d1','bmrk_d1','rf1'])
geo_means = np.array(['port_mean','bmrk_mean','port_up_mean','bmrk_up_mean','port_d_mean','bmrk_d_mean','rf_mean'])
for a,b,c in zip(returns_plus_1,geo_means,returns2):
    globals()[a] = 1+globals()[c]
    globals()[b] =pd.DataFrame.product(globals()[a])**(1/pd.DataFrame.count(globals()[a]))-1

# geometric mean returns (annualized)
geo_means_ann = np.array(['port_mean_ann','bmrk_mean_ann','port_up_mean_ann','bmrk_up_mean_ann','port_d_mean_ann','bmrk_d_mean_ann','rf_mean_ann'])
for a,b in zip(geo_means_ann,geo_means):
    globals()[a] = (1+globals()[b])**annualize-1

geo_means_ann_1 = np.array(['port_mean_ann_1','bmrk_mean_ann_1','port_up_mean_ann_1','bmrk_up_mean_ann_1','port_d_mean_ann_1','bmrk_d_mean_ann_1','rf_mean_ann_1'])
for a,b in zip(geo_means_ann_1,returns2):
    globals()[a] = rs.get_ann_return(globals()[b])

# arithmetic mean returns
ari_means = np.array(['port_ari_mean','bmrk_ari_mean','port_up_ari_mean','bmrk_up_ari_mean','port_d_ari_mean','bmrk_d_ari_mean','rf_ari_mean'])
for a,b in zip(ari_means,returns2):
    globals()[a] = pd.DataFrame.mean(globals()[b])

# logrithmic mean returns
log_means = np.array(['port_log_mean','bmrk_log_mean','port_up_log_mean','bmrk_up_log_mean','port_d_log_mean','bmrk_d_log_mean','rf_log_mean'])
for a,b in zip(log_means,logs):
    globals()[a] = pd.DataFrame.mean(globals()[b])
    
# logrithmic mean returns (annualized)
log_means_ann = np.array(['port_log_mean_ann','bmrk_log_mean_ann','port_up_log_mean_ann','bmrk_up_log_mean_ann','port_d_log_mean_ann','bmrk_d_log_mean_ann','rf_log_mean_ann'])
for a,b in zip(log_means_ann,log_means):
    globals()[a] = globals()[b]*annualize
    
# Total returns
trs = np.array(['port_tr','bmrk_tr','port_up_tr','bmrk_up_tr','port_d_tr','bmrk_d_tr','rf_tr'])
for a,b in zip(trs,returns2):
    globals()[a] = np.prod(1+globals()[b])-1    

# Cumulative returns
cums = np.array(['port_cum','bmrk_cum','port_up_cum','bmrk_up_cum','port_d_cum','bmrk_d_cum','rf_cum'])
for a,b in zip(cums,returns2): 
    globals()[a] = globals()[b].rolling(1).apply(lambda x: np.prod(1+x))
    globals()[a] = globals()[a].cumprod()
    globals()[a] = globals()[a]-1

# excess rolling return
rolls = np.array(['port_rr','bmrk_rr','port_up_rr','bmrk_up_rr','port_d_rr','bmrk_d_rr','rf_rr'])
for a,b in zip(rolls,returns2):
    globals()[a] = globals()[b].rolling(annualize*3).apply(lambda x: np.prod(1+x))
excess_rrs = np.array(['excess_rr','excess_up_rr','excess_d_rr'])
for a,b,c in zip(excess_rrs,rolls[[0,2,4]],rolls[[1,3,5]]):
    globals()[a] = globals()[b] - globals()[c]



"""Analysis on Risks"""
# Volatility (sample standard deviation)
stds = np.array(['port_std','bmrk_std','port_up_std','bmrk_up_std','port_d_std','bmrk_d_std','rf_std'])
for a,b in zip(stds,returns2):
    globals()[a] = pd.DataFrame.std(globals()[b])

# Annualized volatility
stds_ann = np.array(['port_std_ann','bmrk_std_ann','port_up_std_ann','bmrk_up_std_ann','port_d_std_ann','bmrk_d_std_ann','rf_std_ann'])
for a,b in zip(stds_ann,stds):
    globals()[a] = globals()[b]*np.sqrt(annualize)

# Volatility on log returns (sample standard deviation)
log_stds_per = np.array(['port_log_std_per','bmrk_log_std_per','port_up_log_std_per','bmrk_up_log_std_per','port_d_log_std_per','bmrk_d_log_std_per','rf_log_std_per'])
for a,b in zip(log_stds_per,logs):
    globals()[a] = pd.DataFrame.std(globals()[b])

# Annualized Volatility on log returns (sample standard deviation)
log_stds = np.array(['port_log_std','bmrk_log_std','port_up_log_std','bmrk_up_log_std','port_d_log_std','bmrk_d_log_std','rf_log_std'])
for a,b in zip(log_stds,logs):
    globals()[a] = pd.DataFrame.std(globals()[b])
    globals()[a] = globals()[a]*np.sqrt(annualize)


# Tracking Error (annualized)
terrors = np.array(['te','te_up','te_d'])
for a,b,c in zip(terrors,returns2[[0,2,4]],returns2[[1,3,5]]):
    globals()[a] = pd.DataFrame.std(globals()[b]-globals()[c])
    globals()[a] = globals()[a]*np.sqrt(annualize)
    
# Tracking Error (annualized) - log return
log_terrors = np.array(['te_log','te_log_up','te_log_d'])
for a,b,c in zip(log_terrors,logs[[0,2,4]],logs[[1,3,5]]):
    globals()[a] = pd.DataFrame.std(globals()[b]-globals()[c])
    globals()[a] = globals()[a]*np.sqrt(annualize)

# Downside risk (Semideviation, annualized)
belows = np.array(['port_below_mean','bmrk_below_mean'])
semis = np.array(['port_semi','bmrk_semi'])
for a,b,c,d in zip(belows,returns,ari_means[0:2],semis):
    globals()[a] = np.where(globals()[b]<globals()[c],globals()[b],np.nan)
    globals()[a] = pd.DataFrame(globals()[a],index=port.index,columns=port.columns)    
    globals()[d] = pd.DataFrame.std(globals()[a])
    globals()[d] = globals()[d]*np.sqrt(annualize)

# Downside risk 2 - minimum target set to zero (Semideviation, annualized)
belows2 = np.array(['port_below_zero','bmrk_below_zero'])
semis2 = np.array(['port_semi2','bmrk_semi2'])
for a,b,c,d in zip(belows2,returns,ari_means[0:2],semis2):
    globals()[a] = np.where(globals()[b]<0,globals()[b],np.nan)
    globals()[a] = pd.DataFrame(globals()[a],index=port.index,columns=port.columns)    
    globals()[d] = pd.DataFrame.std(globals()[a])
    globals()[d] = globals()[d]*np.sqrt(annualize)

# Downside risk - log return, annualized
log_belows = np.array(['port_log_below_mean','bmrk_log_below_mean'])
log_semis = np.array(['port_log_semi','bmrk_log_semi'])
for a,b,c,d in zip(log_belows,logs[0:2],log_means[0:2],log_semis): 
    globals()[a] = np.where(globals()[b]<globals()[c],globals()[b],np.nan)
    globals()[a] = pd.DataFrame(globals()[a],index=port.index,columns=port.columns)    
    globals()[d] = pd.DataFrame.std(globals()[a])
    globals()[d] = globals()[d]*np.sqrt(annualize)

# Downside risk 2 - log return, annualized
log_belows2 = np.array(['port_log_below_zero','bmrk_log_below_zero'])
log_semis2 = np.array(['port_log_semi2','bmrk_log_semi2'])
for a,b,c,d in zip(log_belows2,logs[0:2],log_means[0:2],log_semis2): 
    globals()[a] = np.where(globals()[b]<0,globals()[b],np.nan)
    globals()[a] = pd.DataFrame(globals()[a],index=port.index,columns=port.columns)    
    globals()[d] = pd.DataFrame.std(globals()[a])
    globals()[d] = globals()[d]*np.sqrt(annualize)

# Maximum drawdown

cums = np.array(['port_cum','bmrk_cum','port_up_cum','bmrk_up_cum','port_d_cum','bmrk_d_cum','rf_cum'])
for a,b in zip(cums,returns2[0:2]): 
    globals()[a] = globals()[b].rolling(1).apply(lambda x: np.prod(1+x))
    globals()[a] = globals()[a].cumprod()
    globals()[a] = globals()[a]-1


dds = np.array(['port_dd','bmrk_dd'])
mdds = np.array(['port_mdd','bmrk_mdd'])
cums1 = np.array(['port_cum1','bmrk_cum1'])
for a,b in zip(cums1,returns2[0:2]): 
    globals()[a] = globals()[b].fillna(0)
    globals()[a] = globals()[a].rolling(1).apply(lambda x: np.prod(1+x))
    globals()[a] = globals()[a].cumprod()

for a,b,c in zip(dds,mdds,cums1):
    maxx2 = pd.Series(dtype='float64')
    globals()[a] = (np.maximum.accumulate(globals()[c]) - globals()[c])/np.maximum.accumulate(globals()[c])
    globals()[b] = globals()[a].max()


# skewness
skews = np.array(['port_skew','bmrk_skew'])
for a,b in zip(skews,returns):
    globals()[a] = pd.DataFrame.skew(globals()[b])

# kurtosis
kurts = np.array(['port_kurt','bmrk_kurt'])
for a,b in zip(kurts,returns):
    globals()[a] = pd.DataFrame.kurtosis(globals()[b])

 
# Var95%
var = np.array(['port_var','bmrk_var'])
for a,b,c in zip(ari_means[0:2],stds[0:2], var):
    globals()[c] = norm.ppf(0.05,globals()[a],globals()[b])
    globals()[c] = pd.Series(globals()[c])
    globals()[c].index = port_skew.index

# Portfolio Covariance
cov_p = port.cov()

mkt = selection['marketValue']
mkt.index = cov_p.index
port_var_dollar = port_var*mkt

# VaR as percentage of All Portfolios combined
var_of_total = port_var_dollar/mkt.sum()
        
# rolling volatility
rolling_vol = port.rolling(window=annualize*rol_year).std()
rolling_vol_b = bmrk.rolling(window=annualize*rol_year).std()



"""Risk/Return"""
# Beta
portbmrks = np.array(['port','port_up','port_d','bmrk','bmrk_up','bmrk_d'])

cors = np.array(['cor', 'cor_up', 'cor_d'])
covs = np.array(['cov', 'cov_up', 'cov_d'])
betas = np.array(['beta', 'beta_up', 'beta_d'])
for a,b,c,d,e,f,g in zip(cors,portbmrks[0:3],portbmrks[3:],covs,stds[[0,2,4]],stds[[1,3,5]],betas):
    globals()[a] = globals()[b].corrwith(globals()[c])
    globals()[d] = globals()[a]*globals()[e]*globals()[f]
    globals()[g] = globals()[d] / (globals()[f]**2)



# Log Beta
portbmrks_log = np.array(['port_log','port_up_log','port_d_log','bmrk_log','bmrk_up_log','bmrk_d_log'])

cors_log = np.array(['cor_log', 'cor_log_up', 'cor_log_d'])
covs_log = np.array(['cov_log', 'cov_log_up', 'cov_log_d'])
betas_log = np.array(['beta_log', 'beta_log_up', 'beta_log_d'])
for a,b,c,d,e,f,g in zip(cors_log,portbmrks_log[0:3],portbmrks_log[3:],covs_log,log_stds_per[[0,2,4]],log_stds_per[[1,3,5]],betas_log):
    globals()[a] = globals()[b].corrwith(globals()[c])
    globals()[d] = globals()[a]*globals()[e]*globals()[f]
    globals()[g] = globals()[d] / (globals()[f]**2)

# Geometric Sharpe Ratio (annualized)
srs = np.array(['port_sr', 'bmrk_sr', 'port_up_sr', 'bmrk_up_sr', 'port_d_sr','bmrk_d_sr'])
for a,b,c in zip(srs,geo_means_ann[0:6],stds_ann[0:6]):
    globals()[a] = (globals()[b] - rf_mean_ann) / globals()[c]

# Logrithmic Sharpe Ratio (annualized)
log_srs = np.array(['port_log_sr', 'bmrk_log_sr', 'port_log_up_sr', 'bmrk_log_up_sr', 'port_log_d_sr','bmrk_log_d_sr'])
for a,b,c in zip(log_srs,log_means_ann[0:6],log_stds[0:6]):
    globals()[a] = (globals()[b] - rf_log_mean_ann) / globals()[c]

# Geometric Information Ratio
irs = np.array(['ir','ir_up','ir_d'])
for a,b,c,d in zip(irs,geo_means_ann[[0,2,4]],geo_means_ann[[1,3,5]],terrors):
    globals()[a] = (globals()[b]-globals()[c])/globals()[d]

# Logrithmic Information Ratio
log_irs = np.array(['log_ir','log_ir_up','log_ir_d'])
for a,b,c,d in zip(log_irs,log_means_ann[[0,2,4]],log_means_ann[[1,3,5]],log_terrors):
    globals()[a] = (globals()[b]-globals()[c])/globals()[d]

# Geometric Treynor Ratio (annualized)
tres = np.array(['tre','tre_up','tre_d'])
for a,b,c in zip(tres,geo_means_ann[[0,2,4]],betas):
    globals()[a] = (globals()[b] - rf_mean_ann) / globals()[c]

# Adjusted Geometric Treynor Ratio (annualized, beta is adjusted to beta x bmrk standard deviation)
tre_adj = (port_mean_ann - rf_mean_ann ) / (bmrk_std_ann*beta)


# Logrithmic Treynor Ratio (annualized)
log_tres = np.array(['log_tre','log_tre_up','log_tre_d'])
for a,b,c in zip(log_tres,log_means_ann[[0,2,4]],betas_log):
    globals()[a] = (globals()[b] - rf_log_mean_ann) / globals()[c]


# Adjusted Logrithmic Treynor Ratio (annualized,beta is adjusted to beta x bmrk standard deviation)
log_tre_adj = (port_log_mean_ann - rf_log_mean_ann)/(bmrk_log_std*beta_log)
    
# Geometric Sortino Ratio
sors = np.array(['port_sor','bmrk_sor'])
for a,b,c in zip(sors,geo_means_ann[[0,1]],semis):
    globals()[a] = (globals()[b] - rf_mean_ann) / globals()[c]
 
# Geometric Sortino Ratio 2
sors2 = np.array(['port_sor2','bmrk_sor2'])
for a,b,c in zip(sors2,geo_means_ann[[0,1]],semis2):
    globals()[a] = (globals()[b] - 0) / globals()[c]
   
# Logrithmic Sortino Ratio
log_sors = np.array(['port_log_sor','bmrk_log_sor'])
for a,b,c in zip(log_sors,log_means_ann[[0,1]],log_semis):
    globals()[a] = (globals()[b] - rf_log_mean_ann) / globals()[c]

# Logrithmic Sortino Ratio 2
log_sors2 = np.array(['port_log_sor2','bmrk_log_sor2'])
for a,b,c in zip(log_sors2,log_means_ann[[0,1]],log_semis2):
    globals()[a] = (globals()[b] - 0) / globals()[c] 
    
# Upside/Downside Capture Ratio
caps = np.array(['capture_up','capture_d'])
for a,b,c in zip(caps,geo_means[[2,4]],geo_means[[3,5]]): 
    globals()[a] = globals()[b] / globals()[c]


# rolling beta
rol_cov = port.rolling(rol_year*annualize).cov(bmrk)
rol_var = bmrk.rolling(rol_year*annualize).var()
rol_beta = rol_cov / rol_var
    

# Excess:
excesses = np.array(['excess_cum','excess_tr','excess_mean_ann',
                     'excess_std_ann','excess_semi','excess_semi2','excess_mdd',
                     'excess_skew','excess_kurt','excess_var','excess_sr','excess_log_sr',
                     'excess_sor','excess_sor2','excess_log_sor','excess_log_sor2'])
ports = np.array(['port_cum','port_tr','port_mean_ann',
                  'port_std_ann','port_semi','port_semi2','port_mdd',
                  'port_skew','port_kurt','port_var','port_sr','port_log_sr',
                  'port_sor','port_sor2','port_log_sor','port_log_sor2'])
bmrks = np.array(['bmrk_cum','bmrk_tr','bmrk_mean_ann',
                  'bmrk_std_ann','bmrk_semi','bmrk_semi2','bmrk_mdd',
                  'bmrk_skew','bmrk_kurt','bmrk_var','bmrk_sr','bmrk_log_sr',
                  'bmrk_sor','bmrk_sor2','bmrk_log_sor','bmrk_log_sor2'])

"""te,beta,ir,ir_log,tre,log_tre,capture_up,capture_d"""

for a,b,c in zip(excesses,ports,bmrks):
    globals()[a] = globals()[b]-globals()[c]


# Portfolio correlations
corr = port.corr()

# Correlation with Benchmark
corr_b = port.corrwith(bmrk)

# rolling correlation with Benchmark
rol_corr = port.rolling(rol_year*annualize).corr(bmrk, pairwise=False)



# Marginal Risk Contribution
weight = selection['marketValue']
weight = pd.DataFrame(weight)
weight.index = cov_p.index
weight = weight/weight.sum()
weight1=weight
weight.columns= [selection['portfolio'][0]]
for i in range(1,len(selection['portfolio'])):
    weight[selection['portfolio'][i]] = weight[selection['portfolio'][0]]
weight_t = pd.DataFrame.transpose(weight)
port_total_std = weight*weight_t*cov_p
port_total_std = port_total_std.sum().sum()
port_total_std = port_total_std**(1/2)
marginal_risk = weight*cov_p
marginal_risk = marginal_risk.sum()
marginal_risk = marginal_risk/port_total_std
marginal_risk = marginal_risk*np.sqrt(annualize)
contribution_to_risk = weight[selection['portfolio'][0]]*marginal_risk
percent_contribution_to_risk = contribution_to_risk / contribution_to_risk.sum()


# Factor analysis
summary = pd.DataFrame()

for i in range(len(selection['portfolio'])):
    #df_i = pd.DataFrame()
    rf_i = pd.DataFrame(rf.iloc[:,i])
    port_i=pd.DataFrame(port.iloc[:,i])
    bmrk_i=pd.DataFrame(bmrk.iloc[:,i])
    ff_i = bmrk_i - rf_i
    #df_i = pd.concat(ff_i,axis=1)
    ff_i = st.add_constant(ff_i,prepend=True)
    result_i = sm.OLS(port_i-rf_i,ff_i,missing='drop').fit()
    list_i = {'Alpha': result_i.params[0],
              'Beta': result_i.params[1],
              'Alpha_tStat': result_i.tvalues[0],
              'Beta_tStat': result_i.tvalues[1],
              'Alpha_pValue': result_i.pvalues[0],
              'Beta_pValue': result_i.pvalues[1],
              'Adj. R-squared': result_i.rsquared_adj}
    summary_i = pd.DataFrame(list_i,index=selection['portfolio'][i:i+1])
    summary = pd.concat([summary,summary_i])

# Create a table to summarize statistics
headers = ['Market Value as of 7/29/16','Time Frame','No. of Observations','Port TR','BmrK TR','Excess TR',
           'Port Return (Annualized)','Bmrk Return (Annualized)','Excess Return (Annualized)',
           'Port Vol (Annualized)','Bmrk Vol (Annualized)','Excess Vol (Annualized)',
           'Tracking Error (Annualized)',
           'Port Semideviation (Annualized)','Bmrk Semideviation (Annualized)','Excess Semideviation (Annualized)',
           'Port Semideviation (Annualized, Minimum Acceptable Return = 0)','Bmrk Semideviation (Annualized, Minimum Acceptable Return = 0)','Excess Semideviation (Annualized, Minimum Acceptable Return = 0)',
           'Port Maximum Drawdown','Bmrk Maximum Drawdown','Excess Maximum Drawdown',
           'Port Skewness','Bmrk Skewness','Excess Skewness',
           'Port Excess Kurtosis','Bmrk Excess Kurtosis','Difference in Excess Kurtosis (the definition here is port-bmrk)',
           'Port VaR95%','Bmrk VaR95%','Excess VaR95%','Port VaR95% in Dollar Amount','Port VaR95% in Dollar Amount as percentage of All Combined Portfolio Market Value',
           'Beta','Bull Beta','Bear Beta',
           'Geometric Port Sharp Ratio (Annualized)','Geometric Bmrk Sharp Ratio (Annualized)','Excess Geometric Sharpe Ratio (Annualized)',
           'Geometric Port Information Ratio (Annualized)',
           'Geometric Port Treynor Measure (Annualized)','Adjusted Geometric Port Treynor Measure (Annualized, Beta was replaced by Beta x Bmrk Standard deviation)',
           'Geometric Port Sortino Ratio (Annualized)','Geometric Bmrk Sortino Ratio (Annualized)','Excess Geometric Sortino Ratio (Annualized)',
            'Geometric Port Sortino Ratio (Annualized, Minimum Acceptable Return = 0)','Geometric Bmrk Sortino Ratio (Annualized, Minimum Acceptable Return = 0)','Excess Geometric Sortino Ratio (Annualized, Minimum Acceptable Return = 0)',
           'Logarithmic Port Sharp Ratio (Annualized)','Logarithmic Bmrk Sharp Ratio (Annualized)','Excess Logarithmic Sharpe Ratio (Annualized)',
           'Logarithmic Port Information Ratio (Annualized)',
           'Logarithmic Port Treynor Measure (Annualized)','Adjusted Logarithmic Port Treynor Measure (Annualized, Beta was replaced by Beta x Bmrk Standard deviation)',
           'Logarithmic Port Sortino Ratio (Annualized)','Logarithmic Bmrk Sortino Ratio (Annualized)','Excess Logarithmic Sortino Ratio (Annualized)',
           'Logarithmic Port Sortino Ratio (Annualized, Minimum Acceptable Return = 0)','Logarithmic Bmrk Sortino Ratio (Annualized, Minimum Acceptable Return = 0)','Excess Logarithmic Sortino Ratio (Annualized, Minimum Acceptable Return = 0)',
           'Upside Capture','Downside Capture','Marginal Risk (Annualized)','Contribution to Risk (Annualized)','Percent Contribution to Risk (Annualized)',
           'Adj. R-squared (single factor)','Alpha (single factor)','Alpha_pValue (single factor)','Alpha_tStat (single factor)','Beta (single factor)','Beta_pValue (single factor)','Beta_tStat (single factor)']


table = pd.DataFrame([selection['marketValue'],period,pd.DataFrame.count(port),
                      port_tr,bmrk_tr,excess_tr,
                       port_mean_ann,bmrk_mean_ann,excess_mean_ann,
                       port_std_ann, bmrk_std_ann,excess_std_ann,
                       te,
                       port_semi,bmrk_semi,excess_semi,
                       port_semi2,bmrk_semi2,excess_semi2,
                       port_mdd,bmrk_mdd,excess_mdd,
                       port_skew,bmrk_skew,excess_skew,
                       port_kurt,bmrk_kurt,excess_kurt,
                       port_var,bmrk_var,excess_var,port_var_dollar,var_of_total,
                       beta,beta_up,beta_d,
                       port_sr,bmrk_sr,excess_sr,
                       ir,
                       tre,tre_adj,
                       port_sor,bmrk_sor,excess_sor,
                       port_sor2,bmrk_sor2,excess_sor2,
                       port_log_sr,bmrk_log_sr,excess_log_sr,
                       log_ir,
                       log_tre,log_tre_adj,
                       port_log_sor,bmrk_log_sor,excess_log_sor,
                       port_log_sor2,bmrk_log_sor2,excess_log_sor2,
                       capture_up,capture_d,marginal_risk,contribution_to_risk,percent_contribution_to_risk,
                       summary['Adj. R-squared'],summary['Alpha'], summary['Alpha_pValue'],summary['Alpha_tStat'],summary['Beta'],
                       summary['Beta_pValue'],summary['Beta_tStat']])
                       
table = pd.DataFrame.transpose(table)
table.columns = headers

# 3-year rolling factor decomposition
alpha = pd.DataFrame()
market = pd.DataFrame()
rsquared = pd.DataFrame()

for i in range(len(selection['portfolio'])):
    df_i = pd.DataFrame()
    rf_i = pd.DataFrame(rf.iloc[:,i])
    port_i=pd.DataFrame(port.iloc[:,i])
    port_i = port_i.dropna(axis=0)
    bmrk_i=pd.DataFrame(bmrk.iloc[:,i])
    pff_i = port_i - rf_i
    pdf_i = pd.concat([pff_i],axis=1)
    pdf_i = pdf_i.dropna(axis=0)
    ff_i = bmrk_i - rf_i
    df_i = pd.concat([ff_i],axis=1)
    df_i = df_i.dropna(axis=0)
    df_i = st.add_constant(df_i,prepend=True)
    alpha_i = pd.DataFrame()
    market_i = pd.DataFrame()    
    rsquared_i = pd.DataFrame()
    alpha_ii = []
    market_ii = []
    rsquared_ii = []


    if len(df_i) <= 36:
        alpha_i['name'] = np.nan
        market_i['name'] = np.nan
        rsquared_i['name'] = np.nan
  
    else:        
        for j in range(0,len(df_i)-35):
            pdf_j=pdf_i.iloc[j:j+36,:]
            df_j=df_i.iloc[j:j+36,:]
            try:
                result_j = sm.OLS(pdf_j,df_j).fit()
                al_j = result_j.params[0]
                be_j = result_j.params[1]
                rsquared_j = result_j.rsquared_adj
   
                alpha_ii.append(al_j)
                market_ii.append(be_j)
                rsquared_ii.append(rsquared_j)
            except ValueError:
                pass
        index_i = port_i.index[35:]
        
        alpha_i = pd.DataFrame(alpha_ii,index=index_i)
        market_i= pd.DataFrame(market_ii,index=index_i)
        rsquared_i= pd.DataFrame(rsquared_ii,index=index_i)
    
    alpha=pd.concat([alpha,alpha_i],axis=1)   
    market=pd.concat([market,market_i],axis=1)
    rsquared=pd.concat([rsquared,rsquared_i],axis=1)

""" Excel Output """
# Set up workbook
writer = pd.ExcelWriter('analysis.xlsx', engine='xlsxwriter')
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

# Output Statistics tab
table.to_excel(writer,sheet_name = 'Statistics',startcol=1)
statistics = writer.sheets['Statistics']
statistics.write_row('C1',headers, format1)
statistics.write_column('A2',selection['portfolio'], format1)
statistics.write_column('B2',selection['benchmark'], format1)
statistics.write(0,0,'Portfolio',format1)
statistics.write(0,1,'Benchmark',format1)
statistics.set_column('A:B', 10, format2)
statistics.set_column('B:D', 18, format2)
statistics.set_column('C:F', 11, format4)
statistics.set_column('E:F', 11, format5)
statistics.set_column('F:ZZ', 11, format2)
statistics.set_column('Y:AD', 11, format3)
statistics.set_column('AH:AI',11, format4)
statistics.set_column('AI:AJ',11, format2)
statistics.set_column('AJ:BJ',11, format3)
statistics.set_column('BQ:CO',11, format6)


# Visulization of Statistics
statistics_visual = workbook.add_worksheet('Statistics Visualization')


charts = ['total_return','annualized_return','annualized_volatility',
          'semideviation','max_drawdown','skewness',
          'kurtosis','value_at_risk','beta_all','bull_beta','bear_beta',
          'geo_sharpe_ratio','geo_sortino_ratio',
          'upside_capture','downside_capture',
          'tracking_error',
          'geo_information_ratio','geo_treynor_ratio','geo_treynor_adj', 
          'log_information_ratio','log_treynor_ratio','log_treynor_adj',
          'marginal_risk','contribution_to_risk','percent_contribution_to_risk']
          
titles = ['Total Return','Annualized Return', 'Annualized Volatility',
          'Semideviation','Maximum Drawdown','Skewness',
          'Kurtosis', 'Value at Risk','Beta','Geometric Sharpe Ratio','Geometric Sortino Ratio',
          'Upside/Downside Capture Ratios',
          'Tracking Error',
          'Geometric Information Ratio','Adjusted Geometric Port Treynor Measure (Annualized, Beta was replaced by Beta x Bmrk Standard deviation)',
          'Marginal Risk',
          'Contribution to Risk','Percent Contribution to Risk']

positions = ['B2','B25','B48','B71','B94','B117','B140','B163','B186','B209','B232','B255']
positions2 = ['U2','U25','U48','U71','U94','U117']


range_start = [5,8,11,15,21,24,27,30,35,38,44,62]
range_end = [8,11,14,18,24,27,30,33,38,41,47,64]
ranges = [14,41,43,64,65,66]
      
for a,b,c,d,e in zip(charts[0:15],titles[0:12],positions,range_start,range_end):
    globals()[a] = workbook.add_chart({'type':'column'})
    for col in range(d,e):
        globals()[a].add_series({
        'name'      : ['Statistics',0,col],
        'categories': ['Statistics',1,0,len(selection['portfolio']),0],
        'values'    : ['Statistics',1,col,len(selection['portfolio']),col],
        'gap'       : 300,})
        globals()[a].set_title({'name':b})
        globals()[a].set_y_axis({'major_gridlines': {'visible': False},'num_format':'0%'})
        globals()[a].set_size({'x_scale': 2.5, 'y_scale': 1.5})
        globals()[a].set_table({'show_keys':True})
        globals()[a].set_legend({'none':True})
        statistics_visual.insert_chart(c,globals()[a])

for a,b,c,d in zip(charts[15:],titles[12:],positions2,ranges):
    globals()[a] = workbook.add_chart({'type':'bar'})
    globals()[a].add_series({
        'name'      : ['Statistics',0,d],
        'categories': ['Statistics',1,0,len(selection['portfolio']),0],
        'values'    : ['Statistics',1,d,len(selection['portfolio']),d],
        'data_labels':{'value': True},
        'gap'       : 300,})
    globals()[a].set_title({'name':b})
    globals()[a].set_x_axis({'major_gridlines': {'visible': False},'num_format':'0.00'})
    globals()[a].set_y_axis({'label_position': 'low'})
    globals()[a].set_size({'x_scale': 1.5, 'y_scale': 1.5})
    globals()[a].set_style(15)
    globals()[a].set_legend({'none':True})
    statistics_visual.insert_chart(c,globals()[a])


# Return distribution
from scipy.stats import norm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

for i in range(len(selection['portfolio'])):
    col = i + 1
    #headers2 = [selection['portfolio'][i],selection['benchmark'][i]]
    #com_i = pd.concat([port.ix[:,i],bmrk.ix[:,i]],axis = 1, keys = headers2)
    #com_i.plot(kind = 'hist',bins=no_bins,normed = True,alpha = 0.3)
    datos = port.iloc[:,i].dropna()
    datos2= bmrk.iloc[:,i].dropna()
    (mu, sigma) = norm.fit(datos)
    (mu2, sigma2) = norm.fit(datos2)    
    n, bins, patches = plt.hist(datos, no_bins, density=True, stacked=True, facecolor='green', alpha=0.6)
    n, bins, patches = plt.hist(datos2, no_bins, density=True, stacked=True, facecolor='yellow', alpha=0.3)
    y = norm.pdf( bins, mu, sigma)
    y2 = norm.pdf( bins, mu2, sigma2)
    l = plt.plot(bins, y, 'r--', linewidth=2)
    plt.xlabel('Returns')
    plt.ylabel('Frequency')
    plt.title(r'$\mathrm{Distribution\ of\ Returns:}\ \mu=%.3f,\ \sigma=%.3f$' %(mu, sigma))
    plt.grid(True)
    plt.legend(['Normal Distribution',selection['portfolio'][i],selection['benchmark'][i]],bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()    

    
# Rolling Beta 
beta_all = pd.DataFrame(beta)
beta_all = pd.DataFrame.transpose(beta_all)
beta_all = beta_all.append([beta_all]*(len(port)-1))
beta_all.index = port.index
lines = ['none','dash']

rolling_beta = workbook.add_worksheet('Rolling Beta')
beta_list = ['rol_beta','beta_all','Rolling Beta Data','Entire Period Beta',
            'rolling_beta_data','entire_period_beta']

for a,b,c in zip(beta_list[0:2],beta_list[4:6],beta_list[2:4]):
    globals()[a].to_excel(writer, sheet_name = c)
    globals()[b] = writer.sheets[c]

rolling_beta_data.write_row('B1',['Rolling Beta']*len(beta))
entire_period_beta.write_row('B1',['Beta for Entire Period']*len(beta))

for i in range(len(selection['portfolio'])):
    col = i + 1
    chart_i = workbook.add_chart({'type':'line'})
    for a,b in zip(beta_list[2:4],lines):
        chart_i.add_series({
            'name':       [a, 0, col],
            'categories': [a, 1, 0, len(port_cum), 0],
            'values':     [a, 1, col, len(port_cum), col],
            'line'  :     {'dash_type':b}
        }) 
        chart_i.set_title({'name':['Rolling Vol Data',0,col]})
        chart_i.set_x_axis({'name': 'Date','num_format': 'm/d/yy'})
        chart_i.set_y_axis({'name': str(rol_year)+'-Year Rolling Beta', 'major_gridlines': {'visible': False},'num_format': '0.00'})
        chart_i.set_size({'x_scale': 2, 'y_scale': 1})
        rolling_beta.insert_chart(2+16*i,1, chart_i)  
rolling_beta_data.hide()
entire_period_beta.hide()


# rolling volatility
port_mean_vol = pd.DataFrame(port_std)
port_mean_vol = pd.DataFrame.transpose(port_mean_vol)
port_mean_vol = port_mean_vol.append([port_mean_vol]*(len(port)-1))
port_mean_vol.index = port.index
bmrk_mean_vol = pd.DataFrame(bmrk_std)
bmrk_mean_vol = pd.DataFrame.transpose(bmrk_mean_vol)
bmrk_mean_vol = bmrk_mean_vol.append([bmrk_mean_vol]*(len(port)-1))
bmrk_mean_vol.index = port.index

lines2 = ['none','none','dash','dash']

rolling_volatility = workbook.add_worksheet('Rolling Volatility')
rol_list = ['rolling_vol','rolling_vol_b','port_mean_vol','bmrk_mean_vol',
            'Rolling Vol Data','Rolling Vol Data b','Mean Vol Data','Mean Vol Data b',
            'rolling_vol_data','rolling_vol_data_b','mean_vol_data','mean_vol_data_b']

for a,b,c in zip(rol_list[0:4],rol_list[8:12],rol_list[4:8]):
    globals()[a].to_excel(writer, sheet_name = c)
    globals()[b] = writer.sheets[c]
    globals()[b].set_column('B:ZZ', 40, format2)
    globals()[b].hide()

rolling_vol_data_b.write_row('B1',selection['benchmark'])
mean_vol_data.write_row('B1',['Portfolio Average Volatility']*len(beta))
mean_vol_data_b.write_row('B1',['Benchmark Average Volatility']*len(beta))


for i in range(len(selection['portfolio'])):
    col = i + 1
    chart_i = workbook.add_chart({'type':'line'})
    for a,b in zip(rol_list[4:8],lines2):
        chart_i.add_series({
            'name':       [a, 0, col],
            'categories': [a, 1, 0, len(port_cum), 0],
            'values':     [a, 1, col, len(port_cum), col],
            'line'  :     {'dash_type':b}              
        }) 
        chart_i.set_title({'name':['Statistics',col,0]})
        chart_i.set_x_axis({'name': 'Date','num_format': 'm/d/yy'})
        chart_i.set_y_axis({'name': str(rol_year)+'-Year Rolling Volatility','num_format':'0%','major_gridlines': {'visible': False}})  
        chart_i.set_size({'x_scale': 2, 'y_scale': 1})
        rolling_volatility.insert_chart(2+16*i,1, chart_i)    


# Correlation Table
cell_format = workbook.add_format()
cell_format.set_align('center')
cell_format.set_align('top')
cell_format.set_text_wrap('True')
cell_format.set_bold('True')
cell_format.set_font_size(9)

corr.to_excel(writer,sheet_name = 'Correlation')
correlation = writer.sheets['Correlation']
correlation.write_row('B1',selection['portfolio'], cell_format)
correlation.write_column('A2',selection['portfolio'], cell_format)
correlation.write(0,0,'Correlation',cell_format)
correlation.set_column('B:ZZ', 10, format3)
correlation.set_column('A:B', 10, format3)
correlation.conditional_format('B2:ZZ100', {'type': '3_color_scale'})

# rolling correlation with benchmark
corr_all = pd.DataFrame(corr_b)
corr_all = pd.DataFrame.transpose(corr_all)
corr_all = corr_all.append([corr_all]*(len(port)-1))
corr_all.index = port.index
lines = ['none','dash']

rolling_corr = workbook.add_worksheet('Rolling Corr with Bmrk')

corr_list = ['rol_corr','corr_all','Rolling Correlation Data','Entire Period Correlation',
            'rol_corr_data','entire_period_correlation']

for a,b,c in zip(corr_list[0:2],corr_list[4:6],corr_list[2:4]):
    globals()[a].to_excel(writer, sheet_name = c)
    globals()[b] = writer.sheets[c]

rol_corr_data.write_row('B1',['Rolling Correlation']*len(beta))
entire_period_correlation.write_row('B1',['Correlation for Entire Period']*len(beta))

for i in range(len(selection['portfolio'])):
    col = i + 1
    chart_i = workbook.add_chart({'type':'line'})
    for a,b in zip(corr_list[2:4],lines):
        chart_i.add_series({
            'name':       [a, 0, col],
            'categories': [a, 1, 0, len(port_cum), 0],
            'values':     [a, 1, col, len(port_cum), col],
            'line'  :     {'dash_type':b}
        }) 
        chart_i.set_title({'name':['Statistics',col,0]})
        chart_i.set_x_axis({'name': 'Date','num_format': 'm/d/yy'})
        chart_i.set_y_axis({'name': str(rol_year)+'-Year Rolling Corr with Bmrk','num_format':'0%','major_gridlines': {'visible': False}})   
        chart_i.set_size({'x_scale': 2, 'y_scale': 1})
        rolling_corr.insert_chart(2+16*i,1, chart_i)    
rol_corr_data.hide()
entire_period_correlation.hide()


#Rolling excess return
excess_rr.to_excel(writer,sheet_name = 'Rolling Return Data')
rolling_return_data = writer.sheets['Rolling Return Data']
rolling_return = workbook.add_worksheet('Rolling Excess Return')

for i in range(len(selection['portfolio'])):
    col = i + 1
    chart_i = workbook.add_chart({'type':'line'})
    chart_i.add_series({
        'name':       ['Rolling Return Data', 0, col],
        'categories': ['Rolling Return Data', 1, 0, len(port_cum), 0],
        'values':     ['Rolling Return Data', 1, col, len(port_cum), col],
                       }) 
    chart_i.set_title({'name':['Statistics',col,0]})
    chart_i.set_x_axis({'name': 'Date','num_format': 'm/d/yy'})
    chart_i.set_y_axis({'name': str(rol_year)+'-Year Rolling Excess Return','num_format':'0%','major_gridlines': {'visible': False}})
    chart_i.set_legend({'none':True})    
    chart_i.set_size({'x_scale': 2, 'y_scale': 1})
    rolling_return.insert_chart(2+16*i,1, chart_i)    

rolling_return_data.hide()

# Cumulative returns chart
cum_chart = workbook.add_worksheet('Cumulative Return')
cum1 = np.array(['port_cum', 'bmrk_cum', 'excess_cum'])
cum2 = np.array(['port_cum_returns', 'bmrk_cum_returns', 'excess_cum_returns'])
cum3 = np.array(['Port Cum Returns', 'Bmrk Cum Returns', 'Excess Cum Returns'])
for a,b,c in zip(cum1,cum2,cum3):
    globals()[a].to_excel(writer, sheet_name = c)
    globals()[b] = writer.sheets[c]
    globals()[b].set_column('B:ZZ', 40, format2)
    globals()[b].hide()


bmrk_cum_returns.write_row('B1',selection['benchmark'])
excess_cum_returns.write_row('B1',['Excess']*len(selection['portfolio']))


for i in range(len(selection['portfolio'])):
    col = i + 1
    chart_i = workbook.add_chart({'type':'line'})
    for a in cum3:
        chart_i.add_series({
            'name':       [a, 0, col],
            'categories': [a, 1, 0, len(port_cum), 0],
            'values':     [a, 1, col, len(port_cum), col],
        }) 
        chart_i.set_title({'name':['Statistics',col,0]})
        chart_i.set_x_axis({'name': 'Date','num_format': 'm/d/yy'})
        chart_i.set_y_axis({'name': 'Cumulative Return','num_format':'0%','major_gridlines': {'visible': False}})
        chart_i.set_size({'x_scale': 2, 'y_scale': 1})
        cum_chart.insert_chart(2+16*i,1, chart_i)    

# Monthly returns chart
mo_sheets = ['port_return','bmrk_return']
mo_sheets2 = ['Port Return','Bmrk Return']
monthly_return = workbook.add_worksheet('Monthly Return')
for a,b,c in zip(returns,mo_sheets,mo_sheets2):
    globals()[a].to_excel(writer, sheet_name = c)
    globals()[b] = writer.sheets[c]
    globals()[b].set_column('B:ZZ', 40, format2)
    globals()[b].hide()

bmrk_return.write_row('B1',selection['benchmark'])
  
for i in range(len(selection['portfolio'])):
    col = i + 1
    chart_i = workbook.add_chart({'type':'line'})
    for a in mo_sheets2:
        chart_i.add_series({
            'name':       [a, 0, col],
            'categories': [a, 1, 0, len(port_cum), 0],
            'values':     [a, 1, col, len(port_cum), col],
        }) 
        chart_i.set_title({'name':['Statistics',col,0]})
        chart_i.set_x_axis({'name': 'Date','num_format': 'm/d/yy'})
        chart_i.set_y_axis({'name': 'Monthly Return','num_format':'0%','major_gridlines': {'visible': False}})
        chart_i.set_size({'x_scale': 2, 'y_scale': 1})
        monthly_return.insert_chart(2+16*i,1, chart_i)    

# R-squared (Return variation source)
rsquared_chart = workbook.add_worksheet('Return Variation Source')
rsquared.to_excel(writer, sheet_name = 'Rsquared')
rol_rsquared = writer.sheets['Rsquared']
rol_rsquared.set_column('B:ZZ', 40, format2)
rol_rsquared.hide()
rol_rsquared.write_row('B1',selection['benchmark'])

chart_rsquared = workbook.add_chart({'type':'area','subtype':'stacked'})
for i in range(len(selection['portfolio'])):
    col = i + 1
    chart_rsquared.add_series({
        'name':       ['Rsquared', 0, col],
        'categories': ['Rsquared', 1, 0, len(port_cum), 0],
        'values':     ['Rsquared', 1, col, len(port_cum), col],
                      }) 
    chart_rsquared.set_title({'name':'Return Variation Source for '+ selection['portfolio'][0]})
    chart_rsquared.set_x_axis({'name': 'Date','num_format': 'm/d/yy'})
    chart_rsquared.set_y_axis({'name': str(rol_year)+'-Year Rolling R-squared','num_format':'0%','major_gridlines': {'visible': False}})
    chart_rsquared.set_size({'x_scale': 2, 'y_scale': 1})
    rsquared_chart.insert_chart(2,1, chart_rsquared)    

## percent R-squared chart
chart_rsquared_p = workbook.add_chart({'type':'area','subtype':'percent_stacked'})
for i in range(len(selection['portfolio'])):
    col = i + 1
    chart_rsquared_p.add_series({
        'name':       ['Rsquared', 0, col],
        'categories': ['Rsquared', 1, 0, len(port_cum), 0],
        'values':     ['Rsquared', 1, col, len(port_cum), col],
                      }) 
    chart_rsquared_p.set_title({'name':'Return Variation Source Percentage for '+ selection['portfolio'][0]})
    chart_rsquared_p.set_x_axis({'name': 'Date','num_format': 'm/d/yy'})
    chart_rsquared_p.set_y_axis({'name': str(rol_year)+'-Year Rolling R-squared Percentage','num_format':'0%','major_gridlines': {'visible': False}})
    chart_rsquared_p.set_size({'x_scale': 2, 'y_scale': 1})
    rsquared_chart.insert_chart(19,1, chart_rsquared_p)  

writer.save()

# Open Excel
from win32com.client import Dispatch
xl = Dispatch('Excel.Application')
xl.Workbooks.Open("C:/Users/nvg9hxp/Documents/Projects/Return based analysis_python/analysis.xlsx")
xl.Visible = True


from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import summary
from EquityHedging.analytics import premia_metrics as pm
from EquityHedging.analytics import returns_stats as rs
import pandas as pd

freq = '1W'
liq_alts = pd.read_excel(dm.NEW_DATA+'liq_alts.xlsx', sheet_name='data_2', index_col=0)
liq_alts.index = pd.to_datetime(liq_alts.index)
bmk_data = pd.read_excel(dm.NEW_DATA+'liq_alts.xlsx', sheet_name='bmk_data',index_col=0)
liq_alts = liq_alts.resample(freq).ffill()
bmk_data = bmk_data.resample(freq).ffill()
df_returns = dm.merge_data_frames(bmk_data, liq_alts)
df_returns = dm.format_data(df_returns, freq)


pm_dict = summary.get_norm_premia_metrics(df_returns)

return_stats = rs.get_return_stats(df_returns,'1W')
premia_metrics = pm.get_premia_metrics(df_returns, '1W')
premia_metrics = pm.get_premia_metrics(df_returns, '1W')
pm_dict = summary.get_norm_premia_metrics(df_returns)


premia_uni= pd.read_excel(dm.NEW_DATA+'liq_alts.xlsx', sheet_name='premia_uni',index_col=0)
premia_uni = dm.format_data(premia_uni,freq)
df_ret_premia = dm.merge_data_frames(df_returns, premia_uni)

premia_metrics = pm.get_premia_metrics(df_ret_premia, freq,False)
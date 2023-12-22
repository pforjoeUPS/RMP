import pandas as pd
from .import formats

CWD = os.getcwd()
RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\returns_data\\'
BMK_DATA_FP = RETURNS_DATA_FP+'bmk_returns.xlsx'
HF_BMK_DATA_FP = RETURNS_DATA_FP+'hf_bmks.xlsx'
LIQ_ALTS_BMK_DATA_FP = RETURNS_DATA_FP+'liq_alts_bmks.xlsx'
LIQ_ALTS_PORT_DATA_FP = RETURNS_DATA_FP+'nexen_liq_alts_data.xlsx'
LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A','Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital', 'JSC Vantage'],
                     'Trend Following': ['1907 ARP TF','1907 Campbell TF', '1907 Systematica TF',
                                         'One River Trend'],
                     'Absolute Return':['1907 ARP EM',  '1907 III CV', '1907 III Class A',
                                        # 'ABC Reversion',
                                        'Acadian Commodity AR',
                                        'Blueshift', 'Duality', 'Elliott']
                     }
EQ_HEDGE_DATA_FP = RETURNS_DATA_FP+'eq_hedge_returns.xlsx'
EQ_HEDGE_STRAT_DICT = {'99%/90% Put Spread':0.0, 'Down Var':1.0, 'Vortex':0.0, 'VOLA':1.25,'Dynamic Put Spread':1.0,
                       'VRR':1.0, 'GW Dispersion':1.0, 'Corr Hedge':0.25,'Def Var':1.0}
FREQ_LIST = ['1D', '1W', '1M', '1Q', '1Y']


def read_ret_data(fp, sheet_name):
    ret_data = pd.read_excel(fp, sheet_name, index_col=0)
    return dm.get_real_cols(ret_data)

class bmkHandler():
    def __init__(self, equity_bmk = 'M1WD',include_fi = True, all_data=False):
        self.equity_bmk = equity_bmk
        self.include_fi = include_fi
        if include_fi:
            self.fi_bmk = 'FI Benchmark'
        self.all_data = all_data
        self.bmk_returns = self.get_bmk_returns()
        
    def get_bmk_returns(self):
        returns_dict = {}
        for freq in FREQ_LIST:
            freq_string = dm.switch_freq_string(freq)
            temp_ret = read_ret_data(BMK_DATA_FP, freq_string)
            if self.all_data:
                returns_dict[freq_string] = temp_ret.copy()
            else:    
                if freq != '1D':
                    if self.include_fi:
                        temp_ret[self.fi_bmk] = temp_ret['Long Corp']*0.6 + temp_ret['STRIPS']*0.4
                        returns_dict[freq_string] = temp_ret[[self.equity_bmk, self.fi_bmk]]
                    else:
                        returns_dict[freq_string] = temp_ret[[self.equity_bmk]]
                else:
                    returns_dict[freq_string] = temp_ret[[self.equity_bmk]]
                returns_dict[freq_string].index.names = ['Date']
        
        return returns_dict
  
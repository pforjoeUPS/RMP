"""
Created on Sun Aug  7 22:18:15 2022

@author: NVG9HXP
"""
import os

from copy import deepcopy
import pandas as pd

from . import data_importer as di

from . import data_manager_new as dm
from . import data_xformer_new as dxf
from .data_updater_new import DATA_FP, RETURNS_DATA_FP

BMK_DATA_FP = RETURNS_DATA_FP + 'bmk_returns-new.xlsx'

# CWD = os.getcwd()
HF_BMK_DATA_FP = RETURNS_DATA_FP + 'hf_bmks-new.xlsx'
UPSGT_DATA_FP = RETURNS_DATA_FP + 'upsgt_returns-new.xlsx'
UPSGT_BMK_DATA_FP = RETURNS_DATA_FP + 'upsgt_bmk_returns-new.xlsx'
EQ_HEDGE_DATA_FP = RETURNS_DATA_FP + 'eq_hedge_returns-new.xlsx'
# LIQ_ALTS_BMK_DATA_FP = RETURNS_DATA_FP+'liq_alts_bmks-old.xlsx'
LIQ_ALTS_PORT_DATA_FP = RETURNS_DATA_FP + 'nexen_liq_alts_data-new.xlsx'
NEW_STRAT_DATA_FP = DATA_FP + 'new_strats\\'
LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A', 'Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital', 'JSC Vantage', 'Capula TM Fund', 'KAF'
                                      # ,'EDL GOF'
                                      ],
                     'Trend Following': ['1907 Campbell TF', '1907 Systematica TF', 'One River Trend'],
                     'Absolute Return': ['1907 ARP EM', '1907 III CV', '1907 III Class A', '1907 Kepos RP',
                                         'Acadian Commodity AR', 'Duality', 'Elliott']
                     }

BMK_KEYS = {'Liquid Alts': {'Global Macro': 'HFRX Macro/CTA', 'Trend Following': 'SG Trend',
                            'Absolute Return': 'HFRX Absolute Return', 'Total Liquid Alts': 'Liquid Alts Bmk'},
            'Public Equity': {'Domestic Equity': 'Russell 3000', 'International Equity': 'MSCI ACWI ex US Net',
                              'Global Equity': 'MSCI World Net Div Index', 'Total Equity': 'MSCI ACWI IMI'},
            'Fixed Income': {},
            'Group Trust': {'Liquid Alts': 'Liquid Alts Bmk', 'Public Equity': 'MSCI ACWI IMI',
                            'Fixed Income': 'Dynamic FI Benchmark'}
            }
EQ_HEDGE_STRAT_DICT = {'Down Var': 1.0, 'VOLA 3': 1.25, 'Dynamic Put Spread': 1.0,
                       'VRR Portfolio': 1.0, 'GW Dispersion': 1.0, 'Corr Hedge': 0.25, 'Def Var': 1.0,
                       'Commodity Basket': 1.0}


# def read_ret_data(fp, sheet_name):
#     ret_data = pd.read_excel(fp, sheet_name, index_col=0)
#     return EquityHedging.datamanager.data_importer.get_real_cols(ret_data)


# TODO: Import data using di. it'll be efficient in the long run.
# TODO: Get mkt_ret_data, bmk_ret_data, hf_ret_data/hf_bmk_ret_data,


class MktDataHandler:
    def __init__(self, include_eq=True, eq_bmk='MSCI ACWI', include_fi=True, fi_bmk='FI Benchmark',
                 include_cm=False, cm_bmk='Commodities (BCOM)', include_fx=False,
                 fx_bmk='U.S. Dollar Index'):

        self.mkt_data_import = di.DataImporter.read_excel_data(filepath=BMK_DATA_FP, sheet_name=None)
        self.include_eq = include_eq
        self.eq_bmk = eq_bmk if self.include_eq else None
        self.include_fi = include_fi
        self.fi_bmk = fi_bmk if self.include_fi else None
        self.include_cm = include_cm
        self.cm_bmk = cm_bmk if self.include_cm else None
        self.include_fx = include_fx
        self.fx_bmk = fx_bmk if self.include_fx else None
        self.mkt_key = self.get_mkt_key()
        self.mkt_returns = self.get_mkt_returns()

    def get_mkt_key(self):
        mkt_key = {'Equity': self.eq_bmk, 'Fixed Income': self.fi_bmk,
                   'Commodities': self.cm_bmk, 'FX': self.fx_bmk}
        return {mkt: value for mkt, value in mkt_key.items() if value is not None}

    def get_mkt_returns(self):
        returns_dict = {}
        print(f'Getting Market returns data...')
        for freq_string, returns_df in self.mkt_data_import.items():
            temp_df = pd.DataFrame(index=returns_df.index)
            for key in self.mkt_key:
                try:
                    if self.fi_bmk == 'FI Benchmark':
                        returns_df[self.fi_bmk] = self.get_wgt_avg_col(returns_df, [0.6, 0.4],
                                                                       ['Long Corp', 'STRIPS'])
                    temp_df = dm.merge_dfs(temp_df, returns_df[[self.mkt_key[key]]], drop_na=False)
                except KeyError:
                    pass
            if temp_df.empty is False:
                returns_dict[freq_string] = temp_df
        return returns_dict

    @staticmethod
    def get_wgt_avg_col(data_df, weights_list, col_list=None):
        if col_list:
            return data_df[col_list].dot(tuple(weights_list)).to_frame()
        else:
            return data_df.dot(tuple(weights_list)).to_frame()


class DataHandler(MktDataHandler):
    def __init__(self, index_data=False, freq_data=True, compute_agg=False,
                 eq_bmk='MSCI ACWI IMI', include_fi=True, fi_bmk='FI Benchmark', **kwargs):
        self.freq = None
        self.index_data = index_data
        self.freq_data = freq_data
        self.compute_agg = compute_agg
        super().__init__(eq_bmk=eq_bmk, include_fi=include_fi, fi_bmk=fi_bmk, **kwargs)
        self.returns = None
        self.col_list = None
        self.mvs = None
        self.weights = None
        self.custom_returns_data = None
        self.update_mkt_returns()

    def get_returns(self, filepath):
        self.returns = di.DataImporter.read_excel_data(filepath, sheet_name='returns')
        self.col_list = list(self.returns.columns)
        if self.freq_data is True:
            self.returns = dxf.get_data_dict(self.returns, drop_na=False)
            print(f'returns data added for {list(self.returns.keys())}')
        else:
            print(f'returns data added')

    def update_mkt_returns(self):
        if self.returns is not None:
            if self.freq_data is True:
                self.mkt_returns = dm.filter_data_dict(self.mkt_returns, self.returns.keys())
            else:
                self.freq = dm.get_freq(self.returns)
                self.mkt_returns = self.mkt_returns[dm.get_freq_string(self.returns)]
                self.mkt_returns = self.update_dfs(self.mkt_returns)

    def get_mvs(self, filepath):
        try:
            print('Getting market values...')
            self.mvs = di.DataImporter.read_excel_data(filepath, sheet_name='market_values')
            print('market values added')
        except KeyError:
            self.mvs = None
            print('No market values')

    def get_weights(self):
        if self.mvs is None:
            returns_data = self.returns[self.freq] if self.freq_data else self.returns
            self.mvs = [float(input('market value (Billions) for ' + strat + ':')) for strat in returns_data]
        self.weights = dm.get_weights(self.mvs)

    def drop_col_data(self, drop_list):
        if self.returns is None:
            print('Warning: no returns in DataHandler object. Please run get_returns()')
        else:
            drop_list = self.filter_drop_list(drop_list)
            if isinstance(self.returns, dict):
                for freq, returns_df in self.returns.items():
                    returns_df.drop(drop_list, axis=1, inplace=True)
            else:
                self.returns.drop(drop_list, axis=1, inplace=True)
            if self.mvs is not None:
                self.mvs.drop(drop_list, axis=1, inplace=True)
                self.get_weights()
            print(f'Dropping columns {drop_list} from returns...')

    def filter_drop_list(self, drop_list):
        check_list = list(set(drop_list) - (set(self.col_list)))
        if any(check_list):
            print(f'removing {check_list} from drop_list')
        return list(set(drop_list) - (set(check_list)))

    def update_dfs(self, data_df):
        # create a Boolean mask for the rows to remove
        mask = data_df.index < self.returns.index[0]
        # select all rows except the ones that are less than first row in returns
        data_df = data_df.loc[~mask]
        return data_df


class GTBmkDataHandler(DataHandler):
    def __init__(self, freq_data=False, eq_bmk='MSCI ACWI IMI', include_fi=True, fi_bmk='FI Benchmark'):
        super().__init__(freq_data=freq_data, eq_bmk=eq_bmk, include_fi=include_fi, fi_bmk=fi_bmk)
        self.bmk_returns = self.get_bmk_returns(filepath=UPSGT_BMK_DATA_FP)

    def get_bmk_returns(self, filepath, drop_na=False):
        returns_data = di.DataImporter.read_excel_data(filepath=filepath, sheet_name=0)
        if self.freq_data:
            returns_data = dxf.get_data_dict(returns_data, drop_na=drop_na)
            self.mkt_returns = dm.filter_data_dict(data_dict=self.mkt_returns, filter_list=returns_data.keys())
        # else:
        #     self.mkt_returns = self.mkt_returns[dm.get_freq_string(returns_data)]
        return returns_data


# TODO: add functionality for bmks
# TODO: make get_returns function for returns of datahandler!
class GTPortDataHandler(GTBmkDataHandler):
    def __init__(self, freq_data=False, eq_bmk='MSCI ACWI IMI', include_fi=True, fi_bmk='FI Benchmark'):
        super().__init__(freq_data=freq_data, eq_bmk=eq_bmk, include_fi=include_fi, fi_bmk=fi_bmk)
        # self.gt_di = None
        self.bmk_key = None
        self.get_returns(filepath=UPSGT_DATA_FP)
        self.get_mvs(filepath=UPSGT_DATA_FP)
        self.update_mkt_returns()
        # self.get_port_data(filepath=UPSGT_DATA_FP)
        self.get_bmk_key()

    # def get_port_data(self, filepath, drop_na=False):
    #     self.gt_di = di.DataImporter(filepath=filepath, sheet_name=None, drop_na=drop_na)
    #     self.returns = dxf.get_data_dict(self.gt_di.data_import['returns'], drop_na=drop_na)
    #     self.mvs = dxf.copy_data(self.gt_di.data_import['market_values'])
    #     self.weights = dm.get_weights(self.mvs, total_col=True, add_total_wgt=True)

    def get_bmk_key(self):
        self.bmk_key = {'Credit': 'Custom Credit Bmk', 'Public Equity w/o Hedgees': 'Equity-MSCI ACWI IMI-Bmk',
                        'Public Equity w/o Derivatives': 'Equity-MSCI ACWI IMI-Bmk',
                        'Public Equity': 'Equity-MSCI ACWI IMI-Bmk', 'Fixed Income': 'FI Bmk-Static',
                        'Liquid Alts': 'Liquid Alts Benchmark', 'Private Equity': 'PE FOF Bmk',
                        'Real Estate': 'RE NCRIEF 1QA^ Bmk'
                        }


# -*- coding: utf-8 -*-


# TODO: filter for only equity, FI and liq alts
# TODO: make get_returns function for returns of datahandler!
class PublicMktsHandler(GTPortDataHandler):
    def __init__(self, eq_bmk='MSCI ACWI IMI', fi_bmk='FI Benchmark'):
        super().__init__(eq_bmk=eq_bmk, fi_bmk=fi_bmk)


# TODO: Re-think bmk_key variable here
class LiqAltsBmkDataHandler(DataHandler):

    def __init__(self, freq_data=False, eq_bmk='MSCI ACWI', fi_bmk='FI Benchmark',
                 include_cm=True, cm_bmk='Commodities (BCOM)', include_fx=True,
                 fx_bmk='U.S. Dollar Index', sub_ports_bmk_key=None):
        super().__init__(freq_data=freq_data, eq_bmk=eq_bmk, fi_bmk=fi_bmk,
                         include_cm=include_cm, cm_bmk=cm_bmk,
                         include_fx=include_fx, fx_bmk=fx_bmk)

        if sub_ports_bmk_key is None:
            sub_ports_bmk_key = BMK_KEYS['Liquid Alts']
        self.sub_ports_bmk_key = sub_ports_bmk_key
        self.sub_port_list = list(self.sub_ports_bmk_key.values())[:-1]
        self.bmk_returns = self.get_bmk_returns()
        self.hf_returns = None

    def get_hf_returns(self):
        print('Getting Hedge Fund returns data...')
        self.hf_returns = di.DataImporter.read_excel_data(filepath=HF_BMK_DATA_FP, sheet_name=None)
        if self.freq_data is False:
            # self.mkt_returns = self.mkt_returns['Monthly']
            self.hf_returns = self.hf_returns['Monthly']

    def get_bmk_returns(self):
        print('Getting Liquid Alts Benchmark returns data...')
        if self.freq_data:
            bmk_returns_data = {}
            for freq_string, returns_df in self.mkt_data_import.items():
                temp_df = dxf.copy_data(returns_df[self.sub_port_list])
                temp_df['Liquid Alts Bmk'] = self.get_wgt_avg_col(temp_df, [0.5, 0.3, 0.2])
                bmk_returns_data[freq_string] = temp_df
            return bmk_returns_data
        else:
            bmk_returns_df = dxf.copy_data(self.mkt_data_import['Monthly'])
            bmk_returns_df = bmk_returns_df[self.sub_port_list]
            bmk_returns_df['Liquid Alts Bmk'] = self.get_wgt_avg_col(bmk_returns_df, [0.5, 0.3, 0.2])
            return bmk_returns_df


# TODO: Add returns from new managers that we just allocated to
# TODO: Add functionality to pull raw data
# TODO: make get_returns function for returns of datahandler!
# TODO: get data dict - monthly, Quarterly, Yearly


def get_mgr_sub_port(mgr):
    mgr_sub_port = ''
    for sub_port in LIQ_ALTS_MGR_DICT:
        if mgr in LIQ_ALTS_MGR_DICT[sub_port]:
            mgr_sub_port = sub_port
            break
    return mgr_sub_port


class LiqAltsPortHandler(LiqAltsBmkDataHandler):

    def __init__(self, eq_bmk='MSCI ACWI', fi_bmk='FI Benchmark', cm_bmk='Commodities (BCOM)',
                 fx_bmk='U.S. Dollar Index', update_mgr_returns=True):
        super().__init__(freq_data=False, eq_bmk=eq_bmk, fi_bmk=fi_bmk, cm_bmk=cm_bmk, fx_bmk=fx_bmk)

        # self.get_raw_data = get_raw_data
        self.update_mgr_returns = update_mgr_returns
        self.mgr_returns_data = self.get_mgr_returns_data() if self.update_mgr_returns else None
        self.sub_ports = self.get_sub_port_data()
        self.returns = self.get_returns()
        self.mvs = self.get_mvs()
        # self.hf_returns = self.update_dfs(self.hf_returns)  # .iloc[24:, ]
        self.bmk_returns = self.update_dfs(self.bmk_returns)
        self.mkt_returns = self.update_dfs(self.mkt_returns['Monthly'])
        self.weights = self.get_full_port_wgts()
        self.bmk_key = self.get_mgr_bmk_key_data()

    def get_sub_port_data(self):
        # pull all returns and mvs
        liq_alts_data = self.get_portfolio_data()
        # liq_alts_mv = read_ret_data(LIQ_ALTS_PORT_DATA_FP, 'market_values')
        # define dicts and dataframes
        liq_alts_dict = {}
        total_ret = pd.DataFrame(index=liq_alts_data['returns'].index)
        total_mv = pd.DataFrame(index=liq_alts_data['market_values'].index)
        # loop through to create sub_ports dict
        for key in LIQ_ALTS_MGR_DICT:
            print(f'Getting {key} sub portfolio data...')
            temp_ret = liq_alts_data['returns'][LIQ_ALTS_MGR_DICT[key]].copy()
            temp_mv = liq_alts_data['market_values'][LIQ_ALTS_MGR_DICT[key]].copy()
            temp_weights = dm.get_weights(temp_mv)
            temp_bmk = self.bmk_returns[[self.sub_ports_bmk_key[key]]].copy()
            temp_dict = dm.get_agg_data(temp_ret, temp_mv, key)
            # if key == 'Trend Following':
            #     temp_dict = {'returns': liq_alts_ret[[key]], 'mv':liq_alts_mv[[key]],
            #                  'weights': dm.get_weights(liq_alts_mv[[key]]),'bmk': temp_bmk}
            liq_alts_dict[key] = {'returns': temp_ret, 'mv': temp_mv,
                                  'weights': temp_weights, 'bmk': temp_bmk}
            total_ret = dm.merge_dfs(total_ret, temp_dict['returns'], False)
            total_mv = dm.merge_dfs(total_mv, temp_dict['mv'], False)
        print(f'Getting Total Liquid Alts sub portfolio data...')
        total_dict = dm.get_agg_data(total_ret, total_mv, 'Total Liquid Alts')
        total_ret = dm.merge_dfs(total_ret, total_dict['returns'], False)
        total_mv = dm.merge_dfs(total_mv, total_dict['mv'], False)
        total_weights = dm.get_weights(total_mv, True, True)
        liq_alts_dict['Total Liquid Alts'] = {'returns': total_ret, 'mv': total_mv,
                                              'weights': total_weights, 'bmk': self.bmk_returns.copy()}
        return liq_alts_dict

    def get_portfolio_data(self):
        print('Getting portfolio data...')
        liq_alts_data = di.DataImporter.read_excel_data(filepath=LIQ_ALTS_PORT_DATA_FP)
        if self.update_mgr_returns:
            liq_alts_data = self.merge_mgr_returns_data(liq_alts_data)
        return liq_alts_data

    @staticmethod
    def get_mgr_returns_data():
        return di.DataImporter.read_excel_data(filepath=RETURNS_DATA_FP + 'liq_alts_mgr_returns.xlsx')

    def merge_mgr_returns_data(self, liq_alts_data):
        print(f'Updating mgr returns {list(self.mgr_returns_data.keys())} data...')
        mgr_returns_df_list = []
        for mgr, mgr_returns_df in self.mgr_returns_data.items():
            liq_alts_mgr_returns_df = dm.drop_nas(dxf.copy_data(liq_alts_data['returns'][[mgr]]))
            while mgr_returns_df.index[-1] >= liq_alts_mgr_returns_df.index[0]:
                liq_alts_mgr_returns_df = liq_alts_mgr_returns_df.iloc[1:, ]
            mgr_returns_df = pd.concat([mgr_returns_df, liq_alts_mgr_returns_df], axis=0)
            mgr_returns_df_list.append(mgr_returns_df)
        liq_alts_data['returns'].drop(list(self.mgr_returns_data.keys()), axis=1, inplace=True)
        liq_alts_data['returns'] = dm.merge_df_lists([*[liq_alts_data['returns'], *mgr_returns_df_list]],
                                                     drop_na=False)
        return liq_alts_data

    def get_returns(self, return_data=True):
        data = 'returns' if return_data else 'mv'
        print(f'Getting Liquid Alts {data} data...')
        liq_alts_port = pd.DataFrame()
        for sub_port in self.sub_ports:
            liq_alts_port = dm.merge_dfs(liq_alts_port, self.sub_ports[sub_port][data], False)
        return liq_alts_port

    def get_mvs(self):
        return self.get_returns(return_data=False)

    def get_full_port_data(self, return_data=True):
        data = 'returns' if return_data else 'mv'
        print(f'Getting Liquid Alts {data} data...')
        liq_alts_port = pd.DataFrame()
        for sub_port in self.sub_ports:
            liq_alts_port = dm.merge_dfs(liq_alts_port, self.sub_ports[sub_port][data], False)
        return liq_alts_port

    def get_full_port_wgts(self):
        print(f'Getting Liquid Alts weights data...')
        mgr_mvs = pd.DataFrame()
        sub_port_mvs = pd.DataFrame()
        for sub_port in self.sub_ports:
            if sub_port == 'Total Liquid Alts':
                sub_port_mvs = dm.merge_dfs(sub_port_mvs, self.sub_ports[sub_port]['mv'], False)
            else:
                mgr_mvs = dm.merge_dfs(mgr_mvs, self.sub_ports[sub_port]['mv'], False)
        mgr_weights = dm.get_weights(mgr_mvs)
        sub_port_weights = dm.get_weights(sub_port_mvs, True, True)
        return dm.merge_dfs(mgr_weights, sub_port_weights, False)

    def get_mgr_bmk_key_data(self):
        bmk_data_dict = {}
        for key in self.sub_ports:
            bmk_name = self.sub_ports_bmk_key[key]
            for mgr in self.sub_ports[key]['returns'].columns:
                if key == 'Total Liquid Alts':
                    bmk_name = self.sub_ports_bmk_key[mgr]
                bmk_data_dict[mgr] = bmk_name
        return bmk_data_dict

    def add_mgr(self, df_mgr_ret, sub_port, mv_amt=100000000):
        self.sub_ports[sub_port]['returns'] = dm.merge_dfs(self.sub_ports[sub_port]['returns'], df_mgr_ret,
                                                           drop_na=False)
        col_list = list(self.sub_ports[sub_port]['returns'].columns)
        self.sub_ports[sub_port]['mv'][col_list[len(col_list) - 1]] = dxf.get_price_data(df_mgr_ret, mv_amt)
        self.sub_ports[sub_port]['weights'] = dm.get_weights(self.sub_ports[sub_port]['mv'])
        self.update_sub_port_total(sub_port)
        self.update_data()
        print(f'Updated {sub_port} portfolio...')

    def remove_mgr(self, mgr):
        sub_port = get_mgr_sub_port(mgr)
        self.sub_ports[sub_port]['returns'].drop([mgr], axis=1, inplace=True)
        self.sub_ports[sub_port]['mv'].drop([mgr], axis=1, inplace=True)
        self.sub_ports[sub_port]['weights'] = dm.get_weights(self.sub_ports[sub_port]['mv'])
        self.update_sub_port_total(sub_port)
        self.update_data()
        print(f'Removed {mgr} from {sub_port} portfolio...')

    def update_mgr(self, mgr, df_mgr_ret, mv_amt=100000000, update_ret=True, update_mv=False):
        sub_port = get_mgr_sub_port(mgr)
        col_list = list(self.sub_ports[sub_port]['returns'].columns)
        if update_ret:
            self.sub_ports[sub_port]['returns'].drop([mgr], axis=1, inplace=True)
            self.sub_ports[sub_port]['returns'] = dm.merge_dfs(self.sub_ports[sub_port]['returns'], df_mgr_ret,
                                                               drop_na=False)
            self.sub_ports[sub_port]['returns'] = self.sub_ports[sub_port]['returns'][col_list]
        if update_mv:
            self.sub_ports[sub_port]['mv'].drop([mgr], axis=1, inplace=True)
            self.sub_ports[sub_port]['mv'][mgr] = dxf.get_price_data(self.sub_ports[sub_port]['returns'][mgr],
                                                                     mv_amt)
            self.sub_ports[sub_port]['mv'] = self.sub_ports[sub_port]['mv'][col_list]
            self.sub_ports[sub_port]['weights'] = dm.get_weights(self.sub_ports[sub_port]['mv'])
        self.update_sub_port_total(sub_port)
        self.update_data(update_mv)
        print(f'Updated {mgr} data in {sub_port} portfolio...')

    # TODO

    def update_sub_port_total(self, sub_port):
        sub_port_dict = dm.get_agg_data(self.sub_ports[sub_port]['returns'],
                                        self.sub_ports[sub_port]['mv'], sub_port)
        self.sub_ports['Total Liquid Alts']['returns'][sub_port] = sub_port_dict['returns'][sub_port]
        self.sub_ports['Total Liquid Alts']['mv'][sub_port] = sub_port_dict['mv'][sub_port]
        total_ret = self.sub_ports['Total Liquid Alts']['returns'][list(LIQ_ALTS_MGR_DICT.keys())]
        total_mv = self.sub_ports['Total Liquid Alts']['mv'][list(LIQ_ALTS_MGR_DICT.keys())]
        total_dict = dm.get_agg_data(total_ret, total_mv, 'Total Liquid Alts')
        self.sub_ports['Total Liquid Alts']['returns']['Total Liquid Alts'] = total_dict['returns'][
            'Total Liquid Alts']
        self.sub_ports['Total Liquid Alts']['mv']['Total Liquid Alts'] = total_dict['mv']['Total Liquid Alts']
        self.sub_ports['Total Liquid Alts']['weights'] = dm.get_weights(self.sub_ports['Total Liquid Alts']['mv'], True,
                                                                        True)

    def update_data(self, update_mv=True):
        self.returns = self.get_full_port_data()
        if update_mv:
            self.mvs = self.get_full_port_data(False)
            self.weights = self.get_full_port_wgts()
        self.bmk_key = self.get_mgr_bmk_key_data()

    def get_sub_mgrs(self, sub_port='Global Macro'):
        mgr_list = []
        mgr_list = mgr_list + LIQ_ALTS_MGR_DICT[sub_port]
        mgr_list.append(sub_port)
        return mgr_list


class LiquidAltsStratDataHandler(LiqAltsBmkDataHandler):
    def __init__(self, filepath, sheet_name=0, bmk_name='HFRX Macro/CTA', eq_bmk='MSCI ACWI', fi_bmk='FI Benchmark',
                 cm_bmk='Commodities (BCOM)', fx_bmk='U.S. Dollar Index'):
        self.filepath = filepath
        self.sheet_name = sheet_name
        self.bmk_name = bmk_name
        self.bmk_key = {}
        super().__init__(freq_data=False, eq_bmk=eq_bmk, fi_bmk=fi_bmk, cm_bmk=cm_bmk, fx_bmk=fx_bmk)
        self.returns = self.get_returns()
        self.update_bmk_key()
        self.update_mkt_returns()

    def get_returns(self):
        returns_data = di.DataImporter.read_excel_data(filepath=self.filepath, sheet_name=self.sheet_name)
        self.col_list = returns_data.columns.tolist()
        return returns_data

    def update_bmk_key(self):
        self.bmk_key[self.col_list[0]] = self.bmk_name
        self.bmk_returns = self.update_dfs(self.bmk_returns)


def create_notional_dict(strategy_list, notional_list=None):
    """
    Updates notional dictionary with strategy(key) and notional(value)

    Parameters:
    strategy_list -- list
    notional_list -- list

    Returns:

    """
    if notional_list is None:
        notional_list = []
    if notional_list:
        notional_list = [float(x) for x in notional_list]
    else:
        notional_list = [float(input('notional value (Billions) for ' + strat + ':')) for strat in strategy_list]
    return dict(zip(strategy_list, notional_list))


class QISDataHandler(MktDataHandler):
    def __init__(self, eq_bmk='S&P 500', include_fi=False, strat_drop_list=None, weight_col='Weighted QIS Strats'):
        super().__init__(eq_bmk=eq_bmk, include_fi=include_fi)

        if strat_drop_list is None:
            strat_drop_list = []
        self.strat_drop_list = strat_drop_list
        self.weight_col = weight_col
        self.returns = self.get_returns()
        self.notional_dict = None
        self.weights = None
        self.get_notional_values()
        self.weighted_hedges_dict = None
        self.weighted_returns = None

    def get_returns(self):
        """
        Returns a dictionary of dataframes with returns data
        in different frequencies

        Parameters:

        Returns:
        dictionary

        """
        data_importer = di.DataImporter(filepath=EQ_HEDGE_DATA_FP, sheet_name=None, drop_na=False, index_data=False)
        returns_dict = dxf.copy_data(data_importer.data_import)
        if self.strat_drop_list:
            for freq_string in returns_dict:
                returns_dict[freq_string].drop(self.strat_drop_list, axis=1, inplace=True)
        return returns_dict

    def add_strategy(self, new_strat_data, notional_list=None):
        """
        Updates returns data with new strategy returns data
        Updates notional weights dictionary with new strategy notional weight

        Parameters:
        filename -- string
        sheet_name -- string
        strategy_list -- list
        notional_list -- list

        Returns:

        """
        if notional_list is None:
            notional_list = []
        if isinstance(new_strat_data, dict):
            strat_list = list(next(iter(new_strat_data.values())).columns)
            new_strat_dict = dxf.copy_data(new_strat_data)
        else:
            strat_list = list(new_strat_data.columns)
            new_strat_dict = dxf.get_data_dict(new_strat_data, index_data=False)

        self.returns = dm.merge_dicts(self.returns, new_strat_dict, drop_na=False)
        print('Added {} to returns'.format(', '.join(strat_list)))
        self.notional_dict.update(create_notional_dict(strat_list, notional_list))
        self.get_weights()

    def get_notional_values(self, equal_weight=True):
        """
        Returns a dictionary of strategy(key) and notional(value)
            Drops strategies
            Updates strategy notionals

        Parameters:

        Returns:
        dictionary

        """
        strategy_list = list(next(iter(self.returns.values())).columns)
        if equal_weight:
            self.notional_dict = {strat: 1.0 for strat in strategy_list}
        else:
            self.update_notional_dict(strategy_list)
        self.get_weights()

    # TODO: Bug in code, check if elements in strategy_list are in self.returns as columns
    def update_notional_dict(self, strategy_list=None):
        if strategy_list is None:
            strategy_list = []
        check_strat_dict = self.check_strat_list(strategy_list)
        if check_strat_dict['not_in_returns']:
            print(f'Following strats not in returns: {check_strat_dict["not_in_returns"]}')

        if check_strat_dict['in_returns']:
            update_notional_list = [float(input('notional value (Billions) for ' + strat + ':')) for strat in
                                    check_strat_dict['in_returns']]
            self.notional_dict.update(create_notional_dict(strategy_list, update_notional_list))
            self.get_weights()

    def check_strat_list(self, strategy_list):
        not_in_returns_list = list(set(strategy_list) - set((next(iter(self.returns.values())))))
        in_returns_list = list(set(strategy_list) - set(not_in_returns_list))
        return {'in_returns': in_returns_list, 'not_in_returns': not_in_returns_list}

    def get_weights(self):
        self.weights = dict(zip(self.notional_dict.keys(), self.get_strat_weights()))

    def get_strat_weights(self, new_strat=False):
        """
        Return weights of each strategy compared to Equity or Equity and FI

        Parameters
        ----------
        new_strat : boolean, optional
            The default is False.

        Returns
        -------
        strat_weights : list

        """

        # get strategy weights (strat_weights)
        notional_values = list(self.notional_dict.values())
        if new_strat:
            notional_values[-1:] = [0]
        strat_total = sum(notional_values)
        # strat_weights = [weight / strat_total for weight in notional_values]
        return [weight / strat_total for weight in notional_values]

    def get_weights_df(self):
        """
        Returns dataframe with portoflio weighting information

        Returns
        -------
        weights_df : dataframe

        """

        # define index of df_weights
        index_list = ['Notional Values (Billions)',
                      'Strategy Weights']

        # compute percentage and strategy weights
        notional_values = list(self.notional_dict.values())
        strat_weights = self.get_strat_weights()

        # create df_weights
        weights_df = pd.DataFrame([notional_values, strat_weights], index=index_list,
                                  columns=[*self.notional_dict])
        return weights_df

    # TODO: Move to datahandler
    # def check_notional(df_returns, notional_weights=[]):
    #     """
    #     Get notional weights if some weights are missing
    #
    #     Parameters
    #     ----------
    #     df_returns : dataframe
    #         dataframe of returns
    #     notional_weights : list, optional
    #         notional weights of strategies. The default is [].
    #
    #     Returns
    #     -------
    #     notional_weights : list
    #
    #     """
    #     # create list of df_returns column names
    #     col_list = list(df_returns.columns)
    #
    #     # get notional weights for weighted strategy returns if not accurate
    #     if len(col_list) != len(notional_weights):
    #         notional_weights = dm.get_notional_weights(df_returns)
    #
    #     return notional_weights

    # TODO: Might have to rename
    def get_weighted_hedges(self, new_strat=False):
        """
        Return dataframe of weighted hedge returns, with and without newest strategy

        Parameters
        ----------
        new_strat : boolean, optional
            Does analysis involve a new strategy. The default is False.

        Returns
        -------
        df_weighted_hedges : dataframe

        """

        strat_weights = self.get_strat_weights()
        strat_weights_old = []
        if new_strat:
            strat_weights_old = self.get_strat_weights(new_strat)
        self.weighted_hedges_dict = {}
        for freq in self.returns:
            temp_returns = self.returns[freq].copy()
            temp_returns = temp_returns.fillna(0)
            weighted_hedges_df = temp_returns.dot(tuple(strat_weights)).to_frame()
            weighted_hedges_df.columns = [self.weight_col]
            if new_strat:
                column_name = f'{self.weight_col} w/o New Strat'
                weighted_hedges_df[column_name] = temp_returns.dot(tuple(strat_weights_old)).to_frame()
            self.weighted_hedges_dict[freq] = weighted_hedges_df

    def get_weighted_returns(self, new_strat=False):
        self.get_weighted_hedges(new_strat)
        self.weighted_returns = dm.merge_dicts(self.returns, self.weighted_hedges_dict, drop_na=False)


# TODO: add comments/explanations for functions
class EQHedgeDataHandler(QISDataHandler):
    def __init__(self, eq_bmk='S&P 500', eq_mv=11.0, include_fi=False, fi_mv=20.0, strat_drop_list=None,
                 update_strat_list=None):
        if update_strat_list is None:
            update_strat_list = []

        self.update_strat_list = update_strat_list

        super().__init__(eq_bmk=eq_bmk, include_fi=include_fi, strat_drop_list=strat_drop_list,
                         weight_col='Weighted Hedges')

        self.eq_mv = eq_mv
        self.fi_mv = fi_mv if self.include_fi else 0.0
        self.bmk_mv_dict = self.get_bmk_mv_data()
        self.weighted_strats_dict = None

    def get_bmk_mv_data(self):
        mv_list = [self.eq_mv, self.fi_mv] if self.include_fi else [self.eq_mv]
        bmk_list = [bmk for bmk in self.mkt_key.values() if bmk is not None]
        return dict(zip(bmk_list, mv_list))

    def get_returns(self):
        """
        Returns a dictionary of dataframes with returns data
        in different frequencies

        Parameters:

        Returns:
        dictionary

        """
        eq_hedge_returns = di.DataImporter.read_excel_data(filepath=EQ_HEDGE_DATA_FP, sheet_name=None)

        returns_dict = {}
        for freq_string, returns_df in eq_hedge_returns.items():
            # TODO: It may be best to just rename the excel column as Dynamic VOLA
            returns_df['VOLA 3'] = returns_df['Dynamic VOLA']
            returns_df['Def Var'] = self.get_wgt_avg_col(returns_df, [0.4, 0.3, 0.3],
                                                         ['Def Var (Fri)', 'Def Var (Mon)', 'Def Var (Wed)'])

            # TODO: The weights may have to be updated
            returns_df['VRR Portfolio'] = self.get_wgt_avg_col(returns_df, [0.75, 0.25],
                                                               ['VRR 2', 'VRR Trend'])

            returns_df = returns_df[list(EQ_HEDGE_STRAT_DICT.keys())]
            if self.strat_drop_list:
                returns_df.drop(self.strat_drop_list, axis=1, inplace=True)
            returns_dict[freq_string] = returns_df.copy()
        return returns_dict

    def get_notional_values(self, **kwargs):
        """
        Returns a dictionary of strategy(key) and notional(value)
            Drops strategies
            Updates strategy notionals

        Parameters:
            **kwargs:

        Returns:
        dictionary

        """
        self.notional_dict = deepcopy(EQ_HEDGE_STRAT_DICT)
        for key in self.strat_drop_list:
            self.notional_dict.pop(key)
        # self.notional_dict
        self.get_weights()

    def get_pct_weights(self, new_strat=False):
        """
        Return percentage weights based off of notional weights

        Parameters
        ----------
        new_strat : boolean, optional
            The default is False.

        Returns
        -------
        pct_weights : list

        """
        total_weight = sum(self.bmk_mv_dict.values())
        pct_weights = [weight / total_weight for weight in [*self.bmk_mv_dict.values(), *self.notional_dict.values()]]
        if new_strat:
            pct_weights[-1:] = [0]
        return pct_weights

    def get_weights_df(self):
        """
        Returns dataframe with portoflio weighting information

        Returns
        -------
        weights_df : dataframe

        """

        # define index of df_weights
        index_list = ['Notional Values (Billions)',
                      'Percentage Weights',
                      'Strategy Weights']

        # compute percentage and strategy weights
        notional_values = [*self.bmk_mv_dict.values(), *self.notional_dict.values()]
        # pct_weights = self.get_pct_weights()
        strat_weights = [*len(self.bmk_mv_dict) * [0], *self.get_strat_weights()]

        # create df_weights
        weights_df = pd.DataFrame([notional_values, self.get_pct_weights(), strat_weights],
                                  index=index_list, columns=[*self.bmk_mv_dict, *self.notional_dict])
        return weights_df

    # TODO: Move to datahandler
    # def check_notional(df_returns, notional_weights=[]):
    #     """
    #     Get notional weights if some weights are missing
    #
    #     Parameters
    #     ----------
    #     df_returns : dataframe
    #         dataframe of returns
    #     notional_weights : list, optional
    #         notional weights of strategies. The default is [].
    #
    #     Returns
    #     -------
    #     notional_weights : list
    #
    #     """
    #     # create list of df_returns column names
    #     col_list = list(df_returns.columns)
    #
    #     # get notional weights for weighted strategy returns if not accurate
    #     if len(col_list) != len(notional_weights):
    #         notional_weights = dm.get_notional_weights(df_returns)
    #
    #     return notional_weights

    def get_weighted_strats(self, new_strat=False):
        """
        Returns dictionary of weighted strategy returns, with and without newest strategy

        Parameters
        ----------
        new_strat : boolean, optional
            Does analysis involve a new strategy. The default is False.

        Returns
        -------
        weighted_strats : dataframe

        """

        returns_dict = dm.merge_dicts(main_dict=self.mkt_returns, new_dict=self.returns,
                                      drop_na=False, fillzeros=True)
        pct_weights = self.get_pct_weights()
        pct_weights_old = []
        if new_strat:
            pct_weights_old = self.get_pct_weights(new_strat)

        self.weighted_strats_dict = {}
        for freq in self.returns:
            weighted_strats_df = returns_dict[freq].dot(tuple(pct_weights)).to_frame()
            weighted_strats_df.columns = ['Weighted Strats']

            # get weighted strategies without new strat
            if new_strat:
                weighted_strats_df['Weighted Strats w/o New Strat'] = returns_dict[freq].dot(
                    tuple(pct_weights_old)).to_frame()

            self.weighted_strats_dict[freq] = weighted_strats_df

    def get_weighted_returns(self, new_strat=False):
        self.get_weighted_hedges(new_strat)
        self.get_weighted_strats(new_strat)
        self.weighted_returns = dm.merge_dicts(self.weighted_hedges_dict, self.weighted_strats_dict)
        self.weighted_returns = dm.merge_dicts(self.returns, self.weighted_returns, drop_na=False)

# -*- coding: utf-8 -*-
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

CWD = os.getcwd()
RETURNS_DATA_FP = CWD + '\\EquityHedging\\data\\returns_data\\'
BMK_DATA_FP = RETURNS_DATA_FP + 'bmk_returns-new.xlsx'
HF_BMK_DATA_FP = RETURNS_DATA_FP + 'hf_bmks-new.xlsx'
UPSGT_DATA_FP = RETURNS_DATA_FP + 'upsgt_returns.xlsx'
EQ_HEDGE_DATA_FP = RETURNS_DATA_FP + 'eq_hedge_returns-new.xlsx'
# LIQ_ALTS_BMK_DATA_FP = RETURNS_DATA_FP+'liq_alts_bmks-old.xlsx'
LIQ_ALTS_PORT_DATA_FP = RETURNS_DATA_FP + 'nexen_liq_alts_data-new.xlsx'

NEW_STRAT_DATA_FP = CWD + '\\EquityHedging\\data\\new_strats\\'

LIQ_ALTS_MGR_DICT = {'Global Macro': ['1907 Penso Class A', 'Bridgewater Alpha', 'DE Shaw Oculus Fund',
                                      'Element Capital', 'JSC Vantage', 'Capula TM Fund', 'KAF'],
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


def read_ret_data(fp, sheet_name):
    ret_data = pd.read_excel(fp, sheet_name, index_col=0)
    return dm.get_real_cols(ret_data)


# TODO: Import data using di. it'll be efficient in the long run.
# TODO: Get mkt_ret_data, bmk_ret_data, hf_ret_data/hf_bmk_ret_data,
class mktHandler(di.dataImporter):
    def __init__(self, eq_bmk='MSCI ACWI', include_fi=True, fi_bmk='FI Benchmark',
                 include_cm=False, cm_bmk='Commodities (BCOM)', include_fx=False,
                 fx_bmk='U.S. Dollar Index'):

        super().__init__(filepath=BMK_DATA_FP, sheet_name=None, drop_na=False)
        self.eq_bmk = eq_bmk
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
        # if self.all_data:
        #     returns_dict = dxf.copy_data(self.data_import)
        # else:
        for freq_string in self.data_import:
            returns_df = self.data_import[freq_string]
            temp_df = pd.DataFrame(index=returns_df.index)
            for key in self.mkt_key:
                try:
                    if freq_string != 'Daily' and self.fi_bmk == 'FI Benchmark':
                        returns_df[self.fi_bmk] = returns_df['Long Corp'] * 0.6 + returns_df['STRIPS'] * 0.4
                    temp_df = dm.merge_data_frames(temp_df, returns_df[[self.mkt_key[key]]])
                except KeyError:
                    pass
            if temp_df.empty is False:
                returns_dict[freq_string] = temp_df
        return returns_dict


# TODO: add functionality for bmks
# TODO: make get_returns function for returns of datahandler!
class gTPortHandler(mktHandler):
    def __init__(self, eq_bmk='MSCI ACWI IMI', include_fi=True, fi_bmk='FI Benchmark', ):
        super().__init__(eq_bmk, include_fi, fi_bmk)
        self.mkt_returns = self.mkt_returns['Monthly']
        self.gt_data = di.dataImporter(UPSGT_DATA_FP, sheet_name=None, drop_na=False).data_import
        self.returns = di.read_excel_data(UPSGT_DATA_FP, 'returns')
        self.mvs = di.read_excel_data(UPSGT_DATA_FP, 'market_values')
        self.weights = dm.get_wgts(self.mvs, True, True)

        self.get_port_data(filepath=UPSGT_DATA_FP)

    def get_port_data(self, filepath, drop_na=False):
        self.data_importer = di.dataImporter(filepath=filepath, sheet_name=None, drop_na=drop_na)
        self.returns1 = self.data_importer.data_import['returns']
        self.mvs1 = self.data_importer.data_import['market_values']
        self.weights1 = dm.get_wgts(self.mvs1, total_col=True, add_total_wgt=True)


# TODO: filter for only equity, FI and liq alts
# TODO: make get_returns function for returns of datahandler!
class publicMktsHandler(gTPortHandler):
    def __init__(self, eq_bmk='MSCI ACWI IMI', fi_bmk='FI Benchmark'):
        super().__init__(eq_bmk, fi_bmk=fi_bmk)


class liqAltsBmkHandler(mktHandler):
    def __init__(self, eq_bmk='MSCI ACWI', fi_bmk='FI Benchmark',
                 include_cm=True, cm_bmk='Commodities (BCOM)', include_fx=True,
                 fx_bmk='U.S. Dollar Index', bmk_key=BMK_KEYS['Liquid Alts']):
        super().__init__(eq_bmk=eq_bmk, fi_bmk=fi_bmk,
                         include_cm=include_cm, cm_bmk=cm_bmk,
                         include_fx=include_fx, fx_bmk=fx_bmk)

        self.bmk_key = bmk_key
        self.sub_port_list = list(self.bmk_key.values())[:-1]
        self.get_bmk_returns1()

    def get_bmk_returns1(self):
        self.hf_di = di.dataImporter(filepath=HF_BMK_DATA_FP, sheet_name=None, drop_na=False)
        self.hf_returns = dxf.copy_data(self.hf_di.data_import)
        self.bmk_returns = {}
        for freq_string in self.data_import:
            self.bmk_returns[freq_string] = self.data_import[freq_string][self.sub_port_list]
            self.bmk_returns[freq_string]['Liquid Alts Bmk'] = self.bmk_returns[freq_string].dot([0.5, 0.3,
                                                                                                  0.2])  # *returns_df['HFRX Macro/CTA'] + 0.3*returns_df['HFRX Absolute Return'] + 0.2*returns_df['SG Trend']


# TODO: Add returns from new managers that we just allocated to
# TODO: Add functionality to pull raw data
# TODO: make get_returns function for returns of datahandler!
# TODO: get data dict - monthly, Quarterly, Yearly
class liqAltsPortHandler(liqAltsBmkHandler):
    def __init__(self, eq_bmk='MSCI ACWI', fi_bmk='FI Benchmark',
                 cm_bmk='Commodities (BCOM)', fx_bmk='U.S. Dollar Index'):
        super().__init__(eq_bmk=eq_bmk, fi_bmk=fi_bmk, cm_bmk=cm_bmk, fx_bmk=fx_bmk)

        self.hf_returns = self.hf_returns['Monthly']
        self.bmk_returns = self.bmk_returns['Monthly']
        self.mkt_returns = self.mkt_returns['Monthly'].iloc[11:, ]
        self.sub_ports = self.get_sub_port_data()
        self.returns = self.get_full_port_data()
        self.mvs = self.get_full_port_data(False)
        self.weights = self.get_full_port_wgts()
        self.mgr_bmk_dict = self.get_mgr_bmk_data()

    def get_sub_port_data(self, filepath=LIQ_ALTS_PORT_DATA_FP):
        # pull all returns and mvs
        liq_alts_ret = read_ret_data(LIQ_ALTS_PORT_DATA_FP, 'returns')
        liq_alts_mv = read_ret_data(LIQ_ALTS_PORT_DATA_FP, 'market_values')
        # define dicts and dataframes
        liq_alts_dict = {}
        total_ret = pd.DataFrame(index=liq_alts_ret.index)
        total_mv = pd.DataFrame(index=liq_alts_mv.index)
        # loop through to create sub_ports dict
        for key in LIQ_ALTS_MGR_DICT:
            temp_dict = {}
            temp_ret = liq_alts_ret[LIQ_ALTS_MGR_DICT[key]].copy()
            temp_mv = liq_alts_mv[LIQ_ALTS_MGR_DICT[key]].copy()
            temp_wgts = dm.get_wgts(temp_mv)
            temp_bmk = self.bmk_returns[[self.bmk_key[key]]].copy()
            temp_dict = dm.get_agg_data(temp_ret, temp_mv, key)
            # if key == 'Trend Following':
            #     temp_dict = {'returns': liq_alts_ret[[key]], 'mv':liq_alts_mv[[key]],
            #                  'weights': dm.get_wgts(liq_alts_mv[[key]]),'bmk': temp_bmk}
            liq_alts_dict[key] = {'returns': temp_ret, 'mv': temp_mv,
                                  'weights': temp_wgts, 'bmk': temp_bmk}
            total_ret = dm.merge_data_frames(total_ret, temp_dict['returns'], False)
            total_mv = dm.merge_data_frames(total_mv, temp_dict['mv'], False)
        total_dict = dm.get_agg_data(total_ret, total_mv, 'Total Liquid Alts')
        total_ret = dm.merge_data_frames(total_ret, total_dict['returns'], False)
        total_mv = dm.merge_data_frames(total_mv, total_dict['mv'], False)
        total_wgts = dm.get_wgts(total_mv, True, True)
        liq_alts_dict['Total Liquid Alts'] = {'returns': total_ret, 'mv': total_mv,
                                              'weights': total_wgts, 'bmk': self.bmk_returns.copy()}
        return liq_alts_dict

    def get_full_port_data(self, return_data=True):
        data = 'returns' if return_data else 'mv'
        liq_alts_port = pd.DataFrame()
        for sub_port in self.sub_ports:
            liq_alts_port = dm.merge_data_frames(liq_alts_port, self.sub_ports[sub_port][data], False)
        return liq_alts_port

    def get_full_port_wgts(self):
        mgr_mvs = pd.DataFrame()
        sub_port_mvs = pd.DataFrame()
        for sub_port in self.sub_ports:
            if sub_port == 'Total Liquid Alts':
                sub_port_mvs = dm.merge_data_frames(sub_port_mvs, self.sub_ports[sub_port]['mv'], False)
            else:
                mgr_mvs = dm.merge_data_frames(mgr_mvs, self.sub_ports[sub_port]['mv'], False)
        mgr_wgts = dm.get_wgts(mgr_mvs)
        sub_port_wgts = dm.get_wgts(sub_port_mvs, True, True)
        return dm.merge_data_frames(mgr_wgts, sub_port_wgts, False)

    def get_mgr_bmk_data(self):
        bmk_data_dict = {}
        for key in self.sub_ports:
            bmk_name = self.bmk_key[key]
            for mgr in self.sub_ports[key]['returns'].columns:
                if key == 'Total Liquid Alts':
                    bmk_name = self.bmk_key[mgr]
                bmk_data_dict[mgr] = bmk_name
        return bmk_data_dict

    def add_mgr(self, df_mgr_ret, sub_port, mv_amt=100000000):
        self.sub_ports[sub_port]['returns'] = dm.merge_data_frames(self.sub_ports[sub_port]['returns'], df_mgr_ret,
                                                                   drop_na=False)
        col_list = list(self.sub_ports[sub_port]['returns'].columns)
        self.sub_ports[sub_port]['mv'][col_list[len(col_list) - 1]] = dm.get_prices_df(df_mgr_ret, mv_amt)
        self.sub_ports[sub_port]['weights'] = dm.get_wgts(self.sub_ports[sub_port]['mv'])
        self.update_sub_port_total(sub_port)
        self.update_data()
        print(f'updated {sub_port} portfolio...')

    def remove_mgr(self, mgr):
        sub_port = self.get_mgr_sub_port(mgr)
        self.sub_ports[sub_port]['returns'].drop([mgr], axis=1, inplace=True)
        self.sub_ports[sub_port]['mv'].drop([mgr], axis=1, inplace=True)
        self.sub_ports[sub_port]['weights'] = dm.get_wgts(self.sub_ports[sub_port]['mv'])
        self.update_sub_port_total(sub_port)
        self.update_data()
        print(f'removed {mgr} from {sub_port} portfolio...')

    def update_mgr(self, mgr, df_mgr_ret, mv_amt=100000000, update_ret=True, update_mv=False):
        sub_port = self.get_mgr_sub_port(mgr)
        col_list = list(self.sub_ports[sub_port]['returns'].columns)
        if update_ret:
            self.sub_ports[sub_port]['returns'].drop([mgr], axis=1, inplace=True)
            self.sub_ports[sub_port]['returns'] = dm.merge_data_frames(self.sub_ports[sub_port]['returns'], df_mgr_ret,
                                                                       drop_na=False)
            self.sub_ports[sub_port]['returns'] = self.sub_ports[sub_port]['returns'][col_list]
        if update_mv:
            self.sub_ports[sub_port]['mv'].drop([mgr], axis=1, inplace=True)
            self.sub_ports[sub_port]['mv'][mgr] = dm.get_prices_df(self.sub_ports[sub_port]['returns'][mgr], mv_amt)
            self.sub_ports[sub_port]['mv'] = self.sub_ports[sub_port]['mv'][col_list]
            self.sub_ports[sub_port]['weights'] = dm.get_wgts(self.sub_ports[sub_port]['mv'])
        self.update_sub_port_total(sub_port)
        self.update_data(update_mv)
        print(f'updated {mgr} data in {sub_port} portfolio...')

    # TODO
    def get_mgr_sub_port(self, mgr):
        for sub_port in LIQ_ALTS_MGR_DICT:
            if mgr in LIQ_ALTS_MGR_DICT[sub_port]:
                break
        return sub_port

    def update_sub_port_total(self, sub_port):
        sub_port_dict = dm.get_agg_data(self.sub_ports[sub_port]['returns'],
                                        self.sub_ports[sub_port]['mv'], sub_port)
        self.sub_ports['Total Liquid Alts']['returns'][sub_port] = sub_port_dict['returns'][sub_port]
        self.sub_ports['Total Liquid Alts']['mv'][sub_port] = sub_port_dict['mv'][sub_port]
        total_ret = self.sub_ports['Total Liquid Alts']['returns'][list(LIQ_ALTS_MGR_DICT.keys())]
        total_mv = self.sub_ports['Total Liquid Alts']['mv'][list(LIQ_ALTS_MGR_DICT.keys())]
        total_dict = dm.get_agg_data(total_ret, total_mv, 'Total Liquid Alts')
        self.sub_ports['Total Liquid Alts']['returns']['Total Liquid Alts'] = total_dict['returns']['Total Liquid Alts']
        self.sub_ports['Total Liquid Alts']['mv']['Total Liquid Alts'] = total_dict['mv']['Total Liquid Alts']
        self.sub_ports['Total Liquid Alts']['weights'] = dm.get_wgts(self.sub_ports['Total Liquid Alts']['mv'], True,
                                                                     True)

    def update_data(self, update_mv=True):
        self.returns = self.get_full_port_data()
        if update_mv:
            self.mvs = self.get_full_port_data(False)
            self.wgts = self.get_full_port_wgts()
        self.mgr_bmk_dict = self.get_mgr_bmk_data()

    def get_sub_mgrs(self, sub_port='Global Macro'):
        mgr_list = []
        mgr_list = mgr_list + LIQ_ALTS_MGR_DICT[sub_port]
        mgr_list.append(sub_port)
        return mgr_list


# TODO: add comments/explanations for functions
class eqHedgeHandler(mktHandler):
    def __init__(self, eq_bmk='S&P 500', eq_mv=11.0, include_fi=False, fi_mv=20.0, strat_drop_list=[]
                 , update_strat_list=[]
                 ):
        super().__init__(eq_bmk, include_fi=include_fi)

        self.update_strat_list = None
        self.eq_mv = eq_mv
        self.fi_mv = fi_mv if self.include_fi else 0.0
        self.bmk_mv_dict = self.get_bmk_mv_data()
        self.strat_drop_list = strat_drop_list
        self.returns = self.get_returns()
        self.notional_dict = self.get_notional_values()
        self.weights = self.get_weights()
        self.weighted_hedges_dict = None
        self.weighted_strats_dict = None
        self.weighted_returns = None

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
        returns_dict = {}
        freq_list = di.get_excel_sheet_names(EQ_HEDGE_DATA_FP)
        for freq_string in freq_list:
            temp_ret = dm.get_real_cols(di.read_excel_data(EQ_HEDGE_DATA_FP, freq_string))
            # TODO: It may be best to just rename the excel column as Dynamic VOLA
            temp_ret['VOLA 3'] = temp_ret['Dynamic VOLA']
            temp_ret['Def Var'] = temp_ret['Def Var (Fri)'] * 0.4 + temp_ret['Def Var (Mon)'] * 0.3 + temp_ret[
                'Def Var (Wed)'] * 0.3

            # TODO: The weights may have to be updated
            temp_ret['VRR Portfolio'] = temp_ret['VRR 2'] * 0.75 + temp_ret['VRR Trend'] * 0.25

            temp_ret = temp_ret[list(EQ_HEDGE_STRAT_DICT.keys())]
            if self.strat_drop_list:
                temp_ret.drop(self.strat_drop_list, axis=1, inplace=True)
            returns_dict[freq_string] = temp_ret.copy()
        return returns_dict

    def add_strategy(self, new_strat_data, notional_list):
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
        if isinstance(new_strat_data, dict):
            first_key = next(iter(new_strat_data))
            strat_list = list(new_strat_data[first_key].columns)
            new_strat_dict = dxf.copy_data(new_strat_data)
        else:
            strat_list = list(new_strat_data.columns)
            new_strat_dict = dm.get_data_dict(new_strat_data, return_data=True)

        self.returns = dm.merge_dicts(self.returns, new_strat_dict, drop_na=False)
        print('Added {} to returns'.format(', '.join(strat_list)))
        self.notional_dict.update(self.create_notional_dict(strat_list, notional_list))

    def create_notional_dict(self, strategy_list, notional_list):
        """
        Updates notional dictionary with strategy(key) and notional(value)

        Parameters:
        strategy_list -- list
        notional_list -- list
        
        Returns:
        
        """
        notional_list = [float(x) for x in notional_list]
        # notional_dict = (dict(zip(strategy_list, notional_list)))
        # return notional_dict
        return (dict(zip(strategy_list, notional_list)))

    def get_notional_values(self):
        """
        Returns a dictionary of strategy(key) and notional(value) 
            Drops strategies
            Updates strategy notionals
        
        Parameters:
        
        Returns:
        dictionary
        
        """
        notional_dict = deepcopy(EQ_HEDGE_STRAT_DICT)
        for key in self.strat_drop_list:
            notional_dict.pop(key)
        return notional_dict

    def update_notional_dict(self, strategy_list):
        if strategy_list:
            update_notional_list = [float(input('notional value (Billions) for ' + strat + ':')) for strat in
                                    self.update_strat_list]
            self.notional_dict.update(self.create_notional_dict(self.update_strat_list, update_notional_list))

    def get_weights(self):
        return (dict(zip(self.notional_dict.keys(), self.get_strat_weights())))

    # TODO: compress
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
    def check_notional(df_returns, notional_weights=[]):
        """
        Get notional weights if some weights are missing

        Parameters
        ----------
        df_returns : dataframe
            dataframe of returns
        notional_weights : list, optional
            notional weights of strategies. The default is [].
        
        Returns
        -------
        notional_weights : list

        """
        # create list of df_returns column names
        col_list = list(df_returns.columns)

        # get notional weights for weighted strategy returns if not accurate
        if len(col_list) != len(notional_weights):
            notional_weights = []
            notional_weights = dm.get_notional_weights(df_returns)

        return notional_weights

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

        return_dict = dm.merge_dicts(main_dict=self.mkt_returns, new_dict=self.returns,
                                     drop_na=False, fillzeros=True)
        pct_weights = self.get_pct_weights()
        pct_weights_old = []
        if new_strat:
            pct_weights_old = self.get_pct_weights(new_strat)

        self.weighted_strats_dict = {}
        for freq in self.returns:
            weighted_strats_df = return_dict[freq].dot(tuple(pct_weights)).to_frame()
            weighted_strats_df.columns = ['Weighted Strats']

            # get weighted strategies without new strat
            if new_strat:
                weighted_strats_df['Weighted Strats w/o New Strat'] = return_dict[freq].dot(
                    tuple(pct_weights_old)).to_frame()

            self.weighted_strats_dict[freq] = weighted_strats_df

    def get_weighted_hedges(self, new_strat=False, weight_col='Weighted Hedges'):
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
            weighted_hedges_df.columns = ['Weighted Hedges']
            if new_strat:
                column_name = 'Weighted Hedges w/o New Strat'
                weighted_hedges_df[column_name] = temp_returns.dot(tuple(strat_weights_old)).to_frame()
            self.weighted_hedges_dict[freq] = weighted_hedges_df

    def get_weighted_returns(self, new_strat=False):
        self.get_weighted_hedges(new_strat)
        self.get_weighted_strats(new_strat)
        self.weighted_returns = dm.merge_dicts(self.weighted_hedges_dict, self.weighted_strats_dict)
        self.weighted_returns = dm.merge_dicts(self.returns, self.weighted_returns, drop_na=False)
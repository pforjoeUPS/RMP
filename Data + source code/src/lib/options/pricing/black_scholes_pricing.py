__author__ = 'kammari030116'

import numpy as np
import pandas as pd
import scipy.optimize as op
from scipy import interpolate
from scipy.stats import norm
import os

from src.lib.options.pricing.pricing import OptionPricing
from src.lib.options.black_scholes.black_scholes import price_single, price_single_no_rate_no_div_bbg_vol
from src.lib.options.black_scholes.black_scholes import delta_diff, get_rate_or_div, get_bs_volga, get_bs_vanna, \
    get_bs_theta

__all__ = ['BlackScholesPricing']


class BlackScholesPricing(OptionPricing):
    NUM_DAYS_YEAR = 365

    def __init__(self, undl, spots):
        super(BlackScholesPricing, self).__init__()

        self._spots = spots
        data_read_path = os.path.abspath(os.path.join("Data_cache.h5"))
        rf_rates_df = pd.read_hdf(data_read_path, key="rates_data").fillna(method='ffill')
        rf_rates_df.columns = list(map(eval, rf_rates_df.columns))
        dividends_df = pd.read_hdf(data_read_path, key="dividends_data").fillna(method='ffill')
        dividends_df.columns = list(map(eval, dividends_df.columns))
        volatilities_df = pd.read_hdf(data_read_path, key="implied_volatility_data").fillna(method='ffill')
        volatilities_df.columns = pd.MultiIndex.from_tuples(list(map(eval, volatilities_df.columns)))

        # volatility arrays
        self.volatilities_3d = np.reshape(volatilities_df.values, (volatilities_df.index.size,
                                                                   volatilities_df.columns.levels[0].size,
                                                                   42))
        self.vol_maturities_list = volatilities_df.columns.levels[0].values
        self.vol_strikes_2d = np.array(list(zip(*volatilities_df.columns.tolist()))[1], dtype=np.float64)
        self.vol_strikes_2d = np.reshape(self.vol_strikes_2d, (self.vol_maturities_list.size, 42))
        self.vol_dates_list = volatilities_df.index.values.astype(np.int64)

        # rates arrays
        self.rf_rates_2d = rf_rates_df.values
        self.rates_maturities_list = rf_rates_df.columns.values
        self.rates_dates_list = rf_rates_df.index.values.astype(np.int64)

        # dividends arrays
        self.dividends_2d = dividends_df.values
        self.div_maturities_list = dividends_df.columns.values / float(BlackScholesPricing.NUM_DAYS_YEAR)
        self.div_dates_list = dividends_df.index.values.astype(np.int64)

    def price(self, dates, options):
        prices, deltas, vegas, volas, gammas = [], [], [], [], []

        for pricing_date, options_batch in zip(dates, options):
            row_prices, row_deltas, row_vegas, row_ivols, row_gammas = [], [], [], [], []
            # TODO: do this for all dates at the same time
            timestamp = pricing_date.to_datetime64().astype(np.int64)
            for option in options_batch:
                call_put = -1 if option.type == 'PUT' else 1
                maturity = (option.maturity - pricing_date).days / float(BlackScholesPricing.NUM_DAYS_YEAR)
                spot = self._spots[pricing_date]
                adj_k = option.strike / spot

                price, delta, vega, gamma, skew, vol = \
                    price_single(call_put, timestamp, spot, maturity, adj_k,
                                 self.volatilities_3d, self.vol_maturities_list, self.vol_strikes_2d,
                                 self.vol_dates_list,
                                 self.rf_rates_2d, self.rates_maturities_list, self.rates_dates_list,
                                 self.dividends_2d, self.div_maturities_list, self.div_dates_list)

                if option.maturity == pricing_date:
                    row_prices.append(option._payoff)
                else:
                    row_prices.append(price)
                row_deltas.append(delta)
                row_vegas.append(vega)
                row_ivols.append(vol)
                row_gammas.append(gamma)

            prices.append(row_prices)
            deltas.append(row_deltas)
            vegas.append(row_vegas)
            volas.append(row_ivols)
            gammas.append(row_gammas)

        return prices, deltas, vegas, volas, gammas

    def price_gamma_no_rate_no_div_bbg_vol(self, dates, options, volas):
        gammas = []

        for pricing_date, options_batch, vol in zip(dates, options, volas):
            row_gammas = []
            timestamp = pricing_date.to_datetime64().astype(np.int64)
            for id_o, option in enumerate(options_batch):
                call_put = -1 if option.type == 'PUT' else 1
                maturity = (option.maturity - pricing_date).days / float(BlackScholesPricing.NUM_DAYS_YEAR)
                spot = self._spots[pricing_date]
                adj_k = option.strike / spot

                price, delta, vega, gamma, skew, __ = \
                    price_single_no_rate_no_div_bbg_vol(call_put, timestamp, spot, maturity, adj_k,
                                                        self.volatilities_3d, self.vol_maturities_list,
                                                        self.vol_strikes_2d,
                                                        self.vol_dates_list, vol[id_o])

                row_gammas.append(gamma)

            gammas.append(row_gammas)

        return gammas

    def get_strike_from_delta(self, delta_ref, pricing_date, opt_type, maturity):

        timestamp = pricing_date.to_datetime64().astype(np.int64)
        call_put = -1 if opt_type == 'PUT' else 1
        maturity = (maturity - pricing_date).days / float(BlackScholesPricing.NUM_DAYS_YEAR)
        spot = self._spots[pricing_date]

        maturity = max(self.vol_maturities_list[0], maturity)
        maturity = min(maturity, self.vol_maturities_list[-1])
        mask = self.vol_maturities_list <= maturity
        id_t1 = mask[mask].size - 1
        t1 = self.vol_maturities_list[id_t1]
        mask = self.vol_dates_list <= timestamp
        id_last_date = mask[mask].size - 1

        volatility_t1 = self.volatilities_3d[id_last_date, id_t1]
        strikes_t1 = self.vol_strikes_2d[id_t1]

        if t1 != maturity:
            id_t2 = id_t1 + 1
            t2 = self.vol_maturities_list[id_t2]
            volatility_t2 = self.volatilities_3d[id_last_date, id_t2]
            strikes_t2 = self.vol_strikes_2d[id_t2]
        else:
            t2 = None
            volatility_t2 = None
            strikes_t2 = None

        rate = get_rate_or_div(timestamp, maturity, self.rf_rates_2d, self.rates_maturities_list, self.rates_dates_list)
        div = get_rate_or_div(timestamp, maturity, self.dividends_2d, self.div_maturities_list, self.div_dates_list)

        adj_k = op.bisect(delta_diff, 0.1, 1.9, args=(delta_ref, call_put, spot, maturity, t1, strikes_t1,
                                                      volatility_t1, t2, strikes_t2, volatility_t2, rate, div),
                          xtol=0.00001)

        return adj_k

    def _get_rates_or_div(self, rate_2d, maturities_list, dates_list, pricing_dates, options):
        option_maturities = self.get_time_to_maturity(pricing_dates, options)
        pricing_dates = pd.to_datetime(pricing_dates).astype(np.int64) / (10 ** 9)
        dates_list = pd.to_datetime(dates_list).astype(np.int64) / (10 ** 9)
        df_rate = pd.DataFrame(rate_2d, index=dates_list, columns=maturities_list)
        df_rate = df_rate.reindex(index=pricing_dates, method='ffill').ffill()
        interporlated_actualiations = []
        for idx_ in range(len(pricing_dates)):
            s_ = df_rate.iloc[idx_]
            model_ = interpolate.interp1d(s_.index, s_.values, bounds_error=False,
                                          fill_value=tuple(s_.iloc[[0, -1]].values))
            interporlated_rates = model_(option_maturities[idx_])
            interporlated_actualiations.append(list(np.exp(- interporlated_rates * option_maturities[idx_])))
        return interporlated_actualiations

    def get_rates_actualisation(self, dates, options):
        return self._get_rates_or_div(self.rf_rates_2d, self.rates_maturities_list, self.rates_dates_list, dates,
                                      options)

    def get_div_actualisation(self, dates, options):
        return self._get_rates_or_div(self.dividends_2d, self.div_maturities_list, self.div_dates_list, dates, options)

    @staticmethod
    def get_time_to_maturity(dates, options):
        dates = pd.to_datetime(dates).astype(np.int64) / (10 ** 9)
        num_days_per_year = float(BlackScholesPricing.NUM_DAYS_YEAR)
        return [[(o.maturity.timestamp() - dates[t]) / (num_days_per_year * 3600 * 24) for o in opts] for t, opts in
                enumerate(options)]

    def get_volga(self, dates, options, volas):
        volgas = []
        rates_actualisation = self.get_rates_actualisation(dates, options)
        div_actualisation = self.get_div_actualisation(dates, options)
        time_to_maturity = self.get_time_to_maturity(dates, options)
        for t in range(len(dates)):
            spot_t = self._spots.iloc[t]
            strikes = np.asarray([o.strike for o in options[t]])
            vol_sqrt_T_t = np.asarray(volas[t]) * np.sqrt(time_to_maturity[t])
            d_1 = (np.log(spot_t * np.asarray(div_actualisation[t]) / (strikes * np.asarray(rates_actualisation[t]))) / vol_sqrt_T_t) + (0.5 * vol_sqrt_T_t)
            d_2 = d_1 - vol_sqrt_T_t
            volga_t = spot_t * np.asarray(div_actualisation[t]) * norm.pdf(d_1) * np.sqrt(time_to_maturity[t]) * d_1 * d_2 / np.asarray(volas[t])
            volgas.append(list(volga_t))
        return volgas

    def get_vanna(self, dates, options, volas):
        vannas = []
        rates_actualisation = self.get_rates_actualisation(dates, options)
        div_actualisation = self.get_div_actualisation(dates, options)
        time_to_maturity = self.get_time_to_maturity(dates, options)
        for t in range(len(dates)):
            spot_t = self._spots.iloc[t]
            strikes = np.asarray([o.strike for o in options[t]])
            vol_sqrt_T_t = np.asarray(volas[t]) * np.sqrt(time_to_maturity[t])
            d_1 = (np.log(spot_t * np.asarray(div_actualisation[t]) / (
                    strikes * np.asarray(rates_actualisation[t]))) / vol_sqrt_T_t) + (0.5 * vol_sqrt_T_t)
            d_2 = d_1 - vol_sqrt_T_t
            vanna = - np.asarray(div_actualisation[t]) * norm.pdf(d_1) * d_2 / np.asarray(volas[t])
            vannas.append(list(vanna))
        return vannas

    def get_theta(self, dates, options, volas):
        thetas = []
        rates_actualisation = self.get_rates_actualisation(dates, options)
        div_actualisation = self.get_div_actualisation(dates, options)
        time_to_maturity = self.get_time_to_maturity(dates, options)
        for t in range(len(dates)):
            spot_t = self._spots.iloc[t]
            strikes = np.asarray([o.strike for o in options[t]])
            put_condition = np.asarray([o.type == 'PUT' for o in options[t]])
            vol_sqrt_T_t = np.asarray(volas[t]) * np.sqrt(time_to_maturity[t])
            d_1 = (np.log(spot_t * np.asarray(div_actualisation[t]) / (
                    strikes * np.asarray(rates_actualisation[t]))) / vol_sqrt_T_t) + (0.5 * vol_sqrt_T_t)
            d_2 = d_1 - vol_sqrt_T_t
            r = - np.log(rates_actualisation[t]) / np.asarray(time_to_maturity[t])
            q = - np.log(div_actualisation[t]) / np.asarray(time_to_maturity[t])

            first_term = - 0.5 * np.asarray(div_actualisation[t]) * spot_t * norm.pdf(d_1) * np.asarray(volas[t]) / np.sqrt(time_to_maturity[t])

            second_term_call = - r * strikes * np.asarray(rates_actualisation[t]) * norm.cdf(d_2)
            second_term_put = r * strikes * np.asarray(rates_actualisation[t]) * norm.cdf(- d_2)
            second_term = np.where(put_condition, second_term_put, second_term_call)

            third_term_call = q * spot_t * np.asarray(div_actualisation[t]) * norm.cdf(d_1)
            third_term_put = - q * spot_t * np.asarray(div_actualisation[t]) * norm.cdf(- d_1)
            third_term = np.where(put_condition, third_term_put, third_term_call)

            thetas.append(list(first_term + second_term + third_term))

        return thetas

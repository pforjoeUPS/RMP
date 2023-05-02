

import numpy as np
from scipy.stats import norm

SPLIT = 7.07106781186547
N0 = 220.206867912376
N1 = 221.213596169931
N2 = 112.079291497871
N3 = 33.912866078383
N4 = 6.37396220353165
N5 = 0.700383064443688
N6 = 3.52624965998911e-02
M0 = 440.413735824752
M1 = 793.826512519948
M2 = 637.333633378831
M3 = 296.564248779674
M4 = 86.7807322029461
M5 = 16.064177579207
M6 = 1.75566716318264
M7 = 8.83883476483184e-02


def norm_cdf(x):
    # Source : http://stackoverflow.com/questions/2328258/cumulative-normal-distribution-function-in-c-c
    z = x if x >= 0 else -x
    c = 0
    if z <= 37:
        e = np.exp(-z ** 2 / 2.0)
        if z < SPLIT:
            n = (((((N6 * z + N5) * z + N4) * z + N3) * z + N2) * z + N1) * z + N0
            d = ((((((M7 * z + M6) * z + M5) * z + M4) * z + M3) * z + M2) * z + M1) * z + M0
            c = e * n / d
        else:
            f = z + 1.0 / (z + 2.0 / (z + 3.0 / (z + 4.0 / (z + 13.0 / 20.0))))
            c = e / (np.sqrt(2 * np.pi) * f)
    return c if x <= 0 else 1 - c


def get_d1_d2(spot, strike, maturity, sigma, risk_free, drift):
    d1 = (np.log(spot / strike) + (risk_free - drift + sigma ** 2 / 2) * maturity) / (sigma * np.sqrt(maturity))
    d2 = d1 - sigma * np.sqrt(maturity)
    return d1, d2


def bs_call_eur(spot, strike, maturity, sigma, risk_free, drift):
    if maturity <= 0:
        return spot - strike if spot > strike else 0, 0, 0, 0

    d1, d2 = get_d1_d2(spot, strike, maturity, sigma, risk_free, drift)
    delta = np.exp(-drift * maturity) * norm_cdf(d1)
    eur_call_price = spot * delta - strike * np.exp(-risk_free * maturity) * norm_cdf(d2)
    vega = spot * np.exp(-drift * maturity - d1 ** 2 / 2) * np.sqrt(maturity) / np.sqrt(2 * np.pi) / 100
    gamma = np.exp(-drift * maturity - d1 ** 2 / 2) / (spot * sigma * np.sqrt(maturity) * np.sqrt(2 * np.pi))
    return eur_call_price, delta, vega, gamma


def bs_put_eur(spot, strike, maturity, sigma, risk_free, drift):
    if maturity <= 0:
        return strike - spot if strike > spot else 0, 0, 0, 0

    d1, d2 = get_d1_d2(spot, strike, maturity, sigma, risk_free, drift)
    delta = -np.exp(-drift * maturity) * norm_cdf(-d1)
    eur_put_price = spot * delta + strike * np.exp(-risk_free * maturity) * norm_cdf(-d2)
    vega = spot * np.exp(-drift * maturity - d1 ** 2 / 2) * np.sqrt(maturity) / np.sqrt(2 * np.pi) / 100
    gamma = np.exp(-drift * maturity - d1 ** 2 / 2) / (spot * sigma * np.sqrt(maturity) * np.sqrt(2 * np.pi))
    return eur_put_price, delta, vega, gamma


def interpolate_1d(x, x_list, f_list):
    x = max(x_list[0], x)
    x = min(x, x_list[-1])
    mask = x_list <= x
    id_x1 = mask[mask].size - 1
    x1 = x_list[id_x1]
    f = f_list[id_x1]
    if x1 != x:
        id_x2 = id_x1 + 1
        x2 = x_list[id_x2]
        f += (x - x1) * (f_list[id_x2] - f_list[id_x1]) / (x2 - x1)
    return f


def get_volatility(date, maturity, strike, volatilities_3d, maturities_list, strikes_2d, dates_list):
    maturity = max(maturities_list[0], maturity)
    maturity = min(maturity, maturities_list[-1])
    mask = maturities_list <= maturity
    id_T1 = mask[mask].size - 1
    T1 = maturities_list[id_T1]
    mask = dates_list <= date
    id_last_date = mask[mask].size - 1
    volatility1 = interpolate_1d(strike, strikes_2d[id_T1], volatilities_3d[id_last_date, id_T1])
    volatility = volatility1
    if T1 != maturity:
        id_T2 = id_T1 + 1
        T2 = maturities_list[id_T2]
        volatility2 = interpolate_1d(strike, strikes_2d[id_T2], volatilities_3d[id_last_date, id_T2])
        volatility += (maturity - T1) * (volatility2 - volatility1) / (T2 - T1)
    return volatility / 100.


def get_rate_or_div(date, maturity, rates_or_div_2d, maturities_list, dates_list):
    mask = dates_list <= date
    id_last_date = mask[mask].size - 1
    rate_or_div = interpolate_1d(maturity, maturities_list, rates_or_div_2d[id_last_date])
    return rate_or_div


def get_bs_volga():
    pass


def get_bs_vanna():
    pass


def get_bs_theta(call_put, date, spot, maturity, adj_k,
                 volatilities_3d, vol_maturities_list, vol_strikes_2d, vol_dates_list,
                 rf_rates_2d, rates_maturities_list, rates_dates_list,
                 dividends_2d, div_maturities_list, div_dates_list):
    vol = get_volatility(date, maturity, adj_k, volatilities_3d, vol_maturities_list, vol_strikes_2d,
                         vol_dates_list)
    r = get_rate_or_div(date, maturity, rf_rates_2d, rates_maturities_list, rates_dates_list)
    rates_actualisation = np.exp(- r * maturity)
    q = get_rate_or_div(date, maturity, dividends_2d, div_maturities_list, div_dates_list)
    div_actualisation = np.exp(- q * maturity)

    strike = adj_k * spot
    vol_sqrt_T_t = np.asarray(vol) * np.sqrt(maturity)
    d_1 = (np.log(spot * np.asarray(div_actualisation) / (
            strike * np.asarray(rates_actualisation))) / vol_sqrt_T_t) + (0.5 * vol_sqrt_T_t)
    d_2 = d_1 - vol_sqrt_T_t

    first_term = - 0.5 * np.asarray(div_actualisation) * spot * norm.pdf(d_1) * np.asarray(vol) / np.sqrt(
        maturity)

    if call_put == 1:
        second_term = - r * strike * np.asarray(rates_actualisation) * norm.cdf(d_2)
    elif call_put == -1:
        second_term = r * strike * np.asarray(rates_actualisation) * norm.cdf(- d_2)
    else:
        raise ValueError("call_put input should be 1 for call and -1 for put")

    if call_put == 1:
        third_term = q * spot * np.asarray(div_actualisation) * norm.cdf(d_1)
    elif call_put == -1:
        third_term = - q * spot * np.asarray(div_actualisation) * norm.cdf(- d_1)
    else:
        raise ValueError("call_put input should be 1 for call and -1 for put")

    return first_term + second_term + third_term


def price_single(call_put, date, spot, maturity, adj_k,
                 volatilities_3d, vol_maturities_list, vol_strikes_2d, vol_dates_list,
                 rf_rates_2d, rates_maturities_list, rates_dates_list,
                 dividends_2d, div_maturities_list, div_dates_list):
    price, delta, vega, gamma, skew, vol = [np.nan] * 6
    if adj_k >= 0 and call_put != 0:
        vol = get_volatility(date, maturity, adj_k, volatilities_3d, vol_maturities_list, vol_strikes_2d,
                             vol_dates_list)
        # rate = get_rate_or_div(date, maturity*365./360., rf_rates_2d, rates_maturities_list, rates_dates_list)
        rate = get_rate_or_div(date, maturity, rf_rates_2d, rates_maturities_list, rates_dates_list)
        div = get_rate_or_div(date, maturity, dividends_2d, div_maturities_list, div_dates_list)
        if call_put == 1:
            price, delta, vega, gamma = bs_call_eur(spot, spot * adj_k, maturity, vol, rate, div)
        elif call_put == -1:
            price, delta, vega, gamma = bs_put_eur(spot, spot * adj_k, maturity, vol, rate, div)
        # computing the skew
        vol_up = get_volatility(date, maturity, adj_k + 10. ** (-4), volatilities_3d, vol_maturities_list,
                                vol_strikes_2d,
                                vol_dates_list)
        vol_down = get_volatility(date, maturity, adj_k - 10. ** (-4), volatilities_3d, vol_maturities_list,
                                  vol_strikes_2d, vol_dates_list)
        skew = (vol_up - vol_down) / (2 * 10. ** (-4))
    return price, delta, vega, gamma, skew, vol


def price_single_no_rate_no_div_bbg_vol(call_put, date, spot, maturity, adj_k,
                                        volatilities_3d, vol_maturities_list, vol_strikes_2d, vol_dates_list, vol):
    price, delta, vega, gamma, skew = [np.nan] * 5
    if adj_k >= 0 and call_put != 0:
        rate = 0
        div = 0
        if call_put == 1:
            price, delta, vega, gamma = bs_call_eur(spot, spot * adj_k, maturity, vol, rate, div)
        elif call_put == -1:
            price, delta, vega, gamma = bs_put_eur(spot, spot * adj_k, maturity, vol, rate, div)
        # computing the skew
        vol_up = get_volatility(date, maturity, adj_k + 10. ** (-4), volatilities_3d, vol_maturities_list,
                                vol_strikes_2d,
                                vol_dates_list)
        vol_down = get_volatility(date, maturity, adj_k - 10. ** (-4), volatilities_3d, vol_maturities_list,
                                  vol_strikes_2d, vol_dates_list)
        skew = (vol_up - vol_down) / (2 * 10. ** (-4))
    return price, delta, vega, gamma, skew, vol


def delta_diff(adj_k, delta_ref, call_put, spot, maturity, t1, t2, strikes_t1, strikes_t2, volatility_t1, volatility_t2,
               rate, div):
    delta = None
    if adj_k >= 0 and call_put != 0:
        vol = get_vol(maturity, adj_k, t1, t2, strikes_t1, strikes_t2, volatility_t1, volatility_t2)

        d1 = get_d1(spot, spot * adj_k, maturity, vol, rate, div)

        if call_put == 1:
            delta = np.exp(-div * maturity) * norm_cdf(d1)
            return delta - delta_ref
        elif call_put == -1:
            delta = -np.exp(-div * maturity) * norm_cdf(-d1)
            return delta_ref - delta
    return delta


def get_vol(maturity, strike, t1, strikes_t1, volatility_t1, t2=None, strikes_t2=None, volatility_t2=None):
    volatility1 = interpolate_1d(strike, strikes_t1, volatility_t1)
    volatility = volatility1
    if t1 != maturity and t2 is not None:
        volatility2 = interpolate_1d(strike, strikes_t2, volatility_t2)
        volatility += (maturity - t1) * (volatility2 - volatility1) / (t2 - t1)
    return volatility / 100.


def get_d1(spot, strike, maturity, sigma, risk_free, drift):
    return (np.log(spot / strike) + (risk_free - drift + sigma ** 2 / 2) * maturity) / (sigma * np.sqrt(maturity))

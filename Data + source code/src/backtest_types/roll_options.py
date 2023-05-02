import bisect
import warnings

import numpy as np
import pandas as pd
from dateutil import parser
from enum import Enum
from scipy.optimize import brentq
from copy import deepcopy

from src.backtest import Backtest
from src.calendar_util.bt_calendar import RecurringDates
from src.exceptions import BacktestException
from src.lib.options.option import Option
from src.lib.options.pricing import BlackScholesPricing

__all__ = ['RollOptions', 'OptionsGroup', 'BudgetType', 'BudgetAdjustment']


class NearestStrikeDir(Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    NEAREST = 'NEAREST'


class BudgetType(Enum):
    FIXED = 'FIXED'


class BudgetAdjustment(Enum):
    STRIKE = 'STRIKE'
    QUANTITY = 'QUANTITY'


class EntryType(Enum):
    PROGRESSIVE = 'PROGRESSIVE'
    CUSTOM = 'CUSTOM'
    ALL = 'ALL'


class LongShort(Enum):
    SHORT = 'SHORT'
    LONG = 'LONG'


class NominalType(Enum):
    FIXED = 'FIXED'
    UNDL = 'UNDL'
    INDEX = 'INDEX'


RRULE_3RD_FRIDAY = 'FREQ=MONTHLY;BYDAY=+3FR'


class OptionsGroup(object):

    def __init__(self, undl, params, calendar):
        super(OptionsGroup, self).__init__()
        self.calendar = calendar
        self.undl = undl
        self.type = params.get('Type')
        strike = params.get('Strike')
        self.strike = float(strike) if strike else None
        self.delta_strike = params.get('DeltaStrike', None)
        self.roll_dates_generator = RecurringDates(params['Roll']) if 'Roll' in params else None
        self.maturities_generator = RecurringDates(params['Maturity']) if 'Maturity' in params else None
        self.exit_dates_generator = RecurringDates(params['Unwind']) if 'Unwind' in params else None
        self.maturity = params.get('NextMaturity', 1) - 1
        self.unwind = params.get('NextUnwind', self.maturity + 1) - 1
        if 'EntryDate' in params:
            self.entry_date = pd.Timestamp(parser.parse(params.get('EntryDate')))
        else:
            self.entry_date = None
        self.entry_type = EntryType(params.get('EntryType'))
        self.nominal_type = NominalType(params.get('NominalType', NominalType.FIXED))
        self.long_short = LongShort(params.get('LongShort'))
        self.sign = 1 if self.long_short == LongShort.LONG else -1
        self.count = params.get('NbOptions', self.maturity + 1)
        self.options_to_keep = params.get('OptionsToKeep', None)
        self.count_fixed = params.get('NbOptionsFixed', False)
        self.budget_type = BudgetType(params.get('BudgetType')) if params.get('BudgetType') is not None else None
        self.budget_adjustment = BudgetAdjustment(params.get('BudgetAdjustment')) \
            if params.get('BudgetAdjustment') is not None else None
        self.budget = params.get('Budget', None)
        self.reference_group_id = params.get('ReferenceGroupIndex', None)
        if not (self.budget_type is None and self.budget_adjustment is None and self.budget is None) and \
                not (self.budget_type is not None and self.budget_adjustment is not None and self.budget is not None):
            raise BacktestException('All of BudgetType and BudgetAdjustment and Budget should be (or not) specified')
        self.solving_pricer = None
        self.delta_hedged = params.get('DeltaHedged', False)
        self.delta_lag = params.get('DeltaLag', False)
        self.vega_fees_factor = params.get('VegaFees', params.get('VegaFeesFactor', None))
        self.vega_entry_fees_factor = params.get('VegaEntryFees', None)
        self.vega_exit_fees_factor = params.get('VegaExitFees', None)
        self.vega_fees_floor = params.get('VegaFeesFloor', 0)
        self.vega_fees_cap = params.get('VegaFeesCap', np.inf)
        self.vega_fees_iv_min = params.get('VegaFeesIVMin', 0)
        self.limit_fees_by_vega_percent = params.get('LimitFeesByPercentOfVega', False)
        if self.vega_fees_factor is not None and (self.vega_entry_fees_factor is not None
                                                  or self.vega_exit_fees_factor is not None):
            raise BacktestException('Only VegaFees or (VegaEntryFees and VegaExitFees) Fees factor must be provided')
        elif self.vega_fees_factor is not None:
            self.vega_entry_fees_factor = self.vega_fees_factor
            self.vega_exit_fees_factor = self.vega_fees_factor
        elif (self.vega_entry_fees_factor is None and self.vega_exit_fees_factor is not None) or (
                self.vega_entry_fees_factor is not None and self.vega_exit_fees_factor is None):
            raise BacktestException('Both Entry and Exit Fees factor must be either provided or not if VegaFees is not')
        self.mvop_includes_fees = params.get('MVOPIncludesFees', False)
        self.optionsSizing = params.get('OptionsSizing', -1)
        self.maturity_min = params.get('MaturityMin', 0)
        self.leverage = params.get('Leverage', 1)
        if isinstance(self.leverage, str):
            self.leverage = 1
            self.extra_leverage = params.get('Leverage', 1)
        self.strike_shift = params.get('StrikeShift', 0)
        self.notional_shift = params.get('NotionalShift', 0)

        self.moving_average = params.get('MovingAverage', dict())
        self.moving_average_w_short = 0
        self.moving_average_w_long = 0
        if len(self.moving_average):
            if self.moving_average['WindowLong'] <= self.moving_average['WindowShort']:
                raise BacktestException('Moving Average WindowLong should be strictly higher than WindowShort')
            self.moving_average_w_short = self.moving_average['WindowShort']
            self.moving_average_w_long = self.moving_average['WindowLong']

        self.spot_moving_average_short = []
        self.spot_moving_average_long = []

        self.series_dates = None
        self.roll_dates = None
        self.maturity_dates = None
        self.exit_dates = None
        self.next_maturity = None
        self.next_exit_date = None

        self.spots = None
        self.roll_spots = None
        self.shifted_roll_spots = None
        self.maturity_spots = None
        self.nominal_spots = None
        self.settle_spots = None
        self.vega_fees_iv = None
        self.maturity_settle = None

        self.in_out_indices = None
        self.all_positions = None
        self.strike_dates = None
        self.strike_spots = None
        self.maturing = None

        self.prices = None
        self.quantity = []
        self.maturing_quantity = None
        self.deltas = None
        self.fwd_deltas = []
        self.fwd_hedge = params.get('Fwd_hedge', False)
        self.vegas = None
        self.volas = None
        self.gammas = None
        self.payoffs = None
        self.payoffs_deltas = None
        self.payoffs_vegas = None

        self.notional = None
        self.delta = None
        self.vega = None
        self.vola = None
        self.gamma = None
        self.volgas = None
        self.vannas = None
        self.thetas = None
        self.skew = None
        self.mvop = None
        self.ccl_diff = None
        self.vega_fees = None
        self.delta_skew_adjust = params.get('DeltaSkewAdjust', False)
        self.delta_skew_factor = params.get('DeltaSkewFactor', 1.0)

        self.rate_actualisation = None
        self.div_actualisation = None

        self.rate_actualisation_till_t = []
        self.div_actualisation_till_t = []

        self.time_to_maturity = None

        self.step = params.get('Step', None)
        self.pseudo_listed_strike_method = params.get('ListedStkMethod', 'ceil')

        self.reference_group = None

        self.dollar_gamma_star = []
        self.volas_0 = []
        self.time_since_entry = []
        self.dollar_gamma_star_sum = []
        self.ret_sq_sum = []
        self.dollar_gamma_star_ret_sq_sum = []

        self.vol_premium_component = []
        self.gamma_covariance_effect = []
        self.vega_term = []
        self.d_gamma_term = []
        self.residual_drift_term = []

        self.delta_pnl = []
        self.theta_pnl = []
        self.gamma_pnl = []
        self.vega_pnl = []
        self.volga_pnl = []
        self.vanna_pnl = []
        self.pnl_to_dP = []

        self.weighting_scheme = params.get('WeightScheme')

    @staticmethod
    def schema():

        return {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'Type': {'type': 'string', 'enum': ['CALL', 'PUT']},
                    'Roll': RecurringDates.schema(),
                    'Maturity': RecurringDates.schema(),
                    'NextMaturity': {'type': 'number'},
                    'Unwind': RecurringDates.schema(),
                    'Strike': {'type': 'number'},
                    'DeltaStrike': {'type': 'number'},
                    'BudgetType': {'type': 'string', 'enum': list(BudgetType.__members__.keys())},
                    'BudgetAdjustment': {'type': 'string', 'enum': list(BudgetAdjustment.__members__.keys())},
                    'Budget': {'type': 'number'},
                    'ReferenceGroupIndex': {'type': 'number'},
                    'Step': {'type': 'number'},
                    'EntryDate': {
                        'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                    },
                    'EntryType': {'type': 'string', 'enum': list(EntryType.__members__.keys())},
                    'NbOptions': {'type': 'number'},
                    'OptionsToKeep': {'type': 'number'},
                    'NbOptionsFixed': {'type': 'number'},
                    'NominalType': {'type': 'string', 'enum': list(NominalType.__members__.keys())},
                    'LongShort': {'type': 'string', 'enum': list(LongShort.__members__.keys())},
                    'DeltaHedged': {'type': 'boolean'},
                    'DeltaLag': {'type': 'boolean'},
                    'VegaFees': {'type': 'number'},
                    'VegaFeesFloor': {'type': 'number'},
                    'VegaFeesIVMin': {'type': 'number'},
                    'VegaFeesCap': {'type': 'number'},
                    'LimitFeesByPercentOfVega': {'type': 'boolean'},
                    'MVOPIncludesFees': {'type': 'boolean'},
                    'MaturityMin': {'type': 'number'},
                    'Leverage': {
                        'anyOf': [{'type': 'number'}, {'type': 'string'}]
                    },
                    'MovingAverage': {
                        'type': 'object',
                        'properties': {
                            'OverBelow': {'type': 'boolean'},
                            'WindowShort': {'type': 'number'},
                            'WindowLong': {'type': 'number'},
                            'Factor': {'type': 'number'},
                            'Operator': {'type': 'string', 'enum': ['Average', 'Maximum']}
                        },
                        'required': ['OverBelow', 'WindowShort', 'WindowLong', 'Factor']
                    },
                    'DeltaSkewAdjust': {'type': 'boolean'},
                    'DeltaSkewFactor': {'type': 'number'},
                },
                'oneOf': [{'required': ['Type', 'Strike', 'EntryType', 'LongShort']},
                          {'required': ['Type', 'DeltaStrike', 'EntryType', 'LongShort']}]
            }
        }

    def get_options(self, strike_date_idx, maturity_idx):
        unwind_lag = self.unwind - self.maturity + maturity_idx
        if unwind_lag < 0:
            return []
        exit_date_idx = self.next_exit_date[strike_date_idx] + unwind_lag
        maturity_idx = self.next_maturity[strike_date_idx] + maturity_idx

        if maturity_idx >= len(self.maturity_dates) or exit_date_idx >= len(self.exit_dates):
            return []

        maturity_date = self.maturity_dates[maturity_idx]
        exit_date = min(maturity_date, self.exit_dates[exit_date_idx])

        if self.delta_strike is None:
            if self.budget_type == BudgetType.FIXED and self.budget_adjustment == BudgetAdjustment.STRIKE:
                if self.solving_pricer is None:
                    self.solving_pricer = BlackScholesPricing(self.undl, pd.Series(self.spots, self.series_dates))
                strike_temp = self.strike * self.shifted_roll_spots[strike_date_idx] / self.roll_spots[strike_date_idx]
                option_temp = Option(self.type, self.roll_spots[strike_date_idx], strike_temp,
                                     maturity_date, exit_date, self.maturity_settle[maturity_idx],
                                     self.undl, step=self.step, strike_date=self.roll_dates[strike_date_idx])
                strike = self.get_strike_from_budget(self.solving_pricer, option_temp,
                                                     self.maturity_settle[maturity_idx])
                if strike is None:
                    return []
            else:
                strike = self.strike * self.shifted_roll_spots[strike_date_idx] / self.roll_spots[strike_date_idx]
            option = Option(self.type, self.roll_spots[strike_date_idx], strike,
                            maturity_date, exit_date, self.maturity_settle[maturity_idx],
                            self.undl, step=self.step, strike_date=self.roll_dates[strike_date_idx],
                            pseudo_strike_method=self.pseudo_listed_strike_method)
        else:
            if self.solving_pricer is None:
                self.solving_pricer = BlackScholesPricing(self.undl, pd.Series(self.spots, self.series_dates))
            pricing_date = self.roll_dates[strike_date_idx]
            if self.strike_shift:
                pricing_date = self.series_dates[self.series_dates.searchsorted(pricing_date) - self.strike_shift]
            strike = self.solving_pricer.get_strike_from_delta(self.delta_strike, pricing_date,
                                                               self.type, maturity_date)
            option = Option(self.type, self.roll_spots[strike_date_idx], strike,
                            maturity_date, exit_date, self.maturity_settle[maturity_idx],
                            self.undl, step=self.step, strike_date=self.roll_dates[strike_date_idx],
                            pseudo_strike_method=self.pseudo_listed_strike_method)

        if len(self.moving_average) == 0:
            option.set_additional_property('trigger', 1)
            return [option]
        else:
            if self.spot_moving_average_short[strike_date_idx + self.calendar.hist_window] >= \
                    self.spot_moving_average_long[strike_date_idx + self.calendar.hist_window] * \
                    self.moving_average['Factor'] \
                    and self.moving_average['OverBelow']:
                option.set_additional_property('trigger', 1)
            elif self.spot_moving_average_short[strike_date_idx + self.calendar.hist_window] <= \
                    self.spot_moving_average_long[strike_date_idx + self.calendar.hist_window] * \
                    self.moving_average['Factor'] \
                    and not (self.moving_average['OverBelow']):
                option.set_additional_property('trigger', 1)
            else:
                option.set_additional_property('trigger', 0)
        return [option]

    def vf_method(self, factor, vg, t):
        iv = 0 if self.vega_fees_iv is None else self.vega_fees_iv[t] / 100.0
        vega_fees_factor = factor + max(0, iv - self.vega_fees_iv_min) if factor != 0 else 0.
        if self.limit_fees_by_vega_percent:
            return min(self.vega_fees_cap, max(vega_fees_factor, self.vega_fees_floor)) * vg
        return min(self.vega_fees_cap, max(vega_fees_factor * vg, self.vega_fees_floor))

    def get_vega_entry_fees(self, vega, dt):
        if self.vega_entry_fees_factor is not None:
            vega_entry_fees = self.vf_method(factor=self.vega_entry_fees_factor, vg=vega,
                                             t=self.series_dates.searchsorted(dt))
            return vega_entry_fees
        else:
            return 0.

    def get_strike_from_budget(self, pricer, option, spot_at_maturity):
        strike_max = 1.5
        strike_min = 0.00001
        solved_strike = None

        def to_optimize(strike):
            option_temp = Option(option.type, option.spot, strike,
                                 option.maturity, option.exit_date, spot_at_maturity,
                                 option.undl, step=option.step, strike_date=option.strike_date)

            vega = pricer.price([option.strike_date], [[option_temp]])[2][0][0]
            vega_fees = self.get_vega_entry_fees(vega, option.strike_date) / option.spot

            return pricer.price([option.strike_date], [[option_temp]])[0][0][0] / option.spot + vega_fees - self.budget

        try:
            solved_strike = brentq(to_optimize, strike_max, strike_min)
        except Exception as error:
            warnings.warn('Unable to solve at :' + option.strike_date.strftime("%d-%m-%Y") + '-- Error : '
                          + error.__str__(), stacklevel=2)
        finally:
            return solved_strike

    def generate_calendar(self, calendar):
        self.series_dates = calendar.series_dates

        self.generate_roll_dates(calendar)

        if self.entry_date is None:
            self.entry_date = self.roll_dates[0]

        try:
            self.entry_date = self.calendar.t0
        except IndexError:
            raise BacktestException('Could not find a computation date newer than Entry Date')

        self.roll_dates = self.roll_dates[self.roll_dates >= self.entry_date]

        if self.entry_date not in self.roll_dates:
            self.roll_dates = self.roll_dates.append(pd.DatetimeIndex([self.entry_date])).sort_values()

        self.generate_maturity_dates(calendar)

        self.generate_exit_dates(calendar)

        self.next_maturity = self.maturity_dates.searchsorted(self.roll_dates)
        invalid_maturities_min_idx = self.next_maturity.searchsorted(len(self.maturity_dates))
        valid_next_maturity = self.next_maturity[:invalid_maturities_min_idx]
        invalid_next_maturity = self.next_maturity[invalid_maturities_min_idx:]
        mask = self.maturity_dates[valid_next_maturity] == \
               self.roll_dates[:invalid_maturities_min_idx]
        self.next_maturity = np.concatenate([np.where(mask, valid_next_maturity + 1, valid_next_maturity),
                                             invalid_next_maturity])
        if self.exit_dates is not None:
            self.next_exit_date = self.exit_dates.searchsorted(self.roll_dates)
            invalid_exit_dates_min_idx = self.next_exit_date.searchsorted(len(self.exit_dates))
            valid_next_exit_date = self.next_exit_date[:invalid_exit_dates_min_idx]
            invalid_next_exit_date = self.next_exit_date[invalid_exit_dates_min_idx:]
            mask = self.exit_dates[valid_next_exit_date] == \
                   self.roll_dates[:invalid_exit_dates_min_idx]
            self.next_exit_date = np.concatenate([np.where(mask, valid_next_exit_date + 1, valid_next_exit_date),
                                                  invalid_next_exit_date])

        self.init_results()

    def generate_roll_dates(self, calendar):
        if self.roll_dates_generator is None:
            raise BacktestException('Roll dates not defined')
        self.roll_dates = self.roll_dates_generator.run(calendar.open_dates)

    def generate_maturity_dates(self, calendar):
        if self.maturities_generator is None:
            self.maturity_dates = self.roll_dates
        else:
            self.maturity_dates = self.maturities_generator.run(calendar.open_dates)

    def generate_exit_dates(self, calendar):
        if self.exit_dates_generator is None:
            self.exit_dates = self.maturity_dates
        else:
            self.exit_dates = self.exit_dates_generator.run(calendar.open_dates)

    def init_moving_average_spots(self):
        if 'Operator' in self.moving_average and self.moving_average['Operator'] == 'Maximum':
            def mv_operator(ls):
                return np.max(ls)
        else:
            def mv_operator(ls):
                return np.mean(ls)

        def get_spot_moving_average(_t, window):
            try:
                return mv_operator([self.spots[i] for i in range(max(0, _t - window), _t)])
            except ValueError:
                return np.nan

        if not (self.moving_average == {}):
            for t in range(len(self.series_dates)):
                self.spot_moving_average_short.append(get_spot_moving_average(t, self.moving_average_w_short))
                self.spot_moving_average_long.append(get_spot_moving_average(t, self.moving_average_w_long))

    def load_all_days_candidate_options_data(self, **kwargs):
        """
        To implement if needed
        """
        pass

    def generate_universe(self, spots, nominal_spots=None, settle_spots=None, vega_fees_iv=None):
        self.spots = spots.values
        if nominal_spots is None:
            self.nominal_spots = self.spots
        else:
            self.nominal_spots = nominal_spots.values

        if settle_spots is None:
            self.settle_spots = spots
        else:
            self.settle_spots = settle_spots

        if vega_fees_iv is None:
            self.vega_fees_iv = None
        else:
            self.vega_fees_iv = vega_fees_iv.values

        self.roll_spots = spots.reindex(index=self.roll_dates)
        self.shifted_roll_spots = spots.shift(self.strike_shift).reindex(index=self.roll_dates)
        self.maturity_spots = spots.reindex(index=self.maturity_dates)
        self.maturity_settle = self.settle_spots.reindex(index=self.maturity_dates)

        self.init_moving_average_spots()

        is_roll_date = self.series_dates.isin(self.roll_dates)

        entry_date_idx = self.series_dates.searchsorted(self.entry_date)

        positions = [[]] * entry_date_idx
        positions_strike_dates = [[]] * entry_date_idx
        positions_strike_spots = [[]] * entry_date_idx
        in_out_indices = [(0, -1)] * entry_date_idx
        position_exit_dates = []  # Reversed to be able to use bisect.bisect_right
        maturing = [[]] * entry_date_idx

        entry_date_roll_idx = self.roll_dates.searchsorted(self.entry_date)

        # Load all candidate options data if implemented
        self.load_all_days_candidate_options_data()

        # Entry date is handled separately to support Entry Modes
        if entry_date_idx < len(self.series_dates):
            position = []
            if self.entry_type == EntryType.PROGRESSIVE:
                position += self.get_options(entry_date_roll_idx, self.maturity)
            elif self.entry_type == EntryType.CUSTOM:
                for i in range(len(self.optionsSizing)):
                    position.extend(self.get_options(entry_date_roll_idx, i) * self.optionsSizing[i])
            else:
                for i in range(self.unwind, -1, -1):
                    position += self.get_options(entry_date_roll_idx, self.maturity - i)

            position = list(reversed(position))
            position = list(filter(lambda x: x is not None, position))
            position_strike_dates = [entry_date_idx] * len(position)
            position_strike_spot = [self.spots[entry_date_idx - self.notional_shift]] * len(position)
            position_exit_dates = [option.exit_date for option in reversed(position)]

            positions.append(position)
            positions_strike_dates.append(position_strike_dates)
            positions_strike_spots.append(position_strike_spot)
            in_out_indices.append((len(position),) * 2)
            maturing.append([])

        roll_date_idx = entry_date_roll_idx
        for t in range(entry_date_idx + 1, len(self.series_dates)):
            new_entries = 0
            position = positions[t - 1]
            position_strike_dates = positions_strike_dates[t - 1]
            position_strike_spots = positions_strike_spots[t - 1]

            if is_roll_date[t]:
                roll_date_idx += 1

                to_keep = len(position) - bisect.bisect_right(position_exit_dates, self.series_dates[t])
                if self.options_to_keep is not None and to_keep >= self.options_to_keep:
                    new_options = []
                else:
                    new_options = self.get_options(roll_date_idx, self.maturity)

                if len(new_options) > 0:
                    position = new_options + position
                    position_strike_dates = [t] * len(new_options) + position_strike_dates
                    position_strike_spots = [self.spots[t - self.notional_shift]] * len(new_options) \
                                            + position_strike_spots
                    for new_option in new_options:
                        position_exit_dates.append(new_option.exit_date)
                    new_entries = len(new_options)

            to_keep = len(position) - bisect.bisect_right(position_exit_dates, self.series_dates[t])
            if self.count_fixed:
                to_keep = min(to_keep, self.count_fixed)
            to_remove = len(position) - to_keep
            position = position[:to_keep]
            position_strike_dates = position_strike_dates[:to_keep]
            position_strike_spots = position_strike_spots[:to_keep]
            if to_keep == 0:
                position_exit_dates = []
            else:
                position_exit_dates = position_exit_dates[-to_keep:]

            positions.append(position)
            positions_strike_dates.append(position_strike_dates)
            positions_strike_spots.append(position_strike_spots)
            to_keep2 = len(positions[t - 1]) - to_remove
            in_out_indices.append((new_entries, to_keep2))
            maturing.append(positions[t - 1][to_keep2:])

        self.in_out_indices = in_out_indices
        self.all_positions = positions
        self.strike_dates = positions_strike_dates
        self.strike_spots = positions_strike_spots
        self.maturing = maturing

    def init_results(self):
        self.notional = [[] for _ in range(len(self.series_dates))]
        self.delta = [0] * len(self.series_dates)
        self.vega = [0] * len(self.series_dates)
        self.vola = [0] * len(self.series_dates)
        self.gamma = [0] * len(self.series_dates)
        self.skew = [0] * len(self.series_dates)
        self.mvop = [0] * len(self.series_dates)
        self.ccl_diff = [0] * len(self.series_dates)
        self.vega_fees = [0] * len(self.series_dates)
        self.quantity = [[] for _ in range(len(self.series_dates))]
        self.maturing_quantity = [[] for _ in range(len(self.series_dates))]

    def compute_notional(self, t, t_rebal, shifted_il, notional_base=1000.0, extra_lev=1):
        new_entry_count, maturing_idx = self.in_out_indices[t]
        if self.weighting_scheme == "InverseDollarGamma":
            qty_t = self.leverage * extra_lev / (np.asarray(self.gammas[t][:new_entry_count]) * np.square(
                self.strike_spots[t][:new_entry_count])) / self.count
            self.quantity[t] = list(qty_t) + self.quantity[t - 1][:maturing_idx] if t > 0 else list(qty_t)
            self.notional[t] = list(np.asarray(self.quantity[t]) * np.asarray(self.strike_spots[t]))
            # return lev
        elif self.weighting_scheme == "InverseDollarGamma_times_vol_impli_sq":
            qty_t = self.leverage * extra_lev / (np.asarray(self.gammas[t][:new_entry_count]) * np.square(
                self.strike_spots[t][:new_entry_count]) * np.square(self.volas_0[t][:new_entry_count])) / self.count

            self.quantity[t] = list(qty_t) + self.quantity[t-1][:maturing_idx] if t > 0 else list(qty_t)
            self.notional[t] = list(np.asarray(self.quantity[t]) * np.asarray(self.strike_spots[t]))
        elif self.weighting_scheme == "PortfolioDollarGammaHedge":
            self.notional[t] = list(np.asarray(self.quantity[t]) * np.asarray(self.strike_spots[t]))
        else:
            if self.nominal_type == NominalType.FIXED:
                self.notional[t] = [notional_base * self.leverage / self.count
                                    * self.all_positions[t][i].get_additional_property('trigger')
                                    for i, d in enumerate(self.strike_dates[t])]
            elif self.nominal_type == NominalType.UNDL:
                self.notional[t] = [notional_base * self.leverage / self.count * self.nominal_spots[d - self.notional_shift]
                                    * self.all_positions[t][i].get_additional_property('trigger')
                                    / self.nominal_spots[t_rebal - self.notional_shift]
                                    for i, d in enumerate(self.strike_dates[t])]
            elif self.nominal_type == NominalType.INDEX:
                self.notional[t] = [notional_base * self.leverage / self.count * shifted_il[d]
                                    * self.all_positions[t][i].get_additional_property('trigger') / shifted_il[t_rebal]
                                    for i, d in enumerate(self.strike_dates[t])]

            if self.budget_type == BudgetType.FIXED and self.budget_adjustment == BudgetAdjustment.QUANTITY:
                for i, d in enumerate(self.strike_dates[t]):
                    self.notional[t][i] *= (self.budget /
                                            ((self.all_positions[d][0].get_additional_property('price_at_strike_date') +
                                              self.get_vega_entry_fees(
                                                  self.all_positions[d][0].get_additional_property('vega_at_strike_date'),
                                                  self.all_positions[d][0].strike_date))
                                             / self.spots[d]))

            self.quantity[t] = [notional / strike_spot
                                for notional, strike_spot in zip(self.notional[t], self.strike_spots[t])]
        if t > self.calendar.t0_index:
            _, maturing_idx = self.in_out_indices[t]
            self.maturing_quantity[t] = [notional / strike_spot for notional, strike_spot in
                                         zip(self.notional[t - 1][maturing_idx:],
                                             self.strike_spots[t - 1][maturing_idx:])]

    def compute_mvop(self, t):
        self.mvop[t] = sum(self.sign * qt * price
                           for qt, price in zip(self.quantity[t], self.prices[t]))
        if self.mvop_includes_fees:
            new_entry_count, _ = self.in_out_indices[t]
            self.mvop[t] += sum(
                self.get_vega_entry_fees(vega, self.series_dates[t]) * qty
                for qty, vega in zip(self.quantity[t][:new_entry_count], self.vegas[t][:new_entry_count])
            )

    def compute_delta(self, t):
        if self.fwd_hedge:
            self.delta[t] = sum(self.sign * qt * option_delta
                                for qt, option_delta in zip(self.quantity[t], self.fwd_deltas[t]))
        else:
            self.delta[t] = sum(self.sign * qt * option_delta
                                for qt, option_delta in zip(self.quantity[t], self.deltas[t]))

    def compute_vega(self, t):
        self.vega[t] = sum(self.sign * qt * option_vega
                           for qt, option_vega in zip(self.quantity[t], self.vegas[t]))

    def compute_gamma(self, t):
        self.gamma[t] = sum(self.sign * qt * option_gamma
                            for qt, option_gamma in zip(self.quantity[t], self.gammas[t]))

    def compute_skew(self, t, skews):
        if self.delta_skew_adjust and skews:
            self.skew[t] = self.delta_skew_factor * sum(self.sign * qt * option_vega *
                                                        (skews[option.maturity]
                                                         if (skews and option.maturity in skews) else 0)
                                                        for qt, option, option_vega
                                                        in zip(self.quantity[t], self.all_positions[t], self.vegas[t]))

    def compute_ccl_diff(self, t):
        if t < self.calendar.t0_index:
            return

        new_entry_count, maturing_idx = self.in_out_indices[t]

        self.ccl_diff[t] = -sum(self.sign * qty * price for qty, price
                                in zip(self.quantity[t][:new_entry_count], self.prices[t][:new_entry_count]))

        if t == self.calendar.t0_index:
            return

        self.ccl_diff[t] += sum(self.sign * (old_qty - qty) * price
                                for old_qty, qty, price
                                in zip(self.quantity[t - 1][:maturing_idx],
                                       self.quantity[t][new_entry_count:],
                                       self.prices[t][new_entry_count:]))

        self.ccl_diff[t] += sum(self.sign * old_qty * price
                                for old_qty, price
                                in zip(self.quantity[t - 1][maturing_idx:], self.payoffs[t]))

    def compute_fees(self, t):
        if self.vega_fees_factor is not None or (
                self.vega_entry_fees_factor is not None and self.vega_exit_fees_factor is not None):
            new_entry_count, maturing_idx = self.in_out_indices[t]

            self.vega_fees[t] += sum(
                self.vf_method(self.vega_entry_fees_factor, vega, t=t) * qty
                for qty, vega in zip(self.quantity[t][:new_entry_count], self.vegas[t][:new_entry_count])
            )

            self.vega_fees[t] += sum(
                self.vf_method(self.vega_exit_fees_factor, vega, t=t) * np.abs(old_qty - qty) if old_qty > qty
                else self.vf_method(self.vega_entry_fees_factor, vega, t=t) * np.abs(old_qty - qty)
                for old_qty, qty, vega
                in zip(
                    self.quantity[t - 1][:maturing_idx],
                    self.quantity[t][new_entry_count:],
                    self.vegas[t][new_entry_count:]
                )
            )

            self.vega_fees[t] += sum(
                self.vf_method(self.vega_exit_fees_factor, vega, t=t) * old_qty * (
                        option.maturity != self.series_dates[t])
                for old_qty, vega, option
                in zip(
                    self.quantity[t - 1][maturing_idx:],
                    self.payoffs_vegas[t],
                    self.maturing[t]
                )
            )

            self.ccl_diff[t] -= self.vega_fees[t]

    def calculate_pnl_explanation_1(self, t):
        self.delta_pnl.append(self.get_greek_pnl(t, self.deltas, self.spots))
        self.theta_pnl.append(self.get_greek_pnl(t, self.thetas, self.time_since_entry))
        self.gamma_pnl.append(
            self.get_greek_pnl(t, self.gammas, self.spots, increment_list_2=self.spots, multiplier=0.5))
        self.vega_pnl.append(self.get_greek_pnl(t, self.vegas, self.volas, multiplier=100.))
        self.volga_pnl.append(
            self.get_greek_pnl(t, self.volgas, self.volas, increment_list_2=self.volas, multiplier=0.5))
        self.vanna_pnl.append(self.get_greek_pnl(t, self.vannas, self.spots, increment_list_2=self.volas))
        self.pnl_to_dP.append(self.get_pnl_to_dP(t))

    def get_greek_pnl(self, t, greek, increment_list_1, increment_list_2=None, multiplier=1.):
        new_entry_count, maturing_idx = self.in_out_indices[t]
        if t == 0:
            return [0.]
        else:
            if isinstance(increment_list_1[t], (np.float64, float, np.float, np.float32)):
                increment_1 = increment_list_1[t] - increment_list_1[t-1]
            else:
                increment_1 = np.asarray(increment_list_1[t][new_entry_count:]) - np.asarray(increment_list_1[t-1][:maturing_idx])

            values = multiplier * np.asarray(greek[t-1][:maturing_idx]) * increment_1 * self.sign
            if increment_list_2 is not None:
                if isinstance(increment_list_2[t], (np.float64, float, np.float, np.float32)):
                    increment_2 = increment_list_2[t] - increment_list_2[t - 1]
                else:
                    increment_2 = np.asarray(
                        increment_list_2[t][new_entry_count:]) - np.asarray(increment_list_2[t - 1][:maturing_idx])
                values *= increment_2
            return [0.] * new_entry_count + list(values)

    def get_pnl_to_dP(self, t):
        new_entry_count, maturing_idx = self.in_out_indices[t]
        if t == 0:
            return [0.]
        else:
            r_list = - np.log(self.rate_actualisation[t - 1][:maturing_idx]) / self.time_to_maturity[t - 1][:maturing_idx]
            q_list = - np.log(self.div_actualisation[t - 1][:maturing_idx]) / self.time_to_maturity[t - 1][:maturing_idx]
            delta_list = np.asarray(self.deltas[t - 1][:maturing_idx]) * self.spots[t - 1]
            dt_list = np.asarray(self.time_to_maturity[t - 1][:maturing_idx]) - np.asarray(self.time_to_maturity[t][new_entry_count:])
            values = [(r * prices - delta_times_spot * (r - q)) * dt * self.sign
                      for prices, r, q, delta_times_spot, dt in
                      zip(self.prices[t - 1][:maturing_idx], r_list, q_list, delta_list, dt_list)]
            return [0.] * new_entry_count + list(values)

    def calculate_pnl_explanation_2(self, t):
        new_entry_count, maturing_idx = self.in_out_indices[t]
        self.calculate_vol_premium_component(t, new_entry_count, maturing_idx)
        self.calculate_gamma_covariance_effect(t, new_entry_count, maturing_idx)
        self.calculate_vega_term(t)
        self.calculate_dgamma_term(t, new_entry_count, maturing_idx)
        self.calculate_residual_drift_term(t, new_entry_count, maturing_idx)

    def add_pnl_up(self, pnl_list, pnl_columns=None, cum_sum=True):
        if pnl_columns is not None:
            if len(pnl_columns) != len(pnl_list):
                pnl_columns = np.arange(len(pnl_list))
        else:
            pnl_columns = np.arange(len(pnl_list))
        final_pnl_list = []
        for pnl_obj in pnl_list:
            pnl_obj_sum = []
            for t in range(len(pnl_obj)):
                new_entry_count, maturing_idx = self.in_out_indices[t]
                if t == 0:
                    increment_t = np.float64(np.dot(pnl_obj[t][:new_entry_count], self.quantity[t][:new_entry_count]))
                else:
                    if cum_sum:
                        increment_t = np.dot(
                            (np.asarray(pnl_obj[t][new_entry_count:]) - np.asarray(pnl_obj[t - 1][:maturing_idx])),
                            self.quantity[t - 1][:maturing_idx]) + np.float64(
                            np.dot(pnl_obj[t][:new_entry_count], self.quantity[t][:new_entry_count]))
                    else:
                        increment_t = np.dot(np.asarray(pnl_obj[t][new_entry_count:]),
                                             self.quantity[t - 1][:maturing_idx]) + np.float64(
                            np.dot(pnl_obj[t][:new_entry_count], self.quantity[t][:new_entry_count]))
                pnl_obj_sum.append(increment_t)
            final_pnl_list.append(pnl_obj_sum)

        df_final_pnl = pd.DataFrame(final_pnl_list)
        if df_final_pnl.shape[1] != len(pnl_columns):
            df_final_pnl = df_final_pnl.T
        df_final_pnl.columns = pnl_columns
        df_final_pnl.index = self.series_dates
        return df_final_pnl.cumsum()

    def calculate_vol_premium_component(self, t, new_entry_count, maturing_idx):
        if t == 0:
            self.time_since_entry.append([0.] * new_entry_count)
        else:
            self.time_since_entry.append([0.] * new_entry_count + list(
                np.asarray(self.time_since_entry[t - 1][:maturing_idx]) + np.asarray(
                    self.time_to_maturity[t - 1][:maturing_idx]) - np.asarray(
                    self.time_to_maturity[t][new_entry_count:])))

        self.rate_actualisation_till_t.append(np.exp(
            np.log(self.rate_actualisation[t]) * np.asarray(self.time_since_entry[t]) / np.asarray(
                self.time_to_maturity[t])))
        self.div_actualisation_till_t.append(np.exp(
            np.log(self.div_actualisation[t]) * np.asarray(self.time_since_entry[t]) / np.asarray(
                self.time_to_maturity[t])))
        self.dollar_gamma_star.append([gamma_ * (self.spots[t] ** 2) * rates_act_ for gamma_, rates_act_ in
                                       zip(self.gammas[t], self.rate_actualisation_till_t[t])])
        if t == 0:
            self.volas_0.append(self.volas[t][:new_entry_count])
            self.dollar_gamma_star_sum.append([0.] * new_entry_count)
            self.ret_sq_sum.append([0.] * new_entry_count)
            self.dollar_gamma_star_ret_sq_sum.append([0.] * new_entry_count)
            self.vol_premium_component.append([0.] * new_entry_count)
        else:
            dt_list = np.asarray(self.time_to_maturity[t - 1][:maturing_idx]) - np.asarray(self.time_to_maturity[t][new_entry_count:])
            self.volas_0.append(self.volas[t][:new_entry_count] + self.volas_0[t - 1][:maturing_idx])
            self.dollar_gamma_star_sum.append([0.] * new_entry_count + list(
                np.asarray(self.dollar_gamma_star[t - 1][:maturing_idx]) * dt_list + np.asarray(
                    self.dollar_gamma_star_sum[t - 1][:maturing_idx])))
            ret_sq = (self.spots[t] / self.spots[t - 1] - 1) ** 2
            self.ret_sq_sum.append([0.] * new_entry_count + list(
                np.asarray([ret_sq] * maturing_idx) + np.asarray(self.ret_sq_sum[t - 1][:maturing_idx])))

            self.dollar_gamma_star_ret_sq_sum.append([0.] * new_entry_count + list(
                np.asarray(self.dollar_gamma_star[t - 1][:maturing_idx]) * ret_sq + np.asarray(
                    self.dollar_gamma_star_ret_sq_sum[t - 1][:maturing_idx])))

            self.vol_premium_component.append([0.] * new_entry_count +
                                              [0.5 * self.sign * dollar_gamma_sum * ( - (vol_0 ** 2))
                                               for time_, dollar_gamma_sum, r_sq_sum, vol_0 in
                                               zip(self.time_since_entry[t][new_entry_count:],
                                                   self.dollar_gamma_star_sum[t][new_entry_count:],
                                                   self.ret_sq_sum[t][new_entry_count:],
                                                   self.volas_0[t][new_entry_count:])])

    def calculate_gamma_covariance_effect(self, t, new_entry_count, maturing_idx):
        if t == 0:
            self.gamma_covariance_effect.append([0.] * new_entry_count)
        else:
            self.gamma_covariance_effect.append([0.] * new_entry_count +
                                                [0.5 * self.sign * dollar_gamma_ret_sq_sum
                                                 for time_, dollar_gamma_sum, r_sq_sum, dollar_gamma_ret_sq_sum in
                                                 zip(self.time_since_entry[t][new_entry_count:],
                                                     self.dollar_gamma_star_sum[t][new_entry_count:],
                                                     self.ret_sq_sum[t][new_entry_count:],
                                                     self.dollar_gamma_star_ret_sq_sum[t][new_entry_count:])])

    def calculate_vega_term(self, t):
        self.vega_term.append(
            [rates_act * self.sign * vega * 100 * ((vol ** 2) - (vol_0 ** 2)) / (2 * vol) for
             vega, vol, vol_0, rates_act in
             zip(self.vegas[t], self.volas[t], self.volas_0[t], self.rate_actualisation_till_t[t])])

    def calculate_dgamma_term(self, t, new_entry_count, maturing_idx):
        if t > 0:
            increment_list = [0.5 * self.sign * time_to_matu * ((vol ** 2) - (vol_0 ** 2)) * (gamma_t - gamma_t_1) for
                              time_to_matu, vol, vol_0, gamma_t, gamma_t_1 in
                              zip(self.time_to_maturity[t - 1][:maturing_idx], self.volas[t - 1][:maturing_idx],
                                  self.volas_0[t - 1][:maturing_idx], self.dollar_gamma_star[t][new_entry_count:],
                                  self.dollar_gamma_star[t - 1][:maturing_idx])]
            d_gamma_t_old_options = [d_gamma - increment for d_gamma, increment in
                                     zip(self.d_gamma_term[t - 1][:maturing_idx], increment_list)]
            self.d_gamma_term.append([0.] * new_entry_count + d_gamma_t_old_options)
        else:
            self.d_gamma_term.append([0.] * len(self.all_positions[t]))

    def calculate_residual_drift_term(self, t, new_entry_count, maturing_idx):
        if t > 0:
            increment_list = [0.5 * self.sign * rate_act_till_t * ((vega * 100) / vol_t_1 - volga) * ((vol_t - vol_t_1) ** 2)
                              for rate_act_till_t, vol_t, vol_t_1, vega, volga in
                              zip(self.rate_actualisation_till_t[t - 1][:maturing_idx], self.volas[t][new_entry_count:],
                                  self.volas[t - 1][:maturing_idx], self.vegas[t-1][:maturing_idx],
                                  self.volgas[t - 1][:maturing_idx])]
            residual_drift_t_old_options = [residual_drift + increment for residual_drift, increment in
                                            zip(self.residual_drift_term[t - 1][:maturing_idx], increment_list)]
            self.residual_drift_term.append([0.] * new_entry_count + residual_drift_t_old_options)
        else:
            self.residual_drift_term.append([0.] * len(self.all_positions[t]))

    def price_options(self, pricer, alternative_pricer=None):
        self.prices, self.deltas, self.vegas, self.volas, self.gammas = pricer.price(self.series_dates,
                                                                                     self.all_positions)

        self.payoffs, self.payoffs_deltas, self.payoffs_vegas, _tmp1, __tmp2 = pricer.price(self.series_dates,
                                                                                            self.maturing)

        self.volgas = pricer.get_volga(self.series_dates, self.all_positions, self.volas)
        self.vannas = pricer.get_vanna(self.series_dates, self.all_positions, self.volas)
        self.thetas = pricer.get_theta(self.series_dates, self.all_positions, self.volas)

        if self.rate_actualisation is None:
            self.rate_actualisation = pricer.get_rates_actualisation(self.series_dates, self.all_positions)
        if self.div_actualisation is None:
            self.div_actualisation = pricer.get_div_actualisation(self.series_dates, self.all_positions)
        if self.time_to_maturity is None:
            self.time_to_maturity = pricer.get_time_to_maturity(self.series_dates, self.all_positions)

        time_to_matu_0 = []
        for t, time_to_matu in enumerate(self.time_to_maturity):
            new_entry_count, maturing_idx = self.in_out_indices[t]
            if t == 0:
                time_to_matu_0.append(time_to_matu[:new_entry_count])
            else:
                time_to_matu_0.append(time_to_matu[:new_entry_count] + time_to_matu_0[t - 1][:maturing_idx])
            self.fwd_deltas.append(list(np.exp(
                (np.asarray(time_to_matu_0[t]) / time_to_matu) * np.log(self.rate_actualisation[t])) * np.asarray(
                self.deltas[t]) / np.asarray(self.div_actualisation[t])))

    def set_budget_adjustement_props(self):
        if self.budget_adjustment == BudgetAdjustment.QUANTITY:
            for t, dt in enumerate(self.series_dates):
                if dt in self.roll_dates:
                    for i, pos in enumerate(self.all_positions[t]):
                        if pos.strike_date == dt:
                            self.all_positions[t][i].set_additional_property('price_at_strike_date',
                                                                             self.prices[t][i])
                            self.all_positions[t][i].set_additional_property('vega_at_strike_date',
                                                                             self.vegas[t][i])


class RollOptions(Backtest):

    def __init__(self):
        super(RollOptions, self).__init__(True, 1, np.inf)

        self.pricing = 'BlackScholes'
        self.source = 'OM'
        self.rate_ticker = None
        self.groups = []
        self.rate = None
        self.act = None
        self.cf = None
        self.mvop = None
        self.oppl = None
        self.er = None
        self.af = None
        self.mvhp = None
        self.hppl = None
        self.delta = None
        self.vega = None
        self.gamma = None
        self.ccl = None
        self.aggregated_vega_fees = None
        self.index_fees = 0.0
        self.is_excess_return = False

        self.calendar_config = None

        self.spots = None
        self.hedge_spots = None

        self.delta_hedged = False
        self.delta_skew_adjustment = None
        self.hedged_delta = None
        self.quantity_to_hedge = None
        self.delta_hedge_tc = None
        self.delta_hedge_rc = None

        self.black_scholes_pricer = None

    @property
    def alternative_pricer(self):
        if self.black_scholes_pricer is None:
            self.black_scholes_pricer = BlackScholesPricing(self.undl().name(), self.undl_il())
        return self.black_scholes_pricer

    @staticmethod
    def params_schema():
        return {
            'Groups': OptionsGroup.schema(),
            'Rate': {'type': 'string'},
            'Source': {'type': 'string', 'enum': ['BBG', 'OM']},
            'Pricing': {'type': 'string', 'enum': ['Interpolation', 'BlackScholes', 'ObjWS']},
            'IndexLaunchValue': {'type': 'number'},
            'IndexFees': {'type': 'number'},
            'DeltaHedgeTC': {'type': 'number'},
            'DeltaHedgeRC': {'type': 'number'},
            'ExcessReturn': {'type': 'boolean'}
        }

    def run(self, conf):
        super(RollOptions, self).run(conf)

        self.calendar_config = conf['Calendar']

        self.load_data()
        self.compute_calendar()
        self.compute_capitalization_factor()
        self.price_options()
        self.compute_il()

    def create_options_group(self, params):
        return OptionsGroup(self.undl().name(), params, self.calendar)

    def load_params(self):
        super(RollOptions, self).load_params()

        self.pricing = self.param('Pricing', self.pricing)
        self.source = self.param('Source', self.source)
        hist_window = self.calendar.hist_window
        for group in self.param('Groups'):
            created_gp = self.create_options_group(group)
            if created_gp.reference_group_id is not None:
                created_gp.reference_group = self.groups[created_gp.reference_group_id]
            self.groups.append(created_gp)
            hist_window = max(hist_window, created_gp.strike_shift, created_gp.notional_shift,
                              created_gp.moving_average_w_short, created_gp.moving_average_w_long)
            if created_gp.delta_hedged:
                self.delta_hedged = True

        self.calendar.hist_window = hist_window
        self.rate_ticker = self.param('Rate')
        self.index_fees = self.param('IndexFees', self.index_fees)
        self.is_excess_return = self.param('ExcessReturn', self.is_excess_return)
        self.delta_hedge_tc = self.param('DeltaHedgeTC', 0)
        self.delta_hedge_rc = self.param('DeltaHedgeRC', 0)

    def load_data(self):
        if self.rate_ticker is not None:
            self.rate = self.load_close_price_from_db(self.rate_ticker)
            self.rate = self.rate.fillna(method='ffill')

    def compute_calendar(self):
        super(RollOptions, self).compute_calendar()

        self.act = self.calendar.get_act()

        if self.rate_ticker is not None:
            self.calendar.compare_to_series({self.rate_ticker: self.rate}, raise_exception=False)

    def reindex_data(self):
        super(RollOptions, self).reindex_data()

        if self.rate_ticker is not None:
            self.rate = self.rate.reindex(index=self.calendar.series_dates, method='ffill')

    def compute_capitalization_factor(self):
        """
        Compute the Capitalization Factor CF(t)
        CF(t) = CF(t-1) * (1 + Rate(t-1) * ACT(t-1, t) / 360)
        CF(t0) = 1000
        Where Rate(t): The Rate
                ACT(t-1, t): Number of calendar_util days between Calculation Dates (t-1) (included) and (t) (excluded)
        """
        if self.rate_ticker is not None:
            cf_perf = 1.0 + self.rate.shift(1) / 100.0 * self.act / 360.0
            cf_perf.iat[self.calendar.t0_index] = self._il_initial_value
            self.cf = cf_perf.iloc[self.calendar.t0_index:].cumprod().reindex(self.calendar.series_dates)
        else:
            self.cf = pd.Series(self._il_initial_value, index=self.calendar.series_dates)

    def price_options(self):
        undl_il = self.undl_il_by_tag('CLOSE').fillna(method='bfill')
        settle_il = self.undl_il_by_tag('SETTLE').fillna(method='bfill')
        nominal_il = self.undl_il_by_tag('NOMINAL').fillna(method='bfill')
        vf_iv = None
        if self.is_tag('VegaFeesIV'):
            vf_iv = self.undl_il_by_tag('VegaFeesIV').fillna(method='bfill')
        self.hedge_spots = self.undl_il_by_tag('HEDGE').fillna(method='bfill').values
        self.spots = undl_il.values

        for group in self.groups:
            group.generate_calendar(self.calendar)
            group.generate_universe(undl_il, nominal_spots=nominal_il, settle_spots=settle_il, vega_fees_iv=vf_iv)

        pricer = None
        alternative_pricer = None
        if self.source == 'BBG':
            alternative_pricer = self.alternative_pricer

        if self.pricing == 'BlackScholes':
            pricer = self.alternative_pricer

        for group in self.groups:
            group.price_options(pricer, alternative_pricer)
            group.set_budget_adjustement_props()

    def compute_il(self):
        cf_perf = (self.cf / self.cf.shift()).values
        ccl = [0.0] * len(self.calendar.series_dates)
        mvop = [0.0] * len(self.calendar.series_dates)
        self.mvhp = [0.0] * len(self.calendar.series_dates)
        self.hppl = [0.0] * len(self.calendar.series_dates)
        oppl = [0.0] * len(self.calendar.series_dates)
        af = [0.0] * len(self.calendar.series_dates)
        il = [self._il_initial_value] * len(self.calendar.series_dates)
        self.delta_skew_adjustment = [0.0] * len(self.calendar.series_dates)
        delta = [0.0] * len(self.calendar.series_dates)
        vega = [0.0] * len(self.calendar.series_dates)
        self.gamma = [0.0] * len(self.calendar.series_dates)
        self.hedged_delta = [0.0] * len(self.calendar.series_dates)
        self.quantity_to_hedge = [0.0] * len(self.calendar.series_dates)
        aggregated_vega_fees = [0.0] * len(self.calendar.series_dates)
        shifted_il = [self._il_initial_value] * (len(self.calendar.series_dates) + 1)

        is_rebalancing = self.calendar.series_dates.isin(self.calendar.rebalancing_dates)
        t_rebal = self.calendar.t0_index

        portfolio_gamma_hedge = np.sum([x.weighting_scheme == "PortfolioDollarGammaHedge" for x in self.groups]) > 0

        for t in range(self.calendar.t0_index, len(self.calendar.series_dates)):
            if is_rebalancing[t]:
                t_rebal = t

            ccl_diff = 0
            # todo: to delete
            extra_lev = 0
            for group in self.groups:
                group.calculate_pnl_explanation_2(t)
                group.calculate_pnl_explanation_1(t)

                if portfolio_gamma_hedge:
                    if group.weighting_scheme == "PortfolioDollarGammaHedge":
                        new_entry_count, maturing_idx = group.in_out_indices[t]
                        if t > 0:
                            qty_list = np.sum([np.asarray(gr_.quantity[t][new_entry_count:]) * gr_.sign * np.asarray(
                                gr_.dollar_gamma_star[t][new_entry_count:]) for gr_ in self.groups[:-1]],
                                              axis=0)
                            upper_bound = np.sum(
                                [gr_.quantity[t][new_entry_count:] for gr_ in self.groups[:-1] if gr_.sign == -1],
                                axis=0)
                            lower_bound = np.asarray([0.] * len(upper_bound))
                            qty_list *= group.leverage / np.asarray(group.dollar_gamma_star[t][new_entry_count:])
                            qty_list = np.minimum(np.maximum(qty_list, lower_bound), upper_bound)
                            group.quantity[t] = [0.] * new_entry_count + list(qty_list)
                        else:
                            group.quantity[t] = [0.] * new_entry_count

                # todo: to delete
                # if group.weighting_scheme == "InverseDollarGamma":
                #     if group.type == 'PUT':
                #         extra_lev = group.compute_notional(t, t_rebal, shifted_il, self._il_initial_value)
                #     else:
                #         group.compute_notional(t, t_rebal, shifted_il, self._il_initial_value, extra_lev)
                # else:
                #     group.compute_notional(t, t_rebal, shifted_il, self._il_initial_value)
                group.compute_notional(t, t_rebal, shifted_il, self._il_initial_value)

            if len(self.groups) > 2:
                new_entry_count, maturing_idx = self.groups[3].in_out_indices[t]
                w_11 = np.asarray(deepcopy(self.groups[1].quantity[t][:new_entry_count]))
                w_22 = np.asarray(deepcopy(self.groups[3].quantity[t][:new_entry_count]))
                w_12 = np.asarray(deepcopy(self.groups[2].quantity[t][:new_entry_count]))
                if self.groups[3].extra_leverage in ['DPR', 'DPR_fixed_notional',
                                                     'DPR_notional_proportional_to_perf']:
                    for i_, group in enumerate(self.groups):
                        if i_ > 1:
                            extra_leverage = 1 / w_22
                        else:
                            extra_leverage = (w_22 - w_12) / (w_11 * w_22)
                        if self.groups[3].extra_leverage == 'DPR_fixed_notional':
                            extra_leverage *= self._il_initial_value / np.asarray(
                                self.groups[1].strike_spots[t][:new_entry_count])
                        elif self.groups[3].extra_leverage == 'DPR_notional_proportional_to_perf':
                            notional_value = self._il_initial_value if t < 1 else il[t-1]
                            extra_leverage *= notional_value / np.asarray(
                                self.groups[1].strike_spots[t][:new_entry_count])
                        extra_leverage /= group.count
                        group.compute_notional(t, t_rebal, shifted_il, self._il_initial_value, extra_lev=extra_leverage)
            else:
                new_entry_count, maturing_idx = self.groups[0].in_out_indices[t]
                if len(self.groups) == 1:
                    w_2 = 1
                else:
                    w_2 = np.asarray(deepcopy(self.groups[1].quantity[t][:new_entry_count]))
                if self.groups[0].weighting_scheme in ['InverseDollarGamma', 'InverseDollarGamma_times_vol_impli_sq']:
                    if self.groups[0].extra_leverage in ['DPR_fixed_notional',
                                                         'DPR_notional_proportional_to_perf']:
                        for i_, group in enumerate(self.groups):
                            extra_leverage = 1 / w_2
                            if self.groups[0].extra_leverage == 'DPR_fixed_notional':
                                extra_leverage *= self._il_initial_value / np.asarray(
                                    self.groups[1].strike_spots[t][:new_entry_count])
                            else:
                                notional_value = self._il_initial_value if t < 1 else il[t - 1]
                                extra_leverage *= notional_value / np.asarray(
                                    self.groups[1].strike_spots[t][:new_entry_count])
                            extra_leverage /= group.count
                            group.compute_notional(t, t_rebal, shifted_il, self._il_initial_value,
                                                   extra_lev=extra_leverage)

            for group in self.groups:
                group.compute_mvop(t)
                group.compute_delta(t)
                group.compute_vega(t)
                group.compute_gamma(t)
                group.compute_ccl_diff(t)
                group.compute_fees(t)

                mvop[t] += group.mvop[t]
                delta[t] += group.delta[t]
                vega[t] += group.vega[t]
                self.gamma[t] += group.gamma[t]
                ccl_diff += group.ccl_diff[t]
                aggregated_vega_fees[t] += group.vega_fees[t]

            oppl[t] = ccl_diff
            self.compute_hedged_delta_and_skew(t)
            self.compute_delta_hedge(t)

            if t == self.calendar.t0_index:
                af[t] = 0
                ccl[t] = self._il_initial_value + ccl_diff + self.hppl[t] - af[t]
                il[t] = self._il_initial_value
            else:
                af[t] = il[t - 1] * self.index_fees * self.act[t] / 360.0
                ccl[t] = ccl[t - 1] * cf_perf[t] + ccl_diff + self.hppl[t] - af[t]
                il[t] = mvop[t] + ccl[t] + self.mvhp[t]

            shifted_il[t + 1] = il[t]

        if self.is_excess_return:
            er = [0.0] * len(self.calendar.series_dates)
            for t in range(self.calendar.t0_index, len(self.calendar.series_dates)):
                if t == self.calendar.t0_index:
                    er[t] = self._il_initial_value
                else:
                    er[t] = er[t - 1] + il[t] - il[t - 1] * cf_perf[t]
            self.er = pd.Series(er, index=self.calendar.series_dates)

        self.mvop = pd.Series(mvop, index=self.calendar.series_dates)
        self.oppl = pd.Series(oppl, index=self.calendar.series_dates)
        self.af = pd.Series(af, index=self.calendar.series_dates)
        self.mvhp = pd.Series(self.mvhp, index=self.calendar.series_dates)
        self.hppl = pd.Series(self.hppl, index=self.calendar.series_dates)
        self.delta = pd.Series(delta, index=self.calendar.series_dates)
        self.vega = pd.Series(vega, index=self.calendar.series_dates)
        self.gamma = pd.Series(self.gamma, index=self.calendar.series_dates)
        self.ccl = pd.Series(ccl, index=self.calendar.series_dates)
        self.il = pd.Series(il, index=self.calendar.series_dates)
        self.aggregated_vega_fees = pd.Series(aggregated_vega_fees, index=self.calendar.series_dates)
        self.delta_skew_adjustment = pd.Series(self.delta_skew_adjustment, index=self.calendar.series_dates)
        self.hedged_delta = pd.Series(self.hedged_delta, index=self.calendar.series_dates)

    def compute_hedged_delta_and_skew(self, t):
        if not self.delta_hedged:
            self.hedged_delta[t], self.delta_skew_adjustment[t] = 0, 0
            return
        skews = self.get_skews(t)
        res_d, res_s = 0, 0
        for group in self.groups:
            if not group.delta_hedged:
                continue
            group.compute_skew(t, skews)
            if group.delta_lag:
                res_d += group.delta[t - 1] if t > self.calendar.t0_index else 0
                res_s += group.skew[t - 1] if t > self.calendar.t0_index else 0
            else:
                res_d += group.delta[t]
                res_s += group.skew[t]
        self.hedged_delta[t], self.delta_skew_adjustment[t] = res_d, res_s

    def get_skews(self, t):
        gps_to_adjust = [gp for gp in self.groups if gp.delta_skew_adjust]
        if len(gps_to_adjust) == 0:
            return
        matus = {}
        for group in gps_to_adjust:
            if len(group.all_positions[t]) == 0:
                continue
            for i, option in enumerate(group.all_positions[t]):
                if np.isnan(group.volas[t][i]):
                    continue
                if option.maturity in matus:
                    matus[option.maturity].update({option.strike: group.volas[t][i]})
                else:
                    matus[option.maturity] = {option.strike: group.volas[t][i]}
        skew = dict()
        for mt, val in matus.items():
            if len(val) <= 1:
                skew[mt] = 0.0
                continue
            listed_strike_high, listed_strike_low = max(val.keys()), min(val.keys())
            listed_implied_vol_high, listed_implied_vol_low = val[listed_strike_high], val[listed_strike_low]
            skew[mt] = 100.0 * (listed_implied_vol_high - listed_implied_vol_low) / \
                       (listed_strike_high - listed_strike_low)
        return skew

    def compute_delta_hedge(self, t):
        if not self.delta_hedged or t < self.calendar.t0_index:
            self.quantity_to_hedge[t] = self.mvhp[t] = self.hppl[t] = 0
            return
        self.quantity_to_hedge[t] = (self.hedged_delta[t] + self.delta_skew_adjustment[t]) \
                                    * self.spots[t] / self.hedge_spots[t]
        self.mvhp[t] = - self.quantity_to_hedge[t] * self.hedge_spots[t]
        self.hppl[t] = - self.quantity_to_hedge[t - 1] * self.hedge_spots[t] - self.mvhp[t]
        # costs
        self.hppl[t] -= self.delta_hedge_tc * abs(self.quantity_to_hedge[t - 1] - self.quantity_to_hedge[t]) \
                        * self.hedge_spots[t]
        self.hppl[t] -= self.delta_hedge_rc * abs(self.quantity_to_hedge[t - 1]) \
                        * self.hedge_spots[t - 1] * self.act[t] / 360.0 if t > self.calendar.t0_index else 0

    def intermediate_results_dump(self):
        df = super(RollOptions, self).intermediate_results_dump()

        df['UNDL'] = self.undl_il()
        for i, param in enumerate(self._undl_params):
            if 'Tag' in param:
                df[param['Tag']] = self.undl_il_by_tag(param['Tag'])

        if self.is_excess_return:
            df['ER'] = self.er
        df['CF'] = self.cf
        df['MVOP'] = self.mvop
        df['OPPL'] = self.oppl
        df['AF'] = self.af
        df['CCL'] = self.ccl
        df['MVHP'] = self.mvhp
        df['HPPL'] = self.hppl
        df['Delta'] = self.delta
        df['HedgedDelta'] = self.hedged_delta
        df['Skew'] = self.delta_skew_adjustment
        df['Vega'] = self.vega
        df['Gamma'] = self.gamma
        df['AggregatedVegaFees'] = self.aggregated_vega_fees

        for group_number, group in enumerate(self.groups):
            df_all_positions = pd.DataFrame(group.all_positions, index=self.calendar.series_dates)
            df_all_positions = df_all_positions.astype(str)
            df_all_positions = df_all_positions.applymap(lambda x: group.long_short.value + ' ' + x)
            df_maturing = pd.DataFrame(group.maturing, index=self.calendar.series_dates)
            df_maturing = df_maturing.astype(str)
            df_prices = pd.DataFrame(group.prices, index=self.calendar.series_dates)
            df_payoffs = pd.DataFrame(group.payoffs, index=self.calendar.series_dates)
            df_qty = pd.DataFrame(group.quantity, index=self.calendar.series_dates)
            df_nominal = pd.DataFrame(group.notional, index=self.calendar.series_dates)
            df_maturing_qty = pd.DataFrame(group.maturing_quantity, index=self.calendar.series_dates)
            df_vegas = pd.DataFrame(group.vegas, index=self.calendar.series_dates)
            df_payoffs_vegas = pd.DataFrame(group.payoffs_vegas, index=self.calendar.series_dates)
            df_deltas = pd.DataFrame(group.deltas, index=self.calendar.series_dates)
            df_gammas = pd.DataFrame(group.gamma, index=self.calendar.series_dates)
            df_payoffs_deltas = pd.DataFrame(group.payoffs_deltas, index=self.calendar.series_dates)
            df_volas = pd.DataFrame(group.volas, index=self.calendar.series_dates)
            df_roll_dates = pd.DataFrame(self.calendar.series_dates.isin(group.roll_dates),
                                         index=self.calendar.series_dates)
            df_vega_fees = pd.DataFrame(group.vega_fees, index=self.calendar.series_dates)
            df_roll_dates.columns = ['IS_ROLL ' + ' Grp_' + str(group_number)]
            df_vega_fees.columns = ['VEGA_FEES ' + ' Grp_' + str(group_number)]
            df_all_positions.columns = ['Ticker ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                        for val in list(df_all_positions.columns)]
            df_maturing.columns = ['MatTicker ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                   for val in list(df_maturing.columns)]
            df_prices.columns = ['Price ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                 for val in list(df_prices.columns)]
            df_payoffs.columns = ['MatPrice ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                  for val in list(df_payoffs.columns)]
            df_qty.columns = ['Qty ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                              for val in list(df_qty.columns)]
            df_nominal.columns = ['Notional ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                  for val in list(df_nominal.columns)]
            df_maturing_qty.columns = ['MatQty ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                       for val in list(df_maturing_qty.columns)]
            df_deltas.columns = ['Delta ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                 for val in list(df_deltas.columns)]
            df_gammas.columns = ['Gammas ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                 for val in list(df_gammas.columns)]
            df_payoffs_deltas.columns = ['MatDelta ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                         for val in list(df_payoffs_deltas.columns)]
            df_volas.columns = ['IVOL ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                for val in list(df_volas.columns)]
            df_vegas.columns = ['Vega ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                for val in list(df_vegas.columns)]
            df_payoffs_vegas.columns = ['MatVega ' + str(int(val) + 1) + ' Grp_' + str(group_number)
                                        for val in list(df_payoffs_vegas.columns)]

            columns_1 = ['theta_pnl', 'gamma_pnl', 'vega_pnl', 'volga_pnl',
                         'vanna_pnl', 'pnl_to_dP']
            columns_1 = [x + ' Grp_' + str(group_number) for x in columns_1]
            df_pnl_explanation_1 = group.add_pnl_up(
                [group.theta_pnl, group.gamma_pnl, group.vega_pnl, group.volga_pnl,
                 group.vanna_pnl, group.pnl_to_dP],
                pnl_columns=columns_1, cum_sum=False)

            columns_2 = ['vol_premium_component', 'gamma_covariance_effect', 'vega_term', 'd_gamma_term',
                         'residual_drift_term']
            columns_2 = [x + ' Grp_' + str(group_number) for x in columns_2]
            df_pnl_explanation_2 = group.add_pnl_up(
                [group.vol_premium_component, group.gamma_covariance_effect, group.vega_term, group.d_gamma_term,
                 group.residual_drift_term],
                pnl_columns=columns_2, cum_sum=True)
            df = pd.concat([df, df_pnl_explanation_1, df_pnl_explanation_2, df_roll_dates, df_vega_fees,
                            df_all_positions, df_maturing, df_qty, df_maturing_qty, df_prices, df_payoffs, df_deltas,
                            df_payoffs_deltas, df_vegas, df_volas, df_payoffs_vegas], axis=1, join_axes=[df.index])
        return df

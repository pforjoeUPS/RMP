from datetime import datetime as dt, timedelta
from enum import Enum
from functools import reduce

import numpy as np
import pandas as pd
import os
from dateutil import parser
from dateutil.rrule import rrulestr
from pandas.tseries.offsets import CustomBusinessDay

from src.exceptions import BacktestCalendarException

__all__ = ['BacktestCalendar', 'RecurringDates', 'TimeDelta']


class Frequency(Enum):
    NEVER = 'NEVER'
    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    QUARTERLY = 'QUARTERLY'
    SEMI_ANNUALLY = 'SEMI_ANNUALLY'
    YEARLY = 'YEARLY'
    RRULE = 'RRULE'
    SELECT_DATES = 'SELECT_DATES'


class OffDayConvention(Enum):
    PRECEDING = 'PRECEDING'
    FOLLOWING = 'FOLLOWING'


class RecurringDates(object):

    def __init__(self, params):
        super(RecurringDates, self).__init__()

        if not isinstance(params, dict):
            params = dict()

        self.frequency = Frequency(params.get('Frequency', Frequency.NEVER))
        self.months = params.get('Months')
        self.day_number = params.get('DayNumber', 1)
        self.rrule = params.get('RRule')
        self.lag = params.get('Lag', 0)
        self.off_day_convention = OffDayConvention(params.get('OffDayConvention', OffDayConvention.PRECEDING))
        self.month_change_convention = OffDayConvention(params.get('MonthChangeConvention', OffDayConvention.PRECEDING))
        self.interval = params.get('Interval', 1)
        self.dates = pd.DatetimeIndex(params.get('Dates', []))

        if self.frequency == Frequency.MONTHLY and self.months is None:
            self.months = list(range(1, 13))
        if self.frequency == Frequency.QUARTERLY and (self.months is None or len(self.months) != 4):
            start = self.months[0] if self.months is not None and len(self.months) > 0 else 1
            self.months = [(start - 1 + 3 * i) % 12 + 1 for i in range(4)]
        elif self.frequency == Frequency.SEMI_ANNUALLY and (self.months is None or len(self.months) != 2):
            start = self.months[0] if self.months is not None and len(self.months) > 0 else 1
            self.months = [(start - 1 + 6 * i) % 12 + 1 for i in range(2)]
        elif self.frequency == Frequency.YEARLY and (self.months is None or len(self.months) != 1):
            self.months = [1]

        if self.frequency == Frequency.RRULE and self.rrule is None:
            self.frequency = Frequency.NEVER

    @staticmethod
    def schema():
        schema = {
            'type': 'object',
            'properties': {
                'Frequency': {'type': 'string', 'enum': list(Frequency.__members__.keys())},
                'Months': {'type': 'array', 'items': {'type': 'number'}},
                'DayNumber': {'type': 'number'},
                'RRule': {'type': 'string'},
                'OffDayConvention': {'type': 'string', 'enum': list(OffDayConvention.__members__.keys())},
                'MonthChangeConvention': {'type': 'string', 'enum': list(OffDayConvention.__members__.keys())},
                'Interval': {'type': 'number'},
                'Dates': {
                    'type': 'array',
                    'items': {
                        'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                    }
                }
            }
        }

        return schema

    def run(self, open_dates):
        if self.frequency == Frequency.SELECT_DATES:
            dates = self.dates
        elif self.frequency == Frequency.RRULE:
            dates = rrule_open_dates(open_dates, self.rrule, self.off_day_convention, self.month_change_convention,
                                     self.lag)
        elif self.frequency == Frequency.DAILY:
            dates = open_dates
        elif self.frequency == Frequency.WEEKLY:
            dates = week_nth_days(open_dates, self.day_number)
        elif self.frequency in [Frequency.MONTHLY, Frequency.QUARTERLY, Frequency.SEMI_ANNUALLY, Frequency.YEARLY]:
            dates = month_nth_days(open_dates, self.day_number)
            mask = reduce(lambda x, y: x | (dates.month == y), self.months, False)
            dates = dates[mask]
        else:
            dates = pd.DatetimeIndex([])
        dates = dates[::self.interval]
        return dates


class TimeDelta(object):

    def __init__(self, params):
        super(TimeDelta, self).__init__()

        if not isinstance(params, dict):
            params = dict()

        self.bdays = abs(int(params.get('BDays', 0)))

    @staticmethod
    def schema():
        schema = {
            'type': 'object',
            'properties': {
                'BDays': {'type': 'number'}
            }
        }

        return schema

    def add(self, calendar, dates):
        shifted_dates = calendar.shift_over_open_dates(dates, self.bdays)
        return dates[:len(shifted_dates)], shifted_dates

    def subtract(self, calendar, dates):
        shifted_dates = calendar.shift_over_open_dates(dates, -self.bdays)
        return dates[-len(shifted_dates):], shifted_dates


class BacktestCalendar(object):
    FREQUENCIES = []

    ELIOT_CALENDAR_IDS = None

    def __init__(self, has_rebalancing_dates=False):
        super(BacktestCalendar, self).__init__()

        self.launch_date = None
        self.end_date = dt.today() - timedelta(days=1)

        self.open_dates = None
        self.disruption_dates = None
        self.additional_open_dates = None
        self.holidays = None

        self.union = False
        self.live_intersection = False

        self.start_calendar_date = None
        self.end_calendar_date = None

        self.series_dates = None
        self.computation_dates = None

        self.start_series_date = None
        self.end_series_date = None

        self.act = None

        self.t0 = None
        self.t0_index = None
        self.hist_window = 0

        self.has_rebalancing_dates = has_rebalancing_dates

        self.rebalancing_frequency = 'NEVER'
        self.rebalancing_months = None
        self.rebalancing_day_number = None
        self.rebalancing_rrule = None
        self.off_day_convention = 1
        self._review_lag = 0
        self.review_lag = 0

        self.rebalancing_dates = None
        self.review_dates = None

        self.first_review_included = None

    def market_holidays(self, market):
        eliot_holidays = pd.read_hdf(os.path.abspath(os.path.join("Data_cache.h5")),
                                     key="calendar")

        return eliot_holidays[eliot_holidays['is_closed_trading_deriv_mkt']].index

    @staticmethod
    def known_markets():
        return ["RINY"]

    @staticmethod
    def schema():
        schema = {
            'type': 'object',
            'properties': {
                'LaunchDate': {
                    'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                },
                'EndDate': {
                    'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                },
                'HistWindow': {
                    'type': 'number'
                },
                'OpenDays': {
                    'type': 'array',
                    'items': {
                        'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                    }
                },
                'Holidays': {
                    'anyOf': [{
                        'type': 'array',
                        'items': {
                            'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                        }
                    }, {
                        'type': 'string',
                        'enum': BacktestCalendar.known_markets()
                    }]
                },
                'Union': {
                    'type': 'boolean'
                },
                'StartCalendarDate': {
                    'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                },
                'EndCalendarDate': {
                    'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                },
                'DisruptionDates': {
                    'type': 'array',
                    'items': {
                        'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                    }
                },
                'AdditionalOpenDates': {
                    'type': 'array',
                    'items': {
                        'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                    }
                },
                'ReviewDates': {
                    'type': 'array',
                    'items': {
                        'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'string', 'format': 'date'}]
                    }
                },
                'RebalancingFrequency': {'type': 'string', 'enum': list(Frequency.__members__.keys())},
                'RebalancingMonths': {'type': 'array', 'items': {'type': 'number'}},
                'RebalancingDayNumber': {'type': 'number'},
                'RRule': {'type': 'string'},
                'RRuleOffDayConvention': {'type': 'string', 'enum': list(OffDayConvention.__members__.keys())},
                'ReviewLag': {'type': 'number'}
            }
        }

        return schema

    def set_calendar(self, calendar_params):
        if not isinstance(calendar_params, dict):
            calendar_params = dict()

        self.union = calendar_params.get('Union', self.union)
        self.live_intersection = calendar_params.get('LiveIntersection', self.live_intersection)
        if self.union and self.live_intersection:
            raise BacktestCalendarException('Either Union or LiveIntersection param should be true, or both false')

        if 'LaunchDate' in calendar_params:
            self.launch_date = parser.parse(calendar_params['LaunchDate'])
        if 'EndDate' in calendar_params:
            self.end_date = parser.parse(calendar_params['EndDate'])
        self.hist_window = int(calendar_params.get('HistWindow', 0))

        if calendar_params.get('DisruptionDates') is not None:
            self.disruption_dates = pd.DatetimeIndex([parser.parse(d)
                                                      for d in calendar_params['DisruptionDates']])

        if 'OpenDays' in calendar_params and calendar_params['OpenDays']:
            self.open_dates = pd.DatetimeIndex([parser.parse(d) for d in calendar_params['OpenDays']])
        elif 'Holidays' in calendar_params:
            # if it's a list
            if isinstance(calendar_params["Holidays"], list):
                # if the input is a list of str datetimes e.g ['2001-6-1', '2002-4-2', ...]
                if calendar_params['Holidays'][0][0].isnumeric():
                    self.holidays = [parser.parse(d) for d in calendar_params['Holidays']]
                # if it's a union of calendars
                else:
                    self.holidays = pd.DatetimeIndex([])
                    for cal in calendar_params['Holidays']:
                        self.holidays = self.holidays.union(self.market_holidays(cal))
            # elif it's a string e.g 'BBG_TE'
            elif isinstance(calendar_params['Holidays'], str):
                self.holidays = self.market_holidays(calendar_params['Holidays'])
            # else, another type !
            else:
                raise BacktestCalendarException("Unknown Holidays input")

            self.start_calendar_date = calendar_params.get('StartCalendarDate')
            self.end_calendar_date = calendar_params.get('EndCalendarDate')

            if self.disruption_dates is not None:
                self.holidays = self.holidays.union(self.disruption_dates)

            self.from_holidays()

            if 'AdditionalOpenDates' in calendar_params and calendar_params['AdditionalOpenDates']:
                self.additional_open_dates = pd.DatetimeIndex([parser.parse(d)
                                                               for d in calendar_params['AdditionalOpenDates']])
                self.open_dates = self.open_dates.union(self.additional_open_dates)

        if self.has_rebalancing_dates:
            if 'ReviewDates' in calendar_params and calendar_params['ReviewDates']:
                calendar_params['RebalancingFrequency'] = 'SELECT_DATES'
                self.review_dates = [parser.parse(d) for d in calendar_params['ReviewDates']]

            self.set_rebalancing_params(calendar_params.get('RebalancingFrequency', 'NEVER'),
                                        calendar_params.get('RebalancingMonths'),
                                        calendar_params.get('RebalancingDayNumber', 1),
                                        calendar_params.get('ReviewLag', 0),
                                        calendar_params.get('RRule', ''),
                                        OffDayConvention(calendar_params.get('RRuleOffDayConvention',
                                                                             OffDayConvention.PRECEDING)))

    def set_review_dates(self, review_dates, review_lag=None):
        if review_lag is None:
            review_lag = self._review_lag
        self.set_rebalancing_params('SELECT_DATES', review_lag=review_lag)
        self.review_dates = review_dates

    def to_dict(self):
        res = dict()

        res['Parameters'] = dict()
        res['Parameters']['LaunchDate'] = self.launch_date
        res['Parameters']['HistWindow'] = self.hist_window
        if self.has_rebalancing_dates:
            res['Parameters']['RebalancingFrequency'] = self.rebalancing_frequency
            res['Parameters']['RebalancingMonths'] = self.rebalancing_months
            res['Parameters']['RebalancingDayNumber'] = self.rebalancing_day_number
            res['Parameters']['ReviewLag'] = self._review_lag

            res['FirstReviewInOpenDays'] = self.first_review_included
            res['RebalancingDates'] = self.rebalancing_dates
            res['ReviewDates'] = self.review_dates

        res['FirstCalculationDateLookback'] = self.t0_index
        res['FirstCalculationDate'] = self.t0
        res['StartCalendarDate'] = self.start_series_date
        res['EndCalendarDate'] = self.end_series_date
        res['StartSeriesDate'] = self.start_series_date
        res['EndSeriesDate'] = self.end_series_date
        res['OpenDays'] = self.open_dates
        res['Holidays'] = self.get_holidays()

        return res

    def from_series(self, timeseries):
        if self.union:
            self.open_dates = reduce(lambda idx1, idx2: idx1.union(idx2), [ts.index for ts in timeseries])
        elif self.live_intersection:
            self.open_dates = reduce(lambda idx1, idx2: idx1.intersection(idx2).union(idx1[idx1 < idx2[0]]),
                                     sorted([ts.index for ts in timeseries], key=lambda x: x[0]))
        else:
            self.open_dates = reduce(lambda idx1, idx2: idx1.intersection(idx2), [ts.index for ts in timeseries])
        if self.disruption_dates is not None:
            self.open_dates = self.open_dates.difference(self.disruption_dates)

    def from_holidays(self, holidays=None):
        if holidays is not None:
            self.holidays = holidays
        if self.start_calendar_date is None and self.launch_date is not None:
            self.start_calendar_date = min(self.launch_date, min(self.holidays))
        if self.end_calendar_date is None:
            self.end_calendar_date = max(self.end_date, max(self.holidays))
        self.open_dates = open_dates_from_holidays(self.holidays, self.start_calendar_date, self.end_calendar_date,
                                                   lag_start_date=-self.hist_window)

    def set_rebalancing_params(self, freq='NEVER', months=None, day_number=1, review_lag=0, rule='', convention=1):
        self.rebalancing_frequency = freq
        self.rebalancing_months = months
        self.rebalancing_day_number = day_number
        self._review_lag = review_lag
        self.review_lag = review_lag

        if freq == 'DAILY':
            self.rebalancing_months = None
            self._review_lag = 0
        elif freq == 'WEEKLY':
            self.rebalancing_months = None
        elif freq == 'MONTHLY':
            if months is None:
                self.rebalancing_months = list(range(1, 13))
        elif freq == 'QUARTERLY':
            if months is None or len(months) != 4:
                start = months[0] if months is not None and len(months) > 0 else 1
                self.rebalancing_months = [(start - 1 + 3 * i) % 12 + 1 for i in range(4)]
        elif freq == 'SEMI_ANNUALLY':
            if months is None or len(months) != 2:
                start = months[0] if months is not None and len(months) > 0 else 1
                self.rebalancing_months = [(start - 1 + 6 * i) % 12 + 1 for i in range(2)]
        elif freq == 'YEARLY':
            if months is None or len(months) != 1:
                self.rebalancing_months = [1]
        elif freq == 'RRULE':
            self.rebalancing_rrule = rule
            self.off_day_convention = convention

    def compute_rebalancing_dates(self):
        # TODO: use all open days in 'week_nth_days' and 'month_nth_days'
        if self.rebalancing_frequency == 'RRULE':
            self.rebalancing_dates = rrule_open_dates(self.open_dates, self.rebalancing_rrule, self.off_day_convention)
            self.rebalancing_dates = self.rebalancing_dates[self.rebalancing_dates <= self.end_series_date]
        elif self.rebalancing_frequency == 'SELECT_DATES':
            self.rebalancing_dates = self.shift_over_open_dates(self.review_dates, self._review_lag)
        elif self.rebalancing_frequency == 'NEVER':
            self.rebalancing_dates = pd.DatetimeIndex([])
        elif self.rebalancing_frequency == 'DAILY':
            self.rebalancing_dates = self.series_dates
        elif self.rebalancing_frequency == 'WEEKLY':
            self.rebalancing_dates = week_nth_days(self.series_dates, self.rebalancing_day_number)
        else:
            self.rebalancing_dates = month_nth_days(self.series_dates, self.rebalancing_day_number)
            self.rebalancing_dates = [d for d in self.rebalancing_dates if d.month in self.rebalancing_months]

        self.rebalancing_dates = [d for d in self.rebalancing_dates if d > self.t0]
        # The launch date is a rebalancing date

        self.rebalancing_dates.insert(0, self.t0)

        self.review_dates = self.shift_over_open_dates(self.rebalancing_dates, -self._review_lag)

        self.review_dates = [d for d in self.review_dates if d > self.t0]

        if len(self.review_dates) == 0:
            self.review_dates.insert(0, self.t0)

        self.first_review_included = bool(self.t0_index - self._review_lag >= 0)

    def compute(self):
        if not self.open_dates_defined():
            raise BacktestCalendarException('No data about open dates')

        if self.start_calendar_date is None:
            self.start_calendar_date = self.open_dates.min()
        if self.end_calendar_date is None:
            self.end_calendar_date = self.open_dates.max()

        self.series_dates = self.open_dates[self.open_dates <= pd.Timestamp(self.end_date)]

        if self.launch_date is not None:
            t0_index = self.series_dates.searchsorted(np.datetime64(self.launch_date))
            if t0_index == len(self.series_dates):
                raise BacktestCalendarException('Could not find an open date newer than or equal to Launch Date')
            self.launch_date = self.series_dates[t0_index]
            start_date = self.series_dates[max(0, t0_index - self.hist_window)]
            self.series_dates = self.series_dates[self.series_dates >= start_date]

            if t0_index < self.hist_window:
                self.launch_date = self.series_dates[self.hist_window]
                self.t0_index = self.hist_window
            else:
                self.t0_index = self.series_dates.get_loc(self.launch_date)
        else:
            self.t0_index = self.hist_window

        if self.t0_index >= len(self.series_dates):
            raise BacktestCalendarException('Historical window greater than the number of series dates')

        self.t0 = self.series_dates[self.t0_index]

        self.computation_dates = self.series_dates[self.series_dates >= self.t0]

        self.start_series_date = self.series_dates.min()
        self.end_series_date = self.series_dates.max()

        if self.has_rebalancing_dates:
            self.compute_rebalancing_dates()

    def compare_to_series(self, series, raise_exception=True):
        for ticker in series:
            # Check end series too
            if series[ticker].index.min() > self.start_series_date:
                error_message = 'Missing data for \'%s\' between %s and %s' \
                                % (ticker, self.start_series_date.date(), series[ticker].index.min().date())
                if raise_exception:
                    raise BacktestCalendarException(error_message)
                else:
                    print(error_message)

    def open_dates_defined(self):
        return self.open_dates is not None

    def get_holidays(self):
        if self.holidays is None:
            self.holidays = open_dates_from_holidays(self.open_dates)
        return self.holidays

    def get_act(self, lag=1):
        series_dates_series = pd.Series(self.series_dates, index=self.series_dates)
        return (series_dates_series - series_dates_series.shift(lag)) / np.timedelta64(1, 'D')

    @staticmethod
    def get_act_over_dates(dates, pdates):
        if isinstance(dates, pd.DatetimeIndex):
            return [(date - pdate) / np.timedelta64(1, 'D') for date, pdate in zip(dates, pdates)]
        else:
            return (dates - pdates) / np.timedelta64(1, 'D')

    def get_roll_dates_over_computation_dates(self, lag):
        roll_dates = pd.Series(self.computation_dates[::lag], index=self.computation_dates[::lag])
        roll_dates = roll_dates.reindex(index=self.computation_dates).fillna(method='ffill')
        return roll_dates

    def shift_over_open_dates(self, dates, lag):
        if lag == 0:
            return dates
        dates_bool = self.open_dates.isin(dates)
        if lag > 0:
            return self.open_dates[lag:][dates_bool[:-lag]]
        return self.open_dates[:lag][dates_bool[-lag:]]

    def frequency_to_open_dates(self, frequency, months=None, day_number=None, rrule=None,
                                off_day_convention=OffDayConvention.PRECEDING):
        return frequency_to_open_dates(self.open_dates, frequency, months, day_number, rrule, off_day_convention)


def frequency_to_open_dates(open_dates, frequency, months=None, day_number=None, rrule=None,
                            off_day_convention=OffDayConvention.PRECEDING):
    if frequency == 'RRULE':
        dates = rrule_open_dates(open_dates, rrule, off_day_convention)
    elif frequency == 'DAILY':
        dates = open_dates
    elif frequency == 'WEEKLY':
        dates = week_nth_days(open_dates, day_number or 1)
    else:
        dates = month_nth_days(open_dates, day_number or 1)
        if frequency != 'MONTHLY':
            dates = [d for d in dates if d.month in months]
    return dates


def holidays_from_open_dates(open_dates, start_date=None, end_date=None, lag_start_date=0, lag_end_date=0):
    """
    Generate a list of holidays based on a list of business days

    Parameters
    ----------
    holidays : list of `datetime`
        The name of the library. e.g. 'library' or 'user.library'
    start_date : `datetime`
        The start date
    end_date : `datetime`
        The end date
    lag_start_date : `int`
        The lag in business days to be added to the start date
        Default: 0
    lag_end_date : `int`
        The lag in business days to be added to the end date
        Default: 0

    Returns
        -------
        `DatetimeIndex`
    """
    holidays_bd = CustomBusinessDay(holidays=open_dates)
    if start_date is None:
        start_date = min(open_dates)
    if end_date is None:
        end_date = max(open_dates)
    holidays = pd.date_range(start_date + lag_start_date * holidays_bd, end_date + lag_end_date * holidays_bd,
                             freq=holidays_bd)
    return holidays


def open_dates_from_holidays(holidays, start_date=None, end_date=None, lag_start_date=0, lag_end_date=0):
    """
    Generate a list of business days based on a list of holidays

    Parameters
    ----------
    holidays : list of `datetime`
        The name of the library. e.g. 'library' or 'user.library'
    start_date : `datetime`
        The start date
    end_date : `datetime`
        The end date
    lag_start_date : `int`
        The lag in business days to be added to the start date
        Default: 0
    lag_end_date : `int`
        The lag in business days to be added to the end date
        Default: 0

    Returns
        -------
        `DatetimeIndex`
    """
    business_days = CustomBusinessDay(holidays=holidays)
    if start_date is None:
        start_date = min(holidays)
    if end_date is None:
        end_date = max(holidays)
    open_dates = pd.date_range(start_date + lag_start_date * business_days, end_date + lag_end_date * business_days,
                               freq=business_days)
    return open_dates


def period_nth_day(open_dates, n, period):
    """
    Generate a list of the nth open day in each period

    Parameters
    ----------
    open_dates : DatetimeIndex
        The open dates
    n : int
        The monthday
    period : str
        attribute of Pandas.Timestamp

    Returns
        -------
        `DatetimeIndex`
    """
    open_dates_period = getattr(open_dates, period)
    if n > 0:
        return open_dates[n:][:-1][(open_dates_period[:-1] != open_dates_period[1:])[:-n]]
    if n != 0:
        n += 1
    if n == 0:
        return open_dates[:-1][open_dates_period[:-1] != open_dates_period[1:]]
    return open_dates[:n][:-1][(open_dates_period[:-1] != open_dates_period[1:])[-n:]]


def month_nth_days(open_dates, n):
    """
    Generate a list of the nth open day in each month

    Parameters
    ----------
    open_dates : DatetimeIndex
        The open dates
    n : int
        The monthday

    Returns
        -------
        DatetimeIndex
    """
    return period_nth_day(open_dates, n, 'month')


def week_nth_days(open_dates, n):
    """
    Generate a list of the nth open day in each week

    Parameters
    ----------
    open_dates : DatetimeIndex
        The open dates
    n : int
        The monthday

    Returns
        -------
        DatetimeIndex
    """
    return period_nth_day(open_dates, n, 'weekofyear')


def rrule_open_dates(open_dates, rule, off_day_convention, month_change_convention=OffDayConvention.PRECEDING, lag=0):
    """
    Generate a list of open dates from an RRule string

    Parameters
    ----------
    open_dates : DatetimeIndex
        The open dates
    rule : str
        The RRule string
    off_day_convention : int
        +1/-1 to choose the next/previous open date if an occurrence is not an open date
    month_change_convention : OffDayConvention
        to avoid the preceding convention if there's a month change
    lag : int
        relative lag to rrule generated dates

    Returns
        -------
        DatetimeIndex
    """
    start_calendar_date = open_dates.min()
    end_calendar_date = open_dates.max()
    try:
        rule = rrulestr('RRULE:' + rule, dtstart=start_calendar_date)
    except ValueError:
        raise BacktestCalendarException('Invalid RRule')
    else:
        occs = pd.DatetimeIndex(rule.between(after=start_calendar_date, before=end_calendar_date))
        cal_indices = open_dates.searchsorted(occs)
        cal_indices = cal_indices[cal_indices < len(open_dates)]
        occs = occs[:len(cal_indices)]
        if off_day_convention == OffDayConvention.PRECEDING:
            if month_change_convention != OffDayConvention.PRECEDING:
                same_month = open_dates[cal_indices].month == open_dates[cal_indices - 1].month
                cal_indices[(occs != open_dates[cal_indices]) & same_month] -= 1
            else:
                cal_indices[occs != open_dates[cal_indices]] -= 1
        cal_indices += lag
        cal_indices = cal_indices[(cal_indices >= 0) & (cal_indices < len(open_dates))]
        return open_dates[cal_indices]

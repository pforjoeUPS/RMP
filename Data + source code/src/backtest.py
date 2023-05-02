import uuid

import jsonschema
import numpy as np
import pandas as pd
import six

from src.calendar_util.bt_calendar import BacktestCalendar
from src.exceptions import BacktestException, BacktestInputException
from src.lib.utils import reindex_dict_of_series, series_to_dict, dataframe_to_dict, strip_strings

__all__ = ['Backtest']


class Backtest:

    def __init__(self, has_rebalancing_dates=False, min_undl=0, max_undl=-1, undl_order=None):
        super(Backtest, self).__init__()

        self._config = None

        self._name = None
        self.has_random_name = False

        self._currency = None
        self._return_type = None
        self._transaction_costs_factor = 0.0
        self._il_initial_value = 1000.

        self.calendar = BacktestCalendar(has_rebalancing_dates)

        self.min_undl = min_undl
        self.max_undl = max_undl

        self._undl_order = undl_order

        self._undl = []
        self._undl_params = []
        self._undl_il = {}

        self.il = pd.Series()  # A default value to avoid checking None when il is not calculated
        self._il_from_t0 = None
        self._performance = None

        self._return_calendar = True
        self._return_intermediate_results = False
        self._return_performance_stats = False

        self._warnings = []

        self._quantities = None
        self._transaction_costs = None

    @classmethod
    def schema(cls):
        schema = {
            'type': 'object',
            'properties': {
                'Name': {'type': 'string'},
                'Type': {'type': 'string'},
                'Parameters': {
                    'type': 'object',
                    'properties': cls.params_schema()
                },
                'Calendar': BacktestCalendar.schema(),
                'Underlyings': {
                    'type': 'array',
                    'items': {
                        'Index': {'type': 'object'},
                        'Parameters': {
                            'type': 'object',
                            'Tag': {'type': 'string'},
                            'properties': cls.undl_params_schema()
                        }
                    }
                }
            },
            'required': ['Type']
        }

        return schema

    @staticmethod
    def params_schema():
        return {}

    @staticmethod
    def undl_params_schema():
        return {}

    def name(self):
        if self._name is None:
            self._name = uuid.uuid4().hex
            self.has_random_name = True

        return self._name

    def currency(self):
        return self._currency

    def return_type(self):
        return self._return_type

    def undl(self, index=0):
        return self._undl[index]

    def count_undl(self):
        return len(self._undl)

    def undl_il(self, index=0):
        return self._undl_il[self._undl[index].name()]  # TODO: Avoid using dicts

    def param(self, name, default_value=None, sub_group=None):
        if sub_group is not None:
            if sub_group in self._config['Parameters']:
                value = self._config['Parameters'][sub_group].get(name, default_value)
            else:
                value = ""
        else:
            value = self._config['Parameters'].get(name, default_value)
        if value == "":
            value = default_value
        return value

    def undl_param(self, index, name, default_value=None):
        value = self._undl_params[index].get(name, default_value)
        if value == "":
            value = default_value
        return value

    def undl_position_by_tag(self, tag):
        pos = None
        for i, param in enumerate(self._undl_params):
            if 'Tag' in param and param['Tag'] == tag:
                pos = i
        return pos

    def is_tag(self, tag):
        for i, param in enumerate(self._undl_params):
            if 'Tag' in param and param['Tag'] == tag:
                return True
        return False

    def undl_il_by_tag(self, tag):
        return self.undl_il(self.undl_position_by_tag(tag) or 0)

    def _reorder_undl(self):
        pos_map = dict()
        undl_left = list(range(self.count_undl()))
        for flag, pos in self._undl_order.items():
            for index, undl_param in enumerate(self._undl_params):
                if undl_param.get('Flag') == flag:
                    pos_map[pos] = index
                    undl_left.remove(index)
                    break
        for i in range(self.count_undl()):
            if i not in pos_map:
                pos_map[i] = undl_left.pop(0)
        self._undl = [self._undl[pos_map[i]] for i in range(self.count_undl())]
        self._undl_params = [self._undl_params[pos_map[i]] for i in range(self.count_undl())]

    def add_warning(self, message):
        if isinstance(message, (six.string_types, six.binary_type)):
            self._warnings.append(message)

    def warnings(self):
        return self._warnings

    def run(self, config):
        if not isinstance(config, dict):
            config = dict()

        self._config = config

        schema = self.__class__.schema()
        try:
            jsonschema.validate(self._config, schema, format_checker=jsonschema.FormatChecker())
        except Exception as e:
            if hasattr(e, 'path'):
                raise BacktestInputException('InputError: (%s) %s' % ('/'.join(map(str, e.path)), str(e)))
            else:
                raise BacktestInputException('InputError: %s' % str(e))

        self._config = strip_strings(self._config)

        if 'Name' in self._config and self._config['Name'] != '':
            self._name = self._config['Name']

        if 'Calendar' in self._config:
            self.calendar.set_calendar(self._config['Calendar'])

        if 'Parameters' not in self._config:
            self._config['Parameters'] = dict()

        if 'Underlyings' in self._config:
            for undl in self._config['Underlyings']:
                self._undl.append(undl['Object'])
                if 'Parameters' not in undl:
                    undl['Parameters'] = dict()
                self._undl_params.append(undl['Parameters'])

        self.assert_correct_undl_number()

        if self._undl_order is not None:
            self._reorder_undl()

        for undl in self._undl:
            self._undl_il[undl.name()] = undl.get_il()

        self.load_params()

    def assert_correct_undl_number(self):
        if self.min_undl == self.max_undl and self.min_undl != len(self._undl):
            raise BacktestException('The number of underlyings must be equal to %d' % self.min_undl)
        if len(self._undl) < self.min_undl:
            raise BacktestException('The number of underlyings must be greater than %d' % self.min_undl)
        if self.max_undl != -1 and len(self._undl) > self.max_undl:
            raise BacktestException('The number of underlyings must be less than %d' % self.max_undl)

    def load_params(self):
        self._return_calendar = self.param('ReturnCalendar', False)
        self._return_intermediate_results = self.param('ReturnIntermediateResults', False)
        self._return_performance_stats = self.param('ReturnPerformanceStats', False)
        self._transaction_costs_factor = self.param('TransactionCosts', 0.0)
        self._il_initial_value = float(self.param('IndexLaunchValue', self._il_initial_value))

    def compute_calendar(self):
        if not self.calendar.open_dates_defined():
            self.calendar.from_series(self._undl_il.values())

        self.calendar.compute()

        # self.calendar.compare_to_series(self._undl_il)  # TODO: Maybe just check 'Na' after reindexing

        self.reindex_data()

    def reindex_data(self):
        reindex_dict_of_series(self._undl_il, self.calendar.series_dates)

    def get_il(self):
        if self._il_from_t0 is None:
            if self.calendar.t0 != self.il.index[0]:
                self._il_from_t0 = self.il[self.calendar.t0:]
            else:
                self._il_from_t0 = self.il

            self._il_from_t0 = self._il_from_t0.dropna()

        return self._il_from_t0

    def get_net_il(self):
        return self.get_il() - self.get_transaction_costs()

    def quantities(self):
        return self._quantities

    def get_undl_quantities_prices_tc(self):
        if self.quantities() is None:
            return [(pd.Series(1.0, index=self.get_il().index), self.get_il(), self._transaction_costs_factor)]

        results = []
        for qtty, undl in zip(self._quantities, self._undl):
            results.extend([(qtty * quantities.reindex(qtty.index, method='ffill'), prices, tc)
                            for quantities, prices, tc in undl.get_undl_quantities_prices_tc()])

        return results

    def get_transaction_costs(self):
        if self._transaction_costs is None:
            index = self.get_il().index
            self._transaction_costs = pd.Series(0.0, index=index)
            for quantity, price, tc_factor in self.get_undl_quantities_prices_tc():
                quantity = quantity.reindex(index, method='ffill')
                price = price.reindex(index, method='ffill')

                self._transaction_costs += tc_factor * np.abs(quantity - quantity.shift()) * price

            self._transaction_costs.iat[0] = 0.0

        return self._transaction_costs

    def to_dict(self):
        result = {
            'Name': self.name(),
            'IndexLevels': series_to_dict(self.get_il(), data_column='Value')
        }

        if self._return_calendar:
            result['Calendar'] = self.calendar.to_dict()

        if self._return_performance_stats:
            result['PerformanceStats'] = self.performance().to_dict()

        if self._return_intermediate_results:
            df = self.intermediate_results_dump()

            result['IntermediateResults'] = dataframe_to_dict(df)
            result['IntermediateResultsColumns'] = ['Date'] + list(df.columns)

        return result

    def intermediate_results_dump(self):
        df = pd.DataFrame(index=self.calendar.series_dates)
        df['IL'] = self.il

        return df

    def get_close_price(self, ticker, calendar_ffill=False):
        close_prices = self.load_close_price_from_db(ticker, 'Close')
        if not calendar_ffill:
            return close_prices.reindex(index=self.calendar.series_dates, method='ffill')
        else:
            return close_prices.reindex(index=self.calendar.series_dates).fillna(method='ffill')

    def load_close_price_from_db(self, ticker, column='Close'):
        is_single_column = not isinstance(column, list)
        columns = [column] if is_single_column else column

        import os
        key = '_'.join(ticker.lower().split(' ') + [column.lower()])
        data = pd.read_hdf(os.path.abspath(os.path.join("Data_cache.h5")), key=key)

        try:
            return data[column if is_single_column else columns]
        except:
            raise BacktestException('Could not find data for ticker: \'%s\'' % ticker)

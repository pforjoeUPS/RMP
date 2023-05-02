from src.backtest import Backtest
from src.lib.return_types import ReturnTypes
from src.exceptions import BacktestException

__all__ = ['DBSeries']


class DBSeries(Backtest):

    @staticmethod
    def params_schema():
        return {
            'ColumnName': {'type': 'string'}
        }

    def __init__(self):
        super(DBSeries, self).__init__(False, max_undl=0)

        self.column = 'Close'

    def run(self, config):
        super(DBSeries, self).run(config)

        self.name()

        if self.has_random_name:
            raise BacktestException('DBSeries: Name is required')

        self.column = self.param('ColumnName', self.column)

        self.load_data()

        self.compute_calendar()

    def load_data(self):
        self.il = self.load_close_price_from_db(self.name(), self.column)

        if not self.calendar.open_dates_defined():
            self.calendar.from_series([self.il])

        metadata = {} if self._name == "SPX Index" else {'ReturnType': 'Excess Return', 'Currency': 'USD'}
        if metadata is not None:
            if 'Currency' in metadata:
                self._currency = metadata['Currency']
            if 'ReturnType' in metadata:
                self._return_type = ReturnTypes.convert_return_type(metadata['ReturnType'])

    def reindex_data(self):
        self.il = self.il.reindex(index=self.calendar.series_dates, method='ffill')
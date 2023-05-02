__all__ = ['Option']

import numpy as np


class Option(object):

    def __init__(self, type_, spot, strike, maturity, exit_date, spot_at_maturity, undl, step=None, ticker=None,
                 strike_date=None, pseudo_strike_method='ceil'):
        super(Option, self).__init__()

        self._type = type_
        self._spot = spot
        self._step = step
        self.psd_stk_meth = pseudo_strike_method
        if self._step is None:
            self._strike = strike * spot
        else:
            if self.psd_stk_meth == "floor":
                self._strike = np.floor(strike * spot / self._step) * self._step
            elif self.psd_stk_meth == 'ceil':
                self._strike = np.ceil(strike * spot / self._step) * self._step
            else:
                self._strike = int(1 + strike * spot / self._step) * self._step
        self._maturity = maturity
        self._exit_date = exit_date
        self._undl = undl
        self._ticker = ticker
        self._strike_date = strike_date

        if self._type == 'CALL':
            self._payoff = max(0, spot_at_maturity - self._strike)
        elif self.type == 'PUT':
            self._payoff = max(0, self._strike - spot_at_maturity)

        self._additional_properties = dict()

    @property
    def type(self):
        return self._type

    @property
    def maturity(self):
        return self._maturity

    @property
    def exit_date(self):
        return self._exit_date

    @property
    def strike(self):
        return self._strike

    @property
    def undl(self):
        return self._undl

    @property
    def ticker(self):
        return self._ticker

    @property
    def strike_date(self):
        return self._strike_date

    @property
    def payoff(self):
        return self._payoff

    @property
    def spot(self):
        return self._spot

    @property
    def step(self):
        return self._step

    def set_additional_property(self, name, value):
        self._additional_properties[name] = value

    def get_additional_property(self, name):
        return self._additional_properties[name]

    def has_additional_property(self, name):
        return name in self._additional_properties

    def __str__(self):
        return '<%s %s %s %s>' % (self.type, self._undl, round(self._strike, 4), self._maturity.strftime('%Y-%m-%d'))

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    __repr__ = __str__

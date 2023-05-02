__all__ = ['BacktestException', 'BacktestCalendarException', 'BacktestFactoryException', 'BacktestInputException']


class BacktestException(Exception):
    pass


class BacktestCalendarException(BacktestException):
    pass


class BacktestFactoryException(BacktestException):
    pass


class BacktestInputException(BacktestException):
    pass
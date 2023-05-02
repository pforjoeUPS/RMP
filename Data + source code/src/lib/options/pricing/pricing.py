__all__ = ['OptionPricing']


class OptionPricing(object):

    def price(self, dates, options):
        raise NotImplementedError

    def get_rates_actualisation(self, dates, options):
        raise NotImplementedError

    def get_div_actualisation(self, dates, options):
        raise NotImplementedError

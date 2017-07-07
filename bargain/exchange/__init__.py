from abc import ABCMeta, abstractmethod
from collections import namedtuple


Ticker = namedtuple('Ticker', 'bid, ask')
Trade = namedtuple('Trade', 'timestamp, signal, price, amount')


class Order:

    def __init__(self, pair, amount, price):
        assert price > 0
        self.pair = pair
        self.amount = amount
        self.price = price

    @property
    def is_buy(self):
        return self.amount > 0

    @property
    def is_sell(self):
        return self.amount < 0

    def __repr__(self):
        return '%s: %.8f @ %.5g' % (self.pair, self.amount, self.price)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


class Exchange(metaclass=ABCMeta):

    @abstractmethod
    def get_orders(self, pair):
        pass

    @abstractmethod
    def place_order(self, pair, signal, amount, price):
        pass

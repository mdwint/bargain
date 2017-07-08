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

    @property
    def cost(self):
        return self.amount * self.price

    def __repr__(self):
        return '%s/%s: %.8f @ %.5g' % (self.pair[0].name, self.pair[1].name, self.amount, self.price)

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
    def get_wallet_balances(self):
        pass

    @abstractmethod
    def get_ticker(self, pair):
        pass

    @abstractmethod
    def get_past_trades(self, pair):
        pass

    @abstractmethod
    def get_active_orders(self, pair):
        pass

    @abstractmethod
    def place_order(self, order):
        pass

    @abstractmethod
    def place_orders(self, orders):
        pass

    @abstractmethod
    def cancel_order(self, order):
        pass

    @abstractmethod
    def cancel_orders(self, orders):
        pass

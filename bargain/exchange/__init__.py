from abc import ABCMeta, abstractmethod
from collections import namedtuple


Ticker = namedtuple('Ticker', 'bid, ask')


class Order:

    def __init__(self, pair, amount, price=None, id=None):
        self.pair = pair
        self.amount = amount
        self.price = price
        self.id = id

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
        return '%s %.8f %s @ %.5g %s' % ('BUY' if self.is_buy else 'SELL',
                                         abs(self.amount), self.pair[0].name,
                                         self.price or -1, self.pair[1].name)

    def __eq__(self, other):
        if isinstance(other, Order):
            # Compare up to significant digits
            return self.__repr__() == other.__repr__()
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Order):
            return not self.__eq__(other)
        return NotImplemented


class Trade(Order):

    def __init__(self, id, timestamp, pair, amount, price):
        super().__init__(pair, amount, price, id)
        self.timestamp = timestamp

    def __eq__(self, other):
        if isinstance(other, Trade):
            if self.timestamp != other.timestamp:
                return False
        return super().__eq__(other)


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

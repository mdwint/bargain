from abc import ABCMeta, abstractmethod
from collections import namedtuple


Ticker = namedtuple('Ticker', 'bid, ask')
Trade = namedtuple('Trade', 'timestamp, signal, price, amount')


class Order:

    def __init__(self, pair, amount, price):
        self.pair = pair
        self.amount = amount
        self.price = price


class Exchange(metaclass=ABCMeta):

    @abstractmethod
    def get_orders(self, pair):
        pass

    @abstractmethod
    def place_order(self, pair, signal, amount, price):
        pass

from collections import defaultdict
from datetime import datetime, timezone

import pytest

from bargain.exchange import Exchange, Order
from bargain.exchange.bitfinex import Bitfinex


class MockExchange(Exchange):

    def __init__(self):
        self._balance = defaultdict(float)
        self._orders = defaultdict(list)
        self._trades = defaultdict(list)
        self._price = defaultdict(float)
        self._prev_price = defaultdict(float)

    def get_wallet_balances(self):
        return self._balance

    def get_price(self, pair):
        return self._price[pair]

    def set_price(self, pair, price):
        self._prev_price[pair] = self._price[pair]
        self._price[pair] = price
        self._execute_orders(pair)
        self._prev_price[pair] = self._price[pair]

    def get_orders(self, pair):
        return tuple(self._orders[pair])

    def get_trades(self, pair):
        return tuple(self._trades[pair])

    def place_order(self, pair, amount, price=None):
        assert amount
        price = price or self.get_price(pair)

        if amount > 0:
            assert self._balance[pair[1]] >= amount * price
            self._balance[pair[1]] -= amount * price
        elif amount < 0:
            assert self._balance[pair[0]] >= abs(amount)
            self._balance[pair[0]] -= abs(amount)

        order = Order(pair, amount, price)
        self._orders[pair].append(order)
        self._execute_orders(pair)
        return order

    def place_orders(self, pair, orders):
        return tuple(self.place_order(pair, amount, price) for amount, price in orders)

    def cancel_order(self, order):
        self._orders[order.pair].remove(order)

    def cancel_orders(self, orders):
        for order in orders:
            self.cancel_order(order)

    def _execute_orders(self, pair):
        for order in self._orders[pair]:
            if not (self._prev_price[pair] <= order.price <= self._price[pair] or
                    self._prev_price[pair] >= order.price >= self._price[pair]):
                continue

            if order.amount > 0:
                self._balance[pair[0]] += order.amount
            elif order.amount < 0:
                self._balance[pair[1]] += abs(order.amount) * order.price

            self._orders[pair].remove(order)
            self._trades[pair].append(order)


@pytest.fixture
def exchange():
    return MockExchange()


@pytest.fixture(scope='session')
def now():
    return datetime.now(timezone.utc)


@pytest.fixture(scope='session')
def bitfinex():
    return Bitfinex()

from collections import defaultdict
from datetime import datetime, timezone

import pytest

from bargain.exchange import Exchange, Ticker, Trade
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

    def get_ticker(self, pair):
        price = self._price[pair]
        return Ticker(bid=price, ask=price)

    def _set_price(self, pair, price):
        self._prev_price[pair] = self._price[pair]
        self._price[pair] = price
        self._execute_orders(pair)
        self._prev_price[pair] = self._price[pair]

    def get_past_trades(self, pair, since, until, limit=1000):
        return tuple(self._trades[pair][-limit:])

    def get_active_orders(self, pair):
        return tuple(self._orders[pair])

    def place_order(self, order):
        if order.is_buy:
            assert self._balance[order.pair[1]] >= order.cost
            self._balance[order.pair[1]] -= order.cost
        elif order.is_sell:
            assert self._balance[order.pair[0]] >= abs(order.amount)
            self._balance[order.pair[0]] -= abs(order.amount)

        self._orders[order.pair].append(order)
        self._execute_orders(order.pair)
        return order

    def place_orders(self, orders):
        return tuple(self.place_order(o) for o in orders)

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
                self._balance[pair[1]] += abs(order.cost)

            trade = Trade(len(self._trades[pair]), datetime.now(timezone.utc),
                          pair, order.amount, order.price)

            self._orders[pair].remove(order)
            self._trades[pair].append(trade)


@pytest.fixture
def exchange():
    return MockExchange()


@pytest.fixture(scope='session')
def now():
    return datetime.now(timezone.utc)


@pytest.fixture(scope='session')
def bitfinex():
    return Bitfinex()
